from typing import List, Dict, Set
from .ir import *

class LLVMGen:
    def __init__(self):
        self.lines = []
        self.globals = []
        self.string_constants = {}
        self.reg_counter = 0

    def gen(self, mod: IRModule) -> str:
        header = [
            "; ModuleID = 'minipy'",
            "source_filename = \"minipy\"",
            "target datalayout = \"e-m:o-i64:64-i128:128-n32:64-S128\"",
            "target triple = \"x86_64-apple-macosx14.0.0\"", 
            "",
            "declare void @print_int(i64)",
            "declare void @print_bool(i1)",
            "declare void @print_float(double)",
            "declare void @print_str(i8*)",
            "declare i1 @str_eq(i8*, i8*)",
            "declare i8* @list_new(i64)",
            "declare void @list_append(i8*, i64)",
            "declare i64 @list_get(i8*, i64)",
            "declare void @list_set(i8*, i64, i64)",
            "declare i64 @list_len(i8*)",
            ""
        ]
        self.lines = []
        self.globals = []
        self.string_constants = {}
        
        for f in mod.functions:
            self._gen_func(f)
            
        return "\n".join(header + self.globals + ([""] if self.globals else []) + self.lines)

    def _gen_func(self, f: IRFunction):
        self.reg_counter = 0
        # Header
        params_str = ", ".join(["i64 %" + p for p in f.params])
        self.lines.append(f"define i64 @{f.name}({params_str}) {{")
        
        # Collect all variables requiring stack slots
        vars_seen: Dict[str, str] = {p: "int" for p in f.params}
        for bb in f.blocks:
            for instr in bb.instrs:
                if instr.dest:
                    vars_seen[instr.dest] = instr.type
        
        # Entry block for allocas
        self.lines.append("entry:")
        for v, typ in vars_seen.items():
           self.lines.append(f"  %{v}.addr = alloca {self._storage_type(typ)}")
        
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

    def _storage_type(self, typ: str) -> str:
        if typ == "float":
            return "double"
        if typ in ["str", "list"]:
            return "i8*"
        return "i64"

    def _runtime_bool(self, val: str, llvm_type: str) -> str:
        if llvm_type == "i1":
            return val
        r = self._new_reg()
        if llvm_type == "double":
            self.lines.append(f"  {r} = fcmp one double {val}, 0.000000e+00")
        else:
            self.lines.append(f"  {r} = icmp ne i64 {val}, 0")
        return r

    def _load(self, op: Operand, expected: str = None) -> str:
        if op.kind == 'lit':
            if op.type == "bool":
                return "1" if op.value else "0"
            if op.type == "float":
                return f"{float(op.value):.6e}"
            if op.type == "str":
                return self._string_ptr(op.value)
            return str(op.value)
        elif op.kind == 'var':
            r = self._new_reg()
            src_ty = self._storage_type(op.type)
            self.lines.append(f"  {r} = load {src_ty}, {src_ty}* %{op.value}.addr")
            if expected == "float" and op.type in ["int", "bool"]:
                conv = self._new_reg()
                self.lines.append(f"  {conv} = sitofp i64 {r} to double")
                return conv
            return r
        else:
            return "0"

    def _string_ptr(self, value: str) -> str:
        name, size = self._string_global(value)
        reg = self._new_reg()
        self.lines.append(f"  {reg} = getelementptr inbounds [{size} x i8], [{size} x i8]* @{name}, i64 0, i64 0")
        return reg

    def _string_global(self, value: str):
        if value in self.string_constants:
            return self.string_constants[value]
        name = f".str.{len(self.string_constants)}"
        raw = value.encode("utf-8") + b"\0"
        escaped = "".join(chr(b) if 32 <= b <= 126 and b not in [34, 92] else f"\\{b:02X}" for b in raw)
        size = len(raw)
        self.globals.append(f"@{name} = private unnamed_addr constant [{size} x i8] c\"{escaped}\"")
        self.string_constants[value] = (name, size)
        return name, size

    def _gen_instr(self, instr: Instr):
        if instr.opcode == OpCode.CONST:
            typ = instr.type
            val = self._load(instr.src1)
            self.lines.append(f"  store {self._storage_type(typ)} {val}, {self._storage_type(typ)}* %{instr.dest}.addr")
            
        elif instr.opcode == OpCode.COPY:
            typ = instr.type
            val = self._load(instr.src1, "float" if typ == "float" else None)
            self.lines.append(f"  store {self._storage_type(typ)} {val}, {self._storage_type(typ)}* %{instr.dest}.addr")
            
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

        elif instr.opcode in [OpCode.FADD, OpCode.FSUB, OpCode.FMUL, OpCode.FDIV]:
            v1 = self._load(instr.src1, "float")
            v2 = self._load(instr.src2, "float")
            dest = self._new_reg()
            op_map = {
                OpCode.FADD: "fadd", OpCode.FSUB: "fsub",
                OpCode.FMUL: "fmul", OpCode.FDIV: "fdiv"
            }
            self.lines.append(f"  {dest} = {op_map[instr.opcode]} double {v1}, {v2}")
            self.lines.append(f"  store double {dest}, double* %{instr.dest}.addr")
            
        elif instr.opcode in [OpCode.ICMP_EQ, OpCode.ICMP_NE, OpCode.ICMP_LT, OpCode.ICMP_LTE, OpCode.ICMP_GT, OpCode.ICMP_GTE]:
            dest_i1 = self._new_reg()
            if instr.src1.type == "str" and instr.src2.type == "str" and instr.opcode in [OpCode.ICMP_EQ, OpCode.ICMP_NE]:
                v1 = self._load(instr.src1)
                v2 = self._load(instr.src2)
                eq = self._new_reg()
                self.lines.append(f"  {eq} = call i1 @str_eq(i8* {v1}, i8* {v2})")
                if instr.opcode == OpCode.ICMP_NE:
                    self.lines.append(f"  {dest_i1} = xor i1 {eq}, true")
                else:
                    dest_i1 = eq
            elif instr.src1.type == "float" or instr.src2.type == "float":
                v1 = self._load(instr.src1, "float")
                v2 = self._load(instr.src2, "float")
                pred_map = {
                    OpCode.ICMP_EQ: "oeq", OpCode.ICMP_NE: "one",
                    OpCode.ICMP_LT: "olt", OpCode.ICMP_LTE: "ole",
                    OpCode.ICMP_GT: "ogt", OpCode.ICMP_GTE: "oge"
                }
                self.lines.append(f"  {dest_i1} = fcmp {pred_map[instr.opcode]} double {v1}, {v2}")
            else:
                v1 = self._load(instr.src1)
                v2 = self._load(instr.src2)
                pred_map = {
                    OpCode.ICMP_EQ: "eq", OpCode.ICMP_NE: "ne",
                    OpCode.ICMP_LT: "slt", OpCode.ICMP_LTE: "sle",
                    OpCode.ICMP_GT: "sgt", OpCode.ICMP_GTE: "sge"
                }
                self.lines.append(f"  {dest_i1} = icmp {pred_map[instr.opcode]} i64 {v1}, {v2}")
            dest_i64 = self._new_reg()
            self.lines.append(f"  {dest_i64} = zext i1 {dest_i1} to i64")
            self.lines.append(f"  store i64 {dest_i64}, i64* %{instr.dest}.addr")

        elif instr.opcode == OpCode.BOOL_NOT:
            val = self._load(instr.src1)
            cond = self._runtime_bool(val, self._storage_type(instr.src1.type))
            neg = self._new_reg()
            self.lines.append(f"  {neg} = xor i1 {cond}, true")
            out = self._new_reg()
            self.lines.append(f"  {out} = zext i1 {neg} to i64")
            self.lines.append(f"  store i64 {out}, i64* %{instr.dest}.addr")

        elif instr.opcode == OpCode.LIST_NEW:
            size = len(instr.args)
            ptr = self._new_reg()
            self.lines.append(f"  {ptr} = call i8* @list_new(i64 {size})")
            self.lines.append(f"  store i8* {ptr}, i8** %{instr.dest}.addr")
            for arg in instr.args:
                val = self._load(arg)
                self.lines.append(f"  call void @list_append(i8* {ptr}, i64 {val})")

        elif instr.opcode == OpCode.LIST_GET:
            collection = self._load(instr.src1)
            index = self._load(instr.src2)
            val = self._new_reg()
            self.lines.append(f"  {val} = call i64 @list_get(i8* {collection}, i64 {index})")
            self.lines.append(f"  store i64 {val}, i64* %{instr.dest}.addr")

        elif instr.opcode == OpCode.LIST_SET:
            collection = self._load(instr.src1)
            index = self._load(instr.src2)
            value = self._load(instr.args[0])
            self.lines.append(f"  call void @list_set(i8* {collection}, i64 {index}, i64 {value})")

        elif instr.opcode == OpCode.JMP:
            self.lines.append(f"  br label %{instr.src1.value}")
            
        elif instr.opcode == OpCode.BR:
            # br cond(i64), t, f
            cond_val = self._load(instr.src1)
            cond_i1 = self._runtime_bool(cond_val, self._storage_type(instr.src1.type))
            
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
                 arg = instr.args[0]
                 val = self._load(arg, "float" if arg.type == "float" else None)
                 if arg.type == "bool":
                     b = self._runtime_bool(val, "i64")
                     self.lines.append(f"  call void @print_bool(i1 {b})")
                 elif arg.type == "float":
                     self.lines.append(f"  call void @print_float(double {val})")
                 elif arg.type == "str":
                     self.lines.append(f"  call void @print_str(i8* {val})")
                 else:
                     self.lines.append(f"  call void @print_int(i64 {val})")
            elif callee_name == "len":
                 val = self._load(instr.args[0])
                 res = self._new_reg()
                 self.lines.append(f"  {res} = call i64 @list_len(i8* {val})")
                 self.lines.append(f"  store i64 {res}, i64* %{instr.dest}.addr")
            elif callee_name == "list_append":
                 list_ptr = self._load(instr.args[0])
                 val = self._load(instr.args[1])
                 self.lines.append(f"  call void @list_append(i8* {list_ptr}, i64 {val})")
            else:
                 res = self._new_reg()
                 self.lines.append(f"  {res} = call i64 @{callee_name}({args_str})")
                 self.lines.append(f"  store i64 {res}, i64* %{instr.dest}.addr")
