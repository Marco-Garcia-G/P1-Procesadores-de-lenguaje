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


def node(kind, line, **data):
    value = {"kind": kind, "line": line}
    value.update(data)
    return value


def append_item(items, item):
    if item is None:
        return items
    return items + [item]


def append_name(names, name):
    return names + [name]


def p_program(p):
    "program : program_items_opt"
    p[0] = p[1]


def p_program_items_opt_empty(p):
    "program_items_opt : empty"
    p[0] = []


def p_program_items_opt_many(p):
    "program_items_opt : program_items_opt program_item"
    p[0] = append_item(p[1], p[2])


def p_program_item_empty(p):
    "program_item : SEMICOLON"
    p[0] = None


def p_program_item_record(p):
    "program_item : record_decl SEMICOLON"
    p[0] = p[1]


def p_program_item_void_function(p):
    "program_item : VOID ID LPAREN param_list_opt RPAREN block"
    p[0] = node(
        "function",
        p.lineno(2),
        return_type="void",
        name=p[2],
        params=p[4],
        body=p[6],
    )


def p_program_item_primitive_function(p):
    "program_item : primitive_type ID LPAREN param_list_opt RPAREN block"
    p[0] = node(
        "function",
        p.lineno(2),
        return_type=p[1],
        name=p[2],
        params=p[4],
        body=p[6],
    )


def p_program_item_custom_function(p):
    "program_item : custom_type ID LPAREN param_list_opt RPAREN block"
    p[0] = node(
        "function",
        p.lineno(2),
        return_type=p[1],
        name=p[2],
        params=p[4],
        body=p[6],
    )


def p_program_item_primitive_init(p):
    "program_item : primitive_type ID ASSIGN expression SEMICOLON"
    p[0] = node("decl", p.lineno(2), type_name=p[1], names=[p[2]], init=p[4])


def p_program_item_primitive_decl(p):
    "program_item : primitive_type ID primitive_id_list_tail SEMICOLON"
    p[0] = node(
        "decl",
        p.lineno(2),
        type_name=p[1],
        names=[p[2]] + p[3],
        init=None,
    )


def p_program_item_custom_init(p):
    "program_item : custom_type ID ASSIGN expression SEMICOLON"
    p[0] = node("decl", p.lineno(2), type_name=p[1], names=[p[2]], init=p[4])


def p_program_item_control(p):
    "program_item : control_statement"
    p[0] = p[1]


def p_program_item_plain(p):
    "program_item : plain_simple_statement SEMICOLON"
    p[0] = p[1]


def p_record_decl(p):
    "record_decl : RECORD ID LPAREN field_list_opt RPAREN"
    p[0] = node("record_decl", p.lineno(2), name=p[2], fields=p[4])


def p_field_list_opt_empty(p):
    "field_list_opt : empty"
    p[0] = []


def p_field_list_opt_list(p):
    "field_list_opt : field_list"
    p[0] = p[1]


def p_field_list_one(p):
    "field_list : field_decl"
    p[0] = [p[1]]


def p_field_list_many(p):
    "field_list : field_list COMMA field_decl"
    p[0] = p[1] + [p[3]]


def p_field_decl(p):
    "field_decl : any_type ID"
    p[0] = {"type": p[1], "name": p[2], "line": p.lineno(2)}


def p_param_list_opt_empty(p):
    "param_list_opt : empty"
    p[0] = []


def p_param_list_opt_list(p):
    "param_list_opt : param_list"
    p[0] = p[1]


def p_param_list_one(p):
    "param_list : param_decl"
    p[0] = [p[1]]


def p_param_list_many(p):
    "param_list : param_list COMMA param_decl"
    p[0] = p[1] + [p[3]]


def p_param_decl(p):
    "param_decl : any_type ID"
    p[0] = {"type": p[1], "name": p[2], "line": p.lineno(2)}


def p_block(p):
    "block : LBRACE block_items_opt RBRACE"
    p[0] = p[2]


def p_block_items_opt_empty(p):
    "block_items_opt : empty"
    p[0] = []


def p_block_items_opt_many(p):
    "block_items_opt : block_items_opt block_item"
    p[0] = append_item(p[1], p[2])


def p_block_item_empty(p):
    "block_item : SEMICOLON"
    p[0] = None


def p_block_item_control(p):
    "block_item : control_statement"
    p[0] = p[1]


def p_block_item_primitive_init(p):
    "block_item : primitive_type ID ASSIGN expression SEMICOLON"
    p[0] = node("decl", p.lineno(2), type_name=p[1], names=[p[2]], init=p[4])


