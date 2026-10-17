from __future__ import annotations

import copy

import pytest

import retrospective_script as public_api
from retrospective_script.models import Action, Retrospective, RetrospectiveItem, ValidationError, parse_retrospective


def valid_data() -> dict:
    return {
        "meeting_title": "  Retrospectiva Sprint 12  ",
        "meeting_date": "2024-06-14",
        "items": [
            {
                "theme": "  Processo ",
                "description": "  Refinar os critérios de aceite. ",
                "status": "open",
                "decision": "  Revisar no planejamento. ",
                "action": {
                    "description": "  Criar checklist. ",
                    "owner": "  Ana ",
                    "due_date": "2024-06-20",
                },
            }
        ],
    }


def test_parse_retrospective_normalizes_data_and_exposes_public_api() -> None:
    retrospective = parse_retrospective(valid_data())

    expected_action = Action(description="Criar checklist.", owner="Ana", due_date="2024-06-20")
    expected_item = RetrospectiveItem(
        theme="Processo",
        description="Refinar os critérios de aceite.",
        status="open",
        decision="Revisar no planejamento.",
        action=expected_action,
    )
    assert retrospective == Retrospective(
        meeting_title="Retrospectiva Sprint 12",
        meeting_date="2024-06-14",
        items=(expected_item,),
    )
    assert public_api.parse_retrospective is parse_retrospective
    assert public_api.Action is Action
    assert "render_markdown" in public_api.__all__


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda data: data.pop("meeting_title"), "meeting_title: é obrigatório"),
        (lambda data: data.__setitem__("meeting_title", "   "), "meeting_title: não pode estar vazio"),
        (lambda data: data["items"][0].__setitem__("theme", ""), "items[0].theme: não pode estar vazio"),
        (lambda data: data["items"][0].pop("description"), "items[0].description: é obrigatório"),
        (lambda data: data["items"][0].__setitem__("status", "blocked"), "items[0].status: deve ser um de: discussed, open, resolved"),
        (lambda data: data.__setitem__("meeting_date", "14/06/2024"), "meeting_date: deve usar o formato de data ISO YYYY-MM-DD"),
        (lambda data: data["items"][0]["action"].__setitem__("due_date", "2024-02-30"), "items[0].action.due_date: deve conter uma data ISO válida YYYY-MM-DD"),
    ],
)
def test_parse_retrospective_rejects_invalid_contract_values(mutate, message: str) -> None:
    data = copy.deepcopy(valid_data())
    mutate(data)

    with pytest.raises(ValidationError) as error:
        parse_retrospective(data)

    assert str(error.value) == f"{message}."


def test_parse_retrospective_rejects_invalid_root_and_empty_items() -> None:
    with pytest.raises(ValidationError, match="raiz: deve ser um objeto JSON"):
        parse_retrospective([])

    data = valid_data()
    data["items"] = []
    with pytest.raises(ValidationError, match="items: não pode estar vazia"):
        parse_retrospective(data)
