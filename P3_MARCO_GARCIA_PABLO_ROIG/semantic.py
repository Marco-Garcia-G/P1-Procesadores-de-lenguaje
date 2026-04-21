class SymbolTable:
    def __init__(self, parent=None):
        self.parent = parent
        self.symbols = {}

    def declare(self, name, type_name, line, initialized=False):
        if name in self.symbols:
            return False, f"[ERROR SEMANTICO] Variable '{name}' ya declarada en este ámbito (línea {line})"
        self.symbols[name] = {
            "type": type_name,
            "initialized": initialized,
            "line": line,
        }
        return True, None

    def lookup(self, name):
        if name in self.symbols:
            return self.symbols[name]
        if self.parent is not None:
            return self.parent.lookup(name)
        return None

    def assign(self, name):
        if name in self.symbols:
            self.symbols[name]["initialized"] = True
            return True
        if self.parent is not None:
            return self.parent.assign(name)
        return False

    def child(self):
        return SymbolTable(parent=self)


class RecordTable:
    def __init__(self):
        self.records = {}

    def declare(self, name, fields, line):
        if name in self.records:
            return False, f"[ERROR SEMANTICO] Registro '{name}' ya declarado (línea {line})"
        self.records[name] = {"fields": fields, "line": line}
        return True, None

    def lookup(self, name):
        return self.records.get(name, None)


class FunctionTable:
    def __init__(self):
        self.functions = {}

    def declare(self, name, return_type, params, line):
        sig = (name, tuple(p["type"] for p in params))
        if sig in self.functions:
            return False, f"[ERROR SEMANTICO] Función '{name}' ya declarada con la misma firma (línea {line})"
        if name not in self.functions:
            self.functions[name] = []
        entry = {"return_type": return_type, "params": params, "line": line}
        self.functions[name].append(entry)
        return True, None

    def lookup(self, name, arg_types):
        overloads = self.functions.get(name)
        if overloads is None:
            return None
        for entry in overloads:
            param_types = [p["type"] for p in entry["params"]]
            if len(param_types) != len(arg_types):
                continue
            if all(types_compatible(a, p) for a, p in zip(arg_types, param_types)):
                return entry
        return None

    def lookup_by_name(self, name):
        return self.functions.get(name)


NUMERIC_TYPES = {"int", "float"}
PRIMITIVE_TYPES = {"int", "float", "char", "boolean"}


def is_numeric(t):
    return t in NUMERIC_TYPES


def is_primitive(t):
    return t in PRIMITIVE_TYPES


def types_compatible(source, target):
    if source == target:
        return True
    if source == "int" and target == "float":
        return True
    return False


def result_type_arithmetic(left, right):
    if left == "float" or right == "float":
        return "float"
    if left == "int" and right == "int":
        return "int"
    return None


