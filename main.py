#!/usr/bin/env python3

import sys, os, argparse

from preprocessor   import Preprocessor
from lexer          import Lexer
from parser         import Parser, ASTPrinter
from semantic       import SemanticAnalyzer
from ir_generator   import IRGenerator
from optimizer      import Optimizer
from code_generator import CodeGenerator


def transpile(source_code, verbose=False, output_path='output.py'):
    print("\n╔══════════════════════════════════════════════╗")
    print("║   CODE GENESIS  —  C to Python Transpiler   ║")
    print("║   Team: Striver  |  TCS-601                 ║")
    print("╚══════════════════════════════════════════════╝\n")

    if not source_code or not source_code.strip():
        print("  ✗ Error: Empty source code provided.")
        sys.exit(1)

    print("▶ Phase 0: Preprocessing (#define, #include)...")
    try:
        pp = Preprocessor(source_code)
        source_code = pp.preprocess()
        if verbose:
            pp.print_report()
        print(f"  ✓ Preprocessing complete.")
    except Exception as e:
        print(f"  ✗ Preprocessing Error: {e}")
        sys.exit(1)

    print("▶ Phase 1: Lexical Analysis (Tokenization)...")
    try:
        lexer  = Lexer(source_code)
        tokens = lexer.tokenize()
        if lexer.errors:
            for err in lexer.errors:
                print(f"  ⚠ {err}")
        if verbose:
            lexer.print_tokens()
        print(f"  ✓ {len(tokens)} tokens produced.")
    except Exception as e:
        print(f"  ✗ Lexical Analysis Error: {e}")
        sys.exit(1)

    print("▶ Phase 2: Parsing & AST Construction...")
    try:
        parser = Parser(tokens)
        ast    = parser.parse()
    except SyntaxError as e:
        print(f"  ✗ Syntax Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"  ✗ Parser Error: {e}")
        sys.exit(1)
    if verbose:
        print("\n  Abstract Syntax Tree:")
        ASTPrinter().print(ast)
    print("  ✓ AST built successfully.")

    print("▶ Phase 3: Semantic Analysis & Symbol Table...")
    try:
        analyzer = SemanticAnalyzer()
        ok       = analyzer.analyze(ast)
        if verbose:
            analyzer.symbol_table.print_table()
        if not ok:
            print("  ✗ Semantic errors found. Stopping.")
            sys.exit(1)
        print("  ✓ No semantic errors.")
    except Exception as e:
        print(f"  ✗ Semantic Analysis Error: {e}")
        sys.exit(1)

    print("▶ Phase 4: Intermediate Representation (TAC)...")
    try:
        irgen = IRGenerator()
        ir    = irgen.generate(ast)
        if verbose:
            irgen.print_ir()
        print(f"  ✓ {len(ir)} IR instructions generated.")
    except Exception as e:
        print(f"  ✗ IR Generation Error: {e}")
        sys.exit(1)

    print("▶ Phase 5: Optimization (fold / propagate / DCE)...")
    try:
        opt           = Optimizer(ir)
        optimized_ir  = opt.optimize()
        if verbose:
            opt.print_comparison()
        removed = opt.stats['removed']
        print(f"  ✓ Optimization done. {removed} instruction(s) removed.")
    except Exception as e:
        print(f"  ✗ Optimization Error: {e}")
        sys.exit(1)

    print("▶ Phase 6: Python Code Generation...")
    try:
        codegen     = CodeGenerator()
        python_code = codegen.generate(ast)
        if verbose:
            print("\n  Generated Python Code:")
            print("  " + "-"*50)
            for line in python_code.splitlines():
                print("  " + line)
            print("  " + "-"*50)
        print("  ✓ Python code generated.")
    except Exception as e:
        print(f"  ✗ Code Generation Error: {e}")
        sys.exit(1)

    try:
        with open(output_path, 'w') as f:
            f.write(python_code)
        print(f"\n✅ Transpilation complete!  Output: {output_path}\n")
    except IOError as e:
        print(f"\n  ✗ Failed to write output file: {e}")
        sys.exit(1)

    return python_code


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

    try:
        with open(args.input, encoding='utf-8') as f:
            source = f.read()
    except UnicodeDecodeError:
        with open(args.input, encoding='latin-1') as f:
            source = f.read()
    except IOError as e:
        print(f"Error: Could not read file '{args.input}': {e}")
        sys.exit(1)

    transpile(source, verbose=args.verbose, output_path=args.output)


if __name__ == '__main__':
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
