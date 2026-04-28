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


def _set_columns(t):
    last_nl = t.lexer.lexdata.rfind("\n", 0, t.lexpos)
    t.col_start = t.lexpos - (last_nl + 1) if last_nl >= 0 else t.lexpos
    t.col_end = t.col_start + (t.lexer.lexpos - t.lexpos)


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
    _set_columns(t)
    return t


def t_LE(t):
    r"<="
    _set_columns(t)
    return t


def t_EQ(t):
    r"=="
    _set_columns(t)
    return t


def t_AND(t):
    r"&&"
    _set_columns(t)
    return t


def t_OR(t):
    r"\|\|"
    _set_columns(t)
    return t


def t_FLOAT_VALUE(t):
    r"((0|[1-9][0-9]*)\.[0-9]+(e[+-]?[0-9]+)?|(0|[1-9][0-9]*)e[+-]?[0-9]+)"
    _set_columns(t)
    t.value = float(t.value)
    return t


def t_INT_VALUE(t):
    r"(0x[0-9A-F]+|0b[01]+|0[0-7]+|0|[1-9][0-9]*)"
    _set_columns(t)
    raw = t.value
    if raw.startswith("0x") or raw.startswith("0X"):
        t.value = int(raw, 16)
    elif raw.startswith("0b") or raw.startswith("0B"):
        t.value = int(raw, 2)
    elif raw == "0":
        t.value = 0
    elif raw.startswith("0"):
        t.value = int(raw, 8)
    else:
        t.value = int(raw)
    return t


def t_CHAR_VALUE(t):
    r"'([\x20-\x26\x28-\x5B\x5D-\xFF]|\\[\x20-\xFF])'"
    _set_columns(t)
    inner = t.value[1:-1]
    if inner.startswith("\\"):
        escape_map = {
            "n": "\n",
            "t": "\t",
            "r": "\r",
            "0": "\0",
            "\\": "\\",
            "'": "'",
            '"': '"',
        }
        t.value = escape_map.get(inner[1], inner[1])
    else:
        t.value = inner
    return t


def t_ID(t):
    r"[A-Za-z_][A-Za-z_0-9]*"
    t.type = reserved.get(t.value, "ID")
    _set_columns(t)
    if t.type == "TRUE":
        t.value = True
    elif t.type == "FALSE":
        t.value = False
    return t


def t_ASSIGN(t):
    r"="
    _set_columns(t)
    return t


def t_GT(t):
    r">"
    _set_columns(t)
    return t


def t_LT(t):
    r"<"
    _set_columns(t)
    return t


def t_PLUS(t):
    r"\+"
    _set_columns(t)
    return t


def t_MINUS(t):
    r"-"
    _set_columns(t)
    return t


def t_TIMES(t):
    r"\*"
    _set_columns(t)
    return t


def t_DIVIDE(t):
    r"/"
    _set_columns(t)
    return t


def t_NOT(t):
    r"!"
    _set_columns(t)
    return t


def t_DOT(t):
    r"\."
    _set_columns(t)
    return t


def t_COMMA(t):
    r","
    _set_columns(t)
    return t


def t_SEMICOLON(t):
    r";"
    _set_columns(t)
    return t


def t_LPAREN(t):
    r"\("
    _set_columns(t)
    return t


def t_RPAREN(t):
    r"\)"
    _set_columns(t)
    return t


def t_LBRACE(t):
    r"\{"
    _set_columns(t)
    return t


def t_RBRACE(t):
    r"\}"
    _set_columns(t)
    return t


def t_error(t):
    t.lexer.skip(1)


def build_lexer(**kwargs):
    return lex.lex(module=sys.modules[__name__], **kwargs)
