import pytest

from blog_generator.agent import _coerce_outline, _coerce_sections, _parse_llm_json


def test_parse_llm_json_accepts_plain_json() -> None:
    assert _parse_llm_json('{"title": "Test", "outline": [], "article": "Body"}')["title"] == "Test"


def test_parse_llm_json_accepts_fenced_json() -> None:
    parsed = _parse_llm_json('```json\n{"title": "Test"}\n```')

    assert parsed["title"] == "Test"


def test_parse_llm_json_extracts_json_from_extra_text() -> None:
    parsed = _parse_llm_json('Here is the JSON:\n{"title": "Test"}\nDone.')

    assert parsed["title"] == "Test"


def test_parse_llm_json_rejects_invalid_json() -> None:
    with pytest.raises(RuntimeError):
        _parse_llm_json("not-json")


def test_coerce_outline_from_lines() -> None:
    assert _coerce_outline("- Intro\n- Details") == ["Intro", "Details"]


def test_coerce_sections_accepts_heading_and_body() -> None:
    sections = _coerce_sections([{"heading": "Intro", "body": "Body text"}])

    assert sections[0].heading == "Intro"
    assert sections[0].body == "Body text"
