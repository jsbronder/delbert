SHELL = /usr/bin/env bash
TOPDIR := $(shell readlink -f $(dir $(lastword $(MAKEFILE_LIST))))

PACKAGE := $(shell python setup.py --name)
TESTS := $(wildcard test/test_*.py)
VERSION := $(shell python setup.py --version)

MODULE_FILES := $(shell find $(PACKAGE)/ -type f -name '*.py')
PLUGIN_FILES := $(shell find plugins/ -type f -name '*.py')
BIN_FILES := $(wildcard bin/*)
REQUIREMENTS := $(wildcard requirements*.txt)
EXTRA_FILES = db/cah-black.txt \
			  db/cah-white.txt \
			  db/sprint.yaml

FLAKE_TARGETS := $(MODULE_FILES:%=flake-%) $(BIN_FILES:%=flake-%) $(PLUGIN_FILES:%=flake-%)
TEST_TARGETS := $(TESTS:test/test_%.py=test_%)

.PHONY: requirements $(REQUIREMENTS) test $(TEST_TARGETS) install clean

all: dist


requirements: $(REQUIREMENTS)
$(REQUIREMENTS):
	@pip install -r $@


dist: dist/$(PACKAGE)-$(VERSION).tar.gz
dist/$(PACKAGE)-$(VERSION).tar.gz: $(MODULE_FILES) setup.py $(EXTRA_FILES)
	python setup.py sdist


flake: $(FLAKE_TARGETS)
$(FLAKE_TARGETS):
	flake8 --filename='*' $(@:flake-%=%)


test: flake
	@failed=""; \
	for test in $(TESTS); do \
		echo "Testing $${test#*_}"; \
		python $${test} --verbose; \
		if [ $$? -ne 0 ]; then \
			failed+=" $${test}"; \
		fi; \
		echo;echo; \
	done; \
	if [ -n "$${failed}" ]; then \
		echo "Failed tests: $${failed}"; \
		exit 1; \
	else \
		echo "All tests passed."; \
	fi
$(TEST_TARGETS):
	python test/$(@).py -v

install: dist
	pip install --no-deps \
		--upgrade --force-reinstall --no-index dist/$(PACKAGE)-$(VERSION).tar.gz


clean:
	rm -rf dist
	rm -rf $(PACKAGE).egg-info
