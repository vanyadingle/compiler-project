import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.lexer.lexer import Lexer

def token_to_string(tok):
    line_col = f"{tok.line}:{tok.column}"
    type_name = tok.type.name
    lexeme = tok.lexeme.replace('"', '\\"')
    if tok.value is not None:
        return f'{line_col} {type_name} "{lexeme}" {tok.value}'
    return f'{line_col} {type_name} "{lexeme}"'

def test_file(src_path, expected_path):
    with open(src_path, encoding='utf-8') as f:
        source = f.read()
    lexer = Lexer(source)
    tokens = []
    while not lexer.is_at_end():
        tok = lexer.next_token()
        tokens.append(tok)
    actual_lines = [token_to_string(tok) for tok in tokens]

    with open(expected_path, encoding='utf-8') as f:
        expected_lines = [line.rstrip() for line in f]

    if actual_lines == expected_lines:
        print(f"OK: {src_path}")
        return True
    else:
        print(f"FAIL: {src_path}")
        import difflib
        diff = difflib.unified_diff(expected_lines, actual_lines,
                                    fromfile='expected', tofile='actual')
        print('\n'.join(diff))
        return False

def main():
    root = Path(__file__).parent / 'lexer'
    success = True

    for src in (root / 'valid').glob('*.src'):
        expected = src.with_suffix('.expected')
        if not expected.exists():
            print(f"Missing expected file for {src}")
            success = False
            continue
        if not test_file(src, expected):
            success = False

    for src in (root / 'invalid').glob('*.src'):
        try:
            with open(src, encoding='utf-8') as f:
                source = f.read()
            lexer = Lexer(source)
            tokens = []
            while not lexer.is_at_end():
                tok = lexer.next_token()
                tokens.append(tok)
            print(f"OK (no crash): {src}")
        except Exception as e:
            print(f"FAIL (crashed): {src} - {e}")
            success = False

    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())