class IRGenerator:
    def __init__(self):
        self.lines = []
        self.temp_count = 0
        self.label_count = 0
        self.loop_end_stack = []

    def generate(self, program):
        for item in program:
            if item is None or item["kind"] == "record_decl":
                continue
            if item["kind"] == "function":
                self.emit_function(item)
            else:
                self.emit_item(item)
        return "\n".join(self.lines) + ("\n" if self.lines else "")

    def emit_function(self, item):
        params = ", ".join(
            f"{param['type']} {param['name']}" for param in item["params"]
        )
        self.emit(f"function {item['name']}({params}) -> {item['return_type']}")
        for statement in item["body"]:
            self.emit_item(statement)
        self.emit(f"end function {item['name']}")

    def emit_item(self, item):
        if item is None:
            return

        kind = item["kind"]
        if kind == "decl":
            for name in item["names"]:
                self.emit(f"declare {item['type_name']} {name}")
            if item["init"] is not None:
                value = self.emit_expression(item["init"])
                self.emit(f"{item['names'][0]} = {value}")
        elif kind == "assign":
            target = self.emit_lvalue(item["target"])
            value = self.emit_expression(item["value"])
            self.emit(f"{target} = {value}")
        elif kind == "print":
            value = self.emit_expression(item["value"])
            self.emit(f"print {value}")
        elif kind == "expr":
            self.emit_expression(item["value"])
        elif kind == "return":
            if item["value"] is None:
                self.emit("return")
            else:
                self.emit(f"return {self.emit_expression(item['value'])}")
        elif kind == "break":
            target = self.loop_end_stack[-1] if self.loop_end_stack else "<break>"
            self.emit(f"goto {target}")
        elif kind == "if":
            self.emit_if(item)
        elif kind == "while":
            self.emit_while(item)
        elif kind == "do_while":
            self.emit_do_while(item)

    def emit_if(self, item):
        else_label = self.new_label()
        end_label = self.new_label()
        condition = self.emit_expression(item["cond"])
        self.emit(f"ifFalse {condition} goto {else_label}")
        for statement in item["then_block"]:
            self.emit_item(statement)
        self.emit(f"goto {end_label}")
        self.emit(f"{else_label}:")
        if item["else_block"] is not None:
            for statement in item["else_block"]:
                self.emit_item(statement)
        self.emit(f"{end_label}:")

    def emit_while(self, item):
        start_label = self.new_label()
        end_label = self.new_label()
        self.loop_end_stack.append(end_label)
        self.emit(f"{start_label}:")
        condition = self.emit_expression(item["cond"])
        self.emit(f"ifFalse {condition} goto {end_label}")
        for statement in item["body"]:
            self.emit_item(statement)
        self.emit(f"goto {start_label}")
        self.emit(f"{end_label}:")
        self.loop_end_stack.pop()

    def emit_do_while(self, item):
        start_label = self.new_label()
        end_label = self.new_label()
        self.loop_end_stack.append(end_label)
        self.emit(f"{start_label}:")
        for statement in item["body"]:
            self.emit_item(statement)
        condition = self.emit_expression(item["cond"])
        self.emit(f"if {condition} goto {start_label}")
        self.emit(f"{end_label}:")
        self.loop_end_stack.pop()

    def emit_expression(self, expr):
        kind = expr["kind"]
        if kind == "literal":
            return str(expr["value"])
        if kind == "id":
            return expr["name"]
        if kind == "field":
            return f"{self.emit_expression(expr['value'])}.{expr['name']}"
        if kind == "new":
            args = ", ".join(self.emit_expression(arg) for arg in expr["args"])
            temp = self.new_temp()
            self.emit(f"{temp} = new {expr['type_name']}({args})")
            return temp
        if kind == "call":
            func = self.emit_expression(expr["func"])
            args = ", ".join(self.emit_expression(arg) for arg in expr["args"])
            temp = self.new_temp()
            self.emit(f"{temp} = call {func}({args})")
            return temp
        if kind == "unary":
            value = self.emit_expression(expr["value"])
            temp = self.new_temp()
            self.emit(f"{temp} = {expr['op']}{value}")
            return temp
        if kind == "binary":
            left = self.emit_expression(expr["left"])
            right = self.emit_expression(expr["right"])
            temp = self.new_temp()
            self.emit(f"{temp} = {left} {expr['op']} {right}")
            return temp
        return "<expr>"

    def emit_lvalue(self, expr):
        if expr["kind"] == "id":
            return expr["name"]
        if expr["kind"] == "field":
            return f"{self.emit_lvalue(expr['value'])}.{expr['name']}"
        return "<lvalue>"

    def emit(self, line):
        self.lines.append(line)

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"


def generate_ir(program):
    return IRGenerator().generate(program)
