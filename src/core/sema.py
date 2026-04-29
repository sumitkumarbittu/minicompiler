from dataclasses import dataclass
from typing import Dict, List, Optional
from .ast import *
from .util import Diagnostic, Severity

@dataclass
class Symbol:
    name: str
    type: str
    params: Optional[List[str]] = None

class Scope:
    def __init__(self, parent=None):
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}
        
    def define(self, name, type, params=None):
        self.symbols[name] = Symbol(name, type, params)
        
    def resolve(self, name):
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.resolve(name)
        return None

class SemanticAnalyzer:
    def __init__(self, diag_engine, file_path=""):
        self.diag = diag_engine
        self.global_scope = Scope()
        self.current_scope = self.global_scope
        self.current_func = None
        self.loop_depth = 0
        self.file_path = file_path
        
        # Builtins
        self.global_scope.define("print", "void", ["any"])
        self.global_scope.define("len", "int", ["list"])
        self.global_scope.define("list_append", "void", ["list", "int"])

    def check(self, node: ASTNode):
        if isinstance(node, Module):
            for f in node.functions:
                # First pass: define function symbols
                if self.global_scope.resolve(f.name):
                    self._error(f"Function {f.name} already defined", f.token)
                self.global_scope.define(f.name, "int", ["int" for _ in f.args])

            for f in node.functions:
                self.check_function(f)
                
    def check_function(self, func: FunctionDef):
        self.current_func = func
        self.current_scope = Scope(self.global_scope)
        
        for arg in func.args:
            self.current_scope.define(arg, "int")
            
        for stmt in func.body:
            self.check_stmt(stmt)
            
        self.current_scope = self.global_scope
        self.current_func = None

    def check_stmt(self, stmt: Stmt):
        if isinstance(stmt, AssignStmt):
            type_rhs = self.check_expr(stmt.value)
            sym = self.current_scope.resolve(stmt.name)
            if not sym:
                # Define on first assignment
                self.current_scope.define(stmt.name, type_rhs)
            elif not self._can_assign(sym.type, type_rhs):
                self._error(f"Cannot assign {type_rhs} to variable '{stmt.name}' of type {sym.type}", stmt.token)

        elif isinstance(stmt, IndexAssignStmt):
            collection_t = self.check_expr(stmt.collection)
            index_t = self.check_expr(stmt.index)
            value_t = self.check_expr(stmt.value)
            if collection_t != "list":
                self._error("Indexed assignment requires a list", stmt.token)
            if index_t != "int":
                self._error("List index must be int", stmt.token)
            if value_t != "int":
                self._error("This V3 list implementation stores int values", stmt.token)
            
        elif isinstance(stmt, ReturnStmt):
            t = self.check_expr(stmt.value)
            if t not in ["int", "bool"]:
                self._error(f"Functions currently return int-compatible values, got {t}", stmt.token)
            
        elif isinstance(stmt, IfStmt):
            self._check_condition(stmt.cond)
            for s in stmt.then_block: self.check_stmt(s)
            for s in stmt.else_block: self.check_stmt(s)
            
        elif isinstance(stmt, WhileStmt):
            self._check_condition(stmt.cond)
            self.loop_depth += 1
            for s in stmt.body: self.check_stmt(s)
            self.loop_depth -= 1

        elif isinstance(stmt, ForStmt):
            for expr in [stmt.start, stmt.stop, stmt.step]:
                t = self.check_expr(expr)
                if t != "int":
                    self._error("range() arguments must be int", expr.token)
            existing = self.current_scope.resolve(stmt.var)
            if existing and existing.type != "int":
                self._error(f"Loop variable '{stmt.var}' must be int", stmt.token)
            if not existing:
                self.current_scope.define(stmt.var, "int")
            self.loop_depth += 1
            for s in stmt.body: self.check_stmt(s)
            self.loop_depth -= 1

        elif isinstance(stmt, BreakStmt):
            if self.loop_depth == 0:
                self._error("'break' used outside a loop", stmt.token)

        elif isinstance(stmt, ContinueStmt):
            if self.loop_depth == 0:
                self._error("'continue' used outside a loop", stmt.token)

        elif isinstance(stmt, PassStmt):
            pass
            
        elif isinstance(stmt, ExprStmt):
            self.check_expr(stmt.expr)

    def check_expr(self, expr: Expr) -> str:
        if isinstance(expr, NumLit):
            expr.inferred_type = "int"
            return "int"

        elif isinstance(expr, BoolLit):
            expr.inferred_type = "bool"
            return "bool"

        elif isinstance(expr, FloatLit):
            expr.inferred_type = "float"
            return "float"

        elif isinstance(expr, StringLit):
            expr.inferred_type = "str"
            return "str"
            
        elif isinstance(expr, VarExpr):
            sym = self.current_scope.resolve(expr.name)
            if not sym:
                # If checking main/top level, might be global but here we treat as scope
                self._error(f"Undefined variable '{expr.name}'", expr.token)
                expr.inferred_type = "int"
                return "int" # fallback
            expr.inferred_type = sym.type
            return sym.type

        elif isinstance(expr, UnaryOp):
            t = self.check_expr(expr.operand)
            if expr.op == "not":
                if t not in ["bool", "int"]:
                    self._error("'not' expects bool or int", expr.token)
                expr.inferred_type = "bool"
                return "bool"
            if expr.op in ["-", "+"]:
                if t not in ["int", "float"]:
                    self._error(f"Unary '{expr.op}' expects a numeric operand", expr.token)
                    expr.inferred_type = "int"
                    return "int"
                expr.inferred_type = t
                return t
            
        elif isinstance(expr, BinOp):
            l = self.check_expr(expr.left)
            r = self.check_expr(expr.right)
            if expr.op in ["and", "or"]:
                if l not in ["bool", "int"] or r not in ["bool", "int"]:
                    self._error(f"Logical '{expr.op}' expects bool or int operands", expr.token)
                expr.inferred_type = "bool"
                return "bool"
            if expr.op in ["==", "!=", "<", "<=", ">", ">="]:
                if expr.op in ["<", "<=", ">", ">="] and ("str" in [l, r] or "list" in [l, r]):
                    self._error(f"Operator '{expr.op}' is not supported for {l} and {r}", expr.token)
                expr.inferred_type = "bool"
                return "bool"
            if l not in ["int", "float"] or r not in ["int", "float"]:
                self._error(f"Operator '{expr.op}' expects numeric operands", expr.token)
                expr.inferred_type = "int"
                return "int"
            result = "float" if "float" in [l, r] else "int"
            expr.inferred_type = result
            return result
            
        elif isinstance(expr, CallExpr):
            func = self.global_scope.resolve(expr.callee)
            if not func:
                self._error(f"Undefined function '{expr.callee}'", expr.token)
                expr.inferred_type = "int"
                return "int"
            arg_types = [self.check_expr(arg) for arg in expr.args]
            if func.params and func.params != ["any"]:
                if len(arg_types) != len(func.params):
                    self._error(f"Function '{expr.callee}' expects {len(func.params)} arguments, got {len(arg_types)}", expr.token)
                else:
                    for actual, expected in zip(arg_types, func.params):
                        if expected != "any" and not self._can_assign(expected, actual):
                            self._error(f"Function '{expr.callee}' expected {expected}, got {actual}", expr.token)
            elif expr.callee == "print" and len(arg_types) != 1:
                self._error("print() expects exactly one argument", expr.token)
            expr.inferred_type = func.type
            return func.type

        elif isinstance(expr, ListLit):
            for elem in expr.elements:
                t = self.check_expr(elem)
                if t != "int":
                    self._error("This V3 list implementation currently stores int values only", elem.token)
            expr.inferred_type = "list"
            return "list"

        elif isinstance(expr, IndexExpr):
            collection_t = self.check_expr(expr.collection)
            index_t = self.check_expr(expr.index)
            if collection_t != "list":
                self._error("Indexing requires a list", expr.token)
            if index_t != "int":
                self._error("List index must be int", expr.token)
            expr.inferred_type = "int"
            return "int"
            
        expr.inferred_type = "int"
        return "int"

    def _check_condition(self, expr):
        t = self.check_expr(expr)
        if t not in ["bool", "int"]:
            self._error(f"Condition must be bool or int, got {t}", expr.token)

    def _can_assign(self, dst, src):
        if dst == src or dst == "any":
            return True
        if dst == "float" and src == "int":
            return True
        if dst == "int" and src == "bool":
            return True
        return False

    def _error(self, msg, token):
        line = token.line if token else 0
        col = token.col if token else 0
        self.diag.report(Diagnostic(Severity.ERROR, self.file_path, line, col, msg))
