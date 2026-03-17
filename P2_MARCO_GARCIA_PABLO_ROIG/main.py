import os
import sys

from lexer import build_lexer
from parser import parse_text


def find_column(text, lexpos):
    last_nl = text.rfind("\n", 0, lexpos)
    if last_nl < 0:
        return lexpos
    return lexpos - (last_nl + 1)


def output_path(input_path):
    base, _ext = os.path.splitext(input_path)
    return base + ".token"


def export_tokens(input_path, data):
    lexer = build_lexer()
    lexer.input(data)

    out_path = output_path(input_path)
    with open(out_path, "w", encoding="utf-8") as out:
        for tok in lexer:
            col_start = find_column(data, tok.lexpos)
            lexeme = str(tok.value)
            col_end = col_start + len(lexeme)
            out.write(
                f"{tok.type}, {lexeme}, {tok.lineno}, {col_start}, {col_end}\n"
            )


def read_input(path):
    if not os.path.exists(path):
        print(f"Error: El archivo {path} no existe.")
        raise SystemExit(1)

    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def main():
    if len(sys.argv) == 2:
        token_mode = False
        input_path = sys.argv[1]
    elif len(sys.argv) == 3 and sys.argv[1] == "--token":
        token_mode = True
        input_path = sys.argv[2]
    else:
        print("Uso: python main.py <file.lava> | python main.py --token <file.lava>")
        return 1

    data = read_input(input_path)

    if token_mode:
        export_tokens(input_path, data)
        return 0

    errors = parse_text(data)
    if errors:
        for error in errors:
            print(error)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
