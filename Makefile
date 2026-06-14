.PHONY: install lint format type test gate

install:
	uv pip install -e ".[dev]"

lint:
	ruff check .

format:
	ruff format .

type:
	mypy src

test:
	pytest -q

# Full local gate — mirrors CI.
gate: lint
	ruff format --check .
	mypy src
	pytest -q
