from __future__ import annotations

import json
from pathlib import Path

from retrospective_script.__main__ import main


def valid_payload() -> dict:
    return {
        "meeting_title": "Retrospectiva de Produto",
        "meeting_date": "2024-08-09",
        "items": [
            {
                "theme": "Entrega",
                "description": "Validar o processo de publicação",
                "status": "open",
                "action": {"description": "Documentar publicação", "owner": "Caio"},
            }
        ],
    }


def test_cli_generates_markdown_from_local_json(tmp_path: Path, capsys) -> None:
    input_path = tmp_path / "retrospectiva.json"
    output_path = tmp_path / "roteiro.md"
    input_path.write_text(json.dumps(valid_payload(), ensure_ascii=False), encoding="utf-8")

    result = main([str(input_path), str(output_path)])

    captured = capsys.readouterr()
    assert result == 0
    assert captured.out == f"Roteiro gerado com sucesso em: {output_path}\n"
    assert captured.err == ""
    assert output_path.read_text(encoding="utf-8") == (
        "# Retrospectiva de Produto\n\n"
        "**Data:** 2024-08-09\n\n"
        "## Agenda\n"
        "1. Entrega\n\n"
        "## Discussão\n\n"
        "### Entrega\n"
        "- **Status:** Aberto **Pendente**\n"
        "  - Validar o processo de publicação\n\n"
        "## Plano de ação\n\n"
        "| Ação | Responsável | Prazo | Situação |\n"
        "| --- | --- | --- | --- |\n"
        "| Documentar publicação | Caio | Não informado | Pendente |\n"
    )


def test_cli_reports_malformed_json_in_portuguese(tmp_path: Path, capsys) -> None:
    input_path = tmp_path / "invalido.json"
    output_path = tmp_path / "roteiro.md"
    input_path.write_text('{"meeting_title":', encoding="utf-8")

    result = main([str(input_path), str(output_path)])

    captured = capsys.readouterr()
    assert result == 1
    assert "Erro: JSON inválido na linha 1, coluna" in captured.out
    assert "Corrija o arquivo de entrada." in captured.out
    assert not output_path.exists()


def test_cli_reports_invalid_structure_in_portuguese(tmp_path: Path, capsys) -> None:
    input_path = tmp_path / "estrutura-invalida.json"
    output_path = tmp_path / "roteiro.md"
    payload = valid_payload()
    payload["items"][0]["status"] = "invalid"
    input_path.write_text(json.dumps(payload), encoding="utf-8")

    result = main([str(input_path), str(output_path)])

    captured = capsys.readouterr()
    assert result == 1
    assert "Erro nos dados da retrospectiva:" in captured.out
    assert "items[0].status: deve ser um de: discussed, open, resolved." in captured.out
    assert "Corrija o arquivo de entrada." in captured.out
    assert not output_path.exists()
