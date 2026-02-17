# MiniPython Compiler (minipycc)

A production-grade, transparent compiler for a Python subset, targeting LLVM IR.
This project emphasizes internal visibility, static analysis, and optimization visualization.

## 🚀 Features

### Core Capabilities
- **Strict MiniPython v1**: Integers (`int64`), function calls, flow control (`if`/`while`).
- **Production Pipeline**: `Lex -> Parse -> Semantic -> IR -> Opt -> Codegen`.
- **LLVM Backend**: Generates optimized native binaries via Clang.

### 🔬 Advanced Analysis & Visualization
The compiler allows you to inspect every stage of compilation:
- **Visual Artifacts**:
  - `ast.png`: Abstract Syntax Tree.
  - `cfg.png`: Control Flow Graph (Pre/Post optimization).
  - `domtree.png`: Dominator Tree for structural analysis.
- **Metrics**:
  - Cyclomatic Complexity calculation per function.
  - Instruction counts and optimization reduction reports.
- **Optimization**:
  - Constant Folding (`3 + 5 -> 8`).
  - Dead Code Elimination (DCE).
  - Control Flow Simplification.

---

## ⚡️ Quick Start

**Prerequisites**:
- Python 3.9+
- Clang / LLVM
- Graphviz (`dot` command)

**1. Setup**
```bash
chmod +x minipycc
```

**2. Compile & Analyze**
Compile `fact.py` with full analysis and visualization:
```bash
./minipycc compile testcases/valid/fact.py \
  --out build/fact \
  --emit all \
  --run
```

**3. Inspect Results**
Check the `build/fact/` directory:
- `result.json`: Build manifest and timings.
- `cfg_optimized.png`: See how the graph changed.
- `domtree_fact.png`: View the structure of the `fact` function.
- `optimization_report.json`: See how many instructions were removed.

---

## 🛠 CLI Usage

```bash
./minipycc compile <SOURCE> --out <DIR> [FLAGS]
```

### Flags
| Flag | Description |
| :--- | :--- |
| `--out <dir>` | Output directory (required). |
| `--emit <list>` | Comma-separated: `tokens,ast,ir,cfg,opt,analysis,llvm,exe,png`. Use `all` for everything. |
| `--run` | Execute the binary after build. |
| `--no-opt` | Disable the optimization phase. |
| `--analysis` | Force static analysis and complexity calculation. |

---

## 🐳 Docker Usage

Build a completely isolated environment:

```bash
# Build
docker build -t minipycc .

# Run with volume mount
docker run --rm -v "$PWD:/work" minipycc \
  compile testcases/valid/fact.py \
  --out build/docker_fact \
  --emit all \
  --run
```

## Architecture

- `src/core/ast`: Tree definition and DOT generator.
- `src/core/ir`: Triple-address code (TAC) representation.
- `src/core/analysis`: Dominator trees, loop detection, complexity metrics.
- `src/core/opt`: Transformation passes (ConstFold, DCE).
- `src/core/codegen_llvm`: Translation to LLVM IR.
