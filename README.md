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
  - Optimizer
  - Code Generator
