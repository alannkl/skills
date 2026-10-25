# ridgeline-triage

Classifies inbound Zendesk tickets and routes them to a queue.

- `triage/classifier.py` — LLM call + parsing
- `triage/router.py` — category -> queue mapping; low-confidence goes to humans

Run tests with `pytest`.
