---
name: pr-description
description: Write the pull request title and body for the current branch. Use when opening a PR or when asked for a PR description.
---

# PR description

1. Run `git log main..HEAD --oneline` and `git diff main...HEAD --stat` to see what changed.
2. Title: `<area>: <summary>`, lowercase, under 70 characters. Areas: `guides`, `api-ref`, `theme`, `build`, `ci`.
3. Body sections, in this order:
   - **Summary** — 1-3 sentences on what changed and why.
   - **Files changed** — every changed file with a one-line note on what changed in it.
   - **Preview** — link to the Netlify deploy preview: `https://deploy-preview-<PR number>--hollowdocs.netlify.app`, pointing at the page most affected by the change.
   - **Checklist** — copy from `.github/pull_request_template.md` and tick what you actually did.
4. If the PR closes an issue, add `Closes #<n>` as the last line.
5. Create the PR with `gh pr create --title "<title>" --body-file <file>`, then edit the Preview link once you know the PR number.

## Example

    guides: add self-hosting walkthrough

    **Summary**
    Adds a step-by-step self-hosting guide covering Docker and bare-metal installs, and links it from the Guides nav.

    **Files changed**
    - `docs/guides/self-hosting.md` — new guide
    - `mkdocs.yml` — add nav entry
    - `docs/assets/selfhost-arch.png` — architecture diagram

    **Preview**
    https://deploy-preview-212--hollowdocs.netlify.app/guides/self-hosting/

    **Checklist**
    - [x] `mkdocs build --strict` passes
    - [x] Images under 300 KB

    Closes #198
