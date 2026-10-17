"""Interface de linha de comando do gerador de roteiros."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .models import ValidationError, parse_retrospective
from .renderer import render_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Gera um roteiro Markdown a partir de uma retrospectiva em JSON."
    )
    parser.add_argument("input_json", help="caminho do arquivo JSON de entrada")
    parser.add_argument("output_markdown", help="caminho do arquivo Markdown de saída")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    input_path = Path(args.input_json)
    output_path = Path(args.output_markdown)

    try:
        with input_path.open("r", encoding="utf-8") as input_file:
            data = json.load(input_file)
        retrospective = parse_retrospective(data)
        markdown = render_markdown(retrospective)
    except FileNotFoundError:
        print(f"Erro: o arquivo de entrada não foi encontrado: {input_path}.")
        return 1
    except PermissionError:
        print(f"Erro: não foi possível ler o arquivo de entrada: {input_path}. Verifique as permissões.")
        return 1
    except UnicodeDecodeError:
        print("Erro: o arquivo de entrada deve estar codificado em UTF-8.")
        return 1
    except json.JSONDecodeError as exc:
        print(f"Erro: JSON inválido na linha {exc.lineno}, coluna {exc.colno}. Corrija o arquivo de entrada.")
        return 1
    except ValidationError as exc:
        print(f"Erro nos dados da retrospectiva: {exc} Corrija o arquivo de entrada.")
        return 1
    except OSError as exc:
        print(f"Erro ao ler o arquivo de entrada: {exc}.")
        return 1

    try:
        with output_path.open("w", encoding="utf-8", newline="\n") as output_file:
            output_file.write(markdown)
    except OSError as exc:
        print(f"Erro: não foi possível gravar a saída em {output_path}: {exc}.")
        return 1

    print(f"Roteiro gerado com sucesso em: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
