# Code Genesis
### A Code Transpiler with Optimization Techniques

Code Genesis is a web-based mini compiler (transpiler) that converts a **C-like language into Python** while demonstrating the core phases of compiler design.

The project aims to bridge the gap between **theoretical compiler concepts and practical implementation** by providing a modular pipeline that illustrates each stage of compilation.

This system helps students and developers understand how source code is transformed internally through different compiler phases such as **lexical analysis, parsing, semantic analysis, intermediate representation, optimization, and code generation.**

---

# Features

- C-like language to Python transpilation  
- Step-by-step compiler pipeline visualization  
- Intermediate Representation (IR) generation  
- Code optimization techniques  
- Modular compiler architecture  
- Web-based interface for easy code input and output visualization

---

# Compiler Pipeline

The transpiler follows the standard compiler design pipeline:

### 1. Lexical Analysis
- Tokenizes the input program
- Identifies keywords, identifiers, operators, and literals
- Produces a sequence of tokens

### 2. Syntax Analysis
- Constructs the **Abstract Syntax Tree (AST)**
- Validates grammar rules
- Detects syntax errors

### 3. Semantic Analysis
- Performs type checking
- Manages the **symbol table**
- Ensures semantic correctness of the program

### 4. Intermediate Representation (IR)
- Converts AST into a structured IR
- Simplifies further transformations and optimizations

### 5. Code Optimization
Applies optimization techniques such as:
- Constant Folding
- Dead Code Elimination
- Loop Optimization

### 6. Python Code Generation
- Generates optimized Python code
- Produces readable and executable output

---

# Compiler Engine
- **Python**
- Implements the complete compiler pipeline including:
  - Lexer
  - Parser
  - Semantic Analyzer
  - IR Generator
  - Code Generator

---

# How to Run

### 1. Prerequisites
Ensure you have **Python 3.8+** installed. You will also need the following dependencies:
```bash
pip install flask flask-cors
```

### 2. Running in VS Code
1. **Open the Project**: Open the `Code-Genesis` folder in VS Code.
2. **Open Terminal**: Go to `Terminal` -> `New Terminal` (or press ``Ctrl + ` ``).
3. **Launch the Web UI**:
   ```bash
   python api_server.py
   ```
4. **Access the App**: Once the terminal says `Running on http://127.0.0.1:5005`, open your browser and navigate to:
   [http://localhost:5005](http://localhost:5005)

### 3. Running via Command Line (CLI)
You can also run the transpiler directly on a C file without the UI:
```bash
python main.py sample.c
```
Use `-v` for verbose output (shows all compiler phases):
```bash
python main.py sample.c -v
```

### 4. Running Tests
To verify all compiler phases are working correctly:
```bash
python test_all.py
```

---

# Team Striver
- **Project**: Code Genesis - C to Python Transpiler
- **Course**: Compiler Design (TCS-601)
