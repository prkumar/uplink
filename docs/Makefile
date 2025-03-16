# Makefile for MkDocs documentation

# You can set these variables from the command line.
MKDOCS = mkdocs

# Default target
.PHONY: help
help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  serve      to start the live-reloading docs server"
	@echo "  build      to build the documentation site"
	@echo "  deploy     to deploy the site to GitHub Pages"

.PHONY: serve
serve:
	$(MKDOCS) serve

.PHONY: build
build:
	$(MKDOCS) build

.PHONY: deploy
deploy:
	$(MKDOCS) gh-deploy --force
