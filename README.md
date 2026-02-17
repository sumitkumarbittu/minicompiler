# 🚀 MiniPython Compiler (`minipycc`)

> **A production-grade, transparent, and explainable compiler for a Python subset.**

`minipycc` is not just a compiler; it is an educational and engineering platform designed to demonstrate the full lifecycle of a modern compiler. It translates **MiniPython** code into high-performance **LLVM IR** and native machine code, while providing deep insights into the compilation process through rich visualizations and static analysis reports.

---

## ✨ Key Features

### 🛠 Production Pipeline
*   **Lexer**: Indentation-aware tokenizer handling Python's significant whitespace.
*   **Parser**: Recursive descent parser building a clean Abstract Syntax Tree (AST).
*   **IR**: Custom Typed Intermediate Representation (Quadruples) before LLVM.
*   **Optimizer**: Multiple passes including Constant Folding and Dead Code Elimination.
*   **Backend**: Generates LLVM IR (`.ll`) optimized by Clang for native execution.

### 🔍 Deep Analysis & Visualization
*   **Explainable Artifacts**: Every stage of compilation outputs human-readable files.
*   **Visual Graphs**:
    *   **AST**: See the structure of your code.
    *   **CFG**: View basic blocks and control flow (Pre & Post optimization).
    *   **Dominator Tree**: Analyze code hierarchy and loops.
*   **Metrics**: Automated reporting on Cyclomatic Complexity and instruction counts.

### ⚡️ MiniPython v1 Language
A strict, statically-compilable subset of Python:
*   **Types**: 64-bit Integers (`int64`) only.
*   **Control Flow**: `if`, `else`, `while`, function calls, recursion.
*   **Math**: `+`, `-`, `*`, `/`, `( )`.
*   **Logic**: `==`, `!=`, `<`, `<=`, `>`, `>=`.
*   **Built-ins**: `print(value)`.

---

## 🚀 Quick Start

### Prerequisites
*   **Python 3.9+**
*   **Clang / LLVM**: `brew install llvm` (Mac) or `apt install clang llvm` (Linux)
*   **Graphviz**: `brew install graphviz` (Mac) or `apt install graphviz` (Linux)

### 1. Installation
Clone the repo and make the compiler executable:
```bash
chmod +x minipycc
```

### 2. Compile & Run
We have provided test cases in `testcases/valid/`. Let's compile a factorial program:

```bash
./minipycc compile testcases/valid/fact.py \
  --out build/fact \
  --emit all \
  --run
```

**Output:**
```text
--- execution output ---
3628800
------------------------
Build successful. Artifacts in build/fact
```

### 3. Inspect the "Black Box"
Go to `build/fact/` to see what the compiler did:
*   Open `ast.png` to see how the code was parsed.
*   Open `cfg.png` to see the flow of the program.
*   Open `out.ll` to see the generated LLVM assembly.
*   Read `complexity_report.json` to see code metrics.

---

## 📖 CLI Reference

The CLI is designed to be intuitive.

```bash
./minipycc compile <SOURCE_FILE> --out <OUTPUT_DIR> [FLAGS]
```

| Flag | Description |
| :--- | :--- |
| **`--out <dir>`** | **Required**. The folder where all build artifacts are saved. |
| **`--emit <list>`** | What to generate. Use `all` for everything, or comma-separated: <br>`tokens, ast, ir, cfg, opt, analysis, llvm, exe, png` |
| **`--run`** | Immediately execute the compiled binary after successful build. |
| **`--no-opt`** | Disable the optimization pass (useful for debugging raw IR). |
| **`--analysis`** | Trigger the advanced static analysis engine (DomTree, Metrics). |

---

## 🏛 Architecture

 The project follows a strict separation of concerns, mimicking industrial compiler architecture:

```
src/
├── core/
│   ├── lexer/       # Source -> Tokens (Handles Indentation)
│   ├── parser/      # Tokens -> AST
│   ├── semantic/    # Symbol Table & Type Checking
│   ├── ir/          # AST -> Linear IR (Quadruples)
│   ├── analysis/    # Static Analysis (Dominators, Loops)
│   ├── opt/         # Optimization Passes (ConstFold, DCE)
│   └── codegen/     # IR -> LLVM IR
├── cli/             # Command Line Interface Driver
└── runtime/         # C Runtime for built-ins (print)
```

### The Compilation Flow
1.  **Lexing**: `fact.py` is read; `INDENT`/`DEDENT` tokens are injected.
2.  **Parsing**: Tokens are consumed to build a tree of `Stmt` and `Expr` nodes.
3.  **Semantics**: Variable existence and scopes are verified.
4.  **Lowering**: AST is flattened into Basic Blocks of instructions (`ADD`, `JMP`, `CALL`).
5.  **Analysis**: The Control Flow Graph is analyzed for complexity and loops.
6.  **Optimization**: The IR is refined (constant math solved, dead code removed).
7.  **Codegen**: Clean IR is translated to LLVM IR macros.
8.  **Linking**: `clang` compiles the LLVM IR + `runtime.c` into a native executable.

---

## 🐳 Docker Support

Keep your host machine clean by running everything in Docker.

**1. Build the Builder Image**
```bash
docker build -t minipycc .
```

**2. Compile with Volume Mount**
This runs the compiler *inside* the container but writes the output *outside* to your machine.
```bash
docker run --rm -v "$PWD:/work" minipycc \
  compile testcases/valid/fact.py \
  --out build/docker_fact \
  --emit all \
  --run
```

---

## 📈 Example Analysis Output

When running with `--analysis` or `--emit all`, the compiler generates detailed reports.

**`complexity_report.json`**:
```json
{
  "functions": {
    "main": {
      "instruction_count": 15,
      "block_count": 3,
      "cyclomatic_complexity": 2,
      "functions_called": ["print"]
    }
  }
}
```

**`optimization_report.json`**:
```json
{
  "initial_instruction_count": 20,
  "final_instruction_count": 15,
  "instructions_removed": 5,
  "constants_folded": 2
}
```

---

*Built for engineers who want to understand compilers, not just use them.*
