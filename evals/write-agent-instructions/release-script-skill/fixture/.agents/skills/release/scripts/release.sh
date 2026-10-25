#!/usr/bin/env bash
# Cut a release of @acme/feature-flags. Run from the repo root.
set -e

read -p "Bump (patch/minor/major)? " BUMP

git fetch origin
git status

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

read -p "Push and publish v$NEW? (y/n) " OK
if [ "$OK" = "y" ]; then
  git push origin main --follow-tags
  npm publish
fi
