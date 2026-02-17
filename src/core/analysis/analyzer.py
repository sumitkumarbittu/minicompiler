from typing import Dict, List, Set, Any
from dataclasses import dataclass, field
import json
from ..ir import IRModule, IRFunction, BasicBlock, OpCode

@dataclass
class FunctionMetrics:
    name: str
    instruction_count: int = 0
    block_count: int = 0
    cyclomatic_complexity: int = 0
    functions_called: List[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "name": self.name,
            "instruction_count": self.instruction_count,
            "block_count": self.block_count,
            "cyclomatic_complexity": self.cyclomatic_complexity,
            "functions_called": self.functions_called
        }

@dataclass
class AnalysisReport:
    functions: Dict[str, FunctionMetrics] = field(default_factory=dict)
    total_instructions: int = 0
    
    def to_dict(self):
        return {
            "functions": {k: v.to_dict() for k, v in self.functions.items()},
            "total_instructions": self.total_instructions
        }

class Analyzer:
    def __init__(self, debug=False):
        self.debug = debug
        self.report = AnalysisReport()
        self.predecessors = {} # func_name -> {block_label -> [pred_labels]}
        self.dominators = {}   # func_name -> {block_label -> {dom_labels}}
        self.immediate_doms = {} # func_name -> {block_label -> idom_label}
        self.back_edges = {}   # func_name -> [(src, dest)]

    def run(self, module: IRModule) -> AnalysisReport:
        self.report.total_instructions = 0
        
        for f in module.functions:
            metrics = FunctionMetrics(f.name)
            metrics.block_count = len(f.blocks)
            
            # Predecessors / Successors map
            preds = {bb.label: [] for bb in f.blocks}
            succs = {bb.label: [] for bb in f.blocks}
            
            # Compute edges
            edge_count = 0
            for bb in f.blocks:
                metrics.instruction_count += len(bb.instrs)
                
                # Check calls
                for instr in bb.instrs:
                    if instr.opcode == OpCode.CALL:
                        metrics.functions_called.append(instr.src1.value)

                # Check terminators
                if not bb.instrs: continue
                last = bb.instrs[-1]
                targets = []
                if last.opcode == OpCode.JMP:
                     targets.append(last.src1.value)
                elif last.opcode == OpCode.BR:
                     targets.append(last.args[0].value)
                     targets.append(last.args[1].value)
                
                # Verify targets exist
                # (Some optimization passes might leave dangling jumps if buggy, assume correct)
                for t in targets:
                    succs[bb.label].append(t)
                    if t in preds:
                        preds[t].append(bb.label)
                    edge_count += 1
            
            self.predecessors[f.name] = preds
            
            # Cyclomatic Complexity = E - N + 2P (P=1 per function)
            # E = edges, N = nodes
            metrics.cyclomatic_complexity = edge_count - len(f.blocks) + 2
            
            self.report.functions[f.name] = metrics
            self.report.total_instructions += metrics.instruction_count
            
            # Dominators
            self._compute_dominators(f, preds)
            
            # Back edges (loops)
            self._detect_loops(f, preds)
            
        return self.report

    def _compute_dominators(self, f: IRFunction, preds):
        # Cooper, Harvey, Kennedy algorithm (Iterative)
        # Dom(n) = {n} U (Intersect(Dom(p)) for p in preds(n))
        
        # Initialize
        all_nodes = set(bb.label for bb in f.blocks)
        doms = {bb.label: all_nodes.copy() for bb in f.blocks}
        
        # Start node
        start_node = f.blocks[0].label
        doms[start_node] = {start_node}
        
        changed = True
        while changed:
            changed = False
            for bb in f.blocks:
                lbl = bb.label
                if lbl == start_node: continue
                
                # Intersect predecessors
                curr_preds = preds[lbl]
                if not curr_preds: continue # Unreachable?
                
                new_dom = doms[curr_preds[0]].copy()
                for p in curr_preds[1:]:
                    if p in doms:
                         new_dom &= doms[p]
                
                new_dom.add(lbl)
                
                if new_dom != doms[lbl]:
                    doms[lbl] = new_dom
                    changed = True
                    
        self.dominators[f.name] = doms
        
        # Compute Immediate Dominators (structuring the tree)
        idoms = {}
        for node, dom_set in doms.items():
            # IDom(n) is the unique node d in Dom(n)-{n} that dominates every other node in Dom(n)-{n}
            # Simplest way: The dominator with set size = len(dom_set) - 1
            strict_doms = dom_set - {node}
            if not strict_doms:
                idoms[node] = None 
            else:
                # Find largest
                best = None
                best_len = -1
                for d in strict_doms:
                    if len(doms[d]) > best_len:
                        best = d
                        best_len = len(doms[d])
                idoms[node] = best
        
        self.immediate_doms[f.name] = idoms

    def _detect_loops(self, f: IRFunction, preds):
        # Back edge: (u, v) where v dominates u
        back_edges = []
        doms = self.dominators[f.name]
        
        for u_bb in f.blocks:
            u = u_bb.label
            # Check successors (implicit in IR structure, but we used preds)
            # wait, loop is edge u -> v
            # check all outgoing edges from u
            succs = []
            if u_bb.instrs:
                last = u_bb.instrs[-1]
                if last.opcode == OpCode.JMP: succs = [last.src1.value]
                elif last.opcode == OpCode.BR: succs = [last.args[0].value, last.args[1].value]
            
            for v in succs:
                if v in doms[u]: # v dominates u
                    back_edges.append((u, v))
                    
        self.back_edges[f.name] = back_edges

    def get_dominator_tree_dot(self, func_name: str) -> str:
        if func_name not in self.immediate_doms: return ""
        idoms = self.immediate_doms[func_name]
        
        lines = [f"digraph DomTree_{func_name} {{", "  node [shape=box];"]
        for node, parent in idoms.items():
            if parent:
                lines.append(f'  "{parent}" -> "{node}";')
            else:
                lines.append(f'  "{node}" [style=bold];') # Root
        lines.append("}")
        return "\n".join(lines)
