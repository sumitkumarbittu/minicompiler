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
	@echo "Running Tests..."
	@mkdir -p $(OUT_DIR)/tests
	@$(PYTHON) minipycc compile testcases/valid/fact.py --out $(OUT_DIR)/tests/fact --emit tokens,ast,ir,cfg,llvm,exe,png --run
	@echo "[PASS] Factorial"
	@$(PYTHON) minipycc compile testcases/valid/fib.py --out $(OUT_DIR)/tests/fib --emit llvm,exe,png --run
	@echo "[PASS] Fibonacci"
	@echo "Tests Completed."

clean:
	rm -rf $(OUT_DIR)
	rm -f *.pyc

viz:
	find $(OUT_DIR) -name "*.dot" -exec dot -Tpng {} -o {}.png \;

docker:
	docker build -t minipycc .
