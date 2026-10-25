#!/usr/bin/env bash
# Prepare a release of @acme/feature-flags: checks, version bump, changelog,
# release commit and tag. Run from the repo root. Pushing and publishing are
# done by hand afterwards.
set -e

read -p "Bump (patch/minor/major)? " BUMP

git fetch origin
git status
read -p "Continue with this tree? (y/n) " OK
[ "$OK" = "y" ] || exit 1

npm ci
npm run lint
npm test
npm run build

NEW=$(npm version "$BUMP" --no-git-tag-version)
NEW=${NEW#v}
sed -i "s/^## Unreleased$/## Unreleased\n\n## $NEW/" CHANGELOG.md

git add package.json package-lock.json CHANGELOG.md
git commit -m "release: v$NEW"
git tag "v$NEW"

echo "Tagged v$NEW. Push with: git push origin main --follow-tags, then npm publish"
