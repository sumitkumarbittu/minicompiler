# MiniPython Compiler Planner

This planner is based on a repository-wide audit of the current codebase. The
project is a Python implementation of a MiniPython compiler named `minipycc`.
It currently compiles a small Python-like language to LLVM IR, optionally links
it with a small C runtime, and emits visual and JSON artifacts for teaching,
debugging, and analysis.

The main implementation lives in:

- `src/cli/driver.py`
- `src/core/lexer.py`
- `src/core/parser.py`
- `src/core/ast.py`
- `src/core/sema.py`
- `src/core/ir.py`
- `src/core/cfg.py`
- `src/core/codegen_llvm.py`
- `src/core/opt/optimizer.py`
- `src/core/analysis/analyzer.py`
- `src/core/util.py`
- `runtime/runtime.c`
- `minipycc`
- `Makefile`
- `Dockerfile`
- `testcases/`

There is also historical or aspirational documentation in `README_custom.md`
that describes a broader Flex/Bison MiniLang compiler. The actual codebase is
the Python MiniPython compiler described by `README.md`, `README2.md`, and the
source files above.

---

## 1. V1: What Is Already Implemented

V1 is a working educational compiler pipeline for a strict integer-only subset
of Python. It includes source loading, diagnostics, lexing, parsing, semantic
checking, AST visualization, custom IR generation, CFG visualization, static
analysis, simple optimization, LLVM IR generation, native executable generation,
runtime support, Docker support, and a small Makefile workflow.

### 1.1 CLI and Build Workflow

Implemented in `minipycc` and `src/cli/driver.py`.

Current command:

```bash
./minipycc compile <source> --out <output_dir> [flags]
```

Implemented flags:

- `--out`: required output directory.
- `--emit`: comma-separated artifact selection.
- `--run`: compile and immediately execute the generated binary.
- `--no-opt`: skip the optimizer.
- `--metrics`: present in CLI arguments, but not currently used directly.
- `--analysis`: run the static analysis path.

Implemented emit values:

- `tokens`
- `ast`
- `ir`
- `cfg`
- `opt`
- `analysis`
- `llvm`
- `exe`
- `png`
- `all`, expanded to all major artifact types.

Implemented generated artifacts:

- `tokens.txt`
- `ast.dot`
- `ast.png`, when Graphviz rendering is requested.
- `ir.txt`
- `cfg.dot`
- `cfg.png`, when Graphviz rendering is requested.
- `complexity_report.json`
- `domtree_<function>.dot`
- `domtree_<function>.png`, when Graphviz rendering is requested.
- `optimization_report.json`
- `ir_optimized.txt`
- `cfg_optimized.dot`
- `cfg_optimized.png`, when Graphviz rendering is requested.
- `out.ll`
- `a.out`
- `run_output.txt`
- `result.json`

Current behavior:

- The output directory is deleted and recreated on every compile.
- Each compiler phase records timing data in `result.json`.
- Diagnostics are written into `result.json` on failure.
- LLVM IR is always emitted as `out.ll`.
- Native executable generation uses `clang`.
- DOT-to-PNG rendering uses the `dot` command from Graphviz.

### 1.2 Source Management and Diagnostics

Implemented in `src/core/util.py`.

Current components:

- `Severity`: `INFO`, `WARNING`, `ERROR`.
- `Diagnostic`: stores severity, file path, line, column, message, and optional snippet.
- `SourceManager`: loads files and stores line arrays.
- `DiagnosticsEngine`: collects diagnostics and reports whether errors exist.
- `Timer`: records phase durations.
- `ResultManifest`: stores status, diagnostics, artifacts, timings, and timestamp.

Current strengths:

- Every major phase can fail with structured diagnostics.
- The compiler records build artifacts and timings in a stable manifest.
- The implementation is small and easy to extend.

Current limitations:

- Diagnostics do not yet include rich source underlines.
- Some semantic errors have an empty file path because `SemanticAnalyzer._error`
  does not retain the source file path.
- `SourceManager.get_line` exists, but diagnostics do not yet use it to show
  source snippets.
- No warning categories or diagnostic codes exist yet.

### 1.3 Lexer

Implemented in `src/core/lexer.py`.

Supported token categories:

- End/control tokens: `EOF`, `NEWLINE`, `INDENT`, `DEDENT`.
- Keywords: `def`, `if`, `else`, `while`, `return`.
- Built-in-like token: `print`.
- Identifiers.
- Integer literals.
- Operators: `+`, `-`, `*`, `/`, `=`, `==`, `!=`, `<`, `<=`, `>`, `>=`.
- Delimiters: `(`, `)`, `:`, `,`.

Implemented language behavior:

- Python-style significant indentation.
- Automatic `INDENT` and `DEDENT` insertion.
- Comment skipping for `#` comments.
- Blank line skipping.
- Identifier scanning with letters, digits, and underscore.
- Integer scanning.
- Basic unexpected-character diagnostics.

Current limitations:

- Spaces only; tabs are not supported as indentation.
- No string literals.
- No floats.
- No boolean literals.
- No list, dict, tuple, or indexing tokens.
- No `for`, `in`, `range`, `break`, `continue`, `and`, `or`, `not`, `class`,
  `import`, `from`, `as`, `pass`, or `None`.
- No unary operator token handling beyond the raw `-` token.
- No indentation normalization policy such as "4 spaces only".
- No multi-character literal handling beyond integers.

### 1.4 Parser

Implemented in `src/core/parser.py`.

Parser style:

- Hand-written recursive descent parser.
- Produces the AST dataclasses from `src/core/ast.py`.

Supported program structure:

