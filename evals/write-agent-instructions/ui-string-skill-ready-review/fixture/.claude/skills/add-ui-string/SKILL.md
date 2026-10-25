---
name: add-ui-string
description: Add, change or rename user-visible text in the web app. Use when a change introduces new UI copy, edits existing copy, or renames a translation key.
---

# Add a UI string

All user-visible text goes through i18next. Never hardcode copy in components.

1. Add the key to `locales/en/<namespace>.json` only. The namespace matches the feature folder under `src/features/` (`checkout`, `account`); shared copy goes in `common`. Keys are camelCase and nested by section, e.g. `summary.totalLabel` in `checkout.json`.
2. In the component: `const { t } = useTranslation("<namespace>")`, then `t("summary.totalLabel")`.
3. Don't edit any other locale. Crowdin syncs them from `en` nightly and overwrites hand edits.
4. For counts, add `<key>_one` and `<key>_other` and call `t("<key>", { count })`.
5. To rename a key, rename it in `en` and in every `t()` call in the same change. Existing translations for the old key are lost, so say so in the PR description.
6. Run `npm run i18n:check`. It fails if code uses a key that is missing from `en`.
