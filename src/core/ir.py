from dataclasses import dataclass, field
from typing import List, Optional, Any
from enum import Enum, auto

class OpCode(Enum):
    CONST = auto()   # dest = const val
    COPY = auto()    # dest = src
    ADD = auto()     # dest = src1 + src2
    SUB = auto()
    MUL = auto()
    DIV = auto()
    ICMP_EQ = auto() # dest = src1 == src2
    ICMP_NE = auto()
    ICMP_LT = auto()
    ICMP_LTE = auto()
    ICMP_GT = auto()
    ICMP_GTE = auto()
    JMP = auto()     # jump label
    BR = auto()      # br cond, true_label, false_label
    CALL = auto()    # dest = call name, [args...]
    RET = auto()     # ret val
    LABEL = auto()   # label:
    PARAM = auto()   # param name (pseudo)

@dataclass
class Operand:
    kind: str # 'var', 'lit', 'label'
    value: Any

    def __str__(self):
        if self.kind == 'lit': return f"#{self.value}"
        return str(self.value)

@dataclass
class Instr:
    opcode: OpCode
    dest: Optional[str] = None
    src1: Optional[Operand] = None
    src2: Optional[Operand] = None
    args: List[Operand] = field(default_factory=list) # for call

    def __str__(self):
        s = f"{self.opcode.name:<8}"
        if self.dest: s += f" {self.dest:<6} = "
        if self.src1: s += f"{self.src1} "
        if self.src2: s += f"{self.src2} "
        if self.args: s += f"args:({', '.join(str(a) for a in self.args)})"
        return s

@dataclass
class BasicBlock:
    label: str
    instrs: List[Instr] = field(default_factory=list)

@dataclass
class IRFunction:
    name: str
    params: List[str]
    blocks: List[BasicBlock] = field(default_factory=list)

@dataclass
class IRModule:
    functions: List[IRFunction] = field(default_factory=list)

class IRBuilder:
    def __init__(self):
        self.module = IRModule()
        self.current_func: Optional[IRFunction] = None
        self.current_block: Optional[BasicBlock] = None
        self.temp_counter = 0
        self.label_counter = 0

    def new_temp(self) -> str:
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def new_label(self, hint="lbl") -> str:
        self.label_counter += 1
        return f"{hint}_{self.label_counter}"

    def start_function(self, name, params):
        self.current_func = IRFunction(name, params)
        self.module.functions.append(self.current_func)
        entry = self.new_block("start")
        self.set_block(entry)

    def new_block(self, label) -> BasicBlock:
        bb = BasicBlock(label)
        self.current_func.blocks.append(bb)
        return bb

    def set_block(self, bb: BasicBlock):
        self.current_block = bb

    def emit(self, instr: Instr):
        self.current_block.instrs.append(instr)

    # --- Helpers ---
    def add(self, dest, s1, s2): self.emit(Instr(OpCode.ADD, dest, s1, s2))
    def sub(self, dest, s1, s2): self.emit(Instr(OpCode.SUB, dest, s1, s2))
    def mul(self, dest, s1, s2): self.emit(Instr(OpCode.MUL, dest, s1, s2))
    def div(self, dest, s1, s2): self.emit(Instr(OpCode.DIV, dest, s1, s2))
    def const(self, dest, val): self.emit(Instr(OpCode.CONST, dest, Operand('lit', val)))
    def copy(self, dest, src): self.emit(Instr(OpCode.COPY, dest, src))
    def jmp(self, label): self.emit(Instr(OpCode.JMP, src1=Operand('label', label)))
    def br(self, cond, t_lbl, f_lbl): 
        self.emit(Instr(OpCode.BR, src1=cond, args=[Operand('label', t_lbl), Operand('label', f_lbl)]))
    def ret(self, val): self.emit(Instr(OpCode.RET, src1=val))
    
    def call(self, dest, name, args):
         self.emit(Instr(OpCode.CALL, dest, Operand('lit', name), args=args))

from .ast import *

