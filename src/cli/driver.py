import argparse
import sys
import os
import subprocess
from pathlib import Path

from src.core.util import SourceManager, DiagnosticsEngine, ResultManifest, Timer, Diagnostic, Severity
from src.core.lexer import Lexer
from src.core.parser import Parser
from src.core.sema import SemanticAnalyzer
from src.core.ast import ASTVisualizer
from src.core.ir import IRBuilder, IRGen
from src.core.cfg import CFGVisualizer
from src.core.codegen_llvm import LLVMGen

def main():
    parser = argparse.ArgumentParser(description="MiniPython v1 Compiler")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Compile subcommand
    compile_parser = subparsers.add_parser("compile", help="Compile a MiniPython file")
    compile_parser.add_argument("source", help="Path to source file")
    compile_parser.add_argument("--out", required=True, help="Output directory")
    compile_parser.add_argument("--emit", default="exe", help="Comma separated list: tokens,ast,ir,cfg,llvm,exe,png")
    compile_parser.add_argument("--run", action="store_true", help="Run the generated executable")
    compile_parser.add_argument("--no-opt", action="store_true", help="Disable optimizations")
    compile_parser.add_argument("--keep-temps", action="store_true", help="Keep temporary files")
    
    args = parser.parse_args()
    
    if args.command == "compile":
        run_compile(args)

def run_compile(args):
    # Setup
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    emit_list = args.emit.split(",")
    manifest = ResultManifest(str(out_dir))
    diag = DiagnosticsEngine()
    sm = SourceManager()
    
    # Load Source
    full_path = str(Path(args.source).resolve())
    code = sm.load_file(full_path)
    if not code:
        print(f"Error: Could not read file {full_path}")
        sys.exit(1)
        
    try:
        # --- 1. Tokenize ---
        t_lex = Timer("lex")
        lexer = Lexer(code, full_path, diag)
        tokens = lexer.tokenize()
        t_lex.stop()
        manifest.add_timing("lex", t_lex.duration_ms)
        
        if "tokens" in emit_list:
            with open(out_dir / "tokens.txt", "w") as f:
                for t in tokens: f.write(str(t) + "\n")
            manifest.add_artifact("tokens", str(out_dir / "tokens.txt"))
                
        if diag.has_errors():
            _fail(manifest, diag)

        # --- 2. Parse ---
        t_parse = Timer("parse")
        parser_mod = Parser(tokens, full_path, diag)
        ast_mod = parser_mod.parse()
        t_parse.stop()
        manifest.add_timing("parse", t_parse.duration_ms)
        
        if diag.has_errors():
            _fail(manifest, diag)
            
        if "ast" in emit_list:
            viz = ASTVisualizer()
            dot = viz.generate(ast_mod)
            with open(out_dir / "ast.dot", "w") as f: f.write(dot)
            manifest.add_artifact("ast_dot", str(out_dir / "ast.dot"))
            if "png" in emit_list:
                _render_dot(out_dir / "ast.dot", out_dir / "ast.png")
                manifest.add_artifact("ast_png", str(out_dir / "ast.png"))

        # --- 3. Semantics ---
        t_sema = Timer("sema")
        sema = SemanticAnalyzer(diag)
        sema.check(ast_mod)
        t_sema.stop()
        manifest.add_timing("sema", t_sema.duration_ms)
        
        if diag.has_errors():
            _fail(manifest, diag)

        # --- 4. IR Gen ---
        t_ir = Timer("ir")
        builder = IRBuilder()
        ir_gen = IRGen(builder)
        ir_gen.gen_module(ast_mod)
        t_ir.stop()
        manifest.add_timing("ir_gen", t_ir.duration_ms)

        if "ir" in emit_list:
            with open(out_dir / "ir.txt", "w") as f:
                for func in builder.module.functions:
                    f.write(f"Function {func.name}:\n")
                    for bb in func.blocks:
                        f.write(f"  {bb.label}:\n")
                        for i in bb.instrs:
                            f.write(f"    {i}\n")
            manifest.add_artifact("ir", str(out_dir / "ir.txt"))

        if "cfg" in emit_list:
            viz_cfg = CFGVisualizer()
            dot_cfg = viz_cfg.generate(builder.module)
            with open(out_dir / "cfg.dot", "w") as f: f.write(dot_cfg)
            manifest.add_artifact("cfg_dot", str(out_dir / "cfg.dot"))
            if "png" in emit_list:
                _render_dot(out_dir / "cfg.dot", out_dir / "cfg.png")
                manifest.add_artifact("cfg_png", str(out_dir / "cfg.png"))

        # --- 5. Codegen (LLVM) ---
        t_llvm = Timer("llvm")
        llvm_gen = LLVMGen()
        llvm_ir = llvm_gen.gen(builder.module)
        t_llvm.stop()
        manifest.add_timing("llvm", t_llvm.duration_ms)
        
        ll_path = out_dir / "out.ll"
        with open(ll_path, "w") as f: f.write(llvm_ir)
        manifest.add_artifact("llvm", str(ll_path))
        
        # --- 6. Compile to Exe ---
        if "exe" in emit_list or args.run:
            t_clang = Timer("clang")
            
            # Path to runtime
            runtime_src = Path(__file__).parent.parent.parent / "runtime" / "runtime.c"
            
            # If not found (e.g. running from build dir), try relative
            if not runtime_src.exists():
                 runtime_src = Path("runtime/runtime.c").resolve()
            
            if not runtime_src.exists():
                print(f"Warning: Runtime not found at {runtime_src}")
            
            exe_path = out_dir / "a.out"
            cmd = ["clang", str(ll_path), str(runtime_src), "-o", str(exe_path), "-Wno-everything"]
            
            res = subprocess.run(cmd, capture_output=True, text=True)
            t_clang.stop()
            manifest.add_timing("clang", t_clang.duration_ms)
            
            if res.returncode != 0:
                diag.report(Diagnostic(Severity.ERROR, "clang", 0, 0, f"Clang failed: {res.stderr}"))
                _fail(manifest, diag)
            else:
                manifest.add_artifact("exe", str(exe_path))
                
        # --- 7. Run ---
        if args.run:
            exe_path = out_dir / "a.out"
            if exe_path.exists():
                t_run = Timer("run")
                res = subprocess.run([str(exe_path)], capture_output=True, text=True)
                t_run.stop()
                manifest.add_timing("run", t_run.duration_ms)
                
                with open(out_dir / "run_output.txt", "w") as f:
                    f.write(res.stdout)
                manifest.add_artifact("run_output", str(out_dir / "run_output.txt"))
                
                print(f"--- execution output ---\n{res.stdout}------------------------")
                
        manifest.save()
        print(f"Build successful. Artifacts in {out_dir}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        diag.report(Diagnostic(Severity.ERROR, "compiler", 0, 0, f"Internal Error: {e}"))
        _fail(manifest, diag)

def _fail(manifest, diag):
    manifest.status = "fail"
    manifest.diagnostics = diag.to_json()
    manifest.save()
    for d in diag.diagnostics:
        print(f"{d.severity.name}: {d.file_path}:{d.line}:{d.col} {d.message}")
    sys.exit(1)

def _render_dot(path_in, path_out):
    try:
        subprocess.run(["dot", "-Tpng", str(path_in), "-o", str(path_out)], check=False)
    except Exception as e:
        print(f"Warning: Failed to render dot: {e}")

if __name__ == "__main__":
    main()
