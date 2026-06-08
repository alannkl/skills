# Frontend / UI Review Overlay

Use this overlay when a change affects rendered UI, user interaction, forms, navigation, client state, accessibility, responsive layout, or browser behavior.

## Review Focus

- User workflow: check the real task path, including entry state, editing, saving, cancellation, validation, errors, loading, empty states, disabled states, and recovery.
- Accessibility: verify semantic controls, labels, focus order, keyboard operation, visible focus, ARIA use, color contrast, reduced-motion behavior, and screen-reader-visible status changes.
- Responsive layout: check mobile and desktop constraints, text wrapping, overflow, scroll behavior, fixed/sticky elements, modals, menus, and viewport-height assumptions.
- State correctness: look for stale data, optimistic update rollback, duplicated submissions, disabled controls that still submit, lost edits, race conditions, and inconsistent URL or route state.
- Forms and validation: check client/server validation consistency, error placement, required fields, input modes, autocomplete, localization, and whether sensitive values are masked or cleared appropriately.
- Performance: check unnecessary rerenders, excessive client bundles, waterfall requests, image sizing, virtualization for long lists, and expensive work on input or scroll paths.
- Design-system fit: report convention breaks only when they create usability, accessibility, maintainability, or consistency risk.
- Tests and checks: prefer interaction tests, accessibility checks, route/state tests, and visual or screenshot checks for layout-sensitive changes.

## Common Findings

- A button is visually disabled but still reachable or submittable through keyboard or form submission.
- Loading or optimistic state allows duplicate writes.
- Text, menus, or dialogs overflow at common viewport sizes.
- A custom control lacks keyboard behavior or accessible name.

Avoid treating subjective visual preference as a finding unless it violates the design system or creates a concrete user-facing risk.
