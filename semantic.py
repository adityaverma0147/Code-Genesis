from lexer import Lexer
from parser import (Parser, ProgramNode, FunctionNode, BlockNode,
                    DeclarationNode, AssignNode, IfNode, WhileNode, ForNode,
                    ReturnNode, PrintNode, BinOpNode, UnaryOpNode,
                    NumberNode, StringNode, IdentifierNode, FunctionCallNode,
                    PointerTypeNode, DereferenceNode, AddressOfNode)


class SymbolTable:
    """
    A scoped symbol table. Each scope is a dict {name: info}.
    Scopes are stacked; inner scopes can shadow outer ones.
    """
    def __init__(self):
        self.scopes = [{}] 

    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        self.scopes.pop()

    def declare(self, name, var_type, scope_label='local'):
        # Check for re-declaration in CURRENT scope only
        if name in self.scopes[-1]:
            raise SemanticError(f"Re-declaration of '{name}' in the same scope.")
        self.scopes[-1][name] = {'type': var_type, 'scope': scope_label}

    def lookup(self, name):
        """Search from inner → outer scope."""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def print_table(self):
        print("\n" + "="*50)
        print("PHASE 3: SYMBOL TABLE")
        print("="*50)
        print(f"{'NAME':<20} {'TYPE':<10} {'SCOPE'}")
        print("-"*50)
        for depth, scope in enumerate(self.scopes):
            label = 'global' if depth == 0 else f'scope-{depth}'
            for name, info in scope.items():
                print(f"{name:<20} {info['type']:<10} {label}")
        print("="*50)



class SemanticError(Exception):
    pass


# ---------------------------------------------------------------
# SEMANTIC ANALYZER
# ---------------------------------------------------------------
class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table   = SymbolTable()
        self.errors         = []
        self.current_fn_ret = None   

    def error(self, msg):
        self.errors.append(f"[SemanticError] {msg}")



    def analyze(self, node):
        self.visit(node)
        if self.errors:
            print("\n[!] Semantic Errors Found:")
            for e in self.errors:
                print("   ", e)
        else:
            print("\n[✓] Semantic Analysis Passed — No Errors Found")
        return len(self.errors) == 0

    def visit(self, node):
        method = f'visit_{type(node).__name__}'
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        pass   


    def visit_ProgramNode(self, node):
        for fn in node.functions:
            
            self.symbol_table.declare(fn.name, fn.return_type, 'global')
            self.visit(fn)

    def visit_FunctionNode(self, node):
        self.current_fn_ret = node.return_type
        self.symbol_table.enter_scope()
        for p_type, p_name in node.params:
            try:
                self.symbol_table.declare(p_name, p_type, 'param')
            except SemanticError as e:
                self.error(str(e))
        self.visit(node.body)
        self.symbol_table.exit_scope()

    def visit_BlockNode(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_DeclarationNode(self, node):
        try:
            var_type = node.var_type
            if isinstance(var_type, PointerTypeNode):
                var_type = f"{var_type.base_type}{'*' * var_type.levels}"
            self.symbol_table.declare(node.name, var_type)
        except SemanticError as e:
            self.error(str(e))
        if node.value:
            self.visit(node.value)

    def visit_AssignNode(self, node):
        if isinstance(node.target, IdentifierNode):
            if self.symbol_table.lookup(node.target.name) is None:
                self.error(f"Assignment to undeclared variable '{node.target.name}'.")
        else:
            self.visit(node.target)
        self.visit(node.value)

    def visit_IdentifierNode(self, node):
        if self.symbol_table.lookup(node.name) is None:
            self.error(f"Use of undeclared variable '{node.name}'.")

    def visit_BinOpNode(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visit_UnaryOpNode(self, node):
        self.visit(node.operand)

    def visit_DereferenceNode(self, node):
        self.visit(node.operand)

    def visit_AddressOfNode(self, node):
        self.visit(node.operand)

    def visit_IfNode(self, node):
        self.visit(node.condition)
        self.symbol_table.enter_scope()
        self.visit(node.then_block)
        self.symbol_table.exit_scope()
        if node.else_block:
            self.symbol_table.enter_scope()
            self.visit(node.else_block)
            self.symbol_table.exit_scope()

    def visit_WhileNode(self, node):
        self.visit(node.condition)
        self.symbol_table.enter_scope()
        self.visit(node.body)
        self.symbol_table.exit_scope()

    def visit_ForNode(self, node):
        self.symbol_table.enter_scope()
        if node.init:
            self.visit(node.init)
        self.visit(node.condition)
        self.visit(node.update)
        self.visit(node.body)
        self.symbol_table.exit_scope()

    def visit_ReturnNode(self, node):
        self.visit(node.value)

    def visit_PrintNode(self, node):
        for arg in node.args:
            self.visit(arg)

    def visit_FunctionCallNode(self, node):
        
        if self.symbol_table.lookup(node.name) is None:
            
            builtins = {'printf', 'scanf', 'main'}
            if node.name not in builtins:
                self.error(f"Call to undeclared function '{node.name}'.")
        for arg in node.args:
            self.visit(arg)




if __name__ == '__main__':
    code = """
int add(int a, int b) {
    int result = a + b;
    return result;
}

int main() {
    int x = 5;
    int y = 10;
    int z = add(x, y);
    if (z > 10) {
        printf("big");
    }
    return 0;
}
"""
    lexer    = Lexer(code)
    tokens   = lexer.tokenize()
    parser   = Parser(tokens)
    ast      = parser.parse()

    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    analyzer.symbol_table.print_table()
