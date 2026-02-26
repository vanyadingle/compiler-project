import sys
from pathlib import Path
from .lexer import Lexer

def token_to_string(tok):
    line_col = f"{tok.line}:{tok.column}"
    type_name = tok.type.name
    lexeme = tok.lexeme.replace('"', '\\"')
    if tok.value is not None:
        return f'{line_col} {type_name} "{lexeme}" {tok.value}'
    return f'{line_col} {type_name} "{lexeme}"'

def main():
    if len(sys.argv) != 2:
        print("Использование: minicompiler-lex <file.src>")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Файл {path} не найден")
        sys.exit(1)

    with open(path, encoding='utf-8') as f:
        source = f.read()

    lexer = Lexer(source)
    while not lexer.is_at_end():
        tok = lexer.next_token()
        print(token_to_string(tok))

if __name__ == "__main__":
    main()