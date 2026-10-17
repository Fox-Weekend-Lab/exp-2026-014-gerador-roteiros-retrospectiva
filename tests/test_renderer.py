from __future__ import annotations

from retrospective_script.models import parse_retrospective
from retrospective_script.renderer import render_markdown


def test_render_markdown_groups_sorts_and_marks_actions() -> None:
    retrospective = parse_retrospective(
        {
            "meeting_title": "Retrospectiva",
            "meeting_date": "2024-07-01",
            "items": [
                {
                    "theme": "Zebra",
                    "description": "Primeiro ponto zebra",
                    "status": "discussed",
                    "action": {"description": "Registrar aprendizado", "owner": "Bia", "due_date": "2024-07-03"},
                },
                {
                    "theme": "alpha",
                    "description": "Ponto aberto",
                    "status": "open",
                    "decision": "Priorizar correção",
                    "action": {"description": "Corrigir fluxo"},
                },
                {
                    "theme": "Alpha",
                    "description": "Segundo ponto alpha",
                    "status": "resolved",
                },
            ],
        }
    )

    markdown = render_markdown(retrospective)

    assert markdown.startswith("# Retrospectiva\n\n**Data:** 2024-07-01\n")
    assert "## Agenda\n1. alpha\n2. Alpha\n3. Zebra" in markdown
    assert markdown.index("### alpha") < markdown.index("### Alpha") < markdown.index("### Zebra")
    assert "- **Status:** Aberto **Pendente**\n  - Ponto aberto" in markdown
    assert "- **Decisão:** Priorizar correção" in markdown
    assert "- **Status:** Resolvido\n  - Segundo ponto alpha" in markdown
    assert "| Ação | Responsável | Prazo | Situação |" in markdown
    assert "| Registrar aprendizado | Bia | 2024-07-03 | Acompanhar |" in markdown
    assert "| Corrigir fluxo | Não informado | Não informado | Pendente |" in markdown
    assert markdown.endswith("\n")


def test_render_markdown_shows_placeholder_when_there_are_no_actions() -> None:
    retrospective = parse_retrospective(
        {
            "meeting_title": "Sem ações",
            "meeting_date": "2024-01-01",
            "items": [{"theme": "Tema", "description": "Observação", "status": "resolved"}],
        }
    )

    markdown = render_markdown(retrospective)

    assert "| Nenhuma ação registrada | — | — | — |" in markdown