- Function definitions with positional arguments.
- Top-level statements.
- Synthetic `main` function when top-level statements exist.

Supported statements:

- Assignment: `name = expr`
- Expression statement, restricted mostly to function calls.
- `print(...)` as a call-like expression statement.
- `return expr`
- `if cond: ...`
- `if cond: ... else: ...`
- `while cond: ...`
- Empty lines.

Supported expressions:

- Integer literals.
- Variable references.
- Function calls.
- Parenthesized expressions.
- Binary arithmetic: `+`, `-`, `*`, `/`.
- Comparisons: `==`, `!=`, `<`, `<=`, `>`, `>=`.

Implemented precedence:

- Parentheses and atoms.
- Multiplication/division.
- Addition/subtraction.
- Single comparison level.

Current limitations:

- Comparisons are not chainable in Python style, such as `a < b < c`.
- No unary minus, unary plus, or logical not.
- No boolean operators.
- No list/dict literals.
- No indexing or slicing.
- No attribute access.
- No method calls.
- No keyword arguments.
- No default arguments.
- No type annotations.
- No nested function scope semantics, even though the parser can encounter
  `def` only at the module level.
- No robust recovery after parser errors; it reports and continues minimally.

### 1.5 AST and AST Visualization

Implemented in `src/core/ast.py`.

Current AST nodes:

- `Module`
- `FunctionDef`
- `AssignStmt`
- `ExprStmt`
- `ReturnStmt`
- `IfStmt`
- `WhileStmt`
- `NumLit`
- `VarExpr`
- `BinOp`
- `CallExpr`

Implemented visualization:

- `ASTVisualizer` emits Graphviz DOT.
- Function definitions, statements, calls, variables, numbers, binary ops, if
  branches, and while bodies are represented.

Current limitations:

- No explicit type objects in AST.
- No source span model beyond optional token references.
- No parent pointers.
- No visitor base class.
- No AST validation pass.
- No symbol table visualization.

### 1.6 Semantic Analysis

Implemented in `src/core/sema.py`.

Current symbol model:

- `Symbol` with name and string type.
- `Scope` with parent links and name resolution.
- Global scope with built-in `print`.
- One function-local scope per function.

Implemented checks:

- Functions are defined in global scope before body checking.
- Duplicate function names are reported.
- Function arguments are defined as `int`.
- First assignment defines a local variable.
- Variable usage checks for undefined names.
- Function calls check whether the callee exists.
- Binary comparisons return `bool`.
- Arithmetic returns `int`.
- User functions are assumed to return `int`.

Current limitations:

- No argument count checking.
- No argument type checking.
- No return type checking.
- No "all paths return" validation.
- No local duplicate declaration model because assignment implicitly defines.
- No block scopes for `if` or `while`.
- No type coercion or explicit type declarations.
- Comparisons produce `bool` semantically, but codegen stores results as `i64`.
- `print` is globally typed as `void`, but call expressions always return `int`.
- No unreachable code detection.

### 1.7 Intermediate Representation

Implemented in `src/core/ir.py`.

Current IR model:

- `IRModule`
- `IRFunction`
- `BasicBlock`
- `Instr`
- `Operand`
- `OpCode`

Current opcodes:

- `CONST`
- `COPY`
- `ADD`
- `SUB`
- `MUL`
- `DIV`
- `ICMP_EQ`
- `ICMP_NE`
- `ICMP_LT`
- `ICMP_LTE`
- `ICMP_GT`
- `ICMP_GTE`
- `JMP`
- `BR`
- `CALL`
- `RET`
- `LABEL`
- `PARAM`

Implemented lowering:

- Each function starts with a `start` block.
- Top-level code becomes a synthetic `main` function.
- Assignments lower to value generation plus `COPY`.
- Integer literals lower to `CONST`.
- Binary operations lower to arithmetic or integer comparison opcodes.
- Calls lower to `CALL`.
- Returns lower to `RET`.
- Missing function terminators get an implicit `return 0`.
- `if` lowers to then/else/merge basic blocks.
- `while` lowers to condition/body/exit blocks.

Current limitations:

- Not in SSA form.
- Variables are mutable symbolic names.
- Temporary counters are global across functions rather than reset per function.
- No explicit type on operands or instructions.
- No call signature information.
- No memory operations other than implicit mutable variables.
- No phi nodes.
- No structured loop metadata.
- No debug/source location attachment to IR instructions.

### 1.8 CFG Visualization

Implemented in `src/core/cfg.py`.

Current behavior:

- Generates DOT graph clusters per function.
- Each basic block is rendered with its instruction list.
- Edges are generated from `JMP` and `BR` terminators.
- Branch edges are labeled `T` and `F`.

Current limitations:

- No fallthrough edges because IR uses explicit terminators.
- No highlighting of loop back edges.
- No dominance overlay.
- No unreachable block styling.
- No per-block metrics in the CFG node.

### 1.9 Static Analysis

Implemented in `src/core/analysis/analyzer.py`.

Current metrics:

- Per-function instruction count.
- Per-function basic block count.
- Per-function cyclomatic complexity.
- Per-function called function list.
- Total instruction count.

Current graph analysis:

- Predecessor map.
- Dominator set computation.
- Immediate dominator computation.
- Back-edge detection.
- Dominator tree DOT generation.

Current limitations:

- Back edges are computed but not surfaced in the JSON report.
- No natural loop extraction.
- No liveness analysis.
- No reaching definitions.
- No use-def chains.
- No call graph DOT.
- No per-block complexity.
- No warning generation for unreachable code or suspicious constructs.

### 1.10 Optimizer

Implemented in `src/core/opt/optimizer.py`.

