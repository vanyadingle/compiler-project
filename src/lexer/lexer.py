import sys
from .tokens import Token, TokenType

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.start = 0
        self.start_col = 1
        self.current_token = None

        self.keywords = {
            'fn': TokenType.KW_FN,
            'if': TokenType.KW_IF,
            'else': TokenType.KW_ELSE,
            'while': TokenType.KW_WHILE,
            'for': TokenType.KW_FOR,
            'int': TokenType.KW_INT,
            'float': TokenType.KW_FLOAT,
            'bool': TokenType.KW_BOOL,
            'return': TokenType.KW_RETURN,
            'void': TokenType.KW_VOID,
            'struct': TokenType.KW_STRUCT,
            'print': TokenType.KW_PRINT,
        }

    def is_at_end(self):
        return self.pos >= len(self.source) and self.current_token is None

    def advance(self):
        char = self.source[self.pos]
        self.pos += 1
        self.column += 1
        return char

    def peek(self):
        if self.pos >= len(self.source):
            return '\0'
        return self.source[self.pos]

    def peek_next(self):
        if self.pos + 1 >= len(self.source):
            return '\0'
        return self.source[self.pos + 1]

    def skip_whitespace(self):
        while not self.is_at_end():
            c = self.peek()
            if c in ' \t\r':
                self.advance()
            elif c == '\n':
                self.line += 1
                self.column = 1
                self.advance()
            else:
                break

    def error(self, message):
        print(f"Ошибка на {self.line}:{self.column}: {message}", file=sys.stderr)

    def make_token(self, type: TokenType, lexeme=None, value=None):
        if lexeme is None:
            lexeme = self.source[self.start:self.pos]
        return Token(type, lexeme, self.line, self.start_col, value)

    def read_number(self):
        while self.peek().isdigit():
            self.advance()
        if self.peek() == '.' and self.peek_next().isdigit():
            self.advance()
            while self.peek().isdigit():
                self.advance()
            num_str = self.source[self.start:self.pos]
            return self.make_token(TokenType.FLOAT, value=float(num_str))
        else:
            num_str = self.source[self.start:self.pos]
            return self.make_token(TokenType.INTEGER, value=int(num_str))

    def read_identifier(self):
        while self.peek().isalnum() or self.peek() == '_':
            self.advance()
        text = self.source[self.start:self.pos]
        if text in ('true', 'false'):
            return self.make_token(TokenType.BOOLEAN, value=(text == 'true'))
        token_type = self.keywords.get(text, TokenType.IDENTIFIER)
        return self.make_token(token_type)

    def read_string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
                self.column = 1
            self.advance()
        if self.is_at_end():
            # self.error("Незакрытая строка")
            lexeme = self.source[self.start:self.pos]
            return self.make_token(TokenType.STRING, lexeme, value=lexeme[1:])
        self.advance()
        lexeme = self.source[self.start:self.pos]
        return self.make_token(TokenType.STRING, value=lexeme[1:-1])

    def handle_comment(self):
        if self.peek() == '/':
            while not self.is_at_end() and self.peek() != '\n':
                self.advance()
        elif self.peek() == '*':
            self.advance()
            while not self.is_at_end():
                if self.peek() == '*' and self.peek_next() == '/':
                    self.advance()
                    self.advance()
                    break
                if self.peek() == '\n':
                    self.line += 1
                    self.column = 1
                self.advance()
            else:
                self.error("Незакрытый многострочный комментарий")

    def _scan_token(self):
        self.skip_whitespace()
        if self.is_at_end():
            return Token(TokenType.EOF, "", self.line, self.column, None)

        self.start = self.pos
        self.start_col = self.column
        c = self.advance()

        # Односимвольные токены
        if c == '(':
            return self.make_token(TokenType.LPAREN)
        if c == ')':
            return self.make_token(TokenType.RPAREN)
        if c == '{':
            return self.make_token(TokenType.LBRACE)
        if c == '}':
            return self.make_token(TokenType.RBRACE)
        if c == '[':
            return self.make_token(TokenType.LBRACKET)
        if c == ']':
            return self.make_token(TokenType.RBRACKET)
        if c == ';':
            return self.make_token(TokenType.SEMICOLON)
        if c == ',':
            return self.make_token(TokenType.COMMA)
        if c == '+':
            return self.make_token(TokenType.PLUS)
        if c == '-':
            return self.make_token(TokenType.MINUS)
        if c == '*':
            return self.make_token(TokenType.STAR)
        if c == '%':
            return self.make_token(TokenType.PERCENT)

        # Операторы с возможными двухсимвольными вариантами
        if c == '/':
            if self.peek() in '/*':
                self.handle_comment()
                return self._scan_token()
            return self.make_token(TokenType.SLASH)

        if c == '=':
            if self.peek() == '=':
                self.advance()
                return self.make_token(TokenType.EQ)
            return self.make_token(TokenType.ASSIGN)

        if c == '!':
            if self.peek() == '=':
                self.advance()
                return self.make_token(TokenType.NE)
            return self.make_token(TokenType.NOT)

        if c == '<':
            if self.peek() == '=':
                self.advance()
                return self.make_token(TokenType.LE)
            return self.make_token(TokenType.LT)

        if c == '>':
            if self.peek() == '=':
                self.advance()
                return self.make_token(TokenType.GE)
            return self.make_token(TokenType.GT)

        if c == '&':
            if self.peek() == '&':
                self.advance()
                return self.make_token(TokenType.AND)
            self.error(f"Неожиданный символ '{c}'")
            return self._scan_token()

        if c == '|':
            if self.peek() == '|':
                self.advance()
                return self.make_token(TokenType.OR)
            self.error(f"Неожиданный символ '{c}'")
            return self._scan_token()

        # Строки, числа, идентификаторы
        if c == '"':
            return self.read_string()

        if c.isdigit():
            return self.read_number()

        if c.isalpha() or c == '_':
            return self.read_identifier()

        # Неизвестный символ
        self.error(f"Неожиданный символ '{c}'")
        return self._scan_token()

    def next_token(self):
        if self.current_token is not None:
            token = self.current_token
            self.current_token = None
            return token
        return self._scan_token()

    def peek_token(self):
        if self.current_token is None:
            self.current_token = self._scan_token()
        return self.current_token