import sys

import ply.yacc as yacc

from lexer import build_lexer, tokens


precedence = (
    ("left", "OR"),
    ("left", "AND"),
    ("nonassoc", "EQ", "GT", "GE", "LT", "LE"),
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE"),
    ("right", "NOT", "UPLUS", "UMINUS"),
)

_parser = None
_parse_errors = []


# ---------------------------------------------------------------------------
# Program
# ---------------------------------------------------------------------------

def p_program(p):
    "program : program_items_opt"


def p_program_items_opt_empty(p):
    "program_items_opt : empty"


def p_program_items_opt_many(p):
    "program_items_opt : program_items_opt program_item"


# A standalone semicolon is a valid (empty) program item.
def p_program_item_empty(p):
    "program_item : SEMICOLON"


def p_program_item_record(p):
    "program_item : record_decl SEMICOLON"


def p_program_item_void_function(p):
    "program_item : VOID ID LPAREN param_list_opt RPAREN block"


# type_spec ID can be either a function or a variable declaration/init.
def p_program_item_typed(p):
    "program_item : type_spec ID typed_program_item_tail"


def p_typed_program_item_tail_function(p):
    "typed_program_item_tail : LPAREN param_list_opt RPAREN block"


def p_typed_program_item_tail_init(p):
    "typed_program_item_tail : ASSIGN expression SEMICOLON"


# Multi-declaration (id_list_tail may be empty → single declaration).
def p_typed_program_item_tail_decl(p):
    "typed_program_item_tail : id_list_tail SEMICOLON"


def p_program_item_control(p):
    "program_item : control_statement"


def p_program_item_simple(p):
    "program_item : plain_simple_statement SEMICOLON"


# ---------------------------------------------------------------------------
# Record declaration
# ---------------------------------------------------------------------------

def p_record_decl(p):
    "record_decl : RECORD ID LPAREN field_list_opt RPAREN"


def p_field_list_opt_empty(p):
    "field_list_opt : empty"


def p_field_list_opt_list(p):
    "field_list_opt : field_list"


def p_field_list_one(p):
    "field_list : field_decl"


def p_field_list_many(p):
    "field_list : field_list COMMA field_decl"


def p_field_decl(p):
    "field_decl : type_spec ID"


# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

def p_param_list_opt_empty(p):
    "param_list_opt : empty"


def p_param_list_opt_list(p):
    "param_list_opt : param_list"


def p_param_list_one(p):
    "param_list : param_decl"


def p_param_list_many(p):
    "param_list : param_list COMMA param_decl"


def p_param_decl(p):
    "param_decl : type_spec ID"


# ---------------------------------------------------------------------------
# Block
# ---------------------------------------------------------------------------

def p_block(p):
    "block : LBRACE block_items_opt RBRACE"


def p_block_items_opt_empty(p):
    "block_items_opt : empty"


def p_block_items_opt_many(p):
    "block_items_opt : block_items_opt block_item"


def p_block_item_empty(p):
    "block_item : SEMICOLON"


# Exactly one mandatory semicolon per statement; additional semicolons are
# handled as standalone block_item : SEMICOLON entries.
def p_block_item_simple(p):
    "block_item : simple_statement SEMICOLON"


def p_block_item_control(p):
    "block_item : control_statement"


# ---------------------------------------------------------------------------
# Statements inside blocks
# ---------------------------------------------------------------------------

def p_simple_statement_typed(p):
    "simple_statement : type_spec ID typed_simple_statement_tail"


def p_typed_simple_statement_tail_init(p):
    "typed_simple_statement_tail : ASSIGN expression"


# Multi-declaration (or empty → single bare declaration).
def p_typed_simple_statement_tail_decl(p):
    "typed_simple_statement_tail : id_list_tail"


def p_simple_statement_plain(p):
    "simple_statement : plain_simple_statement"


def p_plain_simple_statement_assignment(p):
    "plain_simple_statement : assignment"


def p_plain_simple_statement_break(p):
    "plain_simple_statement : BREAK"


def p_plain_simple_statement_return_empty(p):
    "plain_simple_statement : RETURN"


def p_plain_simple_statement_return_expr(p):
    "plain_simple_statement : RETURN expression"


def p_plain_simple_statement_print(p):
    "plain_simple_statement : PRINT LPAREN expression RPAREN"


def p_plain_simple_statement_expr(p):
    "plain_simple_statement : expression"


# ---------------------------------------------------------------------------
# Control flow
# ---------------------------------------------------------------------------

def p_control_statement_if(p):
    "control_statement : IF LPAREN expression RPAREN block"


