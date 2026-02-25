import ply.lex as lex
import sys

reserved = {
    "true": "TRUE",
    "false": "FALSE",
    "int": "INT",
    "float": "FLOAT",
    "char": "CHAR",
    "boolean": "BOOLEAN",
    "void": "VOID",
    "return": "RETURN",
    "if": "IF",
    "else": "ELSE",
    "do": "DO",
    "while": "WHILE",
    "break": "BREAK",
    "print": "PRINT",
    "new": "NEW",
    "record": "RECORD",
}

tokens = [
    "ID",
    "INT_VALUE",
    "FLOAT_VALUE",
    "CHAR_VALUE",
    "ASSIGN",
    "EQ",
    "GT",
    "GE",
    "LT",
    "LE",
    "PLUS",
    "MINUS",
    "TIMES",
    "DIVIDE",
    "AND",
    "OR",
    "NOT",
    "DOT",
    "COMMA",
    "SEMICOLON",
    "LPAREN",
    "RPAREN",
    "LBRACE",
    "RBRACE",
] + list(reserved.values())

t_ignore = " \t\r"

def t_LINE_COMMENT(t):
    r"//[^\n]*"
    pass

def t_BLOCK_COMMENT(t):
    r"/\*(.|\n)*?\*/"
    t.lexer.lineno += t.value.count("\n")
    pass

def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)

def t_GE(t):
    r">="
    return t

def t_LE(t):
    r"<="
    return t

def t_EQ(t):
    r"=="
    return t

def t_AND(t):
    r"&&"
    return t

def t_OR(t):
    r"\|\|"
    return t

def t_FLOAT_VALUE(t):
    r"([0-9]+\.[0-9]+(e[+-]?[0-9]+)?|[0-9]+e[+-]?[0-9]+)"
    return t

def t_INT_VALUE(t):
    r"(0x[0-9A-F]+|0b[01]+|0[0-7]+|0|[1-9][0-9]*)"
    return t

def t_CHAR_VALUE(t):
    r"'([^\\\n']|\\.)'"
    return t

def t_ID(t):
    r"[A-Za-z_][A-Za-z_0-9]*"
    t.type = reserved.get(t.value, "ID")
    return t

t_ASSIGN    = r"="
t_GT        = r">"
t_LT        = r"<"
t_PLUS      = r"\+"
t_MINUS     = r"-"
t_TIMES     = r"\*"
t_DIVIDE    = r"/"
t_NOT       = r"!"
t_DOT       = r"\."
t_COMMA     = r","
t_SEMICOLON = r";"
t_LPAREN    = r"\("
t_RPAREN    = r"\)"
t_LBRACE    = r"\{"
t_RBRACE    = r"\}"

def t_error(t):
    t.lexer.skip(1)

def build_lexer(**kwargs):
    return lex.lex(module=sys.modules[__name__], **kwargs)
