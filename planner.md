# 🗺️ MiniPython Evolution Planner: V2 & V3

This document outlines the current state of the **MiniPython Compiler (`minipycc`)** and the strategic roadmap for the next two major versions, combined into a single comprehensive implementation plan.

---

## ✅ Version 1: The Foundation (Completed)
*Current status of the project.*

### 1. Language Support
- **Types**: 64-bit Integers (`int64`) only.
- **Control Flow**: `if-else` blocks, `while` loops.
- **Functions**: Parameter passing, recursion, and return values.
- **I/O**: Built-in `print()` for integers.
- **Syntax**: Pythonic indentation (significant whitespace) via `INDENT`/`DEDENT` tokens.

### 2. Compiler Pipeline
- **Lexer**: Custom regex-based tokenizer with indentation tracking.
- **Parser**: Recursive descent parser generating a clean AST.
- **Semantic Analysis**: Symbol table management and basic variable scope validation.
- **IR Generation**: Flattening AST into **Quadruple-based Intermediate Representation**.
- **Backend**: Direct LLVM IR generation (`.ll`) using stack-based variable allocation.

### 3. Analysis & Visuals
- **CFG**: Control Flow Graph generation with Basic Block identification.
- **Dominator Tree**: Full analysis of flow dominance (useful for loop detection).
- **Metrics**: Automated Cyclomatic Complexity and instruction count reporting.
- **Graphviz Integration**: Visual exports for AST, CFG, and Dominators.

---

## 🚀 Version 2: Language Maturity & Analysis
*Focus: Broadening language utility and improving compiler intelligence.*

### 1. Expanded Type System
- [ ] **Native Floats**: Support for `double` precision floating point math.
- [ ] **Boolean Type**: Move from integer-based booleans to native `i1` in LLVM with proper logical operators (`and`, `or`, `not`).
- [ ] **Strings**: Basic immutable string support for logging and user interaction.

### 2. Advanced Control Flow
- [ ] **`for` Loops**: Implementation of `for i in range(...)` syntax.
- [ ] **Control Keywords**: Support for `break` and `continue` inside loops.
- [ ] **Nested Functions**: Closures and scope capturing.

### 3. Intermediate Representation Upgrade (SSA)
- [ ] **SSA Transformation**: Convert the IR to **Static Single Assignment** form.
- [ ] **Phi Functions**: Implement phi nodes at CFG merge points to eliminate `alloca` dependency and improve performance.
- [ ] **Memory Analysis**: Distinguish between stack, heap, and register-bound variables.

### 4. Rich Diagnostics
- [ ] **Visual Error Markers**: Underlining the exact column of a syntax or type error.
- [ ] **Type Inference**: Automatically deduce types for variables without explicit declarations.

---

## 👑 Version 3: High-Level Abstractions & Performance
*Focus: Modern language features and production-grade optimizations.*

### 1. Data Structures & Heap Management
- [ ] **Lists**: Implementation of dynamic arrays (`append`, `pop`, indexing).
- [ ] **Dictionaries**: Hash-map implementation for key-value pairs.
- [ ] **Garbage Collection**: Integrate a simple **Reference Counting** or **Mark-and-Sweep** collector for heap-allocated objects.

### 2. Object-Oriented Programming (OOP)
- [ ] **Classes & Objects**: Support for `class` definitions, `self`, and constructors (`__init__`).
- [ ] **Method Dispatch**: Virtual tables (v-tables) for method overriding and inheritance.
- [ ] **Attributes**: Dynamic attribute access and modification.

### 3. Global Optimizations
- [ ] **Inlining**: Automatically inline small function calls to reduce stack overhead.
- [ ] **Loop Optimizations**:
    - Loop Invariant Code Motion (LICM).
    - Loop Unrolling.
- [ ] **Global Value Numbering (GVN)**: Advanced redundancy elimination across the whole program.

### 4. Ecosystem & Tooling
- [ ] **Module System**: Support for `import` to compile and link multiple files.
- [ ] **FFI (Foreign Function Interface)**: Ability to call any C library function directly from MiniPython.
- [ ] **Optimization Heatmaps**: A visual report showing "hot" blocks in the CFG where most cycles are spent.

---

## 🛠 Combined Implementation Priority

| Feature | Phase | Category | Difficulty |
| :--- | :--- | :--- | :--- |
| `for` loops & `break`/`continue` | V2 | Control Flow | Medium |
| Native Float Support | V2 | Types | Low |
| SSA Transformation | V2 | IR | **High** |
| Lists & Indexing | V3 | Data Structures | Medium |
| Basic Class Support | V3 | OOP | **High** |
| Reference Counting | V3 | Memory | Medium |
| Module Imports | V3 | Ecosystem | Medium |

---
*This planner serves as a living document to track the evolution of `minipycc` from a classroom project to a robust system compiler.*
