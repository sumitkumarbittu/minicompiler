from dataclasses import dataclass
from typing import Dict, List, Optional
from .ast import *
from .util import Diagnostic, Severity

@dataclass
class Symbol:
    name: str
    type: str  # 'int', 'bool', 'void' (implicitly everything is int64 except compares)

class Scope:
    def __init__(self, parent=None):
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}
        
    def define(self, name, type):
        self.symbols[name] = Symbol(name, type)
        
    def resolve(self, name):
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.resolve(name)
        return None

class SemanticAnalyzer:
    def __init__(self, diag_engine):
        self.diag = diag_engine
        self.global_scope = Scope()
        self.current_scope = self.global_scope
        self.current_func = None
        
        # Builtins
        self.global_scope.define("print", "void")

    def check(self, node: ASTNode):
        if isinstance(node, Module):
            for f in node.functions:
                # First pass: define function symbols
                if self.global_scope.resolve(f.name):
                    self._error(f"Function {f.name} already defined", f.token)
                self.global_scope.define(f.name, "int") # All user funcs return int for now

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
            if not self.current_scope.resolve(stmt.name):
                # Define on first assignment
                self.current_scope.define(stmt.name, type_rhs)
            
        elif isinstance(stmt, ReturnStmt):
            t = self.check_expr(stmt.value)
            # v1: assume all return int
            
        elif isinstance(stmt, IfStmt):
            self.check_expr(stmt.cond)
            for s in stmt.then_block: self.check_stmt(s)
            for s in stmt.else_block: self.check_stmt(s)
            
        elif isinstance(stmt, WhileStmt):
            self.check_expr(stmt.cond)
            for s in stmt.body: self.check_stmt(s)
            
        elif isinstance(stmt, ExprStmt):
            self.check_expr(stmt.expr)

    def check_expr(self, expr: Expr) -> str:
        if isinstance(expr, NumLit):
            return "int"
            
        elif isinstance(expr, VarExpr):
            sym = self.current_scope.resolve(expr.name)
            if not sym:
                # If checking main/top level, might be global but here we treat as scope
                self._error(f"Undefined variable '{expr.name}'", expr.token)
                return "int" # fallback
            return sym.type
            
        elif isinstance(expr, BinOp):
            l = self.check_expr(expr.left)
            r = self.check_expr(expr.right)
            if expr.op in ["==", "!=", "<", "<=", ">", ">="]:
                return "bool"
            return "int"
            
        elif isinstance(expr, CallExpr):
            func = self.global_scope.resolve(expr.callee)
            if not func:
                self._error(f"Undefined function '{expr.callee}'", expr.token)
                return "int"
            # Argument count check could go here
            for arg in expr.args:
                self.check_expr(arg)
            return "int"
            
        return "int"

    def _error(self, msg, token):
        line = token.line if token else 0
        col = token.col if token else 0
        self.diag.report(Diagnostic(Severity.ERROR, "", line, col, msg))
