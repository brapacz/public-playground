PYTHON := $(shell pwd)/.venv/bin/python
PIP := $(PYTHON) -m pip
DBT := $(shell pwd)/.venv/bin/dbt

.PHONY: default
default: .venv dbt-check help

.PHONY: help
help:
	@echo "\nGo to dbt holder and run dbt commands. You can activate venv with '. .venv/bin/activate' or use $(PYTHON) -m dbt <command>.\n" >&2

.venv: requirements.txt
	python3 -m venv .venv
	$(PIP) install -r requirements.txt

dbt-check: .venv dbt
	cd dbt; $(DBT) debug


.PHONY: clean
clean:
	rm -rf .venv
