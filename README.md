# 🧠 Mini Programming Language Compiler with Visualization

## 📌 Overview

This project implements a production-grade compiler for a custom-designed programming language (MiniLang). It covers the entire compiler pipeline, from lexical analysis to optimized target code generation, with visualization of internal compiler phases.

The project is fully aligned with standard Compiler Design syllabi (Aho–Ullman model) and demonstrates both theoretical concepts and practical implementation.

## 🎯 Objectives

- Design and implement a complete compiler for a high-level programming language
- Apply compiler design concepts such as parsing, semantic analysis, and optimization
- Generate intermediate and target code
- Visualize compiler internals for better understanding and debugging
- Build a modular, extensible, and testable compiler architecture

## 🧩 Language Features (MiniLang)

### 🔹 Data Types

- `int`
- `float`
- `bool`

### 🔹 Supported Constructs

- Variable declarations and assignments
- Arithmetic expressions (`+ - * /`)
- Boolean expressions and relational operators
- Conditional statements (`if–else`)
- Iteration (`while`)
- Selection (`switch–case`)
- Functions and procedure calls
- Nested scopes

## 🏗️ Compiler Architecture

```
Source Code
   ↓
Lexical Analysis
   ↓
Syntax Analysis
   ↓
Semantic Analysis
   ↓
Intermediate Code Generation
   ↓
Code Optimization
   ↓
Target Code Generation
```

Each phase is implemented as an independent module, enabling maintainability and scalability.

## 📚 Syllabus Coverage Mapping

### ✅ Unit 1 – Lexical Analysis

- Token specification using regular expressions
- Input buffering and token recognition
- Error handling for invalid lexemes
- **Tool Used:** Flex (Lex)

### ✅ Unit 2 – Syntax Analysis

- Context-Free Grammar (CFG)
- LALR parsing
- Operator precedence and associativity
- Ambiguous grammar resolution
- **Tool Used:** Bison (Yacc)

### ✅ Unit 3 – Syntax-Directed Translation & Runtime Environment

- Syntax-directed definitions
- Semantic rules and type checking
- Symbol table with scope management
- Storage allocation strategies
- Parameter passing mechanisms
- Stack-based runtime model

### ✅ Unit 4 – Intermediate Code Generation

- Three Address Code (TAC)
- Quadruples / Triples
- Boolean expressions
- Backpatching
- Control flow handling
- Basic blocks and flow graphs
- DAG representation of expressions

### ✅ Unit 5 – Code Optimization & Compiler Development

- Constant folding
- Dead code elimination
- Loop optimization
- Peephole optimization
- Modular compiler design
- Testing and maintenance strategy
- Robust error handling

## 📊 Visualization Features

Visualization is integrated to expose internal compiler behavior:

| Phase | Visualization |
|-------|---------------|
| Lexical Analysis | Token table |
| Syntax Analysis | Parse Tree / AST |
| Semantic Analysis | Symbol Table (scope-wise) |
| Intermediate Code | Three Address Code |
| Control Flow | Control Flow Graph (CFG) |
| Optimization | DAG & optimized TAC |

**Tool Used:** Graphviz (.dot → .png)

## 📁 Project Structure

```
MiniLang-Compiler/
│
├── lexer/
│   └── lexer.l
├── parser/
│   └── parser.y
├── semantic/
│   ├── symbol_table.c
│   └── type_checker.c
├── intermediate/
│   └── tac_generator.c
├── optimizer/
│   └── optimizer.c
├── visualization/
│   ├── ast.dot
│   ├── cfg.dot
│   ├── dag.dot
│   └── token_table.txt
├── codegen/
│   └── target_code.c
├── testcases/
├── build/
└── README.md
```

## 🛠️ Technologies Used

- **Language:** C / C++
- **Lexer Generator:** Flex
- **Parser Generator:** Bison
- **Visualization:** Graphviz
- **Build Tools:** GCC, Make
- **Platform:** Linux / macOS

## ▶️ How to Build & Run

### 1️⃣ Install Dependencies

```bash
sudo apt install flex bison graphviz gcc
```

### 2️⃣ Build the Compiler

```bash
flex lexer/lexer.l
bison -d parser/parser.y
gcc lex.yy.c parser.tab.c semantic/*.c intermediate/*.c optimizer/*.c codegen/*.c -o compiler
```

### 3️⃣ Run the Compiler

```bash
./compiler testcases/sample.min
```

### 4️⃣ Generate Visualizations

```bash
dot -Tpng visualization/ast.dot -o ast.png
dot -Tpng visualization/cfg.dot -o cfg.png
dot -Tpng visualization/dag.dot -o dag.png
```

## 🧪 Testing Strategy

- Valid and invalid syntax test cases
- Type mismatch test cases
- Nested scope tests
- Optimization correctness validation
- Control flow edge cases

## 📈 Future Enhancements

- Register allocation using graph coloring
- SSA (Static Single Assignment) form
- JIT compilation
- GUI-based visualization
- Support for arrays and pointers

## 💬 Viva-Ready Project Description

"This project implements a complete compiler pipeline for a custom programming language, covering lexical analysis, syntax analysis, semantic analysis, intermediate code generation, optimization, and target code generation. The compiler also includes visualization of internal representations such as parse trees, control flow graphs, and DAGs to enhance understanding and debugging."

## 📜 License

This project is intended for academic and educational use.