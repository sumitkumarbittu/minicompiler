.PHONY: test clean build viz help

# Directories
OUT_DIR = build
SRC_DIR = src

# Compiler
PYTHON = python3
CC = clang

# Targets
all: help

help:
	@echo "MiniPython Compiler v1"
	@echo "Targets:"
	@echo "  build   - Permissions setup"
	@echo "  test    - Run test suite"
	@echo "  clean   - Remove artifacts"
	@echo "  viz     - Render PNGs from any DOT files in build/"
	@echo "  docker  - Build docker image"

build:
	chmod +x minipycc

test:
	@$(PYTHON) test_runner.py

clean:
	rm -rf $(OUT_DIR)
	rm -f *.pyc

viz:
	find $(OUT_DIR) -name "*.dot" -exec dot -Tpng {} -o {}.png \;

docker:
	docker build -t minipycc .
