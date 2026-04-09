import sys
import os
import io
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Import transpiler phases
from preprocessor import Preprocessor
from lexer import Lexer
from parser import Parser, ASTPrinter
from semantic import SemanticAnalyzer
from ir_generator import IRGenerator
from optimizer import Optimizer
from code_generator import CodeGenerator

app = Flask(__name__, static_folder='web')
CORS(app)

def capture_output(func, *args, **kwargs):
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        func(*args, **kwargs)
        output = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout
    return output

@app.route('/')
def index():
    return send_from_directory('web', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('web', path)

@app.route('/api/transpile', methods=['POST'])
def transpile():
    data = request.json
    code = data.get('code', '')
    
    if not code:
        return jsonify({'error': 'No code provided'}), 400

    try:
        # 0. Preprocessing
        pp = Preprocessor(code)
        processed_code = pp.preprocess()
        pp_report = pp.get_report()
        
        # 1. Lexing
        lexer = Lexer(processed_code)
        tokens = lexer.tokenize()
        token_str = capture_output(lexer.print_tokens)
        
        # 2. Parsing
        parser = Parser(tokens)
        ast = parser.parse()
        ast_str = capture_output(ASTPrinter().print, ast)
        
        # 3. Semantic Analysis
        analyzer = SemanticAnalyzer()
        ok = analyzer.analyze(ast)
        semantic_str = capture_output(analyzer.symbol_table.print_table)
        if not ok:
            semantic_str = "Semantic Errors:\n" + "\n".join(analyzer.errors)
        
        # 4. IR Generation
        irgen = IRGenerator()
        ir = irgen.generate(ast)
        ir_str = capture_output(irgen.print_ir)
        
        # 5. Optimization
        opt = Optimizer(ir)
        optimized_ir = opt.optimize()
        opt_str = capture_output(opt.print_comparison)
        
        # 6. Code Generation
        codegen = CodeGenerator()
        python_code = codegen.generate(ast)
        
        return jsonify({
            'tokens': token_str,
            'ast': ast_str,
            'symbols': semantic_str,
            'semantic': "✓ Semantic Analysis Passed" if ok else "✗ Semantic Analysis Failed",
            'ir': pp_report + "\n" + ir_str + "\n\n" + opt_str,
            'python': python_code,
            'stats': {
                'tokens': len(tokens) - 1, # Exclude EOF
                'ir': len(ir),
                'symbols': len(analyzer.symbol_table.scopes[0]) if analyzer.symbol_table.scopes else 0,
                'lines': len(python_code.splitlines())
            }
        })
        
    except SyntaxError as e:
        return jsonify({'error': f"Syntax Error: {str(e)}"}), 200
    except Exception as e:
        import traceback
        return jsonify({'error': f"Internal Error: {str(e)}\n{traceback.format_exc()}"}), 200

if __name__ == '__main__':
    # Use the port 5000 by default
    app.run(host='0.0.0.0', port=5000, debug=True)
