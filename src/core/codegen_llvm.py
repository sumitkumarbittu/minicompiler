from typing import List, Dict, Set
from .ir import *

class LLVMGen:
    def __init__(self):
        self.lines = []
        self.reg_counter = 0

    def gen(self, mod: IRModule) -> str:
        self.lines = [
            "; ModuleID = 'minipy'",
            "source_filename = \"minipy\"",
            "target datalayout = \"e-m:o-i64:64-i128:128-n32:64-S128\"",
            "target triple = \"x86_64-apple-macosx14.0.0\"", 
            "",
            "declare i32 @print_int(i64)",
            "declare i32 @print_bool(i1)",
            ""
        ]
        
        for f in mod.functions:
            self._gen_func(f)
            
        return "\n".join(self.lines)

    def _gen_func(self, f: IRFunction):
        self.reg_counter = 0
        # Header
        params_str = ", ".join(["i64 %" + p for p in f.params])
        self.lines.append(f"define i64 @{f.name}({params_str}) {{")
        
        # Collect all variables requiring stack slots
        vars_seen: Set[str] = set(f.params)
        for bb in f.blocks:
            for instr in bb.instrs:
                if instr.dest:
                    vars_seen.add(instr.dest)
        
        # Entry block for allocas
        self.lines.append("entry:")
        for v in vars_seen:
           self.lines.append(f"  %{v}.addr = alloca i64")
        
        # Store params
        for p in f.params:
            self.lines.append(f"  store i64 %{p}, i64* %{p}.addr")
            
        # Jump to first block
        if f.blocks:
            self.lines.append(f"  br label %{f.blocks[0].label}")

        for bb in f.blocks:
            self.lines.append(f"{bb.label}:")
            for instr in bb.instrs:
                self._gen_instr(instr)
                
        self.lines.append("}")

    def _new_reg(self):
        self.reg_counter += 1
        return f"%_{self.reg_counter}"

    def _load(self, op: Operand) -> str:
        if op.kind == 'lit':
            return str(op.value)
        elif op.kind == 'var':
            r = self._new_reg()
            self.lines.append(f"  {r} = load i64, i64* %{op.value}.addr")
            return r
        else:
            return "0"

    def _gen_instr(self, instr: Instr):
        if instr.opcode == OpCode.CONST:
            val = str(instr.src1.value)
            self.lines.append(f"  store i64 {val}, i64* %{instr.dest}.addr")
            
        elif instr.opcode == OpCode.COPY:
            val = self._load(instr.src1)
            self.lines.append(f"  store i64 {val}, i64* %{instr.dest}.addr")
            
        elif instr.opcode in [OpCode.ADD, OpCode.SUB, OpCode.MUL, OpCode.DIV]:
            v1 = self._load(instr.src1)
            v2 = self._load(instr.src2)
            dest = self._new_reg()
            
            op_map = {
                OpCode.ADD: "add", OpCode.SUB: "sub", 
                OpCode.MUL: "mul", OpCode.DIV: "sdiv"
            }
            op = op_map[instr.opcode]
            self.lines.append(f"  {dest} = {op} i64 {v1}, {v2}")
            self.lines.append(f"  store i64 {dest}, i64* %{instr.dest}.addr")
            
        elif instr.opcode in [OpCode.ICMP_EQ, OpCode.ICMP_NE, OpCode.ICMP_LT, OpCode.ICMP_LTE, OpCode.ICMP_GT, OpCode.ICMP_GTE]:
            v1 = self._load(instr.src1)
            v2 = self._load(instr.src2)
            dest_i1 = self._new_reg()
            
            pred_map = {
                OpCode.ICMP_EQ: "eq", OpCode.ICMP_NE: "ne",
                OpCode.ICMP_LT: "slt", OpCode.ICMP_LTE: "sle",
                OpCode.ICMP_GT: "sgt", OpCode.ICMP_GTE: "sge"
            }
            pred = pred_map[instr.opcode]
            
            self.lines.append(f"  {dest_i1} = icmp {pred} i64 {v1}, {v2}")
            dest_i64 = self._new_reg()
            self.lines.append(f"  {dest_i64} = zext i1 {dest_i1} to i64")
            self.lines.append(f"  store i64 {dest_i64}, i64* %{instr.dest}.addr")

        elif instr.opcode == OpCode.JMP:
            self.lines.append(f"  br label %{instr.src1.value}")
            
        elif instr.opcode == OpCode.BR:
            # br cond(i64), t, f
            cond_val = self._load(instr.src1)
            cond_i1 = self._new_reg()
            self.lines.append(f"  {cond_i1} = trunc i64 {cond_val} to i1")
            
            t_lbl = instr.args[0].value
            f_lbl = instr.args[1].value
            self.lines.append(f"  br i1 {cond_i1}, label %{t_lbl}, label %{f_lbl}")
            
        elif instr.opcode == OpCode.RET:
            val = self._load(instr.src1)
            self.lines.append(f"  ret i64 {val}")
            
        elif instr.opcode == OpCode.CALL:
            args_str_list = []
            for arg_op in instr.args:
                val = self._load(arg_op)
                args_str_list.append(f"i64 {val}")
            args_str = ", ".join(args_str_list)
            
            callee_name = instr.src1.value
            
            if callee_name == "print":
                 self.lines.append(f"  call i32 @print_int({args_str})")
            else:
                 res = self._new_reg()
                 self.lines.append(f"  {res} = call i64 @{callee_name}({args_str})")
                 self.lines.append(f"  store i64 {res}, i64* %{instr.dest}.addr")