Current optimizer passes:

- Constant folding for arithmetic instructions when both operands are literal
  operands.
- Dead code elimination for unused definitions.
- Simple CFG simplification:
  - jump threading through blocks that only jump elsewhere.
  - naive reachability-based unreachable block removal after redirects.

Current optimization report:

- Initial instruction count.
- Final instruction count.
- Instructions removed.
- Constants folded.
- Blocks removed.

Current limitations:

- Constant folding rarely triggers after current IR generation because numeric
  literals are generally emitted as `CONST` into temporaries rather than used as
  literal operands in arithmetic instructions.
- No constant propagation.
- No copy propagation.
- No common subexpression elimination.
- No strength reduction.
- No branch simplification for constant conditions.
- No loop optimizations.
- DCE is local and simple; it does not fully model side effects or control flow.
- No pass manager abstraction.
- No optimizer test suite.

### 1.11 LLVM Backend

Implemented in `src/core/codegen_llvm.py`.

Current behavior:

- Emits textual LLVM IR.
- Emits module header with target datalayout and target triple.
- Declares runtime functions:
  - `print_int(i64)`
  - `print_bool(i1)`
- Generates `define i64 @function(...)`.
- Allocates stack slots for function params and all instruction destinations.
- Stores parameters into stack slots.
- Emits an entry block and branches to the first IR block.
- Emits integer arithmetic as LLVM `add`, `sub`, `mul`, `sdiv`.
- Emits comparisons as `icmp`, then zero-extends `i1` to `i64`.
- Emits conditional branches by truncating `i64` to `i1`.
- Emits calls to user functions.
- Special-cases `print` as a runtime call to `print_int`.
- Emits integer returns.

Current limitations:

- Target triple is hard-coded to `x86_64-apple-macosx14.0.0`.
- All user-level values are stored as `i64`.
- Booleans are represented as `i64` after comparison.
- `print_bool` is declared but not used.
- No support for strings or heap objects.
- No module-level declarations.
- No external C function declarations beyond runtime print helpers.
- Stack-based codegen produces many loads and stores.
- No validation step using `llvm-as`, `lli`, or LLVM verifier.

### 1.12 Runtime

Implemented in `runtime/runtime.c`.

Current runtime functions:

- `print_int(int64_t val)`
- `print_bool(int val)`

Current limitations:

- `print_bool` signature does not match the LLVM declaration exactly
  (`int` in C vs `i1` in LLVM declaration).
- No string printing.
- No allocation helpers.
- No list/dict/object runtime.
- No error handling helpers such as division-by-zero traps.

### 1.13 Docker and Makefile

Implemented in `Dockerfile` and `Makefile`.

Docker:

- Based on `python:3.9-slim`.
- Installs clang, llvm, graphviz, build-essential, and make.
- Copies the repo into `/app`.
- Adds `/app` to `PATH`.
- Uses `/app/minipycc` as the entry point.

Makefile:

- `make build`: makes `minipycc` executable.
- `make test`: compiles and runs factorial and Fibonacci test artifacts.
- `make clean`: deletes `build` and `.pyc` files.
- `make viz`: renders DOT files in `build`.
- `make docker`: builds the Docker image.

Current limitations:

- `make test` is a smoke test, not a true assertion-based test suite.
- Several source files in `testcases/valid` and `testcases/invalid` are empty.
- The golden directories contain useful artifacts, but there is no active golden
  comparison harness.
- `test_runner.py` is currently empty.

### 1.14 Test and Example Coverage

Current test-related directories:

- `testcases/valid/`
- `testcases/invalid/`
- `testcases/golden/`
- `build/tests/`
- `build/<example>/`

Currently observed examples:

- Simple arithmetic and print programs.
- Golden factorial IR with recursion.
- Golden Fibonacci IR with a loop.
- Build artifacts showing CFG, AST, optimization reports, complexity reports,
  LLVM IR, executable output, and PNG visualizations.

Current limitations:

- Active `testcases/valid/fact.py` is simple arithmetic, while golden factorial
  artifacts show recursive factorial. The checked-in examples and golden files
  are not fully synchronized.
- Empty test files reduce confidence in `make test`.
- No unit tests for lexer/parser/sema/IR/codegen/optimizer.
- No negative assertion tests for diagnostics.
- No cross-platform LLVM target tests.

---

## 2. V1 Stabilization Before V2/V3

Before building V2 and V3 features, V1 should be stabilized so that new work
does not sit on unclear behavior. This is not a separate product version; it is
the foundation work that should happen first.

### 2.1 Documentation Cleanup

Tasks:

- Decide whether the project is MiniPython only, or whether MiniLang/Flex/Bison
  documentation is historical.
- Update `README.md` to match the actual implementation exactly.
- Move `README_custom.md` into a historical notes section or rewrite it as
  future inspiration.
- Document the exact V1 grammar.
- Document supported and unsupported Python constructs.
- Document artifact formats.
- Document system dependencies and platform assumptions.

Acceptance criteria:

- A new contributor can run one command to compile a known sample.
- README examples match checked-in source files.
- The planner, README, and testcases do not contradict each other.

### 2.2 Test Harness

Tasks:

- Implement `test_runner.py`.
- Add lexer snapshot tests.
- Add parser AST shape tests.
- Add semantic error tests.
- Add IR snapshot tests.
- Add LLVM compile/run tests.
- Add golden artifact comparison for selected stable outputs.
- Add expected stdout files for runnable examples.
- Add expected failure JSON for invalid examples.

Acceptance criteria:

