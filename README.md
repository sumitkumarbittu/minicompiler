# MiniPython Compiler (minipycc) CLI Guide

This guide details how to use the `minipycc` command-line interface to compile, debug, and visualize MiniPython programs.

## ⚡️ Quick Start

**Prerequisites**:
- Python 3.9+
- Clang / LLVM (`brew install llvm` on macOS or `apt install clang llvm` on Linux)
- Graphviz (`brew install graphviz` or `apt install graphviz`) for visualizations

**1. Setup**
Make the CLI executable:
```bash
chmod +x minipycc
```

**2. Compile & Run a Program**
There are example programs in `testcases/valid/`.
```bash
./minipycc compile testcases/valid/fact.py --out build/fact --run
```

---

## 🐍 Language Capabilities (v1)

The compiler currently supports a strict subset of Python known as **MiniPython v1**.

### ✅ Supported Features
*   **Types**: 64-bit Integers (`int64`) only. No strings or floats.
*   **Math Operations**: `+`, `-`, `*`, `/` (Integer division). Parentheses `()` for precedence.
*   **Comparisons**: `==`, `!=`, `<`, `<=`, `>`, `>=`.
*   **Control Flow**:
    *   `if` / `else` blocks (nested allowed).
    *   `while` loops.
    *   Significant whitespace (indentation) is enforced.
*   **Functions**:
    *   `def name(arg1, arg2):` definitions.
    *   `return value` statements.
    *   Recursive function calls.
*   **Built-ins**:
    *   `print(value)`: Prints an integer to standard output.
*   **Comments**: Lines starting with `#`.

### ❌ Not Yet Implemented
*   Floats (`3.14`) or Strings (`"hello"`).
*   Lists, Dictionaries, or Classes.
*   Imports (standard library).
*   Global variables (logic should be wrapped in functions or main script body).

**Example Code:**
```python
def average(a, b):
    sum = a + b
    return sum / 2

x = 10
if x > 5:
    print(average(x, 20)) # Output: 15
```

---

## 🛠 CLI Usage

The general syntax is:
```bash
./minipycc compile <SOURCE_FILE> --out <OUTPUT_DIR> [OPTIONS]
```

### Options

| Flag | Description | Used For |
| :--- | :--- | :--- |
| `--out <dir>` | **Required**. Directory to store output files. | Artifact organization |
| `--emit <list>` | Comma-separated list of artifacts to generate. | specific outputs |
| `--run` | Execute the compiled binary immediately. | Testing |
| `--no-opt` | Disable optimizations (Default in v1). | Debugging |

### `--emit` Options
Control what the compiler generates. Default is `exe`.
- **Intermediate**: `tokens`, `ast` (DOT), `ir`, `cfg` (DOT), `llvm`
- **Visuals**: `png` (Renders AST and CFG DOT files to images)
- **Binary**: `exe` (The final executable)

---

## 📚 Examples

### 1. Visual Debugging (AST & CFG)
Generate PNG images of the syntax tree and control flow graph.
```bash
./minipycc compile testcases/valid/fib.py --out build/fib --emit ast,cfg,png
```
*View `build/fib/ast.png` and `build/fib/cfg.png` to see the compiler's internal representation.*

### 2. Inspect LLVM IR
See exactly what Low-Level Virtual Machine code generates.
```bash
./minipycc compile testcases/valid/cond.py --out build/cond --emit llvm
cat build/cond/out.ll
```

### 3. Full Debug Pipeline
Generate every possible artifact to understand the entire compilation process.
```bash
./minipycc compile testcases/valid/gcd.py --out build/gcd --emit tokens,ast,ir,cfg,llvm,exe,png --run
```

---

## 🐳 Docker Usage

If you don't want to install LLVM/Graphviz locally, use Docker.

**1. Build Image**
```bash
docker build -t minipycc .
```

**2. Run Compiler**
Mount your current directory to `/work` so artifacts appear on your host machine.
```bash
docker run --rm -v "$PWD:/work" minipycc compile testcases/valid/fact.py --out build/docker_fact --emit ast,llvm,png --run
```
