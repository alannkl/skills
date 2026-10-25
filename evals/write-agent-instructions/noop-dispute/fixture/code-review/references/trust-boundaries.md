# Trust Boundaries Review Overlay

Use this overlay when a change affects authorization, authentication, secrets, personal data, input validation, CI workflows, infrastructure configuration, dependencies, permissions, network boundaries, uploads, webhooks, or privileged operations.

## Review Focus

- Boundary identification: identify which inputs, identities, services, files, URLs, dependencies, and generated outputs are untrusted.
- Authorization: check object-level access, tenant isolation, privilege escalation, role changes, confused-deputy paths, and whether server-side checks match client-visible controls; for a new or changed handler, compare against sibling handlers on the same resource for missing or weakened controls.
- Authentication and sessions: check token handling, expiry, refresh, replay, CSRF, cookie attributes, session fixation, and logout or revocation behavior.
- Input validation: check injection risks, path traversal, SSRF, unsafe redirects, command execution, HTML/script injection, deserialization, file uploads, and parser edge cases. When validation and use parse or normalize separately, trace a value they interpret differently; verify the checked identity or field is the one used by the sensitive operation.
- Secrets and sensitive data: check logs, errors, telemetry, traces, cache keys, URLs, browser storage, model-visible context, generated artifacts, and source, config, or CI files for accidental exposure.
- Dependencies and supply chain: check new packages, version bumps, transitive risk, install scripts, license or provenance concerns, and whether dependency behavior changes trust assumptions.
- CI and infrastructure: trace untrusted inputs to privileged steps, and check omitted permission or exposure settings against platform defaults.
- Auditability: check whether sensitive actions have useful, non-sensitive audit trails and whether failures are diagnosable without leaking data.
- Tests: prefer negative authorization tests, tenant-crossing tests, injection cases, webhook authenticity tests, and secret-redaction checks.

## Common Findings

- A client-side permission check is added without enforcing the same rule server-side.
- Logs include tokens, private identifiers, full payloads, or user-provided secrets.
- A new URL fetch path can reach internal services or local files.
- A privileged action trusts a user-controlled ID without checking ownership.

For security findings, name the attacker and victim, the boundary crossed, the concrete attacker capability, the trigger path, and the impact. Do not inflate severity without a plausible exploit path.