- `make test` fails if output is wrong.
- Empty valid/invalid testcases are removed or filled.
- At least these programs are tested:
  - arithmetic
  - variable assignment
  - if/else
  - while loop
  - function call
  - recursion
  - undefined variable
  - bad indentation
  - wrong function arity, once implemented

### 2.3 Diagnostics Upgrade

Tasks:

- Preserve source file path inside semantic diagnostics.
- Attach source spans to AST nodes.
- Include source snippets in diagnostics.
- Add caret/underline output for CLI errors.
- Add diagnostic codes, such as `E001`, `E002`.
- Avoid duplicate printing from both `DiagnosticsEngine.report` and `_fail`,
  or make the output intentionally structured.

Acceptance criteria:

- Syntax, lexical, and semantic errors show file, line, column, source line, and
  caret.
- `result.json` includes enough diagnostic data for an editor or web UI.

### 2.4 Platform Robustness

Tasks:

- Detect target triple using `clang -dumpmachine` or omit hard-coded target data.
- Check availability of `clang` and `dot` before use.
- Make Graphviz rendering failures non-fatal but visible in `result.json`.
- Avoid deleting an output directory unless it is known to be safe.
- Add `--clean` or `--force` if destructive output cleanup is desired.

Acceptance criteria:

- Compilation works on macOS and Linux without editing `codegen_llvm.py`.
- Missing optional tools produce clear diagnostics.

---

## 3. Combined V2 + V3 Strategy

The user request asks what can be done for V2 and V3 if both are done at once.
Doing both at once is possible, but it should be treated as one larger compiler
upgrade program with internal milestones. The safest approach is not to build
every feature in parallel randomly. Instead, define a shared architecture that
supports both V2 language maturity and V3 higher-level features, then deliver
vertical slices.

Recommended combined theme:

- V2: make the language more useful and the compiler more correct.
- V3: add high-level abstractions, runtime support, and stronger optimization.
- Combined execution: build the type system, IR typing, runtime object model,
  tests, and pass infrastructure once so V2 and V3 features do not need to be
  rewritten later.

### 3.1 Core Architectural Work Needed for Both V2 and V3

These items should be started early because many later features depend on them.

#### Typed AST and Typed IR

Why:

- V1 treats almost everything as `int`.
- V2 needs `bool`, `float`, and probably `str`.
- V3 needs lists, dictionaries, objects, and heap references.

Tasks:

- Introduce a type model:
  - `IntType`
  - `BoolType`
  - `FloatType`
  - `StringType`
  - `NoneType`
  - `ListType(element_type)`
  - `DictType(key_type, value_type)`
  - `FunctionType(param_types, return_type)`
  - `ClassType(name)`
  - `ObjectType(class_name)`
  - `UnknownType` for recovery
- Attach inferred or declared type to expressions.
- Attach type to IR operands, temporaries, and instructions.
- Replace string types like `"int"` and `"bool"` with structured type objects.
- Add type compatibility and coercion rules.

Acceptance criteria:

- Every expression after semantic analysis has a known type or an explicit
  diagnostic.
- LLVM codegen no longer guesses all values are `i64`.

#### Function Signatures and Arity Checking

Why:

- V1 only checks whether a called function exists.
- V2/V3 need typed calls, methods, constructors, builtins, imports, and FFI.

Tasks:

- Store function symbols with param count, param names, param types, and return
  type.
- Check argument count.
- Check argument types.
- Support `void`/`None` returns.
- Make `print` a family of overloads or a special typed builtin.

Acceptance criteria:

- Calling a function with the wrong number of arguments fails.
- Calling a function with incompatible types fails or coerces according to rules.

#### Pass Manager

Why:

- V1 optimizer is a single class with hard-coded loops.
- V2/V3 need more analyses and optimization passes.

Tasks:

- Introduce a pass interface:
  - analysis pass
  - transform pass
  - verification pass
- Track pass dependencies.
- Run fixed-point passes intentionally.
- Emit per-pass reports.
- Add `--opt-level 0|1|2|3`.
- Add `--debug-pass` or `--print-after <pass>`.

Acceptance criteria:

- Existing constant folding, DCE, and CFG simplification run through the pass
  manager.
- Each pass can be unit tested independently.

#### Runtime ABI

Why:

- V1 runtime only prints integers and booleans.
- V3 data structures require allocation, reference management, and object
  layout.

Tasks:

- Define a stable runtime naming convention.
- Define object header layout if heap objects are added.
- Add runtime functions for:
  - string allocation/printing
  - list creation
  - list get/set
  - list append
  - list length
  - dictionary creation/get/set
  - object creation
  - reference count retain/release, if reference counting is chosen
- Decide whether all heap values are opaque pointers in LLVM.

Acceptance criteria:

- Runtime functions have matching LLVM declarations and C signatures.
- Runtime behavior is covered by integration tests.

#### Verification

Why:

- Larger features will make silent IR bugs much more expensive.

Tasks:

- Add AST verifier.
- Add semantic verifier.
- Add IR verifier:
  - block terminators are valid.
  - branch targets exist.
  - variables are defined before use.
  - operand types match opcodes.
  - function returns match signature.
- Add LLVM verifier step when LLVM tools are available.

Acceptance criteria:

- Compiler-internal invalid states are caught before codegen.

---

## 4. V2 Roadmap: Language Maturity and Compiler Correctness

V2 should make MiniPython feel like a practical small language while keeping the
implementation understandable. It should focus on types, control flow, better
diagnostics, stronger tests, and a cleaner compiler architecture.

### 4.1 V2 Language Features

#### Booleans

Features:

- Boolean literals: `True`, `False`.
- Boolean type in semantic analysis.
- Logical operators: `and`, `or`, `not`.
- Proper truthiness rules for supported types.
- Boolean printing.

