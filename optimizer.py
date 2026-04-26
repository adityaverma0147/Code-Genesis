from ir_generator import IRInstruction

ARITHMETIC_OPS = {'+', '-', '*', '/', '%'}
COMPARE_OPS    = {'==', '!=', '<', '>', '<=', '>='}


def _is_number(s):
    try:
        float(s)
        return True
    except (TypeError, ValueError):
        return False


def _eval(a, op, b):
    try:
        a, b = float(a), float(b)
    except (TypeError, ValueError):
        return None
    result = {
        '+': a + b, '-': a - b,
        '*': a * b, '/': a / b if b != 0 else None,
        '%': a % b if b != 0 else None,
        '==': int(a == b), '!=': int(a != b),
        '<':  int(a <  b), '>':  int(a >  b),
        '<=': int(a <= b), '>=': int(a >= b),
    }.get(op)
    if result is None:
        return None
    return str(int(result)) if result == int(result) else str(result)


def constant_folding(instructions):
    if not instructions:
        return []
    optimized = []
    for instr in instructions:
        if instr.op in ARITHMETIC_OPS | COMPARE_OPS:
            if _is_number(instr.arg1) and _is_number(instr.arg2):
                value = _eval(instr.arg1, instr.op, instr.arg2)
                if value is not None:
                    new_instr = IRInstruction('=', arg1=value, result=instr.result)
                    optimized.append(new_instr)
                    continue
        if instr.op == 'UNARY_MINUS' and _is_number(instr.arg1):
            value = str(-float(instr.arg1))
            if float(value) == int(float(value)):
                value = str(int(float(value)))
            optimized.append(IRInstruction('=', arg1=value, result=instr.result))
            continue
        optimized.append(instr)
    return optimized


def constant_propagation(instructions):
    if not instructions:
        return []
    const_map = {}
    optimized = []

    def resolve(val):
        return const_map.get(val, val)

    for instr in instructions:
        if instr.op == '=' and _is_number(instr.arg1):
            const_map[instr.result] = instr.arg1
        elif instr.op == '=' and instr.result in const_map:
            if not _is_number(instr.arg1):
                del const_map[instr.result]

        new_instr = IRInstruction(
            op     = instr.op,
            arg1   = resolve(instr.arg1) if instr.arg1 is not None else None,
            arg2   = resolve(instr.arg2) if instr.arg2 is not None else None,
            result = instr.result
        )
        optimized.append(new_instr)

    return constant_folding(optimized)


def dead_code_elimination(instructions):
    if not instructions:
        return []
    used = set()
    for instr in instructions:
        if instr.arg1 is not None and not _is_number(instr.arg1):
            used.add(str(instr.arg1).strip('"'))
        if instr.arg2 is not None and not _is_number(instr.arg2):
            used.add(str(instr.arg2).strip('"'))
        if instr.op in ('IF_FALSE', 'IF', 'RETURN', 'PRINT', 'PARAM'):
            if instr.arg1:
                used.add(str(instr.arg1).strip('"'))

    optimized = []
    for instr in instructions:
        is_temp_assign = (
            instr.result is not None
            and str(instr.result).startswith('t')
            and instr.op not in ('FUNC', 'END_FUNC', 'LABEL',
                                 'GOTO', 'IF_FALSE', 'RETURN',
                                 'PRINT', 'PARAM', 'CALL', 'PARAM_DECL')
        )
        if is_temp_assign and instr.result not in used:
            continue
        optimized.append(instr)
    return optimized


class Optimizer:
    def __init__(self, instructions):
        self.original     = instructions if instructions else []
        self.optimized    = None
        self.stats        = {}

    def optimize(self):
        before = len(self.original)

        step1 = constant_folding(self.original)
        step2 = constant_propagation(step1)
        step3 = dead_code_elimination(step2)

        self.optimized = step3
        after = len(self.optimized)

        self.stats = {
            'before': before,
            'after':  after,
            'removed': before - after,
        }
        return self.optimized

    def print_comparison(self):
        if self.optimized is None:
            print("No optimization results available. Run optimize() first.")
            return
        print("\n" + "="*55)
        print("PHASE 5: OPTIMIZED IR (after 3 passes)")
        print("="*55)
        for i, instr in enumerate(self.optimized):
            prefix = '    ' if instr.op not in ('FUNC', 'END_FUNC', 'LABEL') else ''
            print(f"{i:>3}  {prefix}{instr}")
        print("="*55)
        print(f"Instructions before: {self.stats['before']}")
        print(f"Instructions after : {self.stats['after']}")
        print(f"Instructions removed: {self.stats['removed']}")
        print("="*55)


if __name__ == '__main__':
    from lexer import Lexer
    from parser import Parser
    from ir_generator import IRGenerator

    code = """
int main() {
    int x = 3 + 4;
    int y = x * 2;
    int dead = 99;
    if (x > 5) {
        printf("yes");
    }
    return 0;
}
"""
    lexer  = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast    = parser.parse()

    irgen = IRGenerator()
    ir    = irgen.generate(ast)

    optimizer = Optimizer(ir)
    optimizer.optimize()
    optimizer.print_comparison()
