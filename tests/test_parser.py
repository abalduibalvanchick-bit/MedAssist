from pathlib import Path

from src.markdown_parser import parse_markdown_file


def test_parse_markdown_card():
    path = Path("kb/diag/symptoms/diag_symptom_chest_pain.md")
    card = parse_markdown_file(path)

    assert card.id == "DIAG-SYMPTOM-002"
    assert card.title == "Боль в груди"
    assert card.category == "symptom"
    assert "chest_pain" in card.tags
    assert "Боль в груди" in card.content


def test_parsed_card_is_schema_v2():
    card = parse_markdown_file(Path("kb/diag/symptoms/diag_symptom_chest_pain.md"))
    assert card.schema_version == 2
    assert "related" not in card.metadata
    assert card.related  # вычисляется из relations
