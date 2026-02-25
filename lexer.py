import ply.lex as lex
import sys

# Palabras reservadas [cite: 99, 211]
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
    "break": "BREAK",  # Identificada en la sección de control de flujo 
    "print": "PRINT",
    "new": "NEW",
    "record": "RECORD",
}

# Lista completa de tokens [cite: 131, 135, 139, 292]
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

# Caracteres ignorados [cite: 326]
t_ignore = " \t\r"

# --- Comentarios [cite: 91, 93, 95] ---
def t_LINE_COMMENT(t):
    r"//[^\n]*"
    pass

def t_BLOCK_COMMENT(t):
    r"/\*(.|\n)*?\*/"
    t.lexer.lineno += t.value.count("\n")
    pass

# --- Saltos de línea ---
def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)

# --- Operadores multi-carácter (deben ir antes que los simples) [cite: 135, 139] ---
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

# --- Literales [cite: 103-125] ---
# Float con punto o notación científica [cite: 115, 116]
def t_FLOAT_VALUE(t):
    r"([0-9]+\.[0-9]+(e[+-]?[0-9]+)?|[0-9]+e[+-]?[0-9]+)"
    return t

# Enteros: Hex (0x), Bin (0b), Oct (0) o Dec (sin ceros a la izq) [cite: 105-108]
def t_INT_VALUE(t):
    r"(0x[0-9A-F]+|0b[01]+|0[0-7]+|0|[1-9][0-9]*)"
    return t

# Carácter en ASCII-extendido [cite: 121]
def t_CHAR_VALUE(t):
    r"'([^\\\n']|\\.)'"
    return t

# Identificadores y palabras reservadas [cite: 97, 98]
def t_ID(t):
    r"[A-Za-z_][A-Za-z_0-9]*"
    t.type = reserved.get(t.value, "ID")
    return t

# --- Operadores y puntuación de 1 carácter [cite: 131, 139, 165] ---
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

# --- Gestión de Errores [cite: 276, 326] ---
def t_error(t):
    # Opcional: imprimir por consola para depuración
    t.lexer.skip(1)

def build_lexer(**kwargs):
    # module=sys.modules[__name__] es vital para que PLY encuentre las reglas tras importar
    return lex.lex(module=sys.modules[__name__], **kwargs)