# MiniPython Compiler (`minipycc`)

`minipycc` is an educational compiler for a statically compilable Python subset.
It lexes and parses MiniPython source, performs semantic checks, lowers the AST
to a small custom IR, optionally runs optimization and analysis passes, emits
LLVM IR, links against a C runtime, and can run the generated native executable.

The compiler is intentionally transparent: each phase can emit artifacts such as
tokens, AST graphs, IR dumps, CFG graphs, optimization reports, LLVM IR, and run
output.

## What It Supports

### Core Language

- Python-style significant indentation using spaces.
- Top-level statements, compiled into a synthetic `main` function.
- Function definitions with positional arguments.
- Recursive and non-recursive function calls.
- Assignment with first-assignment variable definition.
- `return`.
- `if` / `else`.
- `while`.
- `for i in range(...)` with:
  - `range(stop)`
  - `range(start, stop)`
  - `range(start, stop, step)`
- `break`, `continue`, and `pass`.

### Types and Values

- 64-bit integers.
- Booleans: `True`, `False`.
- Floats using LLVM `double`.
- Strings for literals, printing, and equality/inequality checks.
- Integer lists:
  - list literals: `[1, 2, 3]`
  - indexing: `xs[0]`
  - indexed assignment: `xs[0] = 10`
  - append: `xs.append(4)`
  - length: `len(xs)`
  - runtime bounds checking.

### Operators

- Arithmetic: `+`, `-`, `*`, `/`.
- Unary: `+x`, `-x`, `not x`.
- Comparisons: `==`, `!=`, `<`, `<=`, `>`, `>=`.
- Boolean/logical: `and`, `or`, `not`.
- Parenthesized expressions.

### Builtins

- `print(value)` supports integers, booleans, floats, and strings.
- `len(xs)` supports lists.
- `range(...)` is supported in `for` loops.

### Diagnostics and Checks

- Undefined variable checks.
- Undefined function checks.
- Function arity checks.
- Assignment type compatibility checks.
- Invalid `break` / `continue` outside loops.
- List index type checks.
- Basic function return compatibility checks.
- Structured failure output in `result.json`.

## Current Limitations

This is still a compact teaching compiler, not full Python.

- Tabs are not supported for indentation.
- Function parameters are currently treated as integers.
- User-defined functions currently return int-compatible values.
- Lists currently store integers only.
- Strings support printing and equality, but not concatenation.
- Negative-step `range(...)` loops are not yet implemented correctly.
- No dictionaries, classes, imports/modules, exceptions, lambdas, decorators, or
  comprehensions.
- No keyword arguments, default arguments, type annotations, or nested function
  scopes.
- The LLVM target triple is currently hard-coded for macOS in the backend.

## Requirements

Local development requires:

- Python 3.9+
- Clang / LLVM
- Graphviz, only if you want PNG graph rendering
- `make`, optional

macOS:

```bash
brew install llvm graphviz
```

Debian/Ubuntu:

```bash
sudo apt update
sudo apt install clang llvm graphviz build-essential make
```

## Quick Start

Make the compiler executable:

```bash
chmod +x minipycc
```

Compile and run a sample:

```bash
./minipycc compile testcases/valid/v2_v3.py \
  --out build/v2_v3 \
  --emit all \
  --run
```

Expected output:

```text
--- execution output ---
True
5.5
MiniPython
True
7
14
4
------------------------
Build successful. Artifacts in build/v2_v3
```

Compile a smaller arithmetic sample:

```bash
./minipycc compile testcases/valid/fact.py \
  --out build/fact \
  --emit llvm,exe \
  --run
```

Expected program output:

```text
-28183
```

## CLI Reference

```bash
./minipycc compile <SOURCE_FILE> --out <OUTPUT_DIR> [FLAGS]
```

| Flag | Description |
| :--- | :--- |
| `--out <dir>` | Required output directory. The directory is deleted and recreated for each compile. |
| `--emit <list>` | Comma-separated artifacts to emit. Use `all` for the full set. |
| `--run` | Execute the generated native binary after a successful build. |
| `--no-opt` | Skip the optimizer. |
| `--metrics` | Accepted by the CLI for metrics workflows. |
| `--analysis` | Run static analysis and emit complexity/dominator information. |

Supported `--emit` values:

```text
tokens, ast, ir, cfg, opt, analysis, llvm, exe, png, all
```