Required changes:

- Lexer: add tokens for `True`, `False`, `and`, `or`, `not`.
- AST: add `BoolLit`, `UnaryOp`, and logical `BinOp` support.
- Parser: add precedence levels for `or`, `and`, `not`.
- Sema: type-check logical operations.
- IR: add native boolean ops or typed comparison ops.
- LLVM: emit `i1` where possible.
- Runtime: align `print_bool` signature with LLVM.

Acceptance criteria:

```python
a = True
b = False
print(a and not b)
```

prints:

```text
True
```

#### Floats

Features:

- Float literals.
- Float arithmetic.
- Float comparisons.
- Float printing.
- Mixed int/float arithmetic by promoting int to float.

Required changes:

- Lexer: scan decimal literals.
- AST: add `FloatLit`.
- Sema: implement numeric promotion.
- IR: add typed arithmetic instructions or typed operands.
- LLVM: emit `double`, `fadd`, `fsub`, `fmul`, `fdiv`, `fcmp`.
- Runtime: add `print_float`.

Acceptance criteria:

```python
x = 3.5
y = 2
print(x + y)
```

prints a reasonable float representation.

#### Strings

Features:

- String literals.
- String printing.
- String equality.
- Optional string concatenation with `+`.

Required changes:

- Lexer: handle quoted strings and escapes.
- AST: add `StringLit`.
- Sema: string type.
- IR/LLVM: decide between global constants for literals and runtime string
  objects.
- Runtime: add string print and compare helpers.

Acceptance criteria:

```python
name = "MiniPython"
print(name)
print(name == "MiniPython")
```

prints the string and `True`.

#### For Loops and Range

Features:

- `for i in range(n):`
- `for i in range(start, stop):`
- `for i in range(start, stop, step):`
- Optional range object can be compiler-lowered rather than runtime allocated.

Required changes:

- Lexer: `for`, `in`, `range`.
- AST: `ForStmt`.
- Parser: parse `for name in range(...):`.
- Sema: validate range arguments as integers.
- IR: lower to while-style blocks.
- CFG/analysis: support generated loop structure.

Acceptance criteria:

```python
total = 0
for i in range(1, 5):
    total = total + i
print(total)
```

prints:

```text
10
```

#### Break and Continue

Features:

- `break` exits nearest loop.
- `continue` jumps to nearest loop continuation point.

Required changes:

- Lexer: `break`, `continue`.
- AST: `BreakStmt`, `ContinueStmt`.
- Parser: statement parsing.
- Sema: error if used outside a loop.
- IRGen: maintain loop context stack with break and continue labels.

Acceptance criteria:

- `break` inside a loop exits the loop.
- `continue` inside a loop skips to next iteration.
- `break` outside a loop produces a clear semantic error.

#### Pass Statement

Features:

- `pass` as an empty statement.

Why:

- Makes empty blocks legal and simplifies examples.

Acceptance criteria:

```python
if True:
    pass
```

compiles.

### 4.2 V2 Semantic Improvements

Tasks:

- Function arity checking.
- Function return type checking.
- Detect missing return in non-void functions.
- Detect unreachable code after return/break/continue.
- Distinguish local variables, parameters, globals, and builtins.
- Add block scope policy and document it.
- Improve assignment rules:
  - first assignment defines a variable.
  - later assignment must be type-compatible.
- Add clearer built-in function typing.

Acceptance criteria:

- Incorrect programs fail before IR generation.
- Diagnostics identify the precise source line and reason.

### 4.3 V2 IR Improvements

Tasks:

- Add types to `Operand` and `Instr`.
- Add explicit `BOOL_CONST`, `FLOAT_CONST`, or unify constants with typed values.
- Add `FADD`, `FSUB`, `FMUL`, `FDIV` or make arithmetic opcode type-polymorphic.
- Add logical operations.
- Add explicit conversion instructions:
  - `SITOFP`
  - `FPTOSI`, if allowed.
  - `ZEXT`
  - `TRUNC`
- Add compare instructions for int, float, bool, and string equality.
- Add source location metadata.

Acceptance criteria:

- The IR dump clearly shows types.
- Codegen does not need to infer instruction types from names.

### 4.4 V2 Optimizer Improvements

Tasks:

- Constant propagation.
- Copy propagation.
- Better constant folding over current `CONST` + arithmetic patterns.
- Algebraic simplification:
  - `x + 0 -> x`
  - `x * 1 -> x`
  - `x * 0 -> 0`
- Branch simplification:
  - `if True` only keeps the true branch.
  - `while False` removes the loop body.
- Unreachable block elimination as a standalone pass.
- Preserve correctness around side-effecting calls.

Acceptance criteria:

- `optimization_report.json` shows meaningful improvements on real examples.
- Optimized and unoptimized binaries produce identical output for testcases.

### 4.5 V2 Analysis Improvements

Tasks:

- Surface back edges in `complexity_report.json`.
- Extract natural loops.
- Add call graph report.
- Add variable use/definition report.
- Add unreachable block report.
- Add dominator tree and CFG styling improvements.

Acceptance criteria:

- `--analysis` produces useful reports for functions with loops and calls.

### 4.6 V2 Tooling Improvements

Tasks:

- Implement a real `test_runner.py`.
- Add `make test-unit`, `make test-integration`, and `make test-golden`.
- Add `--dump-ast-json`.
- Add `--dump-ir-json`.
- Add `--check-only` to stop after semantic analysis.
- Add `--emit-dir-policy clean|append|fail`.

Acceptance criteria:

- CI or local `make test` gives reliable pass/fail results.

---

## 5. V3 Roadmap: High-Level Abstractions and Performance