class IRGen:
    def __init__(self, builder: IRBuilder):
        self.builder = builder

    def gen_module(self, mod: Module):
        for f in mod.functions:
            self.builder.start_function(f.name, f.args)
            self._gen_block(f.body)
            
            # Terminator check
            if not self.builder.current_block.instrs or \
               self.builder.current_block.instrs[-1].opcode not in [OpCode.RET, OpCode.JMP, OpCode.BR]:
                 zero = self.builder.new_temp()
                 self.builder.const(zero, 0)
                 self.builder.ret(Operand('var', zero))

    def _gen_block(self, stmts: List[Stmt]):
        for stmt in stmts:
            self.gen_stmt(stmt)

    def gen_stmt(self, stmt: Stmt):
        if isinstance(stmt, AssignStmt):
            val = self.gen_expr(stmt.value)
            self.builder.copy(stmt.name, val)
            
        elif isinstance(stmt, ReturnStmt):
            val = self.gen_expr(stmt.value)
            self.builder.ret(val)
            
        elif isinstance(stmt, ExprStmt):
            self.gen_expr(stmt.expr)
            
        elif isinstance(stmt, IfStmt):
            cond = self.gen_expr(stmt.cond)
            then_lbl = self.builder.new_label("then")
            else_lbl = self.builder.new_label("else")
            merge_lbl = self.builder.new_label("if_cont")
            
            has_else = len(stmt.else_block) > 0
            
            self.builder.br(cond, then_lbl, else_lbl if has_else else merge_lbl)
            
            # Then
            bb_then = self.builder.new_block(then_lbl)
            self.builder.set_block(bb_then)
            self._gen_block(stmt.then_block)
            if not self._is_terminated(bb_then):
                self.builder.jmp(merge_lbl)
                
            # Else
            if has_else:
                bb_else = self.builder.new_block(else_lbl)
                self.builder.set_block(bb_else)
                self._gen_block(stmt.else_block)
                if not self._is_terminated(bb_else):
                    self.builder.jmp(merge_lbl)
                    
            # Merge
            bb_merge = self.builder.new_block(merge_lbl)
            self.builder.set_block(bb_merge)
            
        elif isinstance(stmt, WhileStmt):
            cond_lbl = self.builder.new_label("while_cond")
            body_lbl = self.builder.new_label("while_body")
            exit_lbl = self.builder.new_label("while_exit")
            
            self.builder.jmp(cond_lbl)
            
            # Cond
            bb_cond = self.builder.new_block(cond_lbl)
            self.builder.set_block(bb_cond)
            cond = self.gen_expr(stmt.cond)
            self.builder.br(cond, body_lbl, exit_lbl)
            
            # Body
            bb_body = self.builder.new_block(body_lbl)
            self.builder.set_block(bb_body)
            self._gen_block(stmt.body)
            self.builder.jmp(cond_lbl)
            
            # Exit
            bb_exit = self.builder.new_block(exit_lbl)
            self.builder.set_block(bb_exit)

    def _is_terminated(self, bb):
        if not bb.instrs: return False
        return bb.instrs[-1].opcode in [OpCode.RET, OpCode.JMP, OpCode.BR]

    def gen_expr(self, expr: Expr) -> Operand:
        if isinstance(expr, NumLit):
            t = self.builder.new_temp()
            self.builder.const(t, expr.value)
            return Operand('var', t)
            
        elif isinstance(expr, VarExpr):
            return Operand('var', expr.name)
            
        elif isinstance(expr, CallExpr):
            args = [self.gen_expr(a) for a in expr.args]
            dest = self.builder.new_temp()
            self.builder.call(dest, expr.callee, args)
            return Operand('var', dest)
            
        elif isinstance(expr, BinOp):
            l = self.gen_expr(expr.left)
            r = self.gen_expr(expr.right)
            dest = self.builder.new_temp()
            
            op_map = {
                "+": OpCode.ADD, "-": OpCode.SUB, 
                "*": OpCode.MUL, "/": OpCode.DIV,
                "==": OpCode.ICMP_EQ, "!=": OpCode.ICMP_NE,
                "<": OpCode.ICMP_LT, "<=": OpCode.ICMP_LTE,
                ">": OpCode.ICMP_GT, ">=": OpCode.ICMP_GTE
            }
            self.builder.emit(Instr(op_map[expr.op], dest, l, r))
            return Operand('var', dest)
            
        return Operand('lit', 0)