def p_block_item_primitive_decl(p):
    "block_item : primitive_type ID primitive_id_list_tail SEMICOLON"
    p[0] = node(
        "decl",
        p.lineno(2),
        type_name=p[1],
        names=[p[2]] + p[3],
        init=None,
    )


def p_block_item_custom_init(p):
    "block_item : custom_type ID ASSIGN expression SEMICOLON"
    p[0] = node("decl", p.lineno(2), type_name=p[1], names=[p[2]], init=p[4])


def p_block_item_plain(p):
    "block_item : plain_simple_statement SEMICOLON"
    p[0] = p[1]


def p_plain_simple_statement_assignment(p):
    "plain_simple_statement : assignment"
    p[0] = p[1]


def p_plain_simple_statement_break(p):
    "plain_simple_statement : BREAK"
    p[0] = node("break", p.lineno(1))


def p_plain_simple_statement_return_empty(p):
    "plain_simple_statement : RETURN"
    p[0] = node("return", p.lineno(1), value=None)


def p_plain_simple_statement_return_expr(p):
    "plain_simple_statement : RETURN expression"
    p[0] = node("return", p.lineno(1), value=p[2])


def p_plain_simple_statement_print(p):
    "plain_simple_statement : PRINT LPAREN expression RPAREN"
    p[0] = node("print", p.lineno(1), value=p[3])


def p_plain_simple_statement_expr(p):
    "plain_simple_statement : expression"
    p[0] = node("expr", p[1]["line"], value=p[1])


def p_control_statement_if(p):
    "control_statement : IF LPAREN expression RPAREN block"
    p[0] = node("if", p.lineno(1), cond=p[3], then_block=p[5], else_block=None)


def p_control_statement_if_else(p):
    "control_statement : IF LPAREN expression RPAREN block ELSE block"
    p[0] = node("if", p.lineno(1), cond=p[3], then_block=p[5], else_block=p[7])


def p_control_statement_while(p):
    "control_statement : WHILE LPAREN expression RPAREN block"
    p[0] = node("while", p.lineno(1), cond=p[3], body=p[5])


def p_control_statement_do_while(p):
    "control_statement : DO block WHILE LPAREN expression RPAREN"
    p[0] = node("do_while", p.lineno(1), body=p[2], cond=p[5])


def p_primitive_id_list_tail_empty(p):
    "primitive_id_list_tail : empty"
    p[0] = []


def p_primitive_id_list_tail_list(p):
    "primitive_id_list_tail : comma_id_list"
    p[0] = p[1]


def p_comma_id_list_one(p):
    "comma_id_list : COMMA ID"
    p[0] = [p[2]]


def p_comma_id_list_many(p):
    "comma_id_list : comma_id_list COMMA ID"
    p[0] = append_name(p[1], p[3])


def p_assignment(p):
    "assignment : postfix_expr ASSIGN expression"
    p[0] = node("assign", p.lineno(2), target=p[1], value=p[3])


def p_primitive_type_int(p):
    "primitive_type : INT"
    p[0] = p[1]


def p_primitive_type_float(p):
    "primitive_type : FLOAT"
    p[0] = p[1]


def p_primitive_type_char(p):
    "primitive_type : CHAR"
    p[0] = p[1]


def p_primitive_type_boolean(p):
    "primitive_type : BOOLEAN"
    p[0] = p[1]


def p_custom_type(p):
    "custom_type : ID"
    p[0] = p[1]


def p_any_type_primitive(p):
    "any_type : primitive_type"
    p[0] = p[1]


def p_any_type_custom(p):
    "any_type : custom_type"
    p[0] = p[1]


def p_expression_postfix(p):
    "expression : postfix_expr"
    p[0] = p[1]


def p_expression_unary_plus(p):
    "expression : PLUS expression %prec UPLUS"
    p[0] = node("unary", p.lineno(1), op=p[1], value=p[2])


def p_expression_unary_minus(p):
    "expression : MINUS expression %prec UMINUS"
    p[0] = node("unary", p.lineno(1), op=p[1], value=p[2])


def p_expression_not(p):
    "expression : NOT expression"
    p[0] = node("unary", p.lineno(1), op=p[1], value=p[2])


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
    p[0] = node("binary", p[1]["line"], op=p[2], left=p[1], right=p[3])


def p_postfix_expr_primary(p):
    "postfix_expr : primary_expr"
    p[0] = p[1]


def p_postfix_expr_call(p):
    "postfix_expr : postfix_expr LPAREN arg_list_opt RPAREN"
    p[0] = node("call", p[1]["line"], func=p[1], args=p[3])


def p_postfix_expr_dot(p):
    "postfix_expr : postfix_expr DOT ID"
    p[0] = node("field", p[1]["line"], value=p[1], name=p[3])


