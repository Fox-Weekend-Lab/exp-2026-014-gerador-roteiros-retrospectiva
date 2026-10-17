"""Renderização determinística de retrospectivas em Markdown."""

from __future__ import annotations

from collections import OrderedDict

from .models import Retrospective, RetrospectiveItem


STATUS_LABELS = {
    "open": "Aberto",
    "discussed": "Discutido",
    "resolved": "Resolvido",
}


def _groups(retrospective: Retrospective) -> OrderedDict[str, list[RetrospectiveItem]]:
    grouped: dict[str, list[RetrospectiveItem]] = {}
    for item in retrospective.items:
        grouped.setdefault(item.theme, []).append(item)
    return OrderedDict((theme, grouped[theme]) for theme in sorted(grouped, key=str.casefold))


def _table_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def render_markdown(retrospective: Retrospective) -> str:
    """Transforma uma retrospectiva validada em um roteiro Markdown."""
    groups = _groups(retrospective)
    lines = [
        f"# {retrospective.meeting_title}",
        "",
        f"**Data:** {retrospective.meeting_date}",
        "",
        "## Agenda",
    ]
    lines.extend(f"{position}. {theme}" for position, theme in enumerate(groups, start=1))

    lines.extend(["", "## Discussão"])
    for theme, items in groups.items():
        lines.extend(["", f"### {theme}"])
        for item in items:
            pending = " **Pendente**" if item.status == "open" else ""
            lines.append(f"- **Status:** {STATUS_LABELS[item.status]}{pending}")
            lines.append(f"  - {item.description}")
            if item.decision is not None:
                lines.append(f"  - **Decisão:** {item.decision}")

    lines.extend(["", "## Plano de ação", "", "| Ação | Responsável | Prazo | Situação |", "| --- | --- | --- | --- |"])
    action_count = 0
    for item in retrospective.items:
        if item.action is None:
            continue
        action_count += 1
        owner = item.action.owner or "Não informado"
        due_date = item.action.due_date or "Não informado"
        situation = "Pendente" if item.status == "open" else "Acompanhar"
        lines.append(
            "| "
            + " | ".join(
                _table_cell(value)
                for value in (item.action.description, owner, due_date, situation)
            )
            + " |"
        )

    if action_count == 0:
        lines.append("| Nenhuma ação registrada | — | — | — |")

    return "\n".join(lines) + "\n"
