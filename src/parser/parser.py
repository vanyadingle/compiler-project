"""
Recursive-descent parser for MiniLang.
Produces an AST (from ast_nodes) and a list of error strings.
"""

import sys
from typing import List, Optional, Tuple

from ..lexer.lexer import Lexer
from ..lexer.tokens import Token, TokenType
from .ast_nodes import (
    Program, FunctionDecl, Param, Block,
    VarDecl, AssignStmt, ReturnStmt, IfStmt, WhileStmt, ForStmt,
    PrintStmt, ExprStmt,
    BinaryExpr, UnaryExpr, CallExpr,
    Identifier, IntLiteral, FloatLiteral, BoolLiteral, StringLiteral,
    ASTNode,
)

TYPE_KEYWORDS = {TokenType.KW_INT, TokenType.KW_FLOAT, TokenType.KW_BOOL, TokenType.KW_VOID}


class ParseError(Exception):
    def __init__(self, message: str, line: int, col: int):
        super().__init__(message)
        self.line = line
        self.col = col


class Parser:
    def __init__(self, source: str):
        self.lexer = Lexer(source)
        self.errors: List[str] = []
        self._current: Optional[Token] = None
        self._advance()  # prime the pump

    # ── Low-level token API ─────────────────────────────────────────────────

    def _advance(self) -> Token:
        tok = self._current
        self._current = self.lexer.next_token()
        return tok

    def _peek(self) -> Token:
        return self._current

    def _check(self, *types: TokenType) -> bool:
        return self._current.type in types

    def _match(self, *types: TokenType) -> bool:
        if self._check(*types):
            self._advance()
            return True
        return False

    def _expect(self, ttype: TokenType, msg: str) -> Token:
        if self._check(ttype):
            return self._advance()
        tok = self._current
        self.errors.append(f"Строка {tok.line}:{tok.column}: {msg} (получено '{tok.lexeme}')")
        return tok  # return anyway to let parser continue

    def _skip_until(self, *types: TokenType):
        """Panic-mode error recovery: consume tokens until one of `types`."""
        while not self._check(TokenType.EOF) and not self._check(*types):
            self._advance()

    # ── Entry point ─────────────────────────────────────────────────────────

    def parse(self) -> Program:
        decls = []
        while not self._check(TokenType.EOF):
            try:
                decls.append(self._parse_top_level())
            except ParseError as e:
                self.errors.append(f"Строка {e.line}:{e.col}: {e}")
                self._skip_until(TokenType.KW_FN, TokenType.EOF)
        return Program(decls)

    # ── Top-level declarations ───────────────────────────────────────────────

    def _parse_top_level(self) -> ASTNode:
        if self._check(TokenType.KW_FN):
            return self._parse_function()
        # bare statement at top level
        return self._parse_statement()

    def _parse_function(self) -> FunctionDecl:
        self._expect(TokenType.KW_FN, "ожидалось 'fn'")
        name_tok = self._expect(TokenType.IDENTIFIER, "ожидалось имя функции")
        self._expect(TokenType.LPAREN, "ожидалось '('")
        params = self._parse_param_list()
        self._expect(TokenType.RPAREN, "ожидалось ')'")

        # Optional return type annotation (not in lexer, so we check type kw)
        ret = None
        if self._check(*TYPE_KEYWORDS):
            ret = self._advance().lexeme

        body = self._parse_block()
        return FunctionDecl(name_tok.lexeme, params, ret, body)

    def _parse_param_list(self) -> List[Param]:
        params = []
        while not self._check(TokenType.RPAREN) and not self._check(TokenType.EOF):
            type_tok = self._expect_type("ожидался тип параметра")
            name_tok = self._expect(TokenType.IDENTIFIER, "ожидалось имя параметра")
            params.append(Param(name_tok.lexeme, type_tok.lexeme))
            if not self._match(TokenType.COMMA):
                break
        return params

    def _expect_type(self, msg: str) -> Token:
        if self._check(*TYPE_KEYWORDS):
            return self._advance()
        tok = self._current
        self.errors.append(f"Строка {tok.line}:{tok.column}: {msg}")
        return tok

    # ── Statements ───────────────────────────────────────────────────────────

    def _parse_block(self) -> Block:
        self._expect(TokenType.LBRACE, "ожидалось '{'")
        stmts = []
        while not self._check(TokenType.RBRACE) and not self._check(TokenType.EOF):
            try:
                stmts.append(self._parse_statement())
            except ParseError as e:
                self.errors.append(f"Строка {e.line}:{e.col}: {e}")
                self._skip_until(TokenType.SEMICOLON, TokenType.RBRACE)
                self._match(TokenType.SEMICOLON)
        self._expect(TokenType.RBRACE, "ожидалось '}'")
        return Block(stmts)

    def _parse_statement(self) -> ASTNode:
        tok = self._peek()

        if self._check(TokenType.KW_RETURN):
            return self._parse_return()

        if self._check(TokenType.KW_IF):
            return self._parse_if()

        if self._check(TokenType.KW_WHILE):
            return self._parse_while()

        if self._check(TokenType.KW_FOR):
            return self._parse_for()

        if self._check(TokenType.KW_PRINT):
            return self._parse_print()

        if self._check(*TYPE_KEYWORDS):
            return self._parse_var_decl()

        if self._check(TokenType.LBRACE):
            return self._parse_block()

        # Assign or expression
        return self._parse_expr_or_assign()

    def _parse_return(self) -> ReturnStmt:
        self._advance()  # consume 'return'
        if self._check(TokenType.SEMICOLON):
            self._advance()
            return ReturnStmt(None)
        expr = self._parse_expression()
        self._expect(TokenType.SEMICOLON, "ожидалась ';' после return")
        return ReturnStmt(expr)

    def _parse_if(self) -> IfStmt:
        self._advance()  # consume 'if'
        self._expect(TokenType.LPAREN, "ожидалось '('")
        cond = self._parse_expression()
        self._expect(TokenType.RPAREN, "ожидалось ')'")
        then_b = self._parse_block()
        else_b = None
        if self._match(TokenType.KW_ELSE):
            else_b = self._parse_block()
        return IfStmt(cond, then_b, else_b)

    def _parse_while(self) -> WhileStmt:
        self._advance()
        self._expect(TokenType.LPAREN, "ожидалось '('")
        cond = self._parse_expression()
        self._expect(TokenType.RPAREN, "ожидалось ')'")
        body = self._parse_block()
        return WhileStmt(cond, body)

    def _parse_for(self) -> ForStmt:
        self._advance()
        self._expect(TokenType.LPAREN, "ожидалось '('")
        init = None
        if not self._check(TokenType.SEMICOLON):
            if self._check(*TYPE_KEYWORDS):
                init = self._parse_var_decl_no_semi()
            else:
                init = self._parse_expression()
        self._expect(TokenType.SEMICOLON, "ожидалась ';'")
        cond = None
        if not self._check(TokenType.SEMICOLON):
            cond = self._parse_expression()
        self._expect(TokenType.SEMICOLON, "ожидалась ';'")
        update = None
        if not self._check(TokenType.RPAREN):
            update = self._parse_expression()
        self._expect(TokenType.RPAREN, "ожидалось ')'")
        body = self._parse_block()
        return ForStmt(init, cond, update, body)

    def _parse_print(self) -> PrintStmt:
        self._advance()
        self._expect(TokenType.LPAREN, "ожидалось '('")
        expr = self._parse_expression()
        self._expect(TokenType.RPAREN, "ожидалось ')'")
        self._expect(TokenType.SEMICOLON, "ожидалась ';'")
        return PrintStmt(expr)

    def _parse_var_decl(self) -> VarDecl:
        node = self._parse_var_decl_no_semi()
        self._expect(TokenType.SEMICOLON, "ожидалась ';'")
        return node

    def _parse_var_decl_no_semi(self) -> VarDecl:
        type_tok = self._advance()
        name_tok = self._expect(TokenType.IDENTIFIER, "ожидалось имя переменной")
        init = None
        if self._match(TokenType.ASSIGN):
            init = self._parse_expression()
        return VarDecl(type_tok.lexeme, name_tok.lexeme, init)

    def _parse_expr_or_assign(self) -> ASTNode:
        # Look ahead: if IDENTIFIER followed by '=' (not '==')
        if self._check(TokenType.IDENTIFIER):
            name_tok = self._advance()
            if self._match(TokenType.ASSIGN):
                expr = self._parse_expression()
                self._expect(TokenType.SEMICOLON, "ожидалась ';'")
                return AssignStmt(name_tok.lexeme, expr)
            else:
                # It was the start of an expression — put name back via fake expr
                ident = Identifier(name_tok.lexeme)
                expr = self._parse_binary_rest(ident, 0)
                self._expect(TokenType.SEMICOLON, "ожидалась ';'")
                return ExprStmt(expr)

        expr = self._parse_expression()
        self._expect(TokenType.SEMICOLON, "ожидалась ';'")
        return ExprStmt(expr)

    # ── Expressions (Pratt-style precedence climbing) ────────────────────────

    PREC = {
        TokenType.OR:    1,
        TokenType.AND:   2,
        TokenType.EQ:    3, TokenType.NE: 3,
        TokenType.LT:    4, TokenType.LE: 4, TokenType.GT: 4, TokenType.GE: 4,
        TokenType.PLUS:  5, TokenType.MINUS: 5,
        TokenType.STAR:  6, TokenType.SLASH: 6, TokenType.PERCENT: 6,
    }

    def _parse_expression(self) -> ASTNode:
        left = self._parse_unary()
        return self._parse_binary_rest(left, 0)

    def _parse_binary_rest(self, left: ASTNode, min_prec: int) -> ASTNode:
        while True:
            prec = self.PREC.get(self._peek().type)
            if prec is None or prec <= min_prec:
                break
            op_tok = self._advance()
            right = self._parse_unary()
            right = self._parse_binary_rest(right, prec)
            left = BinaryExpr(op_tok.lexeme, left, right)
        return left

    def _parse_unary(self) -> ASTNode:
        if self._check(TokenType.NOT, TokenType.MINUS):
            op = self._advance()
            operand = self._parse_unary()
            return UnaryExpr(op.lexeme, operand)
        return self._parse_call()

    def _parse_call(self) -> ASTNode:
        expr = self._parse_primary()
        if isinstance(expr, Identifier) and self._check(TokenType.LPAREN):
            self._advance()  # consume '('
            args = []
            while not self._check(TokenType.RPAREN) and not self._check(TokenType.EOF):
                args.append(self._parse_expression())
                if not self._match(TokenType.COMMA):
                    break
            self._expect(TokenType.RPAREN, "ожидалось ')'")
            return CallExpr(expr.name, args)
        return expr

    def _parse_primary(self) -> ASTNode:
        tok = self._peek()

        if self._check(TokenType.INTEGER):
            self._advance()
            return IntLiteral(tok.value)

        if self._check(TokenType.FLOAT):
            self._advance()
            return FloatLiteral(tok.value)

        if self._check(TokenType.BOOLEAN):
            self._advance()
            return BoolLiteral(tok.value)

        if self._check(TokenType.STRING):
            self._advance()
            return StringLiteral(tok.value)

        if self._check(TokenType.IDENTIFIER):
            self._advance()
            return Identifier(tok.lexeme)

        if self._check(TokenType.LPAREN):
            self._advance()
            expr = self._parse_expression()
            self._expect(TokenType.RPAREN, "ожидалось ')'")
            return expr

        # Error
        self._advance()  # skip bad token
        self.errors.append(f"Строка {tok.line}:{tok.column}: неожиданный токен '{tok.lexeme}'")
        return Identifier("__error__")
