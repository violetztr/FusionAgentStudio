from app.services.ingestion.cleaning import clean_text


def test_clean_text_collapses_blank_lines_and_spaces():
    raw = "Title\n\n\n  line   with   spaces  \n"

    cleaned = clean_text(raw)

    assert cleaned == "Title\n\nline with spaces"
