from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional

class TokenType(Enum):
    # Ключевые слова
    KW_FN = "FN"
    KW_IF = "IF"
    KW_ELSE = "ELSE"
    KW_WHILE = "WHILE"
    KW_FOR = "FOR"
    KW_INT = "INT"
    KW_FLOAT = "FLOAT"
    KW_BOOL = "BOOL"
    KW_RETURN = "RETURN"
    KW_VOID = "VOID"
    KW_STRUCT = "STRUCT"
    KW_PRINT = "PRINT"

    # Литералы
    IDENTIFIER = "IDENTIFIER"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"
    STRING = "STRING"

    # Операторы
    PLUS = "PLUS"        # +
    MINUS = "MINUS"       # -
    STAR = "STAR"        # *
    SLASH = "SLASH"       # /
    PERCENT = "PERCENT"    # %
    ASSIGN = "ASSIGN"      # =
    EQ = "EQ"          # ==
    NE = "NE"          # !=
    LT = "LT"          # <
    LE = "LE"          # <=
    GT = "GT"          # >
    GE = "GE"          # >=
    AND = "AND"        # &&
    OR = "OR"          # ||
    NOT = "NOT"        # !

    # Разделители
    LPAREN = "LPAREN"      # (
    RPAREN = "RPAREN"      # )
    LBRACE = "LBRACE"      # {
    RBRACE = "RBRACE"      # }
    LBRACKET = "LBRACKET"   # [
    RBRACKET = "RBRACKET"   # ]
    SEMICOLON = "SEMICOLON"  # ;
    COMMA = "COMMA"       # ,

    # Специальные
    EOF = "EOF"

@dataclass
class Token:
    type: TokenType
    lexeme: str
    line: int
    column: int
    value: Optional[Any] = None

    def __repr__(self):
        if self.value is not None:
            return f"Token({self.type.name}, '{self.lexeme}', value={self.value})"
        return f"Token({self.type.name}, '{self.lexeme}')"