Examples:

```bash
# Emit only LLVM IR.
./minipycc compile testcases/valid/fib.py --out build/fib --emit llvm

# Emit LLVM and executable, then run it.
./minipycc compile testcases/valid/gcd.py --out build/gcd --emit llvm,exe --run

# Emit every artifact, including DOT/PNG visualizations when Graphviz is present.
./minipycc compile testcases/valid/v2_v3.py --out build/v2_v3 --emit all --run

# Compile without optimization.
./minipycc compile testcases/valid/v2_v3.py --out build/v2_v3_noopt --emit llvm,exe --run --no-opt
```

## Generated Artifacts

Depending on `--emit`, the output directory can contain:

| Artifact | Description |
| :--- | :--- |
| `tokens.txt` | Lexer token stream. |
| `ast.dot` / `ast.png` | AST visualization. |
| `ir.txt` | Custom IR before optimization. |
| `cfg.dot` / `cfg.png` | Control-flow graph before optimization. |
| `complexity_report.json` | Static analysis metrics. |
| `domtree_<function>.dot` / `.png` | Dominator tree visualization. |
| `optimization_report.json` | Optimizer summary. |
| `ir_optimized.txt` | Custom IR after optimization. |
| `cfg_optimized.dot` / `.png` | CFG after optimization. |
| `out.ll` | Generated LLVM IR. |
| `a.out` | Native executable. |
| `run_output.txt` | Captured stdout from `--run`. |
| `result.json` | Build manifest with status, diagnostics, timings, and artifacts. |

## Docker Usage

Build the Docker image:

```bash
docker build -t minipycc .
```

Compile and run from inside the container while writing artifacts back to your
host checkout:

```bash
docker run --rm -v "$PWD:/work" minipycc \
  compile testcases/valid/v2_v3.py \
  --out build/docker_v2_v3 \
  --emit all \
  --run
```

The image uses `/app/minipycc` as its entrypoint and `/work` as the working
directory. Mounting the repository at `/work` lets the compiler read your local
testcases and write build artifacts into your local `build/` directory.

Run a compile-only Docker build:

```bash
docker run --rm -v "$PWD:/work" minipycc \
  compile testcases/valid/fib.py \
  --out build/docker_fib \
  --emit llvm,exe
```

## Tests

Run the test harness:

```bash
python3 test_runner.py
```

or:

```bash
make test
```

The harness compiles selected valid programs, runs them, checks stdout, and
verifies selected invalid programs fail with the expected diagnostics.

## Architecture

```text
src/
├── cli/
│   └── driver.py          # CLI and pipeline orchestration
├── core/
│   ├── lexer.py           # Source -> tokens
│   ├── parser.py          # Tokens -> AST
│   ├── ast.py             # AST nodes and DOT visualization
│   ├── sema.py            # Symbol table and semantic checks
│   ├── ir.py              # Custom IR and AST lowering
│   ├── cfg.py             # CFG DOT generation
│   ├── analysis/          # Complexity and dominator analysis
│   ├── opt/               # Optimization passes
│   ├── codegen_llvm.py    # Custom IR -> LLVM IR
│   └── util.py            # Diagnostics, source manager, manifest, timers
├── runtime/
│   └── runtime.c          # C runtime for print, strings, and lists
└── minipycc               # Executable compiler entrypoint
```

Compilation flow:

1. Load source and tokenize indentation-aware MiniPython.
2. Parse tokens into AST.
3. Run semantic analysis and annotate expression types.
4. Lower AST into a typed custom IR.
5. Emit IR/CFG/analysis artifacts when requested.
6. Optimize IR unless `--no-opt` is set.
7. Generate LLVM IR.
8. Link LLVM IR with `runtime/runtime.c` using `clang`.
9. Optionally run the generated executable and capture stdout.

## Example MiniPython Program

```python
a = True
b = False
print(a and not b)

x = 3.5
y = 2
print(x + y)

name = "MiniPython"
print(name)
print(name == "MiniPython")

total = 0
for i in range(1, 5):
    if i == 3:
        continue
    total = total + i
print(total)

xs = [1, 2, 3]
xs.append(4)
xs[0] = 10
print(xs[0] + xs[3])
print(len(xs))

while True:
    pass
    break
```

This program is checked in as `testcases/valid/v2_v3.py`.
