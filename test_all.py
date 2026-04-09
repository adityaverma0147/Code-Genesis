# =============================================================
# TEST SUITE
# Course: Compiler Design (TCS-601)
# Project: Code Genesis - C to Python Transpiler
# Team: Striver (CD-VI-T080)
# =============================================================
# Run all tests:   python tests/test_all.py
# =============================================================

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from main import transpile

PASS = 0
FAIL = 0

def run_test(name, c_code, expected_fragments):
    global PASS, FAIL
    print(f"\n{'─'*50}")
    print(f"TEST: {name}")
    print(f"{'─'*50}")
    try:
        py_code = transpile(c_code, verbose=False, output_path=os.devnull)
        errors  = []
        for frag in expected_fragments:
            if frag not in py_code:
                errors.append(f"  Missing: '{frag}'")
        if errors:
            print("  FAIL")
            for e in errors: print(e)
            FAIL += 1
        else:
            print(f"  PASS — all {len(expected_fragments)} fragments found.")
            PASS += 1
    except Exception as e:
        print(f"  FAIL (exception): {e}")
        FAIL += 1


# ──────────────────────────────────────────────────────────────
# TEST CASES
# ──────────────────────────────────────────────────────────────

run_test(
    "Basic variable declaration and arithmetic",
    """
int main() {
    int x = 10;
    int y = 5;
    int z = x + y;
    return 0;
}
""",
    ['x = 10', 'y = 5', 'z = (x + y)', 'def main()', 'return 0']
)

run_test(
    "If-else statement",
    """
int main() {
    int a = 15;
    if (a > 10) {
        printf("big");
    } else {
        printf("small");
    }
    return 0;
}
""",
    ['if (a > 10):', 'print("big")', 'else:', 'print("small")']
)

run_test(
    "While loop",
    """
int main() {
    int i = 0;
    while (i < 5) {
        i = i + 1;
    }
    return 0;
}
""",
    ['while (i < 5):', 'i = (i + 1)']
)

run_test(
    "For loop (converted to while)",
    """
int main() {
    int sum = 0;
    for (int i = 0; i < 3; i++) {
        sum = sum + i;
    }
    return 0;
}
""",
    ['i = 0', 'while (i < 3):', 'sum = (sum + i)']
)

run_test(
    "Function with parameters",
    """
int add(int a, int b) {
    return a + b;
}

int main() {
    int result = add(3, 4);
    printf(result);
    return 0;
}
""",
    ['def add(a, b):', 'return (a + b)', 'result = add(3, 4)', 'print(result)']
)

run_test(
    "Recursive factorial",
    """
int factorial(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

int main() {
    int r = factorial(5);
    printf(r);
    return 0;
}
""",
    ['def factorial(n):', 'if (n <= 1):', 'return 1', 'return (n * factorial((n - 1)))']
)

run_test(
    "Nested if-else",
    """
int main() {
    int x = 10;
    if (x > 20) {
        printf("large");
    } else {
        if (x > 5) {
            printf("medium");
        } else {
            printf("small");
        }
    }
    return 0;
}
""",
    ['if (x > 20):', 'print("large")', 'if (x > 5):', 'print("medium")', 'print("small")']
)

# ──────────────────────────────────────────────────────────────
# SUMMARY
# ──────────────────────────────────────────────────────────────
print(f"\n{'='*50}")
print(f"TEST SUMMARY:  {PASS} passed,  {FAIL} failed")
print(f"{'='*50}")
if FAIL == 0:
    print("🎉 All tests passed!\n")
else:
    print("⚠️  Some tests failed.\n")
    sys.exit(1)
