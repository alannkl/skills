#!/usr/bin/env bash
# Usage: release.sh <patch|minor|major> [--dry-run]
# Bumps package.json, commits, tags v<version> and pushes main and the tag.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

bump="${1:-}"; dry_run="${2:-}"
case "$bump" in patch|minor|major) ;; *) echo "usage: release.sh <patch|minor|major> [--dry-run]" >&2; exit 2 ;; esac

[[ "$(git branch --show-current)" == main ]] || { echo "not on main" >&2; exit 1; }
[[ -z "$(git status --porcelain)" ]] || { echo "working tree is dirty" >&2; exit 1; }

IFS=. read -r major minor patch <<<"$(node -p 'require("./package.json").version')"
case "$bump" in
  patch) patch=$((patch + 1)) ;;
  minor) minor=$((minor + 1)); patch=0 ;;
  major) major=$((major + 1)); minor=0; patch=0 ;;
esac
version="$major.$minor.$patch"

if [[ "$dry_run" == --dry-run ]]; then echo "would release v$version"; exit 0; fi

npm version "$version" --no-git-tag-version >/dev/null
git commit -qam "Release v$version"
git tag "v$version"
git push -q origin main "v$version"
echo "released v$version"
