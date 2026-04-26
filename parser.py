from lexer import Lexer, Token


class ProgramNode:
    def __init__(self, functions):
        self.functions = functions

class FunctionNode:
    def __init__(self, return_type, name, params, body):
        self.return_type = return_type
        self.name        = name
        self.params      = params
        self.body        = body

class BlockNode:
    def __init__(self, statements):
        self.statements = statements

class DeclarationNode:
    def __init__(self, var_type, name, value=None):
        self.var_type = var_type
        self.name     = name
        self.value    = value

class AssignNode:
    def __init__(self, target, value):
        self.target = target
        self.value  = value

class IfNode:
    def __init__(self, condition, then_block, else_block=None):
        self.condition  = condition
        self.then_block = then_block
        self.else_block = else_block

class WhileNode:
    def __init__(self, condition, body):
        self.condition = condition
        self.body      = body

class ForNode:
    def __init__(self, init, condition, update, body):
        self.init      = init
        self.condition = condition
        self.update    = update
        self.body      = body

class ReturnNode:
    def __init__(self, value):
        self.value = value

class PrintNode:
    def __init__(self, args):
        self.args = args

class BinOpNode:
    def __init__(self, left, op, right):
        self.left  = left
        self.op    = op
        self.right = right

class UnaryOpNode:
    def __init__(self, op, operand):
        self.op      = op
        self.operand = operand

class NumberNode:
    def __init__(self, value):
        self.value = value

class StringNode:
    def __init__(self, value):
        self.value = value

class IdentifierNode:
    def __init__(self, name):
        self.name = name

class FunctionCallNode:
    def __init__(self, name, args):
        self.name = name
        self.args = args

class PointerTypeNode:
    def __init__(self, base_type, levels):
        self.base_type = base_type
        self.levels    = levels

class DereferenceNode:
    def __init__(self, operand):
        self.operand = operand

class AddressOfNode:
    def __init__(self, operand):
        self.operand = operand


