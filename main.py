#!/usr/bin/env python3
# =============================================================
# MAIN TRANSPILER — Code Genesis
# Course: Compiler Design (TCS-601)
# Project: Code Genesis - C to Python Transpiler
# Team: Striver (CD-VI-T080)
# =============================================================
# Usage:
#   python main.py input.c              → writes output.py
#   python main.py input.c -v           → verbose (all phases)
#   python main.py input.c -o result.py → custom output name
# =============================================================

import sys, os, argparse

# ---- Import all phases ----
# Everything is in the same directory, so standard imports work.
from preprocessor   import Preprocessor
from lexer          import Lexer
from parser         import Parser, ASTPrinter
from semantic       import SemanticAnalyzer
from ir_generator   import IRGenerator
from optimizer      import Optimizer
from code_generator import CodeGenerator


# ---------------------------------------------------------------
# PIPELINE
# ---------------------------------------------------------------
def transpile(source_code, verbose=False, output_path='output.py'):
    print("\n╔══════════════════════════════════════════════╗")
    print("║   CODE GENESIS  —  C to Python Transpiler   ║")
    print("║   Team: Striver  |  TCS-601                 ║")
    print("╚══════════════════════════════════════════════╝\n")

    # ── PHASE 0: Preprocessing ────────────────────────────────
    print("▶ Phase 0: Preprocessing (#define, #include)...")
    pp = Preprocessor(source_code)
    source_code = pp.preprocess()
    if verbose:
        pp.print_report()
    print(f"  ✓ Preprocessing complete.")

    # ── PHASE 1: Lexical Analysis ──────────────────────────────
    print("▶ Phase 1: Lexical Analysis (Tokenization)...")
    lexer  = Lexer(source_code)
    tokens = lexer.tokenize()
    if verbose:
        lexer.print_tokens()
    print(f"  ✓ {len(tokens)} tokens produced.")

    # ── PHASE 2: Parsing & AST Construction ───────────────────
    print("▶ Phase 2: Parsing & AST Construction...")
    try:
        parser = Parser(tokens)
        ast    = parser.parse()
    except SyntaxError as e:
        print(f"  ✗ Syntax Error: {e}")
        sys.exit(1)
    if verbose:
        print("\n  Abstract Syntax Tree:")
        ASTPrinter().print(ast)
    print("  ✓ AST built successfully.")

    # ── PHASE 3: Semantic Analysis ────────────────────────────
    print("▶ Phase 3: Semantic Analysis & Symbol Table...")
    analyzer = SemanticAnalyzer()
    ok       = analyzer.analyze(ast)
    if verbose:
        analyzer.symbol_table.print_table()
    if not ok:
        print("  ✗ Semantic errors found. Stopping.")
        sys.exit(1)
    print("  ✓ No semantic errors.")

    # ── PHASE 4: IR Generation ────────────────────────────────
    print("▶ Phase 4: Intermediate Representation (TAC)...")
    irgen = IRGenerator()
    ir    = irgen.generate(ast)
    if verbose:
        irgen.print_ir()
    print(f"  ✓ {len(ir)} IR instructions generated.")

    # ── PHASE 5: Optimization ─────────────────────────────────
    print("▶ Phase 5: Optimization (fold / propagate / DCE)...")
    opt           = Optimizer(ir)
    optimized_ir  = opt.optimize()
    if verbose:
        opt.print_comparison()
    removed = opt.stats['removed']
    print(f"  ✓ Optimization done. {removed} instruction(s) removed.")

    # ── PHASE 6: Python Code Generation ───────────────────────
    print("▶ Phase 6: Python Code Generation...")
    codegen     = CodeGenerator()
    python_code = codegen.generate(ast)
    if verbose:
        print("\n  Generated Python Code:")
        print("  " + "-"*50)
        for line in python_code.splitlines():
            print("  " + line)
        print("  " + "-"*50)
    print("  ✓ Python code generated.")

    # ── SAVE OUTPUT ───────────────────────────────────────────
    with open(output_path, 'w') as f:
        f.write(python_code)
    print(f"\n✅ Transpilation complete!  Output: {output_path}\n")
    return python_code


# ---------------------------------------------------------------
# CLI
# ---------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(
        description='Code Genesis: C to Python Transpiler'
    )
    ap.add_argument('input',  help='Input C source file')
    ap.add_argument('-o', '--output', default='output.py',
                    help='Output Python file (default: output.py)')
    ap.add_argument('-v', '--verbose', action='store_true',
                    help='Show all phase details')
    args = ap.parse_args()

    if not os.path.isfile(args.input):
        print(f"Error: File '{args.input}' not found.")
        sys.exit(1)

    with open(args.input) as f:
        source = f.read()

    transpile(source, verbose=args.verbose, output_path=args.output)


if __name__ == '__main__':
    # If called with no args, run the built-in demo
    if len(sys.argv) == 1:
        demo = """
int factorial(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

int main() {
    int i = 1;
    while (i <= 5) {
        int f = factorial(i);
        printf(i);
        printf(f);
        i = i + 1;
    }
    return 0;
}
"""
        transpile(demo, verbose=True, output_path='output.py')
    else:
        main()