def p_primary_expr_literal(p):
    "primary_expr : literal"
    p[0] = p[1]


def p_primary_expr_id(p):
    "primary_expr : ID"
    p[0] = node("id", p.lineno(1), name=p[1])


def p_primary_expr_grouped(p):
    "primary_expr : LPAREN expression RPAREN"
    p[0] = p[2]


def p_primary_expr_new(p):
    "primary_expr : NEW ID LPAREN arg_list_opt RPAREN"
    p[0] = node("new", p.lineno(1), type_name=p[2], args=p[4])


def p_literal_int(p):
    "literal : INT_VALUE"
    p[0] = node("literal", p.lineno(1), literal_type="int", value=p[1])


def p_literal_float(p):
    "literal : FLOAT_VALUE"
    p[0] = node("literal", p.lineno(1), literal_type="float", value=p[1])


def p_literal_char(p):
    "literal : CHAR_VALUE"
    p[0] = node("literal", p.lineno(1), literal_type="char", value=p[1])


def p_literal_true(p):
    "literal : TRUE"
    p[0] = node("literal", p.lineno(1), literal_type="boolean", value=p[1])


def p_literal_false(p):
    "literal : FALSE"
    p[0] = node("literal", p.lineno(1), literal_type="boolean", value=p[1])


def p_arg_list_opt_empty(p):
    "arg_list_opt : empty"
    p[0] = []


def p_arg_list_opt_list(p):
    "arg_list_opt : arg_list"
    p[0] = p[1]


def p_arg_list_one(p):
    "arg_list : expression"
    p[0] = [p[1]]


def p_arg_list_many(p):
    "arg_list : arg_list COMMA expression"
    p[0] = p[1] + [p[3]]


def p_empty(p):
    "empty :"
    p[0] = []


def p_error(p):
    if p is None:
        _parse_errors.append("[ERROR] Fin de archivo inesperado")
    else:
        _parse_errors.append(f"[ERROR] Token '{p.type}' inesperado en la línea {p.lineno}")
    raise SyntaxError


def is_lvalue(expr):
    if expr["kind"] == "id":
        return True
    if expr["kind"] == "field":
        return is_lvalue(expr["value"])
    return False


def validate_block(items, errors, in_function, in_loop, function_type, state):
    for item in items:
        validate_item(item, errors, in_function, in_loop, function_type, state)


def validate_item(item, errors, in_function, in_loop, function_type, state):
    if item is None:
        return

    kind = item["kind"]

    if kind == "assign":
        if not is_lvalue(item["target"]):
            errors.append(
                f"[ERROR] Lado izquierdo de asignación inválido en la línea {item['line']}"
            )
        return

    if kind == "break":
        if not in_loop:
            errors.append(f"[ERROR] 'break' fuera de bucle en la línea {item['line']}")
        return

    if kind == "return":
        if not in_function:
            errors.append(f"[ERROR] 'return' fuera de función en la línea {item['line']}")
            return
        state["has_return"] = True
        if function_type == "void":
            errors.append(
                f"[ERROR] 'return' no permitido en función void en la línea {item['line']}"
            )
            return
        if item["value"] is None:
            errors.append(
                f"[ERROR] 'return' sin expresión en función no void en la línea {item['line']}"
            )
            return
        state["has_value_return"] = True
        return

    if kind == "if":
        validate_block(
            item["then_block"], errors, in_function, in_loop, function_type, state
        )
        if item["else_block"] is not None:
            validate_block(
                item["else_block"], errors, in_function, in_loop, function_type, state
            )
        return

    if kind == "while":
        validate_block(item["body"], errors, in_function, True, function_type, state)
        return

    if kind == "do_while":
        validate_block(item["body"], errors, in_function, True, function_type, state)
        return


def validate_function(item, errors):
    state = {"has_return": False, "has_value_return": False}
    validate_block(item["body"], errors, True, False, item["return_type"], state)
    if item["return_type"] != "void" and not state["has_value_return"]:
        errors.append(
            f"[ERROR] La función '{item['name']}' debe contener al menos un return con expresión en la línea {item['line']}"
        )


def validate_program(items):
    errors = []

    for item in items:
        if item is None:
            continue
        if item["kind"] == "function":
            validate_function(item, errors)
            continue
        if item["kind"] == "record_decl":
            continue
        validate_item(item, errors, False, False, None, {})

    return errors


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
        program = _parser.parse(text, lexer=lexer)
    except SyntaxError:
        return lexer.errors + _parse_errors

    return lexer.errors + _parse_errors + validate_program(program)
