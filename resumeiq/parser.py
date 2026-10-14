"""Extract plain text from PDF, DOCX or TXT uploads."""
import io
import re


def clean_text(text: str) -> str:
    text = text.replace("•", "-").replace("●", "-")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_text(file_bytes: bytes, filename: str) -> str:
    name = filename.lower()
    if name.endswith(".pdf"):
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(file_bytes))
        return clean_text("\n".join(page.extract_text() or "" for page in reader.pages))
    if name.endswith(".docx"):
        from docx import Document

        doc = Document(io.BytesIO(file_bytes))
        return clean_text("\n".join(p.text for p in doc.paragraphs))
    return clean_text(file_bytes.decode("utf-8", errors="ignore"))


def split_chunks(text: str, max_words: int = 60):
    """Split text into small chunks (bullets / sentences) used for evidence retrieval."""
    chunks = []
    for line in re.split(r"\n+", text):
        line = line.strip(" -\t")
        if len(line.split()) < 4:
            continue
        words = line.split()
        for i in range(0, len(words), max_words):
            chunks.append(" ".join(words[i : i + max_words]))
    return chunks
