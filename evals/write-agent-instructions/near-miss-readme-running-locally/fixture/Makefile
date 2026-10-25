.PHONY: setup dev test

# One-time: create the venv and download the sample dataset (~200 MB)
setup:
	python3 -m venv .venv
	.venv/bin/pip install -e ".[dev]"
	.venv/bin/python -m labelkit.sample download

# Runs the web app with auto-reload on http://localhost:8080
dev:
	.venv/bin/uvicorn labelkit.app:app --reload --port 8080

test:
	.venv/bin/pytest
