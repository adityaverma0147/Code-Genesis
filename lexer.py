import re


TOKEN_TYPES = [
    # Keywords
    ('KEYWORD',     r'\b(int|float|char|void|if|else|while|for|return|printf|scanf)\b'),
    # Identifiers (variable/function names)
    ('IDENTIFIER',  r'[a-zA-Z_][a-zA-Z0-9_]*'),
    # Float literals (must come before INT)
    ('FLOAT',       r'\d+\.\d+'),
    # Integer literals
    ('INTEGER',     r'\d+'),
    # String literals
    ('STRING',      r'"[^"]*"'),
    # Char literals
    ('CHAR_LIT',    r"'[^']'"),
    # Comparison operators (must come before single-char ops)
    ('OP',          r'==|!=|<=|>=|&&|\|\||\+\+|--|->'),
    # Whitespace and comments (skipped)
    ('COMMENT',     r'//[^\n]*|/\*.*?\*/'),
    # Assignment and arithmetic operators
    ('ASSIGN',      r'='),
    ('PLUS',        r'\+'),
    ('MINUS',       r'-'),
    ('MULTIPLY',    r'\*'),
    ('DIVIDE',      r'/'),
    ('MODULO',      r'%'),
    ('LT',          r'<'),
    ('GT',          r'>'),
    ('NOT',         r'!'),
    ('ADDR',        r'&'),
    # Delimiters
    ('LPAREN',      r'\('),
    ('RPAREN',      r'\)'),
    ('LBRACE',      r'\{'),
    ('RBRACE',      r'\}'),
    ('LBRACKET',    r'\['),
    ('RBRACKET',    r'\]'),
    ('SEMICOLON',   r';'),
    ('COMMA',       r','),
    ('NEWLINE',     r'\n'),
    ('WHITESPACE',  r'[ \t]+'),
]

class Token:
    def __init__(self, type_, value, line):
        self.type  = type_
        self.value = value
        self.line  = line

    def __repr__(self):
        return f'Token({self.type}, {repr(self.value)}, line={self.line})'



class Lexer:
    def __init__(self, source_code):
        self.source = source_code
        self.tokens = []
        self.errors = []

    def tokenize(self):
        
        pos  = 0
        line = 1
        master_pattern = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_TYPES)
        regex = re.compile(master_pattern, re.DOTALL)

        for match in regex.finditer(self.source):
            kind  = match.lastgroup
            value = match.group()

            
            if kind == 'NEWLINE':
                line += 1
                continue
            
            if kind in ('WHITESPACE', 'COMMENT'):
                line += value.count('\n')
                continue

            self.tokens.append(Token(kind, value, line))

        return self.tokens

    def print_tokens(self):
        print(f"\n{'='*55}")
        print(f"{'PHASE 1: LEXICAL ANALYSIS — TOKEN TABLE':^55}")
        print(f"{'='*55}")
        print(f"{'LINE':<6} {'TYPE':<14} {'VALUE'}")
        print(f"{'-'*55}")
        for tok in self.tokens:
            print(f"{tok.line:<6} {tok.type:<14} {tok.value}")
        print(f"{'='*55}")
        print(f"Total tokens: {len(self.tokens)}\n")


if __name__ == '__main__':
    sample_code = """
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
    lexer = Lexer(sample_code)
    tokens = lexer.tokenize()
    lexer.print_tokens()
