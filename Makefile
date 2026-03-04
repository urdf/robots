PYTHON := python3

.DEFAULT_GOAL := help

.PHONY: help lint validate

help:
	@echo "Targets:"
	@echo "  lint      Validate catalog.json is well-formed JSON"
	@echo "  validate  Check catalog.json entries match robot directories and all paths exist"

lint:
	@$(PYTHON) -m json.tool catalog.json > /dev/null \
		&& echo "catalog.json: valid JSON" \
		|| (echo "catalog.json: invalid JSON" && exit 1)

validate: lint
	@$(PYTHON) scripts/validate.py
