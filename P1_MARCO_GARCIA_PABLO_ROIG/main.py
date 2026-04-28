import os
import sys
from lexer import build_lexer


def output_path(input_path: str) -> str:
    base, _ext = os.path.splitext(input_path)
    return base + ".token"


def main():
    if len(sys.argv) != 2:
        print("Uso: python main.py <file.lava>")
        sys.exit(1)

    in_path = sys.argv[1]
    if not os.path.exists(in_path):
        print(f"Error: El archivo {in_path} no existe.")
        sys.exit(1)

    with open(in_path, "r", encoding="utf-8") as f:
        data = f.read()

    lexer = build_lexer()
    lexer.input(data)

    out_path = output_path(in_path)

    with open(out_path, "w", encoding="utf-8") as out:
        for tok in lexer:
            line = f"{tok.type}, {tok.value}, {tok.lineno}, {tok.col_start}, {tok.col_end}\n"
            out.write(line)


if __name__ == "__main__":
    main()