V3 should build on the typed architecture from V2 and introduce heap-backed
data structures, object-oriented features, modules, FFI, and more serious
optimization.

### 5.1 Lists

Features:

- List literals: `[1, 2, 3]`.
- Empty lists with type inference or annotation strategy.
- Indexing: `xs[0]`.
- Assignment to index: `xs[0] = 10`.
- `append`.
- `pop`, optional.
- `len(xs)`.
- Bounds checking.

Required changes:

- Lexer: `[` and `]`.
- Parser: list literals, indexing, indexed assignment.
- AST: `ListLit`, `IndexExpr`, `IndexAssignStmt`.
- Sema: element type inference and index type checking.
- IR: heap object references and runtime calls.
- Runtime: list object, capacity, length, get, set, append, pop.
- Codegen: pointer values and runtime declarations.

Acceptance criteria:

```python
xs = [1, 2, 3]
xs.append(4)
print(xs[0] + xs[3])
```

prints:

```text
5
```

### 5.2 Dictionaries

Features:

- Dictionary literals: `{"a": 1}`.
- Lookup: `d["a"]`.
- Assignment: `d["b"] = 2`.
- `len(d)`.
- String keys at minimum.

Required changes:

- Lexer: `{`, `}`, string support, possibly additional colon handling already
  exists.
- Parser: dict literals and indexing.
- AST: `DictLit`.
- Sema: key and value type validation.
- Runtime: hash table implementation.
- Codegen: runtime calls.

Acceptance criteria:

```python
d = {"x": 4}
d["y"] = 5
print(d["x"] + d["y"])
```

prints:

```text
9
```

### 5.3 Memory Management

Recommended V3 choice:

- Start with reference counting because it is easier to explain and easier to
  integrate with explicit runtime calls.
- Later add cycle detection or a mark-and-sweep collector if needed.

Tasks:

- Add object header with refcount and type tag.
- Add `retain` and `release`.
- Define ownership rules:
  - functions return owned or borrowed values.
  - local variables release at scope/function exit.
  - assignments retain new values and release overwritten values.
- Add cleanup on early returns, breaks, and continues.
- Add runtime debug mode to detect leaks or double releases.

Acceptance criteria:

- List/string/dict examples do not leak under runtime debug counters.
- Early returns release local heap values.

### 5.4 Classes and Objects

Features:

- `class` definitions.
- `__init__`.
- `self`.
- Attribute access: `obj.x`.
- Attribute assignment: `obj.x = value`.
- Method calls: `obj.method(args)`.
- Optional single inheritance after basic classes work.

Required changes:

- Lexer: `class`, `.`
- Parser:
  - class definitions
  - method definitions
  - attribute expressions
  - method calls
- AST:
  - `ClassDef`
  - `AttributeExpr`
  - `AttributeAssignStmt`
  - method-aware `CallExpr`
- Sema:
  - class symbol table
  - field tracking
  - method signatures
  - `self` binding
  - constructor validation
- IR:
  - object allocation
  - field get/set
  - method dispatch
- Runtime:
  - object layout
  - class metadata

Recommended staging:

1. Classes with fixed fields and no inheritance.
2. Methods lowered to functions with explicit `self`.
3. Constructors.
4. Single inheritance.
5. Dynamic dispatch or vtables.

Acceptance criteria:

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def sum(self):
        return self.x + self.y

