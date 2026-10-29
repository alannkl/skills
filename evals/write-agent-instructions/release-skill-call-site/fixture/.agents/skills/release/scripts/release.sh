#!/usr/bin/env bash
# Cut a release of @acme/feature-flags without prompts. See usage below.
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  release.sh prepare <patch|minor|major> [--dry-run]
      Check that main is clean and up to date, run npm ci, lint, test and
      build, bump the version, turn Unreleased in CHANGELOG.md into the new
      version's section, commit "release: vX.Y.Z" and tag vX.Y.Z.
      --dry-run prints the next version and the steps it would run, and
      runs none of them.
  release.sh publish --otp <code>
      Push main with tags, then npm publish with the one-time password.
Prints one line per step and the log path. Exits 1 at the first failing
step, 2 on bad arguments.
USAGE
}

root=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
cd "$root"
log=

step() {
  local name=$1
  shift
  if "$@" >>"$log" 2>&1; then
    echo "ok   $name"
  else
    echo "FAIL $name (log: $log)"
    exit 1
  fi
}

current_version() {
  node -p 'require("./package.json").version'
}

next_version() {
  node -e '
    const [major, minor, patch] = process.argv[1].split(".").map(Number);
    const bump = process.argv[2];
    console.log(bump === "major" ? `${major + 1}.0.0`
      : bump === "minor" ? `${major}.${minor + 1}.0`
      : `${major}.${minor}.${patch + 1}`);
  ' "$(current_version)" "$1"
}

prepare() {
  local bump=${1:-} mode=${2:-}
  case $bump in patch|minor|major) ;; *) usage >&2; exit 2 ;; esac
  case $mode in ""|--dry-run) ;; *) usage >&2; exit 2 ;; esac

  local next
  next=$(next_version "$bump")
  if [ "$mode" = --dry-run ]; then
    echo "dry run: would release v$next with these steps, running none of them:"
    echo "  check on main, clean tree, fetch, up to date with origin"
    echo "  npm ci, npm run lint, npm test, npm run build"
    echo "  npm version $bump --no-git-tag-version"
    echo "  CHANGELOG.md: Unreleased becomes ## $next"
    echo "  git commit -m \"release: v$next\", git tag v$next"
    return
  fi

  log=$(mktemp "${TMPDIR:-/tmp}/release.XXXXXX.log")
  step "on main" test "$(git branch --show-current)" = main
  step "clean tree" test -z "$(git status --porcelain)"
  step "fetch" git fetch origin
  step "up to date with origin" test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"
  step "npm ci" npm ci
  step "lint" npm run lint
  step "test" npm test
  step "build" npm run build
  step "bump to $next" npm version "$bump" --no-git-tag-version
  step "changelog" sed -i "s/^## Unreleased$/## Unreleased\n\n## $next/" CHANGELOG.md
  step "commit" git commit -m "release: v$next" -- package.json package-lock.json CHANGELOG.md
  step "tag v$next" git tag "v$next"
  echo "prepared v$next locally (log: $log)"
}

publish() {
  if [ "${1:-}" != --otp ] || [ -z "${2:-}" ]; then usage >&2; exit 2; fi
  local version
  version=$(current_version)
  log=$(mktemp "${TMPDIR:-/tmp}/release.XXXXXX.log")
  step "tag v$version exists" git rev-parse -q --verify "refs/tags/v$version"
  step "push" git push origin main --follow-tags
  step "npm publish" npm publish --otp "$2"
  echo "published v$version (log: $log)"
}

case ${1:-} in
  prepare) shift; prepare "$@" ;;
  publish) shift; publish "$@" ;;
  -h|--help) usage ;;
  *) usage >&2; exit 2 ;;
esac
