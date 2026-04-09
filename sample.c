/* =====================================================
   Sample C program for Code Genesis transpiler
   Demonstrates: variables, loops, functions, if-else
   ===================================================== */

int max(int a, int b) {
    if (a > b) {
        return a;
    } else {
        return b;
    }
}

int factorial(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

int main() {
    int x = 10;
    int y = 25;
    int bigger = max(x, y);
    printf("Bigger value:");
    printf(bigger);

    int i = 1;
    while (i <= 5) {
        int f = factorial(i);
        printf(f);
        i = i + 1;
    }

    int sum = 0;
    for (int j = 1; j <= 10; j++) {
        sum = sum + j;
    }
    printf("Sum 1 to 10:");
    printf(sum);

    return 0;
}
