# MiniPython Compiler (minipycc)

A production-grade compiler for a Python subset, targeting LLVM IR.

## Features
- **Lexer**: Handles significant whitespace (INDENT/DEDENT).
- **Parser**: Recursive descent parser building a clean AST.
- **IR**: Custom intermediate representation (quadruples) with control flow graph.
- **Backend**: Emits valid LLVM IR (`.ll`).
- **Optimization**: (Stubbed for expansion).
- **Diagnostics**: Rich error messages with file/line/col context.
- **Visuals**: Auto-generates Graphviz DOT files for AST and CFG.

## Usage

### Local Build
Prerequisites: `python3`, `clang`, `graphviz`.

```bash
# Setup
chmod +x minipycc

# Compile a file
./minipycc compile testcases/valid/fact.py --out build/fact --emit tokens,ast,ir,cfg,llvm,exe,png --run

# Run full suite
make test
```

### Docker
Builds a container with all dependencies pre-installed.

```bash
# Build image
docker build -t minipycc .

# Run compiler inside container
docker run --rm -v "$PWD:/work" minipycc compile testcases/valid/fact.py --out build/fact_docker --run
```

## Architecture

- `src/core`: Reusable compiler library.
- `src/cli`: Command-line driver.
- `runtime`: Minimal C runtime for builtins (`print`).

## Output Artifacts (in --out dir)
- `result.json`: Manifest of build status and timings.
- `ast.png`: Visualization of the Abstract Syntax Tree.
- `cfg.png`: Visualization of the Control Flow Graph.
- `out.ll`: Generated LLVM IR.
- `a.out`: Final executable.
