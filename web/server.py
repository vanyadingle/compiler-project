"""
Flask backend for the MiniLang compiler visualizer.
Endpoints:
  POST /api/compile   { "source": "<code>" }
  →  { "tokens": [...], "ast": {...}, "errors": [...] }
  GET  /              Serves the interactive HTML page
"""

import json
import sys
import os

# Make sure the project root is on sys.path so `src` is importable.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, send_from_directory
from src.lexer.lexer import Lexer
from src.lexer.tokens import TokenType
from src.parser.parser import Parser

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), "static"))


# ── API ────────────────────────────────────────────────────────────────────────

@app.post("/api/compile")
def compile_source():
    body = request.get_json(silent=True) or {}
    source: str = body.get("source", "")

    # Lexer pass — collect all tokens
    lex = Lexer(source)
    tokens = []
    while True:
        tok = lex.next_token()
        tokens.append({
            "type": tok.type.name,
            "lexeme": tok.lexeme,
            "line": tok.line,
            "column": tok.column,
            "value": tok.value,
        })
        if tok.type == TokenType.EOF:
            break

    # Parser pass — build AST
    parser = Parser(source)
    program = parser.parse()
    ast_dict = program.to_dict()

    return jsonify({
        "tokens": tokens,
        "ast": ast_dict,
        "errors": parser.errors,
    })


# ── Static files ───────────────────────────────────────────────────────────────

@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    print("MiniLang Compiler Visualizer running at http://localhost:5000")
    app.run(debug=True, port=5000)
