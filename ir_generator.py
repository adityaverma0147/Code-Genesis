from lexer import Lexer
from parser import (Parser, ProgramNode, FunctionNode, BlockNode,
                    DeclarationNode, AssignNode, IfNode, WhileNode, ForNode,
                    ReturnNode, PrintNode, BinOpNode, UnaryOpNode,
                    NumberNode, StringNode, IdentifierNode, FunctionCallNode,
                    PointerTypeNode, DereferenceNode, AddressOfNode)


class IRInstruction:
    def __init__(self, op, arg1=None, arg2=None, result=None):
        self.op     = op
        self.arg1   = arg1
        self.arg2   = arg2
        self.result = result

    def __repr__(self):
        if self.op == 'LABEL':
            return f"LABEL {self.result}:"
        if self.op == 'GOTO':
            return f"GOTO {self.result}"
        if self.op == 'IF':
            return f"IF {self.arg1} GOTO {self.result}"
        if self.op == 'IF_FALSE':
            return f"IF_FALSE {self.arg1} GOTO {self.result}"
        if self.op == 'PARAM':
            return f"PARAM {self.arg1}"
        if self.op == 'CALL':
            return f"{self.result} = CALL {self.arg1}, {self.arg2} args"
        if self.op == 'RETURN':
            return f"RETURN {self.arg1}"
        if self.op == 'PRINT':
            return f"PRINT {self.arg1}"
        if self.op == 'FUNC':
            return f"\nFUNC {self.result}({self.arg1})"
        if self.op == 'END_FUNC':
            return f"END_FUNC\n"
        if self.arg2 is not None:
            return f"{self.result} = {self.arg1} {self.op} {self.arg2}"
        if self.arg1 is not None:
            return f"{self.result} = {self.arg1}"
        return f"{self.op}"


class IRGenerator:
    def __init__(self):
        self.instructions = []
        self._temp_count  = 0
        self._label_count = 0

    def new_temp(self):
        name = f't{self._temp_count}'
        self._temp_count += 1
        return name

    def new_label(self):
        name = f'L{self._label_count}'
        self._label_count += 1
        return name

    def emit(self, op, arg1=None, arg2=None, result=None):
        instr = IRInstruction(op, arg1, arg2, result)
        self.instructions.append(instr)
        return instr

    def generate(self, node):
        if node is None:
            return self.instructions
        self.visit(node)
        return self.instructions

    def visit(self, node):
        if node is None:
            return None
        method = f'visit_{type(node).__name__}'
        return getattr(self, method, self.generic_visit)(node)

    def generic_visit(self, node):
        return None

    def visit_ProgramNode(self, node):
        for fn in node.functions:
            self.visit(fn)

    def visit_FunctionNode(self, node):
        param_names = ', '.join(p[1] for p in node.params)
        self.emit('FUNC', arg1=param_names, result=node.name)
        for p_type, p_name in node.params:
            self.emit('PARAM_DECL', arg1=p_type, result=p_name)
        self.visit(node.body)
        self.emit('END_FUNC')

    def visit_BlockNode(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_DeclarationNode(self, node):
        res_name = node.name
        if isinstance(node.var_type, PointerTypeNode):
            var_type = f"{node.var_type.base_type}{'*' * node.var_type.levels}"
        else:
            var_type = node.var_type

        if node.value:
            val = self.visit(node.value)
            self.emit('=', arg1=val, result=res_name)
        else:
            self.emit('DECL', arg1=var_type, result=res_name)

    def visit_AssignNode(self, node):
        val = self.visit(node.value)
        if isinstance(node.target, DereferenceNode):
            ptr = self.visit(node.target.operand)
            self.emit('STORE', arg1=val, result=ptr)
        else:
            self.emit('=', arg1=val, result=node.target.name)

    def visit_IfNode(self, node):
        cond      = self.visit(node.condition)
        else_lbl  = self.new_label()
        end_lbl   = self.new_label()

        self.emit('IF_FALSE', arg1=cond, result=else_lbl)
        self.visit(node.then_block)
        self.emit('GOTO', result=end_lbl)
        self.emit('LABEL', result=else_lbl)
        if node.else_block:
            self.visit(node.else_block)
        self.emit('LABEL', result=end_lbl)

    def visit_WhileNode(self, node):
        start_lbl = self.new_label()
        end_lbl   = self.new_label()
        self.emit('LABEL', result=start_lbl)
        cond = self.visit(node.condition)
        self.emit('IF_FALSE', arg1=cond, result=end_lbl)
        self.visit(node.body)
        self.emit('GOTO', result=start_lbl)
        self.emit('LABEL', result=end_lbl)

    def visit_ForNode(self, node):
        if node.init:
            if isinstance(node.init, list):
                for stmt in node.init:
                    self.visit(stmt)
            else:
                self.visit(node.init)
        start_lbl = self.new_label()
        end_lbl   = self.new_label()
        self.emit('LABEL', result=start_lbl)
        cond = self.visit(node.condition)
        self.emit('IF_FALSE', arg1=cond, result=end_lbl)
        self.visit(node.body)
        self.visit(node.update)
        self.emit('GOTO', result=start_lbl)
        self.emit('LABEL', result=end_lbl)

    def visit_ReturnNode(self, node):
        val = self.visit(node.value)
        self.emit('RETURN', arg1=val)

    def visit_PrintNode(self, node):
        for arg in node.args:
            val = self.visit(arg)
            self.emit('PRINT', arg1=val)

    def visit_BinOpNode(self, node):
        left  = self.visit(node.left)
        right = self.visit(node.right)
        temp  = self.new_temp()
        self.emit(node.op, arg1=left, arg2=right, result=temp)
        return temp

    def visit_UnaryOpNode(self, node):
        operand = self.visit(node.operand)
        temp    = self.new_temp()
        op = 'UNARY_MINUS' if node.op == '-' else node.op
        self.emit(op, arg1=operand, result=temp)
        return temp

    def visit_DereferenceNode(self, node):
        operand = self.visit(node.operand)
        temp    = self.new_temp()
        self.emit('DEREF', arg1=operand, result=temp)
        return temp

    def visit_AddressOfNode(self, node):
        operand = self.visit(node.operand)
        temp    = self.new_temp()
        self.emit('ADDR', arg1=operand, result=temp)
        return temp

    def visit_NumberNode(self, node):
        return str(node.value)

    def visit_StringNode(self, node):
        return f'"{node.value}"'

    def visit_IdentifierNode(self, node):
        return node.name

    def visit_FunctionCallNode(self, node):
        for arg in node.args:
            val = self.visit(arg)
            self.emit('PARAM', arg1=val)
        temp = self.new_temp()
        self.emit('CALL', arg1=node.name, arg2=len(node.args), result=temp)
        return temp

    def print_ir(self):
        print("\n" + "="*55)
        print("PHASE 4: THREE-ADDRESS CODE (INTERMEDIATE REPR.)")
        print("="*55)
        for i, instr in enumerate(self.instructions):
            prefix = '    ' if instr.op not in ('FUNC', 'END_FUNC', 'LABEL') else ''
            print(f"{i:>3}  {prefix}{instr}")
        print("="*55)


if __name__ == '__main__':
    code = """
int main() {
    int x = 5;
    int y = 3;
    int z = x + y * 2;
    if (z > 10) {
        printf("big");
    } else {
        printf("small");
    }
    int i = 0;
    while (i < 3) {
        i = i + 1;
    }
    return 0;
}
"""
    lexer  = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast    = parser.parse()

    irgen = IRGenerator()
    irgen.generate(ast)
    irgen.print_ir()
