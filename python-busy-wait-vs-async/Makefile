PYTHON := $(shell pwd)/.venv/bin/python
PIP := $(PYTHON) -m pip

THE_FILE ?= /tmp/the_file.txt
export

.PHONY: default
default: .venv help

.PHONY: help
help:
	@echo "commands:"; \
	echo "  make                         # create venv if needed and print info how to use it"; \
	echo "  make run                     # run the example script"; \
	echo "  make watch_the_file          # watch the file for changes (requires 'watch' command)"; \
	echo "  make write_to_file           # append lines to the file (Ctrl-D to stop)"; \
	echo ;\
	echo "variables:"; \
	echo "  THE_FILE=/tmp/the_file.txt"  # path to the file to be used


.venv: requirements.txt
	python3 -m venv .venv
	$(PIP) install -r requirements.txt

.PHONY: run
run: .venv
	$(PYTHON) async_file_write_class.py

.PHONY: watch_the_file $(THE_FILE)
watch_the_file: $(THE_FILE)
	watch -n 0.1 cat $(THE_FILE)

.PHONY: write_to_file $(THE_FILE)
write_to_file: $(THE_FILE)
	cat >> $(THE_FILE)

$(THE_FILE):
	touch $@

.PHONY: clean
clean:
	rm -rf .venv
