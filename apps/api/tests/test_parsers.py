from app.services.ingestion.parsers import parse_markdown, parse_text, parse_web_url


def test_parse_text_reads_utf8_file(tmp_path):
    path = tmp_path / "note.txt"
    path.write_text("Hello knowledge", encoding="utf-8")

    assert parse_text(path) == "Hello knowledge"


def test_parse_markdown_reads_raw_markdown(tmp_path):
    path = tmp_path / "guide.md"
    path.write_text("# Guide\n\nContent", encoding="utf-8")

    assert parse_markdown(path) == "# Guide\n\nContent"


def test_parse_web_url_raises_when_fetch_fails(monkeypatch):
    monkeypatch.setattr("app.services.ingestion.parsers.trafilatura.fetch_url", lambda url: None)

    try:
        parse_web_url("https://example.invalid")
    except ValueError as exc:
        assert str(exc) == "Unable to fetch URL"
    else:
        raise AssertionError("parse_web_url should raise when fetch fails")
