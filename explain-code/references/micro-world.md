# Micro-World

Build a tiny interactive simulation the user inhabits to feel the logic work.

- Build a single self-contained HTML file — embedded CSS and JavaScript, no external dependencies — that simulates just the target logic with example data and lets the user probe it: scrub steps, drag inputs, toggle branches, watch the result change.
- Derive the simulated logic directly from the source and name every simplification. It models the code — it is not the code, and passing in the simulation proves nothing about runtime.
- Every control must answer a "what happens if" question the user could actually ask; interactivity that only decorates teaches nothing — fall back to a static diagram.
- Write it to a `.tmp/` folder under the repo root (creating the folder if needed), or publish it as an artifact where the harness supports that. It is throwaway: never commit it and never write it anywhere else in the project tree.
- A micro-world drifts from the source easily: rebuild it after the code changes rather than trusting an old simulation.
