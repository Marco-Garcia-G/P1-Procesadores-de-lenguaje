import os
import sys

from lexer import build_lexer
from parser import parse_text


def main():
    if len(sys.argv) == 2:
        mode = "semantic"
        input_path = sys.argv[1]
    elif len(sys.argv) == 3 and sys.argv[1] == "--token":
        mode = "token"
        input_path = sys.argv[2]
    else:
        print(
            "Uso: python main.py <file.lava> | python main.py --token <file.lava>"
        )
        return 1

    if not os.path.exists(input_path):
        print(f"Error: El archivo {input_path} no existe.")
        return 1

    with open(input_path, "r", encoding="utf-8") as handle:
        data = handle.read()

    if mode == "token":
        lexer = build_lexer()
        lexer.input(data)

        base, _ext = os.path.splitext(input_path)
        out_path = base + ".token"

        with open(out_path, "w", encoding="utf-8") as out:
            for tok in lexer:
                out.write(
                    f"{tok.type}, {tok.value}, {tok.lineno}, {tok.col_start}, {tok.col_end}\n"
                )
        return 0

    errors = parse_text(data)
    if errors:
        for error in errors:
            print(error)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