class Parser:
    def __init__(self, tokens):
        if not tokens:
            raise SyntaxError("No tokens to parse — input may be empty.")
        self.tokens = tokens
        self.pos    = 0

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token('EOF', '', -1)

    def peek(self, offset=1):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return Token('EOF', '', -1)

    def eat(self, expected_type=None, expected_value=None):
        tok = self.current()
        if tok.type == 'EOF':
            raise SyntaxError(
                f"Unexpected end of input. Expected '{expected_type or 'token'}'"
                + (f" with value '{expected_value}'" if expected_value else "")
            )
        if expected_type and tok.type != expected_type:
            raise SyntaxError(
                f"Line {tok.line}: Expected token type '{expected_type}' "
                f"but got '{tok.type}' ('{tok.value}')"
            )
        if expected_value and tok.value != expected_value:
            raise SyntaxError(
                f"Line {tok.line}: Expected '{expected_value}' "
                f"but got '{tok.value}'"
            )
        self.pos += 1
        return tok

    def is_type_keyword(self):
        return self.current().type == 'KEYWORD' and \
               self.current().value in ('int', 'float', 'char', 'void')

    def parse(self):
        functions = []
        while self.current().type != 'EOF':
            functions.append(self.parse_function())
        if not functions:
            raise SyntaxError("No functions found in the input.")
        return ProgramNode(functions)

    def parse_function(self):
        ret_type = self.eat('KEYWORD').value
        name     = self.eat('IDENTIFIER').value
        self.eat('LPAREN')
        params = self.parse_params()
        self.eat('RPAREN')
        body = self.parse_block()
        return FunctionNode(ret_type, name, params, body)

    def parse_params(self):
        params = []
        while self.current().type != 'RPAREN':
            if self.current().type == 'EOF':
                raise SyntaxError("Unexpected end of input while parsing function parameters.")
            p_type = self.eat('KEYWORD').value
            p_name = self.eat('IDENTIFIER').value
            params.append((p_type, p_name))
            if self.current().type == 'COMMA':
                self.eat('COMMA')
        return params

    def parse_block(self):
        self.eat('LBRACE')
        stmts = []
        while self.current().type not in ('RBRACE', 'EOF'):
            res = self.parse_statement()
            if isinstance(res, list):
                stmts.extend(res)
            else:
                stmts.append(res)
        self.eat('RBRACE')
        return BlockNode(stmts)

    def parse_statement(self):
        tok = self.current()

        if self.is_type_keyword():
            return self.parse_declaration()

        if tok.type == 'KEYWORD' and tok.value == 'if':
            return self.parse_if()

        if tok.type == 'KEYWORD' and tok.value == 'while':
            return self.parse_while()

        if tok.type == 'KEYWORD' and tok.value == 'for':
            return self.parse_for()

        if tok.type == 'KEYWORD' and tok.value == 'return':
            return self.parse_return()

        if tok.type == 'KEYWORD' and tok.value == 'printf':
            return self.parse_print()

        if tok.type == 'IDENTIFIER' and self.peek().type == 'ASSIGN':
            return self.parse_assignment()

        if tok.type == 'MULTIPLY' and self.peek().type == 'IDENTIFIER' and self.peek(2).type == 'ASSIGN':
             self.eat('MULTIPLY')
             name = self.eat('IDENTIFIER').value
             self.eat('ASSIGN')
             value = self.parse_expr()
             self.eat('SEMICOLON')
             return AssignNode(DereferenceNode(IdentifierNode(name)), value)

        expr = self.parse_expr()
        self.eat('SEMICOLON')
        return expr

    def parse_declaration(self):
        base_type_raw = self.eat('KEYWORD').value

        decls = []
        while True:
            stars = 0
            while self.current().type == 'MULTIPLY':
                self.eat('MULTIPLY')
                stars += 1

            var_type = base_type_raw
            if stars > 0:
                var_type = PointerTypeNode(base_type_raw, stars)

            name = self.eat('IDENTIFIER').value
            value = None
            if self.current().type == 'ASSIGN':
                self.eat('ASSIGN')
                value = self.parse_expr()

            decls.append(DeclarationNode(var_type, name, value))

            if self.current().type == 'COMMA':
                self.eat('COMMA')
            else:
                break

        self.eat('SEMICOLON')
        return decls

    def parse_assignment(self):
        name = self.eat('IDENTIFIER').value
        self.eat('ASSIGN')
        value = self.parse_expr()
        self.eat('SEMICOLON')
        return AssignNode(IdentifierNode(name), value)

    def parse_if(self):
        self.eat('KEYWORD', 'if')
        self.eat('LPAREN')
        cond = self.parse_expr()
        self.eat('RPAREN')
        then_block = self.parse_block()
        else_block = None
        if self.current().type == 'KEYWORD' and self.current().value == 'else':
            self.eat('KEYWORD', 'else')
            else_block = self.parse_block()
        return IfNode(cond, then_block, else_block)

    def parse_while(self):
        self.eat('KEYWORD', 'while')
        self.eat('LPAREN')
        cond = self.parse_expr()
        self.eat('RPAREN')
        body = self.parse_block()
        return WhileNode(cond, body)

    def parse_for(self):
        self.eat('KEYWORD', 'for')
        self.eat('LPAREN')
        init = None
        if self.is_type_keyword():
            init = self.parse_declaration_no_semi()
        elif self.current().type == 'IDENTIFIER':
             init = self.parse_update()

        self.eat('SEMICOLON')
        cond = self.parse_expr()
        self.eat('SEMICOLON')
        update = self.parse_update()
        self.eat('RPAREN')
        body = self.parse_block()
        return ForNode(init, cond, update, body)

    def parse_declaration_no_semi(self):
        base_type_raw = self.eat('KEYWORD').value
        decls = []
        while True:
            stars = 0
            while self.current().type == 'MULTIPLY':
                self.eat('MULTIPLY')
                stars += 1
            var_type = base_type_raw
            if stars > 0:
                var_type = PointerTypeNode(base_type_raw, stars)
            name = self.eat('IDENTIFIER').value
            value = None
            if self.current().type == 'ASSIGN':
                self.eat('ASSIGN')
                value = self.parse_expr()
            decls.append(DeclarationNode(var_type, name, value))
            if self.current().type == 'COMMA':
                self.eat('COMMA')
            else:
                break
        return decls

    def parse_update(self):
        name = self.eat('IDENTIFIER').value
        if self.current().type == 'OP' and self.current().value == '++':
            self.eat('OP')
            return AssignNode(IdentifierNode(name), BinOpNode(IdentifierNode(name), '+', NumberNode(1)))
        if self.current().type == 'OP' and self.current().value == '--':
            self.eat('OP')
            return AssignNode(IdentifierNode(name), BinOpNode(IdentifierNode(name), '-', NumberNode(1)))
        self.eat('ASSIGN')
        val = self.parse_expr()
        return AssignNode(IdentifierNode(name), val)

    def parse_return(self):
        self.eat('KEYWORD', 'return')
        value = self.parse_expr()
        self.eat('SEMICOLON')
        return ReturnNode(value)

    def parse_print(self):
        self.eat('KEYWORD', 'printf')
        self.eat('LPAREN')
        args = []
        while self.current().type != 'RPAREN':
            if self.current().type == 'EOF':
                raise SyntaxError("Unexpected end of input inside printf arguments.")
            args.append(self.parse_expr())
            if self.current().type == 'COMMA':
                self.eat('COMMA')
        self.eat('RPAREN')
        self.eat('SEMICOLON')
        return PrintNode(args)

    def parse_expr(self):
        left = self.parse_comparison()
        while self.current().type == 'OP' and self.current().value in ('&&', '||'):
            op    = self.eat('OP').value
            right = self.parse_comparison()
            left  = BinOpNode(left, op, right)
        return left

    def parse_comparison(self):
        left = self.parse_term()
        while True:
            tok = self.current()
            if tok.type in ('LT', 'GT') or \
               (tok.type == 'OP' and tok.value in ('==', '!=', '<=', '>=')):
                op    = self.eat(tok.type).value
                right = self.parse_term()
                left  = BinOpNode(left, op, right)
            else:
                break
        return left

    def parse_term(self):
        left = self.parse_factor()
        while self.current().type in ('PLUS', 'MINUS'):
            op    = self.eat(self.current().type).value
            right = self.parse_factor()
            left  = BinOpNode(left, op, right)
        return left

    def parse_factor(self):
        left = self.parse_unary()
        while self.current().type in ('MULTIPLY', 'DIVIDE', 'MODULO'):
            op    = self.eat(self.current().type).value
            right = self.parse_unary()
            left  = BinOpNode(left, op, right)
        return left

    def parse_unary(self):
        if self.current().type == 'MINUS':
            self.eat('MINUS')
            operand = self.parse_unary()
            return UnaryOpNode('-', operand)

        if self.current().type == 'MULTIPLY':
            self.eat('MULTIPLY')
            operand = self.parse_unary()
            return DereferenceNode(operand)

        if self.current().type == 'ADDR':
            self.eat('ADDR')
            operand = self.parse_unary()
            return AddressOfNode(operand)

        return self.parse_primary()

    def parse_primary(self):
        tok = self.current()

        if tok.type == 'INTEGER':
            self.eat('INTEGER')
            return NumberNode(int(tok.value))

        if tok.type == 'FLOAT':
            self.eat('FLOAT')
            return NumberNode(float(tok.value))

        if tok.type == 'STRING':
            self.eat('STRING')
            return StringNode(tok.value[1:-1])

        if tok.type == 'CHAR_LIT':
            self.eat('CHAR_LIT')
            return StringNode(tok.value[1:-1])

        if tok.type == 'IDENTIFIER':
            name = self.eat('IDENTIFIER').value
            if self.current().type == 'LPAREN':
                self.eat('LPAREN')
                args = []
                while self.current().type != 'RPAREN':
                    if self.current().type == 'EOF':
                        raise SyntaxError(f"Unexpected end of input in call to '{name}'.")
                    args.append(self.parse_expr())
                    if self.current().type == 'COMMA':
                        self.eat('COMMA')
                self.eat('RPAREN')
                return FunctionCallNode(name, args)
            return IdentifierNode(name)

        if tok.type == 'LPAREN':
            self.eat('LPAREN')
            expr = self.parse_expr()
            self.eat('RPAREN')
            return expr

        raise SyntaxError(f"Line {tok.line}: Unexpected token '{tok.value}' ({tok.type})")


