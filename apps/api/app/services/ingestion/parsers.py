from pathlib import Path

import docx
import fitz
import trafilatura


def parse_pdf(path: Path) -> str:
    with fitz.open(path) as doc:
        return "\n\n".join(page.get_text("text") for page in doc)


def parse_docx(path: Path) -> str:
    document = docx.Document(path)
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def parse_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def parse_markdown(path: Path) -> str:
    return parse_text(path)


def parse_web_url(url: str) -> str:
    downloaded = trafilatura.fetch_url(url)
    if downloaded is None:
        raise ValueError("Unable to fetch URL")
    extracted = trafilatura.extract(downloaded)
    if extracted is None:
        raise ValueError("Unable to extract readable text from URL")
    return extracted
