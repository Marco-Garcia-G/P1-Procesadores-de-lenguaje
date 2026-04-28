PRIMITIVE_TYPES = {"int", "float", "char", "boolean"}
NUMERIC_TYPES = {"int", "float"}


class Scope:
    def __init__(self, parent=None):
        self.parent = parent
        self.symbols = {}

    def declare(self, name, type_name, line, errors):
        if name in self.symbols:
            errors.append(
                f"[ERROR] Simbolo '{name}' ya declarado en este ambito en la linea {line}"
            )
            return False
        self.symbols[name] = {"type": type_name, "line": line}
        return True

    def lookup(self, name):
        if name in self.symbols:
            return self.symbols[name]
        if self.parent is not None:
            return self.parent.lookup(name)
        return None


class SemanticAnalyzer:
    def __init__(self):
        self.errors = []
        self.records = {}
        self.functions = {}
        self.global_names = {}
        self.global_scope = Scope()

    def analyze(self, program):
        self.collect_records_and_functions(program)
        self.analyze_top_level(program)
        self.analyze_functions(program)
        return self.errors

    def collect_records_and_functions(self, program):
        for item in program:
            if item is None:
                continue
            if item["kind"] == "record_decl":
                self.collect_record(item)
            elif item["kind"] == "function":
                self.collect_function(item)

    def collect_record(self, item):
        name = item["name"]
        if name in self.records:
            self.error(item["line"], f"Registro '{name}' ya declarado")
            return
        if not self.reserve_global_name(name, "registro", item["line"]):
            return

        fields = []
        field_names = set()
        valid = True
        for field in item["fields"]:
            field_name = field["name"]
            field_type = field["type"]
            if field_name in field_names:
                self.error(
                    field["line"],
                    f"Campo '{field_name}' repetido en el registro '{name}'",
                )
                valid = False
            field_names.add(field_name)

            if not self.type_exists(field_type):
                self.error(
                    field["line"],
                    f"Tipo '{field_type}' no declarado en el campo '{field_name}'",
                )
                valid = False
            fields.append(field)

        if valid:
            self.records[name] = {
                "line": item["line"],
                "fields": fields,
                "field_map": {field["name"]: field for field in fields},
            }

    def collect_function(self, item):
        return_type = item["return_type"]
        name = item["name"]
        owner = self.global_names.get(name)
        if owner is not None and owner != "funcion":
            self.error(
                item["line"],
                f"Funcion '{name}' entra en conflicto con {owner} global del mismo nombre",
            )
            return
        self.global_names[name] = "funcion"

        if not self.type_exists(return_type, allow_void=True):
            self.error(
                item["line"],
                f"Tipo de retorno '{return_type}' no declarado en la funcion '{name}'",
            )
            return

        valid = True
        for param in item["params"]:
            if not self.type_exists(param["type"]):
                self.error(
                    param["line"],
                    f"Tipo '{param['type']}' no declarado en el parametro '{param['name']}'",
                )
                valid = False

        param_types = tuple(param["type"] for param in item["params"])
        overloads = self.functions.setdefault(name, [])
        if any(signature["param_types"] == param_types for signature in overloads):
            signature_text = self.format_signature(name, param_types)
            self.error(item["line"], f"Funcion duplicada '{signature_text}'")
            valid = False

        if valid:
            overloads.append(
                {
                    "name": name,
                    "return_type": return_type,
                    "params": item["params"],
                    "param_types": param_types,
                    "line": item["line"],
                    "node": item,
                }
            )

    def analyze_top_level(self, program):
        for item in program:
            if item is None or item["kind"] in {"record_decl", "function"}:
                continue
            self.analyze_item(item, self.global_scope, None, False, None)

    def analyze_functions(self, program):
        for item in program:
            if item is not None and item["kind"] == "function":
                self.analyze_function(item)

    def analyze_function(self, item):
        scope = Scope(self.global_scope)
        param_names = set()
        for param in item["params"]:
            if param["name"] in param_names:
                self.error(
                    param["line"],
                    f"Parametro '{param['name']}' repetido en la funcion '{item['name']}'",
                )
                continue
            param_names.add(param["name"])
            scope.declare(param["name"], param["type"], param["line"], self.errors)

        state = {"has_value_return": False}
        self.analyze_block(item["body"], scope, item["return_type"], False, state, False)

        if item["return_type"] != "void" and not state["has_value_return"]:
            self.error(
                item["line"],
                f"La funcion '{item['name']}' debe contener al menos un return con expresion",
            )

    def analyze_block(
        self, items, parent_scope, function_type, in_loop, state, create_scope=True
    ):
        scope = Scope(parent_scope) if create_scope else parent_scope
        for item in items:
            self.analyze_item(item, scope, function_type, in_loop, state)

    def analyze_item(self, item, scope, function_type, in_loop, state):
        if item is None:
            return

        kind = item["kind"]

        if kind == "decl":
            self.analyze_declaration(item, scope)
        elif kind == "assign":
            self.analyze_assignment(item, scope)
        elif kind == "break":
            if not in_loop:
                self.error(item["line"], "'break' fuera de bucle")
        elif kind == "return":
            self.analyze_return(item, scope, function_type, state)
        elif kind == "print":
            self.analyze_print(item, scope)
        elif kind == "expr":
            self.analyze_expression(item["value"], scope)
        elif kind == "if":
            cond_type = self.analyze_expression(item["cond"], scope)
            self.require_boolean(cond_type, item["line"], "condicion de if")
            self.analyze_block(item["then_block"], scope, function_type, in_loop, state)
            if item["else_block"] is not None:
                self.analyze_block(
                    item["else_block"], scope, function_type, in_loop, state
                )
        elif kind == "while":
            cond_type = self.analyze_expression(item["cond"], scope)
            self.require_boolean(cond_type, item["line"], "condicion de while")
            self.analyze_block(item["body"], scope, function_type, True, state)
        elif kind == "do_while":
            self.analyze_block(item["body"], scope, function_type, True, state)
            cond_type = self.analyze_expression(item["cond"], scope)
            self.require_boolean(cond_type, item["line"], "condicion de do-while")

    def analyze_declaration(self, item, scope):
        type_name = item["type_name"]
        type_ok = self.type_exists(type_name, line=item["line"])
        if not type_ok:
            self.error(item["line"], f"Tipo '{type_name}' no declarado")

        if item["init"] is not None:
            value_type = self.analyze_expression(item["init"], scope)
            if type_ok and not self.can_assign(type_name, value_type):
                self.error(
                    item["line"],
                    f"No se puede inicializar '{item['names'][0]}' de tipo {type_name} con {self.type_label(value_type)}",
                )

        for name in item["names"]:
            if scope is self.global_scope and not self.reserve_global_name(
                name, "variable", item["line"]
            ):
                continue
            scope.declare(name, type_name, item["line"], self.errors)

    def analyze_assignment(self, item, scope):
        target_type = self.analyze_lvalue(item["target"], scope)
        value_type = self.analyze_expression(item["value"], scope)
        if not self.can_assign(target_type, value_type):
            self.error(
                item["line"],
                f"No se puede asignar {self.type_label(value_type)} a {self.type_label(target_type)}",
            )

    def analyze_return(self, item, scope, function_type, state):
        if function_type is None:
            self.error(item["line"], "'return' fuera de funcion")
            return

        if function_type == "void":
            self.error(
                item["line"],
                "'return' no permitido en funcion void",
            )
            return

        if item["value"] is None:
            self.error(
                item["line"],
                "'return' sin expresion en funcion no void",
            )
            return

        value_type = self.analyze_expression(item["value"], scope)
        if self.can_assign(function_type, value_type):
            state["has_value_return"] = True
        else:
            self.error(
                item["line"],
                f"El return de tipo {self.type_label(value_type)} no coincide con {function_type}",
            )

    def analyze_print(self, item, scope):
        value_type = self.analyze_expression(item["value"], scope)
        if value_type == "void":
            self.error(item["line"], "No se puede imprimir una expresion void")
        elif value_type is not None and value_type not in PRIMITIVE_TYPES:
            self.error(
                item["line"],
                f"No se puede imprimir directamente un registro de tipo {value_type}",
            )

    def analyze_lvalue(self, expr, scope):
        if expr["kind"] == "id":
            return self.lookup_variable(expr["name"], expr["line"], scope)

        if expr["kind"] == "field":
            base = expr["value"]
            if base["kind"] not in {"id", "field"}:
                self.error(expr["line"], "Lado izquierdo de asignacion invalido")
                return None
            base_type = self.analyze_lvalue(base, scope)
            return self.resolve_field_type(base_type, expr["name"], expr["line"])

        self.error(expr["line"], "Lado izquierdo de asignacion invalido")
        return None

    def analyze_expression(self, expr, scope):
        kind = expr["kind"]

        if kind == "literal":
            return expr["literal_type"]

        if kind == "id":
            return self.lookup_variable(expr["name"], expr["line"], scope)

        if kind == "new":
            return self.analyze_new(expr, scope)

        if kind == "field":
            base_type = self.analyze_expression(expr["value"], scope)
            return self.resolve_field_type(base_type, expr["name"], expr["line"])

        if kind == "call":
            return self.analyze_call(expr, scope)

        if kind == "unary":
            return self.analyze_unary(expr, scope)

        if kind == "binary":
            return self.analyze_binary(expr, scope)

        if kind == "assign":
            self.error(expr["line"], "La asignacion no puede usarse como expresion")
            return None

        return None

    def analyze_new(self, expr, scope):
        type_name = expr["type_name"]
        record = self.records.get(type_name)
        arg_types = [self.analyze_expression(arg, scope) for arg in expr["args"]]

        if record is None:
            self.error(expr["line"], f"Registro '{type_name}' no declarado")
            return None
        if record["line"] > expr["line"]:
            self.error(
                expr["line"],
                f"Registro '{type_name}' usado antes de su declaracion",
            )
            return None

        fields = record["fields"]
        if len(arg_types) != len(fields):
            self.error(
                expr["line"],
                f"Constructor de '{type_name}' espera {len(fields)} argumentos y recibe {len(arg_types)}",
            )
            return type_name

        for index, (arg_type, field) in enumerate(zip(arg_types, fields), start=1):
            if not self.can_assign(field["type"], arg_type):
                self.error(
                    expr["line"],
                    f"Argumento {index} de '{type_name}' espera {field['type']} y recibe {self.type_label(arg_type)}",
                )
        return type_name

    def analyze_call(self, expr, scope):
        arg_types = [self.analyze_expression(arg, scope) for arg in expr["args"]]
        func = expr["func"]
        if func["kind"] != "id":
            self.error(expr["line"], "Solo se pueden llamar funciones por identificador")
            return None

        name = func["name"]
        overloads = self.functions.get(name)
        if not overloads:
            self.error(expr["line"], f"Funcion '{name}' no declarada")
            return None

        arity_matches = [
            signature
            for signature in overloads
            if len(signature["param_types"]) == len(arg_types)
        ]
        if not arity_matches:
            self.error(
                expr["line"],
                f"Ninguna sobrecarga de '{name}' recibe {len(arg_types)} argumentos",
            )
            return None

        matches = []
        for signature in arity_matches:
            score = self.match_score(signature["param_types"], arg_types)
            if score is not None:
                matches.append((score, signature))

        if not matches:
            received = ", ".join(self.type_label(type_name) for type_name in arg_types)
            self.error(
                expr["line"],
                f"Ninguna sobrecarga de '{name}' acepta ({received})",
            )
            return None

        matches.sort(key=lambda item: item[0])
        best_score = matches[0][0]
        best_matches = [
            signature for score, signature in matches if score == best_score
        ]
        if len(best_matches) > 1:
            self.error(expr["line"], f"Llamada ambigua a la funcion '{name}'")
            return None

        return best_matches[0]["return_type"]

    def analyze_unary(self, expr, scope):
        value_type = self.analyze_expression(expr["value"], scope)
        op = expr["op"]

        if op in {"+", "-"}:
            if value_type in NUMERIC_TYPES:
                return value_type
            self.error(
                expr["line"],
                f"Operador unario '{op}' no aplicable a {self.type_label(value_type)}",
            )
            return None

        if op == "!":
            if value_type == "boolean":
                return "boolean"
            self.error(
                expr["line"],
                f"Operador '!' no aplicable a {self.type_label(value_type)}",
            )
            return None

        return None

    def analyze_binary(self, expr, scope):
        left_type = self.analyze_expression(expr["left"], scope)
        right_type = self.analyze_expression(expr["right"], scope)
        op = expr["op"]

        if op in {"+", "-", "*", "/"}:
            if left_type in NUMERIC_TYPES and right_type in NUMERIC_TYPES:
                if left_type == "float" or right_type == "float":
                    return "float"
                return "int"
            self.error(
                expr["line"],
                f"Operador '{op}' requiere operandos numericos y recibe {self.type_label(left_type)} y {self.type_label(right_type)}",
            )
            return None

        if op in {">", ">=", "<", "<="}:
            if left_type in NUMERIC_TYPES and right_type in NUMERIC_TYPES:
                return "boolean"
            self.error(
                expr["line"],
                f"Operador '{op}' requiere operandos numericos y recibe {self.type_label(left_type)} y {self.type_label(right_type)}",
            )
            return None

        if op == "==":
            if self.are_comparable(left_type, right_type):
                return "boolean"
            self.error(
                expr["line"],
                f"Operador '==' no aplicable a {self.type_label(left_type)} y {self.type_label(right_type)}",
            )
            return None

        if op in {"&&", "||"}:
            if left_type == "boolean" and right_type == "boolean":
                return "boolean"
            self.error(
                expr["line"],
                f"Operador '{op}' requiere boolean y recibe {self.type_label(left_type)} y {self.type_label(right_type)}",
            )
            return None

        return None

    def resolve_field_type(self, base_type, field_name, line):
        if base_type is None:
            return None

        record = self.records.get(base_type)
        if record is None:
            self.error(line, f"El tipo {base_type} no tiene campos")
            return None

        field = record["field_map"].get(field_name)
        if field is None:
            self.error(line, f"El registro {base_type} no tiene campo '{field_name}'")
            return None

        return field["type"]

    def lookup_variable(self, name, line, scope):
        symbol = scope.lookup(name)
        if symbol is None:
            self.error(line, f"Variable '{name}' no declarada")
            return None
        return symbol["type"]

    def require_boolean(self, type_name, line, context):
        if type_name is not None and type_name != "boolean":
            self.error(line, f"La {context} debe ser boolean y es {type_name}")

    def type_exists(self, type_name, allow_void=False, line=None):
        if type_name in PRIMITIVE_TYPES:
            return True
        if allow_void and type_name == "void":
            return True
        record = self.records.get(type_name)
        if record is None:
            return False
        return line is None or record["line"] <= line

    def can_assign(self, target_type, source_type):
        if target_type is None or source_type is None:
            return True
        if target_type == source_type:
            return True
        return target_type == "float" and source_type == "int"

    def match_score(self, param_types, arg_types):
        score = 0
        for param_type, arg_type in zip(param_types, arg_types):
            if not self.can_assign(param_type, arg_type):
                return None
            if param_type != arg_type:
                score += 1
        return score

    def are_comparable(self, left_type, right_type):
        if left_type is None or right_type is None:
            return True
        if left_type in NUMERIC_TYPES and right_type in NUMERIC_TYPES:
            return True
        if left_type == right_type and left_type in {"char", "boolean"}:
            return True
        return False

    def reserve_global_name(self, name, kind, line):
        owner = self.global_names.get(name)
        if owner is None:
            self.global_names[name] = kind
            return True
        if owner == kind == "funcion":
            return True
        self.error(
            line,
            f"Nombre global '{name}' duplicado: ya existe como {owner} y se declara como {kind}",
        )
        return False

    def format_signature(self, name, param_types):
        return f"{name}({', '.join(param_types)})"

    def type_label(self, type_name):
        return "tipo desconocido" if type_name is None else type_name

    def error(self, line, message):
        self.errors.append(f"[ERROR] {message} en la linea {line}")


def analyze_program(program):
    return SemanticAnalyzer().analyze(program)