p = Point(2, 3)
print(p.sum())
```

prints:

```text
5
```

### 5.5 Modules and Imports

Features:

- Compile multiple files.
- `import module`
- `from module import name`, optional.
- Module-level symbols.
- Cross-file function calls.

Required changes:

- Source manager that can load multiple files.
- Module resolver.
- Per-module symbol tables.
- Name mangling or namespaces in LLVM.
- Multi-file result manifest.
- Cache parsed modules to avoid duplicate work.

Acceptance criteria:

- A program can call a function defined in another `.py` file.

### 5.6 FFI

Features:

- Declare external C functions.
- Call external functions from MiniPython.
- Link additional C/object files.

Possible syntax:

```python
extern def abs(x: int) -> int
```

or a simpler config-based declaration for V3:

```json
{
  "externs": {
    "abs": {"params": ["int"], "return": "int"}
  }
}
```

Tasks:

- Add external function symbol kind.
- Add CLI option for extra link args.
- Add LLVM declarations.
- Add type checking for FFI calls.

Acceptance criteria:

- A MiniPython program can call a simple C function with integer arguments.

### 5.7 SSA and Advanced Optimization

SSA can be V2 or V3 depending on ambition. If V2 and V3 are done together, SSA
should be part of the shared compiler architecture after typed IR lands.

Tasks:

- Compute dominance frontiers.
- Insert phi nodes.
- Rename variables.
- Convert mutable variables to SSA temporaries.
- Add SSA verifier.
- Add mem2reg-like lowering where possible.
- Implement optimizations:
  - sparse conditional constant propagation
  - global value numbering
  - common subexpression elimination
  - loop invariant code motion
  - function inlining
  - dead branch elimination

Acceptance criteria:

- SSA IR can be dumped and verified.
- Optimized code reduces loads/stores versus V1 stack-heavy codegen.
- Existing examples produce the same output.

### 5.8 Debugging and Visualization

Features:

- AST JSON.
- Typed AST view.
- Symbol table report.
- Call graph DOT.
- Loop tree DOT.
- Optimization before/after diff.
- Per-pass artifact folders.
- Optional HTML report that links all generated artifacts.

Acceptance criteria:

- A user can inspect what changed after each compiler phase without opening
  many unrelated files manually.

---

## 6. Recommended Combined V2 + V3 Milestones

If V2 and V3 are implemented together, use milestones that preserve a working
compiler after each step.

### Milestone 0: Stabilize V1

Scope:

- Fix README/test mismatch.
- Implement test runner.
- Add real tests for current features.
- Improve diagnostics path handling.
- Add basic IR verifier.

Deliverable:

- A stable V1 baseline that can prevent regressions.

### Milestone 1: Type System Foundation

Scope:

- Structured type model.
- Typed symbols.
- Typed expressions.
- Function signatures and arity checking.
- Typed IR operands/instructions.

Deliverable:

- Existing integer programs still compile, but the compiler internally knows
  the type of every value.

### Milestone 2: Booleans, Logical Operators, and Better Conditions

Scope:

- `True`, `False`, `and`, `or`, `not`.
- Native boolean type.
- Boolean print.
- Proper conditional lowering.

Deliverable:

- MiniPython supports real boolean programming.

### Milestone 3: Floats and Strings

Scope:

- Float literals/arithmetic/comparisons/printing.
- String literals/printing/equality.
- Runtime string support if needed.

Deliverable:

- MiniPython supports basic numeric and text programs.

### Milestone 4: Control Flow Upgrade

Scope:

- `for range`.
- `break`.
- `continue`.
- `pass`.
- Loop context stack in IR generation.

Deliverable:

- MiniPython supports common structured loops.

### Milestone 5: Pass Manager and Real Optimizations

Scope:

- Pass manager.
- Constant propagation.
- Copy propagation.
- Branch simplification.
- Unreachable block elimination.
- Better optimization reports.

Deliverable:

- Optimizer produces measurable improvements on common examples.

### Milestone 6: Runtime Object Foundation

Scope:

- Runtime ABI.
- Heap object header.
- Reference counting or other selected memory strategy.
- String/list-compatible object representation.

Deliverable:

- Compiler and runtime can safely create and destroy heap values.

### Milestone 7: Lists

Scope:

- List literals.
- Indexing.
- Append.
- Len.
- Bounds checks.

Deliverable:

- Programs can use dynamic arrays.

### Milestone 8: Dictionaries

Scope:

- Dict literals.
- String-key lookup.
- Assignment.
- Len.

Deliverable:

- Programs can use basic maps.

### Milestone 9: Classes

Scope:

- Class definitions.
- Constructors.
- Attributes.
- Methods.
- `self`.

Deliverable:

- Programs can model simple objects.

### Milestone 10: Modules, FFI, and Advanced Reports

Scope:

- Multi-file compile.
- Import resolution.
- Optional C FFI.
- HTML or linked artifact report.

Deliverable:

- MiniPython moves from single-file examples to small projects.

### Milestone 11: SSA and Global Optimizations

Scope:

- SSA conversion.
- Phi nodes.
- SSA verifier.
- GVN.
- LICM.
- Function inlining.

Deliverable:

- Compiler has a modern optimization core.

---

## 7. Feature Dependency Map

Some features can be built independently, while others require foundations.

| Feature | Depends On | Recommended Version |
| --- | --- | --- |
| Better diagnostics | Source spans | V1 stabilization |
| Test runner | Stable CLI outputs | V1 stabilization |
| Function arity checking | Function signatures | V2 |
| Booleans | Type model | V2 |
| Logical operators | Booleans, parser precedence | V2 |
| Floats | Type model, LLVM typed codegen | V2 |
| Strings | Type model, runtime ABI | V2/V3 bridge |
| For loops | Parser/AST/IR loop lowering | V2 |
| Break/continue | Loop context stack | V2 |
| Lists | Runtime object model, indexing syntax | V3 |
| Dictionaries | Runtime object model, hashing | V3 |
| Classes | Type model, object runtime | V3 |
| Modules | Multi-file source manager | V3 |
| FFI | Typed function signatures, linker options | V3 |
| SSA | Dominators, typed IR, verifier | V3 |
| LICM | SSA or robust data-flow analysis | V3 |
| GVN | SSA preferred | V3 |
| Inlining | Call graph, function signatures | V3 |

---

## 8. Proposed Repository Structure Evolution

Current structure is small and readable. V2/V3 will benefit from splitting
larger concerns without over-engineering.

Suggested future structure:

```text
src/
  cli/
    driver.py
  core/
    ast.py
    lexer.py
    parser.py
    types.py
    symbols.py
    sema.py
    diagnostics.py
    source.py
    ir/
      __init__.py
      model.py
      builder.py
      verifier.py
      printer.py
    analysis/
      analyzer.py
      dominators.py
      loops.py
      callgraph.py
      dataflow.py
    opt/
      pass_manager.py
      const_fold.py
      const_prop.py
      copy_prop.py
      dce.py
      simplify_cfg.py
      ssa.py
      gvn.py
      licm.py
      inline.py
    codegen/
      llvm.py
      llvm_types.py
      runtime_abi.py
    viz/
      ast_dot.py
      cfg_dot.py
      dom_dot.py
      report.py
runtime/
  runtime.c
  runtime.h
testcases/
  valid/
  invalid/
  golden/
tests/
  unit/
  integration/
