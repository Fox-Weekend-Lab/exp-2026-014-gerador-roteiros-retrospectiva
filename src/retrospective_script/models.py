"""Modelos e validação do contrato de entrada da retrospectiva."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any


VALID_STATUSES = frozenset({"open", "discussed", "resolved"})


class ValidationError(ValueError):
    """Indica que os dados da retrospectiva não respeitam o contrato."""


@dataclass(frozen=True)
class Action:
    description: str
    owner: str | None
    due_date: str | None


@dataclass(frozen=True)
class RetrospectiveItem:
    theme: str
    description: str
    status: str
    decision: str | None
    action: Action | None


@dataclass(frozen=True)
class Retrospective:
    meeting_title: str
    meeting_date: str
    items: tuple[RetrospectiveItem, ...]


def _error(path: str, message: str) -> ValidationError:
    return ValidationError(f"{path}: {message}.")


def _required_text(value: Any, path: str) -> str:
    if not isinstance(value, str):
        raise _error(path, "deve ser um texto")
    normalized = value.strip()
    if not normalized:
        raise _error(path, "não pode estar vazio")
    return normalized


def _optional_text(value: Any, path: str) -> str | None:
    if value is None:
        return None
    return _required_text(value, path)


def _iso_date(value: Any, path: str) -> str:
    text = _required_text(value, path)
    if len(text) != 10 or text[4] != "-" or text[7] != "-":
        raise _error(path, "deve usar o formato de data ISO YYYY-MM-DD")
    try:
        date.fromisoformat(text)
    except ValueError as exc:
        raise _error(path, "deve conter uma data ISO válida YYYY-MM-DD") from exc
    return text


def _parse_action(value: Any, path: str) -> Action:
    if not isinstance(value, dict):
        raise _error(path, "deve ser um objeto")
    if "description" not in value:
        raise _error(f"{path}.description", "é obrigatório")

    owner = _optional_text(value.get("owner"), f"{path}.owner") if "owner" in value else None
    due_date = _iso_date(value["due_date"], f"{path}.due_date") if "due_date" in value else None
    return Action(
        description=_required_text(value["description"], f"{path}.description"),
        owner=owner,
        due_date=due_date,
    )


def _parse_item(value: Any, index: int) -> RetrospectiveItem:
    path = f"items[{index}]"
    if not isinstance(value, dict):
        raise _error(path, "deve ser um objeto")

    for field in ("theme", "description", "status"):
        if field not in value:
            raise _error(f"{path}.{field}", "é obrigatório")

    status = _required_text(value["status"], f"{path}.status")
    if status not in VALID_STATUSES:
        allowed = ", ".join(sorted(VALID_STATUSES))
        raise _error(f"{path}.status", f"deve ser um de: {allowed}")

    decision = _optional_text(value["decision"], f"{path}.decision") if "decision" in value else None
    action = _parse_action(value["action"], f"{path}.action") if "action" in value else None
    return RetrospectiveItem(
        theme=_required_text(value["theme"], f"{path}.theme"),
        description=_required_text(value["description"], f"{path}.description"),
        status=status,
        decision=decision,
        action=action,
    )


def parse_retrospective(data: Any) -> Retrospective:
    """Valida dados JSON decodificados e produz um modelo imutável."""
    if not isinstance(data, dict):
        raise _error("raiz", "deve ser um objeto JSON")

    for field in ("meeting_title", "meeting_date", "items"):
        if field not in data:
            raise _error(field, "é obrigatório")

    items_data = data["items"]
    if not isinstance(items_data, list):
        raise _error("items", "deve ser uma lista")
    if not items_data:
        raise _error("items", "não pode estar vazia")

    return Retrospective(
        meeting_title=_required_text(data["meeting_title"], "meeting_title"),
        meeting_date=_iso_date(data["meeting_date"], "meeting_date"),
        items=tuple(_parse_item(item, index) for index, item in enumerate(items_data)),
    )
