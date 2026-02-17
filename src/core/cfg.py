from .ir import *

class CFGVisualizer:
    def __init__(self):
        self.lines = []

    def generate(self, mod: IRModule) -> str:
        self.lines = ["digraph CFG {", "  node [shape=box, fontname=\"Courier\"];"]
        for f in mod.functions:
            self.lines.append(f'  subgraph cluster_{f.name} {{')
            self.lines.append(f'    label = "Func {f.name}";')
            
            block_map = {} # label -> id
            for bb in f.blocks:
                bid = f"{f.name}_{bb.label}"
                block_map[bb.label] = bid
                
                # HTML label for instructions
                rows = [f"<b>{bb.label}:</b>"]
                for instr in bb.instrs:
                    rows.append(f"{str(instr)}")
                lbl_html = "<br align='left'/>".join(rows)
                self.lines.append(f'    {bid} [label=<{lbl_html}>];')

            # Edges
            for bb in f.blocks:
                src_id = block_map[bb.label]
                if not bb.instrs: continue
                last = bb.instrs[-1]
                
                if last.opcode == OpCode.JMP:
                    tgt_lbl = last.src1.value
                    if tgt_lbl in block_map:
                        self.lines.append(f"    {src_id} -> {block_map[tgt_lbl]};")
                elif last.opcode == OpCode.BR:
                    t_lbl = last.args[0].value
                    f_lbl = last.args[1].value
                    if t_lbl in block_map:
                         self.lines.append(f'    {src_id} -> {block_map[t_lbl]} [label="T"];')
                    if f_lbl in block_map:
                         self.lines.append(f'    {src_id} -> {block_map[f_lbl]} [label="F"];')
                         
            self.lines.append("  }")
        self.lines.append("}")
        return "\n".join(self.lines)
