# =============================================================
# PHASE 5: CODE OPTIMIZER
# Course: Compiler Design (TCS-601)
# Project: Code Genesis - C to Python Transpiler
# Team: Striver (CD-VI-T080)
# =============================================================
# Applies three classic optimization passes on the IR (TAC)
# produced by Phase 4:
#
#   1. CONSTANT FOLDING
#      Evaluate constant expressions at compile time.
#      Example: t0 = 3 + 4   →   t0 = 7
#
#   2. CONSTANT PROPAGATION
#      Replace variable uses with their known constant values.
#      Example: x = 7; t1 = x + 2   →   t1 = 7 + 2   →   t1 = 9
#
#   3. DEAD CODE ELIMINATION
#      Remove assignments to temporary/variables whose values
#      are never used by any subsequent instruction.
# =============================================================

from ir_generator import IRInstruction

ARITHMETIC_OPS = {'+', '-', '*', '/', '%'}
COMPARE_OPS    = {'==', '!=', '<', '>', '<=', '>='}


# ---------------------------------------------------------------
# HELPER: is a string a numeric literal?
# ---------------------------------------------------------------
def _is_number(s):
    try:
        float(s)
        return True
    except (TypeError, ValueError):
        return False

def _eval(a, op, b):
    """Evaluate a constant binary expression."""
    a, b = float(a), float(b)
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
    # Return int string when possible
    return str(int(result)) if result == int(result) else str(result)


# ---------------------------------------------------------------
# PASS 1: CONSTANT FOLDING
# ---------------------------------------------------------------
def constant_folding(instructions):
    """
    Replaces   t = <const> op <const>   with   t = <value>.
    Also handles unary minus on constants.
    """
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


# ---------------------------------------------------------------
# PASS 2: CONSTANT PROPAGATION
# ---------------------------------------------------------------
def constant_propagation(instructions):
    """
    Tracks which variables hold constant values and substitutes
    those values into later uses.
    """
    const_map = {}   # name → constant string value
    optimized = []

    def resolve(val):
        return const_map.get(val, val)

    for instr in instructions:
        # If this is a simple assignment of a constant, remember it
        if instr.op == '=' and _is_number(instr.arg1):
            const_map[instr.result] = instr.arg1
        # If a variable is reassigned to a non-constant, forget it
        elif instr.op == '=' and instr.result in const_map:
            if not _is_number(instr.arg1):
                del const_map[instr.result]

        # Substitute known constants into args
        new_instr = IRInstruction(
            op     = instr.op,
            arg1   = resolve(instr.arg1) if instr.arg1 is not None else None,
            arg2   = resolve(instr.arg2) if instr.arg2 is not None else None,
            result = instr.result
        )
        optimized.append(new_instr)

    # Run constant folding again after propagation (may expose new folds)
    return constant_folding(optimized)


# ---------------------------------------------------------------
# PASS 3: DEAD CODE ELIMINATION
# ---------------------------------------------------------------
def dead_code_elimination(instructions):
    """
    Remove assignments whose result is never read.
    Only removes temporaries (t0, t1, ...) to stay safe.
    """
    # Collect all values that are READ (appear as arg1 / arg2)
    used = set()
    for instr in instructions:
        if instr.arg1 is not None and not _is_number(instr.arg1):
            used.add(str(instr.arg1).strip('"'))
        if instr.arg2 is not None and not _is_number(instr.arg2):
            used.add(str(instr.arg2).strip('"'))
        # result of CALL/IF_FALSE/PRINT/RETURN is also "used"
        if instr.op in ('IF_FALSE', 'IF', 'RETURN', 'PRINT', 'PARAM'):
            if instr.arg1:
                used.add(str(instr.arg1).strip('"'))

    optimized = []
    for instr in instructions:
        # Only eliminate writes to temporaries that are never read
        is_temp_assign = (
            instr.result is not None
            and str(instr.result).startswith('t')
            and instr.op not in ('FUNC', 'END_FUNC', 'LABEL',
                                 'GOTO', 'IF_FALSE', 'RETURN',
                                 'PRINT', 'PARAM', 'CALL', 'PARAM_DECL')
        )
        if is_temp_assign and instr.result not in used:
            continue  # dead — skip
        optimized.append(instr)
    return optimized


# ---------------------------------------------------------------
# OPTIMIZER — runs all passes
# ---------------------------------------------------------------
class Optimizer:
    def __init__(self, instructions):
        self.original     = instructions
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
