.PHONY: install test verify

install:
	pip install -e ".[dev]"

test:
	pytest -q

verify:
	bash scripts/verify.sh
