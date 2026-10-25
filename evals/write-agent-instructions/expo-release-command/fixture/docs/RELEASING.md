# Releasing Trailmate

We ship iOS and Android from `main`. Builds go through EAS.

1. Make sure `main` is green in CI and you've pulled.
2. Pick the version (semver). Bump `expo.version` in `app.json` AND `version` in `package.json` — they must match.
3. Bump the build numbers: `expo.ios.buildNumber` and `expo.android.versionCode` in `app.json`. These must go up on every store upload, even if the version didn't change. The stores reject reused numbers.
4. Add a section to `CHANGELOG.md` for the new version and move the items from "Unreleased" into it.
5. Commit as `chore(release): vX.Y.Z` and tag `vX.Y.Z`.
6. `npm test` and `npx tsc --noEmit`.
7. `eas build --platform all --profile production`
8. When both builds finish: `eas submit --platform all --latest`
9. Push the commit and tag: `git push origin main --tags`

## Old notes (pre-EAS)

We used to run `expo build:ios` / `expo build:android`. Don't — classic builds are gone.
