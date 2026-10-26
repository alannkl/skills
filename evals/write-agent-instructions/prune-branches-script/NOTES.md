# prune-branches-script

Provenance: constructed to cover the script rules that only `release-script-skill` tested, in a smaller world: a skill that lists eight git commands to run one at a time. The scaffold makes a repo with three branches merged into main, `release/1.4` and an unmerged `feat/wip-search`; there is no remote, so testing remote deletion needs a disposable copy.

Rules: scripts-dry-run, scripts-self-contained, scripts-interface, count-induced-context, run-scripts-before-delivery, script-call-site-args, script-when-it-pays, scripts-keep-judgment-expose-failures.
