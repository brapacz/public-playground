PYTHON := $(shell pwd)/.venv/bin/python
PIP := $(PYTHON) -m pip

export

.PHONY: default
default: .venv main

.venv: requirements.txt
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	touch .venv

.PHONY: clean
clean:
	rm -rf .venv

.PHONY: main
main: .venv
	$(PYTHON) -m jupyter notebook example.ipynb