class ASTPrinter:
    def print(self, node, indent=0):
        if node is None:
            return
        pad = '  ' * indent
        name = type(node).__name__

        if isinstance(node, ProgramNode):
            print(f"{pad}ProgramNode")
            for fn in node.functions:
                self.print(fn, indent + 1)

        elif isinstance(node, FunctionNode):
            print(f"{pad}FunctionNode: {node.return_type} {node.name}({node.params})")
            self.print(node.body, indent + 1)

        elif isinstance(node, BlockNode):
            print(f"{pad}BlockNode ({len(node.statements)} stmts)")
            for s in node.statements:
                self.print(s, indent + 1)

        elif isinstance(node, DeclarationNode):
            print(f"{pad}DeclarationNode: {node.var_type} {node.name}")
            if node.value:
                self.print(node.value, indent + 1)

        elif isinstance(node, AssignNode):
            print(f"{pad}AssignNode")
            self.print(node.target, indent + 1)
            self.print(node.value, indent + 1)

        elif isinstance(node, IfNode):
            print(f"{pad}IfNode")
            print(f"{pad}  condition:")
            self.print(node.condition, indent + 2)
            print(f"{pad}  then:")
            self.print(node.then_block, indent + 2)
            if node.else_block:
                print(f"{pad}  else:")
                self.print(node.else_block, indent + 2)

        elif isinstance(node, WhileNode):
            print(f"{pad}WhileNode")
            self.print(node.condition, indent + 1)
            self.print(node.body, indent + 1)

        elif isinstance(node, ForNode):
            print(f"{pad}ForNode")
            if node.init:
                if isinstance(node.init, list):
                    for item in node.init:
                        self.print(item, indent + 1)
                else:
                    self.print(node.init, indent + 1)
            self.print(node.condition, indent + 1)
            self.print(node.update, indent + 1)
            self.print(node.body, indent + 1)

        elif isinstance(node, ReturnNode):
            print(f"{pad}ReturnNode")
            self.print(node.value, indent + 1)

        elif isinstance(node, PrintNode):
            print(f"{pad}PrintNode")
            for a in node.args:
                self.print(a, indent + 1)

        elif isinstance(node, BinOpNode):
            print(f"{pad}BinOpNode: '{node.op}'")
            self.print(node.left, indent + 1)
            self.print(node.right, indent + 1)

        elif isinstance(node, UnaryOpNode):
            print(f"{pad}UnaryOpNode: '{node.op}'")
            self.print(node.operand, indent + 1)

        elif isinstance(node, NumberNode):
            print(f"{pad}NumberNode: {node.value}")

        elif isinstance(node, StringNode):
            print(f"{pad}StringNode: \"{node.value}\"")

        elif isinstance(node, IdentifierNode):
            print(f"{pad}IdentifierNode: {node.name}")

        elif isinstance(node, PointerTypeNode):
            print(f"{pad}PointerType: {node.base_type}{'*' * node.levels}")

        elif isinstance(node, DereferenceNode):
            print(f"{pad}DereferenceNode")
            self.print(node.operand, indent + 1)

        elif isinstance(node, AddressOfNode):
            print(f"{pad}AddressOfNode")
            self.print(node.operand, indent + 1)

        elif isinstance(node, FunctionCallNode):
            print(f"{pad}FunctionCallNode: {node.name}()")
            for a in node.args:
                self.print(a, indent + 1)

        else:
            print(f"{pad}{name}")


if __name__ == '__main__':
    code = """
int main() {
    int x = 10;
    int y = 20;
    int sum = x + y;
    if (sum > 25) {
        printf("Sum is large");
    } else {
        printf("Sum is small");
    }
    return 0;
}
"""
    lexer  = Lexer(code)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast    = parser.parse()

    print("\n" + "="*50)
    print("PHASE 2: ABSTRACT SYNTAX TREE")
    print("="*50)
    ASTPrinter().print(ast)
    print("="*50)
