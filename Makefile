ECHOCMD:=/bin/echo -e
SHELL := /bin/bash

args = `arg="$(filter-out $@,$(MAKECMDGOALS))" && echo $${arg:-${1}}`

PYTHON_VERSION := $(shell python3 --version)

PROJECT_NAME := $(shell python3 setup.py --name)
PROJECT_VERSION := $(shell python3 setup.py --version)

# guess OS (Linux, Darwin,...)
OS_NAME := $(shell uname -s 2>/dev/null || echo "unknown")
CPU_ARCH := $(shell uname -m 2>/dev/null || uname -p 2>/dev/null || echo "unknown")

# Included custom configs change the value of MAKEFILE_LIST
# Extract the required reference beforehand so we can use it for help target
MAKEFILE_NAME := $(word $(words $(MAKEFILE_LIST)),$(MAKEFILE_LIST))

# Application
APP_ROOT := $(abspath $(lastword $(MAKEFILE_NAME))/..)

# it is evaluated when is used (recursively expanded variable)
# https://ftp.gnu.org/old-gnu/Manuals/make-3.79.1/html_chapter/make_6.html#SEC59
# get the tag
git_tag = $(shell git describe --abbrev=0 --tag)
# regex version project
tag_regex := ^[0-9]+\.[0-9]+(\.[0-9]+)?$$

BOLD := \033[1m
RESET := \033[0m

.PHONY: version
version: ## display current version
	@-echo "$(PROJECT_NAME) version: $(PROJECT_VERSION)"

.PHONY: info
info: ## display make information
	@echo "Information about your make execution:"
	@echo "  OS Name                $(OS_NAME)"
	@echo "  CPU Architecture       $(CPU_ARCH)"
	@echo "  Python Version         $(PYTHON_VERSION)"
	@echo "  Application Root       $(APP_ROOT)"
	@echo "  Application Name       $(PROJECT_NAME)"
	@echo "  Application Version    $(PROJECT_VERSION)"

.PHONY: bake
bake: ## bake without inputs and overwrite if exists.
	@cookiecutter --no-input . --overwrite-if-exists

.PHONY: bake-with-inputs
bake-with-inputs: ## bake with inputs and overwrite if exists.
	@cookiecutter . --overwrite-if-exists

.PHONY: install
install: ## Install the poetry environment
	@echo "🚀 Creating virtual environment using pyenv and poetry"
	@poetry install
	@poetry shell

.PHONY: format
format: ## Format code using isort and black.
	@echo "🚀 Formatting code: Running isort and black"
	@isort .
	@black .

.PHONY: lint
lint: ## Check code formatting using isort and black.
	@echo "🚀 Checking code formatting: Running isort and black"
	@isort --check-only --diff $(APP_ROOT)
	@black --check $(APP_ROOT)

.PHONY: test
test: ## Test the code with pytest
	@echo "🚀 Testing code: Running pytest"
	@pytest -s --doctest-modules tests

.PHONY: bump-version
bump-version: ## Bump the project version
	@poetry version $(PROJECT_VERSION)

## --- Build and publish packages --- ##

.PHONY: git-tags-local
git-tags-local: ## List local repository tags list
	@echo "Local Tags:"
	@git tag -n

.PHONY: git-tags-remote
git-tags-remote: ## List remote repository tags list
	@echo "Remote tags:"
	@git ls-remote --tags origin

.PHONY: git-tags
git-tags: git-tags-local git-tags-remote ## List local and remote repository tags


.PHONY: release
release: ## Create a Github release commit + tag
ifeq ($(PROJECT_VERSION),)
	@echo "nothing yet here"
else
	@if ! [[ $(PROJECT_VERSION) =~ ^[0-9]+\.[0-9]+(\.[0-9]+)?$$ ]]; then \
		echo "(!!) ERROR - bad version; expected x.y[.z], where x, y, and z are all integers." >&2; \
		exit 1; \
	fi
#	@if git status --porcelain | grep .; then \
#		echo "(!!) ERROR - Git working tree is dirty; commit changes and try again." >&2; \
#		exit 1; \
#	fi
	@if git tag | grep $(PROJECT_VERSION); then \
		echo "(!!) ERROR - release $(PROJECT_VERSION) already exists." >&2; \
		exit 1; \
	fi
	@git add $^ && git commit -m 'Release $(PROJECT_VERSION)'
	@git tag $(PROJECT_VERSION)

	@git push && git push --tags
endif

.PHONY: build
build: clean-build bump-version ## Build wheel file using poetry
	@echo "🚀 Creating wheel file"
	@poetry build

.PHONY: publish
publish: ## publish a release to pypi.
	@echo "🚀 Publishing: Dry run."
	@echo $(PYPI_TOKEN)
	@poetry config pypi-token.pypi $(PYPI_TOKEN)
	@poetry publish --dry-run
	@echo "🚀 Publishing."
	@poetry publish

.PHONY: build-and-publish
build-and-publish: build publish ## Build and publish.

## --- Cleanup targets --- ##

.PHONY: clean
clean: clean-all ## alias for 'clean-all' target

.PHONY: clean-all
clean-all: clean-build clean-pyc clean-test ## remove all artifacts

.PHONY: clean-build
clean-build: ## remove build artifacts
	@echo "Cleaning build artifacts..."
	@-rm -fr build/
	@-rm -fr dist/
	@-rm -fr downloads/
	@-rm -fr .eggs/
	@find . -type d -name '*.egg-info' -exec rm -fr {} +
	@find . -type f -name '*.egg' -exec rm -f {} +

.PHONY: clean-pyc
clean-pyc: ## Remove Python file artifacts
	@echo "Cleaning Python artifacts..."
	@find . -type f -name '*.pyc' -exec rm -f {} +
	@find . -type f -name '*.pyo' -exec rm -f {} +
	@find . -type f -name '*~' -exec rm -f {} +
	@find . -type f -name '__pycache__' -exec rm -fr {} +

.PHONY: clean-test
clean-test: ## remove test and coverage artifacts
	@echo "Cleaning tests artifacts..."
	@-rm -fr .tox/
	@-rm -fr .pytest_cache/
	@-rm -fr htmlcov/
	@-rm -f .coverage*
	@-rm -f coverage.*
	@-rm -fr "$(APP_ROOT)/coverage/"
	@-rm -fr "$(APP_ROOT)/node_modules"
	@-rm -f "$(APP_ROOT)/package-lock.json"

## --- Documentation section --- ##

.PHONY: docs-test
docs-test: ## Test if documentation can be built without warnings or errors
	@mkdocs build -s

.PHONY: docs
docs: ## Build and serve the documentation
	@mkdocs serve

.PHONY: coverage
coverage: ## Generate coverage reports
	@coverage erase
	@coverage run --source $(APP_ROOT) setup.py test
	@coverage report -m --skip-empty
	@coverage html -q


## --- Misc --- ##

.PHONY: todos
todos:  ## Look for TODOs in the source files.
	@git grep -EIn "TODO|FIXME|XXX" -- './*' ':(exclude)Makefile'

.PHONY: authors
authors: ## Recreate the AUTHORS.md file with all the authors that have committed to the code
	@echo "Authors\n=======\n\nA huge thanks to all of our contributors:\n" > docs/AUTHORS.md
	@git log --raw | grep "^Author: " | cut -d ' ' -f2- | cut -d '<' -f1 | sed 's/^/- /' | sort | uniq >> docs/AUTHORS.md

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
