from dataclasses import dataclass, field
from typing import List, Optional, Union
from .lexer import Token

# Abstract bases
class ASTNode:
    pass

class Stmt(ASTNode):
    pass

class Expr(ASTNode):
    pass

# --- Expressions ---
@dataclass
class NumLit(Expr):
    value: int
    token: Optional[Token] = None

@dataclass
class VarExpr(Expr):
    name: str
    token: Optional[Token] = None

@dataclass
class BinOp(Expr):
    left: Expr
    op: str
    right: Expr
    token: Optional[Token] = None

@dataclass
class CallExpr(Expr):
    callee: str
    args: List[Expr]
    token: Optional[Token] = None

# --- Statements ---
@dataclass
class AssignStmt(Stmt):
    name: str
    value: Expr
    token: Optional[Token] = None

@dataclass
class ExprStmt(Stmt):
    expr: Expr
    token: Optional[Token] = None

@dataclass
class ReturnStmt(Stmt):
    value: Expr
    token: Optional[Token] = None

@dataclass
class IfStmt(Stmt):
    cond: Expr
    then_block: List[Stmt]
    else_block: List[Stmt]
    token: Optional[Token] = None

@dataclass
class WhileStmt(Stmt):
    cond: Expr
    body: List[Stmt]
    token: Optional[Token] = None

@dataclass
class FunctionDef(Stmt):
    name: str
    args: List[str]
    body: List[Stmt]
    token: Optional[Token] = None

@dataclass
class Module(ASTNode):
    functions: List[FunctionDef]
    token: Optional[Token] = None

# --- Visualization ---
def escape(s):
    return s.replace('"', '\\"')

class ASTVisualizer:
    def __init__(self):
        self.lines = []
        self.idx = 0

    def generate(self, node: ASTNode) -> str:
        self.lines = ["digraph AST {", "  node [shape=box, fontname=\"Courier\"];"]
        self._visit(node)
        self.lines.append("}")
        return "\n".join(self.lines)

    def _id(self):
        self.idx += 1
        return f"n{self.idx}"

    def _visit(self, node: Union[ASTNode, List[Stmt]]):
        my_id = self._id()
        
        if isinstance(node, Module):
            self.lines.append(f'  {my_id} [label="Module"];')
            for f in node.functions:
                child_id = self._visit(f)
                self.lines.append(f"  {my_id} -> {child_id};")
                
        elif isinstance(node, FunctionDef):
            args_str = ",".join(node.args)
            self.lines.append(f'  {my_id} [label="Def {node.name}({args_str})"];')
            for stmt in node.body:
                child_id = self._visit(stmt)
                self.lines.append(f"  {my_id} -> {child_id};")

        elif isinstance(node, AssignStmt):
            self.lines.append(f'  {my_id} [label="Assign: {node.name}"];')
            child_id = self._visit(node.value)
            self.lines.append(f"  {my_id} -> {child_id};")

        elif isinstance(node, ExprStmt):
            self.lines.append(f'  {my_id} [label="ExprStmt"];')
            child_id = self._visit(node.expr)
            self.lines.append(f"  {my_id} -> {child_id};")

        elif isinstance(node, ReturnStmt):
            self.lines.append(f'  {my_id} [label="Return"];')
            child_id = self._visit(node.value)
            self.lines.append(f"  {my_id} -> {child_id};")

        elif isinstance(node, IfStmt):
            self.lines.append(f'  {my_id} [label="If"];')
            cond_id = self._visit(node.cond)
            self.lines.append(f'  {my_id} -> {cond_id} [label="cond"];')
            
            then_node = self._id()
            self.lines.append(f'  {then_node} [label="Block (Then)"];')
            self.lines.append(f"  {my_id} -> {then_node};")
            for s in node.then_block:
                self.lines.append(f"  {then_node} -> {self._visit(s)};")
                
            if node.else_block:
                else_node = self._id()
                self.lines.append(f'  {else_node} [label="Block (Else)"];')
                self.lines.append(f"  {my_id} -> {else_node};")
                for s in node.else_block:
                    self.lines.append(f"  {else_node} -> {self._visit(s)};")

        elif isinstance(node, WhileStmt):
            self.lines.append(f'  {my_id} [label="While"];')
            cond_id = self._visit(node.cond)
            self.lines.append(f'  {my_id} -> {cond_id} [label="cond"];')
            
            body_node = self._id()
            self.lines.append(f'  {body_node} [label="Body"];')
            self.lines.append(f"  {my_id} -> {body_node};")
            for s in node.body:
                self.lines.append(f"  {body_node} -> {self._visit(s)};")
        
        elif isinstance(node, BinOp):
            self.lines.append(f'  {my_id} [label="Op {escape(node.op)}"];')
            self.lines.append(f"  {my_id} -> {self._visit(node.left)};")
            self.lines.append(f"  {my_id} -> {self._visit(node.right)};")
            
        elif isinstance(node, NumLit):
            self.lines.append(f'  {my_id} [label="Num {node.value}"];')
            
        elif isinstance(node, VarExpr):
            self.lines.append(f'  {my_id} [label="Var {node.name}"];')
            
        elif isinstance(node, CallExpr):
            self.lines.append(f'  {my_id} [label="Call {node.callee}"];')
            for arg in node.args:
                self.lines.append(f"  {my_id} -> {self._visit(arg)};")

        else:
            self.lines.append(f'  {my_id} [label="Unknown {type(node)}"];')

        return my_id
