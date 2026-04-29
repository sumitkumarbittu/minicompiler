from typing import List, Dict, Set, Optional
from dataclasses import dataclass
from ..ir import IRModule, IRFunction, BasicBlock, OpCode, Instr
from collections import defaultdict

@dataclass
class OptimizationReport:
    initial_instructions: int = 0
    instructions_removed: int = 0
    constants_folded: int = 0
    blocks_removed: int = 0
    
    def to_dict(self):
        final = self.initial_instructions - self.instructions_removed
        return {
            "initial_instruction_count": self.initial_instructions,
            "final_instruction_count": final,
            "instructions_removed": self.instructions_removed,
            "constants_folded": self.constants_folded,
            "blocks_removed": self.blocks_removed
        }

class Optimizer:
    def __init__(self, debug=False):
        self.debug = debug
        self.report = OptimizationReport()

    def run(self, module: IRModule) -> OptimizationReport:
        # Initial stats
        count = 0
        for f in module.functions:
            for bb in f.blocks:
                count += len(bb.instrs)
        self.report.initial_instructions = count
        
        changed = True
        while changed:
            changed = False
            # Constant Folding
            if self._run_const_fold(module): 
                changed = True
            
            # Dead Code Elimination
            if self._run_dce(module):
                changed = True
                
            # Simplify CFG (merge blocks, remove empty)
            if self._run_simplify_cfg(module):
                changed = True

        return self.report

    def _run_const_fold(self, module: IRModule) -> bool:
        changed = False
        for f in module.functions:
            for bb in f.blocks:
                new_instrs = []
                for instr in bb.instrs:
                    folded = self._try_fold(instr)
                    if folded:
                        new_instrs.append(folded)
                        if folded.opcode == OpCode.CONST and instr.opcode != OpCode.CONST:
                            self.report.constants_folded += 1
                            changed = True
                    else:
                        new_instrs.append(instr)
                bb.instrs = new_instrs
        return changed

    def _try_fold(self, instr: Instr) -> Optional[Instr]:
        if instr.opcode in [OpCode.ADD, OpCode.SUB, OpCode.MUL, OpCode.DIV]:
            if instr.src1.kind == 'lit' and instr.src2.kind == 'lit':
                v1 = instr.src1.value
                v2 = instr.src2.value
                res = 0
                if instr.opcode == OpCode.ADD: res = v1 + v2
                elif instr.opcode == OpCode.SUB: res = v1 - v2
                elif instr.opcode == OpCode.MUL: res = v1 * v2
                elif instr.opcode == OpCode.DIV: 
                    if v2 == 0: return None # divide by zero check
                    res = v1 // v2
                
                # Create CONST instruction replacement
                from ..ir import Operand
                new_instr = Instr(OpCode.CONST, dest=instr.dest, src1=Operand('lit', res))
                return new_instr
        return None

    def _run_dce(self, module: IRModule) -> bool:
        # Simple DCE based on unused definitions
        # Build use-def chain or ref counts
        changed = False
        for f in module.functions:
            # Gather all uses
            uses = set()
            for bb in f.blocks:
                for instr in bb.instrs:
                    if instr.src1 and instr.src1.kind == 'var': uses.add(instr.src1.value)
                    if instr.src2 and instr.src2.kind == 'var': uses.add(instr.src2.value)
                    for arg in instr.args:
                        if arg.kind == 'var': uses.add(arg.value)
            
            # Remove definitions of unused variables (unless side effect like CALL)
            # CALL and JMP/BR/RET have side effects or control flow logic so keep them
            side_effect_ops = [OpCode.CALL, OpCode.JMP, OpCode.BR, OpCode.RET, OpCode.PARAM, OpCode.LABEL, OpCode.LIST_SET]
            
            for bb in f.blocks:
                new_instrs = []
                for instr in bb.instrs:
                    if instr.opcode not in side_effect_ops and instr.dest:
                        if instr.dest not in uses and instr.dest not in f.params:
                            # Dead code
                            self.report.instructions_removed += 1
                            changed = True
                            continue
                    new_instrs.append(instr)
                bb.instrs = new_instrs
        return changed

    def _run_simplify_cfg(self, module: IRModule) -> bool:
        # Merge linear blocks or remove empty jumps
        # This is a bit complex for v1 but let's try basic jump threading
        changed = False
        for f in module.functions:
            # Map label -> block
            lbl_map = {bb.label: bb for bb in f.blocks}
            
            # 1. Remove blocks that are just JMP to another block and not entry
            # (threading)
            # Find such blocks
            redirects = {} # old_target -> new_target
            
            for bb in f.blocks:
                if len(bb.instrs) == 1 and bb.instrs[0].opcode == OpCode.JMP:
                     target = bb.instrs[0].src1.value
                     if target != bb.label: # avoid self loop infinite
                         redirects[bb.label] = target

            if redirects:
                # Update all jumps in other blocks
                for bb in f.blocks:
                    if not bb.instrs: continue
                    last = bb.instrs[-1]
                    if last.opcode == OpCode.JMP:
                        targets = [last.src1.value]
                        if targets[0] in redirects:
                           last.src1.value = redirects[targets[0]]
                           changed = True
                    elif last.opcode == OpCode.BR:
                         # Check true/false targets
                         t_lbl = last.args[0].value
                         f_lbl = last.args[1].value
                         if t_lbl in redirects:
                             last.args[0].value = redirects[t_lbl]
                             changed = True
                         if f_lbl in redirects:
                             last.args[1].value = redirects[f_lbl]
                             changed = True
                             
                # Now remove unreachable blocks? 
                # Doing naive reachability
                reachable = set()
                worklist = [f.blocks[0].label]
                reachable.add(worklist[0])
                while worklist:
                    curr = worklist.pop()
                    if curr not in lbl_map: continue
                    bb = lbl_map[curr]
                    
                    # Successors
                    succs = []
                    if bb.instrs:
                        last = bb.instrs[-1]
                        if last.opcode == OpCode.JMP: succs.append(last.src1.value)
                        elif last.opcode == OpCode.BR: 
                            succs.append(last.args[0].value)
                            succs.append(last.args[1].value)
                    
                    for s in succs:
                        if s not in reachable:
                            reachable.add(s)
                            worklist.append(s)

                # Remove unreachable
                new_blocks = [b for b in f.blocks if b.label in reachable]
                if len(new_blocks) < len(f.blocks):
                    self.report.blocks_removed += (len(f.blocks) - len(new_blocks))
                    f.blocks = new_blocks
                    changed = True

        return changed