def p_control_statement_if_else(p):
    "control_statement : IF LPAREN expression RPAREN block ELSE block"


def p_control_statement_while(p):
    "control_statement : WHILE LPAREN expression RPAREN block"


def p_control_statement_do_while(p):
    "control_statement : DO block WHILE LPAREN expression RPAREN"


# ---------------------------------------------------------------------------
# Multi-declaration tail: zero or more comma-separated identifiers.
# ---------------------------------------------------------------------------

def p_id_list_tail_empty(p):
    "id_list_tail : empty"


def p_id_list_tail_list(p):
    "id_list_tail : comma_id_list"


def p_comma_id_list_one(p):
    "comma_id_list : COMMA ID"


def p_comma_id_list_many(p):
    "comma_id_list : comma_id_list COMMA ID"


# ---------------------------------------------------------------------------
# Assignment
# ---------------------------------------------------------------------------

# Using postfix_expr on the left-hand side avoids the lvalue/primary_expr
# reduce/reduce conflict. Semantic validation (lvalue must be an actual
# writable location) is deferred to P3.
def p_assignment(p):
    "assignment : postfix_expr ASSIGN expression"


# ---------------------------------------------------------------------------
# Type specifier
# ---------------------------------------------------------------------------

def p_type_spec_primitive(p):
    """type_spec : INT
                 | FLOAT
                 | CHAR
                 | BOOLEAN"""


def p_type_spec_record(p):
    "type_spec : ID"


# ---------------------------------------------------------------------------
# Expressions
# ---------------------------------------------------------------------------

def p_expression_postfix(p):
    "expression : postfix_expr"


def p_expression_unary_plus(p):
    "expression : PLUS expression %prec UPLUS"


def p_expression_unary_minus(p):
    "expression : MINUS expression %prec UMINUS"


def p_expression_not(p):
    "expression : NOT expression"


def p_expression_binary(p):
    """expression : expression TIMES expression
                  | expression DIVIDE expression
                  | expression PLUS expression
                  | expression MINUS expression
                  | expression GT expression
                  | expression GE expression
                  | expression LT expression
                  | expression LE expression
                  | expression EQ expression
                  | expression AND expression
                  | expression OR expression"""


# ---------------------------------------------------------------------------
# Postfix expressions (calls and field access)
# ---------------------------------------------------------------------------

def p_postfix_expr_primary(p):
    "postfix_expr : primary_expr"


def p_postfix_expr_call(p):
    "postfix_expr : postfix_expr LPAREN arg_list_opt RPAREN"


def p_postfix_expr_dot(p):
    "postfix_expr : postfix_expr DOT ID"


# ---------------------------------------------------------------------------
# Primary expressions
# ---------------------------------------------------------------------------

def p_primary_expr_literal(p):
    "primary_expr : literal"


def p_primary_expr_id(p):
    "primary_expr : ID"


# Parenthesised sub-expressions (highest precedence).
def p_primary_expr_grouped(p):
    "primary_expr : LPAREN expression RPAREN"


def p_primary_expr_new(p):
    "primary_expr : NEW ID LPAREN arg_list_opt RPAREN"


# ---------------------------------------------------------------------------
# Literals
# ---------------------------------------------------------------------------

def p_literal(p):
    """literal : INT_VALUE
               | FLOAT_VALUE
               | CHAR_VALUE
               | TRUE
               | FALSE"""


# ---------------------------------------------------------------------------
# Argument list
# ---------------------------------------------------------------------------

def p_arg_list_opt_empty(p):
    "arg_list_opt : empty"


def p_arg_list_opt_list(p):
    "arg_list_opt : arg_list"


def p_arg_list_one(p):
    "arg_list : expression"


def p_arg_list_many(p):
    "arg_list : arg_list COMMA expression"


# ---------------------------------------------------------------------------
# Epsilon
# ---------------------------------------------------------------------------

def p_empty(p):
    "empty :"


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

def p_error(p):
    if p is None:
        _parse_errors.append("[ERROR] Fin de archivo inesperado")
    else:
        _parse_errors.append(f"[ERROR] Token '{p.type}' inesperado en la línea {p.lineno}")
    raise SyntaxError


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_parser(**kwargs):
    return yacc.yacc(
        module=sys.modules[__name__],
        start="program",
        debug=False,
        write_tables=False,
        **kwargs,
    )


def parse_text(text):
    global _parser, _parse_errors

    if _parser is None:
        _parser = build_parser()

    lexer = build_lexer()
    _parse_errors = []

    try:
        _parser.parse(text, lexer=lexer)
    except SyntaxError:
        pass

    return lexer.errors + _parse_errors