class SemanticAnalyzer:
    def __init__(self):
        self.errors = []
        self.record_table = RecordTable()
        self.function_table = FunctionTable()
        self.global_scope = SymbolTable()
        self.in_loop = False
        self.current_function_type = None

    def error(self, msg):
        self.errors.append(msg)

    def analyze(self, program):
        self._register_declarations(program)
        self._analyze_items(program, self.global_scope)
        return self.errors

    def _register_declarations(self, items):
        for item in items:
            if item is None:
                continue
            if item["kind"] == "record_decl":
                self._register_record(item)
            elif item["kind"] == "function":
                self._register_function(item)

    def _register_record(self, item):
        fields = item["fields"]
        for f in fields:
            ft = f["type"]
            if not is_primitive(ft) and self.record_table.lookup(ft) is None:
                self.error(
                    f"[ERROR SEMANTICO] Tipo '{ft}' no definido para campo '{f['name']}' del registro '{item['name']}' (línea {f['line']})"
                )
        ok, err = self.record_table.declare(item["name"], fields, item["line"])
        if not ok:
            self.error(err)

    def _register_function(self, item):
        rt = item["return_type"]
        if rt != "void" and not is_primitive(rt) and self.record_table.lookup(rt) is None:
            self.error(
                f"[ERROR SEMANTICO] Tipo de retorno '{rt}' no definido para función '{item['name']}' (línea {item['line']})"
            )
        for p in item["params"]:
            pt = p["type"]
            if not is_primitive(pt) and self.record_table.lookup(pt) is None:
                self.error(
                    f"[ERROR SEMANTICO] Tipo '{pt}' no definido para parámetro '{p['name']}' de función '{item['name']}' (línea {p['line']})"
                )
        ok, err = self.function_table.declare(
            item["name"], item["return_type"], item["params"], item["line"]
        )
        if not ok:
            self.error(err)

    def _analyze_items(self, items, scope):
        for item in items:
            if item is None:
                continue
            self._analyze_item(item, scope)

    def _analyze_item(self, item, scope):
        kind = item["kind"]

        if kind == "record_decl":
            return

        if kind == "function":
            self._analyze_function(item, scope)
            return

        if kind == "decl":
            self._analyze_decl(item, scope)
            return

        if kind == "assign":
            self._analyze_assign(item, scope)
            return

        if kind == "return":
            self._analyze_return(item, scope)
            return

        if kind == "break":
            if not self.in_loop:
                self.error(f"[ERROR SEMANTICO] 'break' fuera de bucle (línea {item['line']})")
            return

        if kind == "print":
            self._analyze_expr(item["value"], scope)
            return

        if kind == "expr":
            self._analyze_expr(item["value"], scope)
            return

        if kind == "if":
            self._analyze_if(item, scope)
            return

        if kind == "while":
            self._analyze_while(item, scope)
            return

        if kind == "do_while":
            self._analyze_do_while(item, scope)
            return

    def _analyze_function(self, item, scope):
        fn_scope = scope.child()
        for p in item["params"]:
            fn_scope.declare(p["name"], p["type"], p["line"], initialized=True)

        old_fn_type = self.current_function_type
        self.current_function_type = item["return_type"]

        has_return = self._analyze_block(item["body"], fn_scope)

        if item["return_type"] != "void" and not has_return:
            self.error(
                f"[ERROR SEMANTICO] Función '{item['name']}' de tipo '{item['return_type']}' debe contener un return con expresión (línea {item['line']})"
            )

        self.current_function_type = old_fn_type

    def _analyze_block(self, items, scope):
        block_scope = scope.child()
        has_return = False
        for item in items:
            if item is None:
                continue
            self._analyze_item(item, block_scope)
            if item["kind"] == "return" and item.get("value") is not None:
                has_return = True
        return has_return

    def _analyze_decl(self, item, scope):
        type_name = item["type_name"]

        if not is_primitive(type_name) and self.record_table.lookup(type_name) is None:
            self.error(
                f"[ERROR SEMANTICO] Tipo '{type_name}' no definido (línea {item['line']})"
            )
            return

        has_init = item["init"] is not None
        init_type = None
        if has_init:
            init_type = self._analyze_expr(item["init"], scope)

        for name in item["names"]:
            ok, err = scope.declare(name, type_name, item["line"], initialized=has_init)
            if not ok:
                self.error(err)
                continue

            if has_init and init_type is not None:
                if not types_compatible(init_type, type_name):
                    self.error(
                        f"[ERROR SEMANTICO] No se puede asignar tipo '{init_type}' a variable '{name}' de tipo '{type_name}' (línea {item['line']})"
                    )

    def _analyze_assign(self, item, scope):
        target_type = self._analyze_lvalue(item["target"], scope)
        value_type = self._analyze_expr(item["value"], scope)

        if target_type is not None and value_type is not None:
            if not types_compatible(value_type, target_type):
                self.error(
                    f"[ERROR SEMANTICO] No se puede asignar tipo '{value_type}' a tipo '{target_type}' (línea {item['line']})"
                )

        if item["target"]["kind"] == "id":
            scope.assign(item["target"]["name"])

    def _analyze_return(self, item, scope):
        if self.current_function_type is None:
            self.error(f"[ERROR SEMANTICO] 'return' fuera de función (línea {item['line']})")
            return

        if self.current_function_type == "void":
            if item["value"] is not None:
                self.error(
                    f"[ERROR SEMANTICO] 'return' con valor en función void (línea {item['line']})"
                )
            return

        if item["value"] is None:
            self.error(
                f"[ERROR SEMANTICO] 'return' sin valor en función de tipo '{self.current_function_type}' (línea {item['line']})"
            )
            return

        ret_type = self._analyze_expr(item["value"], scope)
        if ret_type is not None and not types_compatible(ret_type, self.current_function_type):
            self.error(
                f"[ERROR SEMANTICO] Tipo de retorno '{ret_type}' incompatible con tipo de función '{self.current_function_type}' (línea {item['line']})"
            )

    def _analyze_if(self, item, scope):
        cond_type = self._analyze_expr(item["cond"], scope)
        if cond_type is not None and cond_type != "boolean":
            self.error(
                f"[ERROR SEMANTICO] La condición del 'if' debe ser boolean, se encontró '{cond_type}' (línea {item['line']})"
            )
        self._analyze_block(item["then_block"], scope)
        if item["else_block"] is not None:
            self._analyze_block(item["else_block"], scope)

    def _analyze_while(self, item, scope):
        cond_type = self._analyze_expr(item["cond"], scope)
        if cond_type is not None and cond_type != "boolean":
            self.error(
                f"[ERROR SEMANTICO] La condición del 'while' debe ser boolean, se encontró '{cond_type}' (línea {item['line']})"
            )
        old_in_loop = self.in_loop
        self.in_loop = True
        self._analyze_block(item["body"], scope)
        self.in_loop = old_in_loop

    def _analyze_do_while(self, item, scope):
        old_in_loop = self.in_loop
        self.in_loop = True
        self._analyze_block(item["body"], scope)
        self.in_loop = old_in_loop
        cond_type = self._analyze_expr(item["cond"], scope)
        if cond_type is not None and cond_type != "boolean":
            self.error(
                f"[ERROR SEMANTICO] La condición del 'do-while' debe ser boolean, se encontró '{cond_type}' (línea {item['line']})"
            )

    def _analyze_lvalue(self, expr, scope):
        if expr["kind"] == "id":
            sym = scope.lookup(expr["name"])
            if sym is None:
                self.error(
                    f"[ERROR SEMANTICO] Variable '{expr['name']}' no declarada (línea {expr['line']})"
                )
                return None
            return sym["type"]

        if expr["kind"] == "field":
            obj_type = self._analyze_lvalue(expr["value"], scope)
            if obj_type is None:
                return None
            rec = self.record_table.lookup(obj_type)
            if rec is None:
                self.error(
                    f"[ERROR SEMANTICO] Tipo '{obj_type}' no es un registro (línea {expr['line']})"
                )
                return None
            for f in rec["fields"]:
                if f["name"] == expr["name"]:
                    return f["type"]
            self.error(
                f"[ERROR SEMANTICO] El registro '{obj_type}' no tiene campo '{expr['name']}' (línea {expr['line']})"
            )
            return None

        self.error(
            f"[ERROR SEMANTICO] Lado izquierdo de asignación inválido (línea {expr['line']})"
        )
        return None

    def _analyze_expr(self, expr, scope):
        if expr is None:
            return None

        kind = expr["kind"]

        if kind == "literal":
            return expr["literal_type"]

        if kind == "id":
            sym = scope.lookup(expr["name"])
            if sym is None:
                self.error(
                    f"[ERROR SEMANTICO] Variable '{expr['name']}' no declarada (línea {expr['line']})"
                )
                return None
            return sym["type"]

        if kind == "unary":
            operand_type = self._analyze_expr(expr["value"], scope)
            if operand_type is None:
                return None
            op = expr["op"]
            if op in ("+", "-"):
                if not is_numeric(operand_type):
                    self.error(
                        f"[ERROR SEMANTICO] Operador '{op}' no aplicable a tipo '{operand_type}' (línea {expr['line']})"
                    )
                    return None
                return operand_type
            if op == "!":
                if operand_type != "boolean":
                    self.error(
                        f"[ERROR SEMANTICO] Operador '!' requiere tipo boolean, se encontró '{operand_type}' (línea {expr['line']})"
                    )
                    return None
                return "boolean"

        if kind == "binary":
            left_type = self._analyze_expr(expr["left"], scope)
            right_type = self._analyze_expr(expr["right"], scope)
            if left_type is None or right_type is None:
                return None
            op = expr["op"]
            return self._check_binary_op(op, left_type, right_type, expr["line"])

        if kind == "call":
            return self._analyze_call(expr, scope)

        if kind == "field":
            return self._analyze_field_access(expr, scope)

        if kind == "new":
            return self._analyze_new(expr, scope)

        return None

    def _check_binary_op(self, op, left, right, line):
        if op in ("+", "-", "*", "/"):
            if not is_numeric(left):
                self.error(
                    f"[ERROR SEMANTICO] Operador '{op}' no aplicable a tipo '{left}' (línea {line})"
                )
                return None
            if not is_numeric(right):
                self.error(
                    f"[ERROR SEMANTICO] Operador '{op}' no aplicable a tipo '{right}' (línea {line})"
                )
                return None
            return result_type_arithmetic(left, right)

        if op in ("&&", "||"):
            if left != "boolean":
                self.error(
                    f"[ERROR SEMANTICO] Operador '{op}' requiere boolean, se encontró '{left}' (línea {line})"
                )
                return None
            if right != "boolean":
                self.error(
                    f"[ERROR SEMANTICO] Operador '{op}' requiere boolean, se encontró '{right}' (línea {line})"
                )
                return None
            return "boolean"

        if op in (">", ">=", "<", "<=", "=="):
            if op == "==":
                if left == right:
                    return "boolean"
                if is_numeric(left) and is_numeric(right):
                    return "boolean"
                self.error(
                    f"[ERROR SEMANTICO] No se pueden comparar tipos '{left}' y '{right}' con '{op}' (línea {line})"
                )
                return None
            if not is_numeric(left):
                self.error(
                    f"[ERROR SEMANTICO] Operador '{op}' no aplicable a tipo '{left}' (línea {line})"
                )
                return None
            if not is_numeric(right):
                self.error(
                    f"[ERROR SEMANTICO] Operador '{op}' no aplicable a tipo '{right}' (línea {line})"
                )
                return None
            return "boolean"

        return None

    def _analyze_call(self, expr, scope):
        func_expr = expr["func"]

        if func_expr["kind"] != "id":
            self.error(
                f"[ERROR SEMANTICO] Solo se permiten llamadas a funciones por nombre (línea {expr['line']})"
            )
            return None

        func_name = func_expr["name"]
        arg_types = []
        for arg in expr["args"]:
            t = self._analyze_expr(arg, scope)
            arg_types.append(t)

        if any(t is None for t in arg_types):
            return None

        entry = self.function_table.lookup(func_name, arg_types)
        if entry is None:
            overloads = self.function_table.lookup_by_name(func_name)
            if overloads is None:
                self.error(
                    f"[ERROR SEMANTICO] Función '{func_name}' no declarada (línea {expr['line']})"
                )
            else:
                arg_str = ", ".join(arg_types)
                self.error(
                    f"[ERROR SEMANTICO] No existe sobrecarga de '{func_name}' compatible con argumentos ({arg_str}) (línea {expr['line']})"
                )
            return None

        return entry["return_type"]

    def _analyze_field_access(self, expr, scope):
        obj_type = self._analyze_expr(expr["value"], scope)
        if obj_type is None:
            return None

        rec = self.record_table.lookup(obj_type)
        if rec is None:
            self.error(
                f"[ERROR SEMANTICO] Tipo '{obj_type}' no es un registro, no se puede acceder a '{expr['name']}' (línea {expr['line']})"
            )
            return None

        for f in rec["fields"]:
            if f["name"] == expr["name"]:
                return f["type"]

        self.error(
            f"[ERROR SEMANTICO] El registro '{obj_type}' no tiene campo '{expr['name']}' (línea {expr['line']})"
        )
        return None

    def _analyze_new(self, expr, scope):
        type_name = expr["type_name"]
        rec = self.record_table.lookup(type_name)
        if rec is None:
            self.error(
                f"[ERROR SEMANTICO] Registro '{type_name}' no definido (línea {expr['line']})"
            )
            return None

        fields = rec["fields"]
        args = expr["args"]
        if len(args) != len(fields):
            self.error(
                f"[ERROR SEMANTICO] '{type_name}' espera {len(fields)} argumentos, se proporcionaron {len(args)} (línea {expr['line']})"
            )
            return None

        for i, (arg, field) in enumerate(zip(args, fields)):
            arg_type = self._analyze_expr(arg, scope)
            if arg_type is None:
                continue
            if not types_compatible(arg_type, field["type"]):
                self.error(
                    f"[ERROR SEMANTICO] Argumento {i+1} de '{type_name}': tipo '{arg_type}' incompatible con '{field['type']}' (línea {expr['line']})"
                )

        return type_name