```

This refactor should happen gradually. Do not split files before tests exist,
and do not move code and change behavior in the same commit if avoidable.

---

## 9. Testing Plan for V2 and V3

### 9.1 Unit Tests

Lexer tests:

- indentation and dedentation
- comments and blank lines
- integers, floats, strings, booleans
- operators and delimiters
- invalid characters

Parser tests:

- expression precedence
- if/else
- while
- for
- function definitions
- calls
- list/dict/class syntax as implemented

Semantic tests:

- undefined variables
- duplicate functions
- wrong function arity
- incompatible assignment
- invalid return type
- invalid break/continue location
- invalid index type

IR tests:

- block generation for if/else and loops
- typed instructions
- correct branch labels
- return terminators
- break/continue lowering

Optimizer tests:

- constant folding
- constant propagation
- DCE
- branch simplification
- CFG simplification
- no removal of side-effecting calls

Codegen tests:

- LLVM syntax generation
- function calls
- runtime calls
- typed arithmetic
- heap object calls

### 9.2 Integration Tests

Programs:

- arithmetic
- comparison and booleans
- nested conditionals
- while loop
- for loop
- recursion
- float calculations
- strings
- lists
- dictionaries
- class methods
- imports
- FFI sample, if enabled

Each integration test should include:

- source input
- expected stdout
- expected success/failure
- optional expected artifacts

### 9.3 Golden Tests

Golden outputs should be stable for selected phases:

- tokens
- AST DOT or AST JSON
- IR text
- optimized IR text
- selected analysis JSON

LLVM text can be golden-tested, but it may be more brittle. It is often better
to validate LLVM with execution output and verifier checks.

---

## 10. Risk Register

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Building V2 and V3 simultaneously creates too many moving parts | High | Use vertical milestones and keep compiler runnable after each one |
| Type system retrofitting touches every phase | High | Add structured types while preserving V1 int behavior first |
| Runtime heap management can become complex | High | Start with simple reference counting and debug counters |
| SSA can delay user-facing features | Medium/High | Build typed non-SSA IR first; add SSA after tests and verifier |
| LLVM target hard-coding breaks non-macOS users | Medium | Detect target or use portable LLVM IR defaults |
| Optimizer may change behavior incorrectly | High | Add unoptimized vs optimized output equivalence tests |
| Golden tests may become noisy | Medium | Golden-test stable internal artifacts, not every generated file |
| Object model scope can expand endlessly | High | Start with fixed-field classes and no inheritance |
| Python compatibility expectations may become unrealistic | Medium | Document MiniPython as a subset with explicit differences |

---

## 11. Suggested Priority If Time Is Limited

If only the most valuable subset of combined V2/V3 can be done, prioritize:

1. V1 stabilization and real tests.
2. Structured type system.
3. Function signatures and arity checking.
4. Booleans and logical operators.
5. For loops, break, continue, and pass.
6. Constant propagation and branch simplification.
7. Strings and string printing.
8. Lists with append/index/len.
9. Runtime memory management.
10. Classes only after lists and runtime references are stable.

This order gives the compiler the biggest practical language improvement while
minimizing rewrites.

---

## 12. Concrete Acceptance Checklist

### V1 Baseline Done

- [x] CLI wrapper exists.
- [x] Source loading exists.
- [x] Diagnostics collection exists.
- [x] Indentation-aware lexer exists.
- [x] Recursive descent parser exists.
- [x] AST model exists.
- [x] AST DOT generation exists.
- [x] Basic semantic analysis exists.
- [x] Custom IR exists.
- [x] CFG DOT generation exists.
- [x] Static analysis exists.
- [x] Dominator tree generation exists.
- [x] Optimizer exists.
- [x] LLVM IR backend exists.
- [x] Runtime print helpers exist.
- [x] Native executable generation exists through clang.
- [x] Dockerfile exists.
- [x] Makefile exists.
- [ ] Full assertion-based test suite exists.
- [ ] README and testcases are fully synchronized.
- [ ] Diagnostics include source snippets and carets.
- [ ] Cross-platform target detection exists.

### V2 Done

- [ ] Structured type system.
- [ ] Typed AST expressions.
- [ ] Typed IR.
- [ ] Function signatures.
- [ ] Function arity checks.
- [ ] Return type checks.
- [ ] Boolean literals.
- [ ] Logical operators.
- [ ] Native boolean codegen.
- [ ] Float literals and arithmetic.
- [ ] Float printing.
- [ ] String literals and printing.
- [ ] String equality.
- [ ] For-range loops.
- [ ] Break and continue.
- [ ] Pass statement.
- [ ] Better diagnostics.
- [ ] Real pass manager.
- [ ] Constant propagation.
- [ ] Copy propagation.
- [ ] Branch simplification.
- [ ] Reliable unit and integration tests.

### V3 Done

- [ ] Runtime object ABI.
- [ ] Memory management strategy.
- [ ] Lists.
- [ ] List indexing and mutation.
- [ ] Dictionaries.
- [ ] Classes.
- [ ] Constructors.
- [ ] Attributes.
- [ ] Methods.
- [ ] Modules/imports.
- [ ] Optional FFI.
- [ ] SSA conversion.
- [ ] Phi nodes.
- [ ] SSA verifier.
- [ ] Global value numbering.
- [ ] Loop invariant code motion.
- [ ] Function inlining.
- [ ] Rich linked visualization/reporting.

---

## 13. Final Recommendation

Do V2 and V3 together only at the architecture level. Build shared foundations
once: tests, diagnostics, structured types, typed IR, function signatures,
runtime ABI, pass manager, and verifier. Then deliver language features in
vertical slices so the compiler remains runnable at all times.

The highest-value path is:

```text
V1 stabilization
-> typed compiler core
-> booleans/floats/strings
-> for/break/continue
-> pass manager and better optimization
-> runtime object model
-> lists
-> dictionaries
-> classes
-> modules/FFI
-> SSA and advanced optimization
```

That sequence turns the current V1 compiler into a larger MiniPython platform
without losing the codebase's biggest strength: the pipeline is small enough to
understand, inspect, visualize, and teach from end to end.
