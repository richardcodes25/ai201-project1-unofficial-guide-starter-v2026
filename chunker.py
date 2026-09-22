"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

import re
from dataclasses import dataclass

import config
from ingest import Document

# First paragraph is a title if it's a single short line. Measured titles in
# campus_life are 10–47 characters; 60 leaves room without swallowing a body
# sentence like "Expect 4 hours a week outside class."
_TITLE_MAX = 60


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def _title_of(paragraphs: list[str]) -> str | None:
    """The first block is a title when it's one short line, not a body paragraph."""
    first = paragraphs[0]
    if "\n" not in first and len(first) <= _TITLE_MAX:
        return first
    return None


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p]


def _fit_size(text: str, title: str | None) -> list[str]:
    """Keep a paragraph as one piece unless it overruns CHUNK_SIZE.

    The only time this fires on campus_life is a safety net: the longest body
    paragraph I measured was 373 characters. If one ever exceeds the cap, cut
    on sentence ends and repeat the title plus CHUNK_OVERLAP of the previous
    sentence so a number isn't stranded without its subject.
    """
    if len(text) <= config.CHUNK_SIZE:
        return [text]

    body = text
    prefix = ""
    if title and text.startswith(title):
        prefix = title
        body = text[len(title) :].lstrip()

    sentences = _split_sentences(body)
    if len(sentences) <= 1:
        return [text]

    pieces: list[str] = []
    current = ""
    for sentence in sentences:
        candidate = f"{current} {sentence}".strip() if current else sentence
        wrapped = f"{prefix}\n\n{candidate}".strip() if prefix else candidate
        if current and len(wrapped) > config.CHUNK_SIZE:
            pieces.append(f"{prefix}\n\n{current}".strip() if prefix else current)
            carry = current[-config.CHUNK_OVERLAP :].strip() if config.CHUNK_OVERLAP else ""
            current = f"{carry} {sentence}".strip() if carry else sentence
        else:
            current = candidate
    if current:
        pieces.append(f"{prefix}\n\n{current}".strip() if prefix else current)
    return pieces or [text]


def _paragraph_chunks(text: str) -> list[str]:
    """One chunk per body paragraph, with the post's title repeated on each.

    campus_life posts hold two or three thoughts (hours vs exams, rooms vs
    laundry). A whole-post chunk buries the useful sentence. A title-only
    chunk answers nothing. Repeating the title is the overlap.
    """
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if not paragraphs:
        return [text.strip()] if text.strip() else []

    title = _title_of(paragraphs)
    body = paragraphs[1:] if title else paragraphs
    if not body:
        return [title] if title else []

    chunks: list[str] = []
    for paragraph in body:
        piece = f"{title}\n\n{paragraph}" if title else paragraph
        chunks.extend(_fit_size(piece, title))
    return chunks


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Split campus_life posts on paragraph boundaries, not character windows.

    Each body paragraph becomes its own chunk, with the post title prepended
    so a fact like "90 square feet" still names Calder Annexe. produced_by
    is this function so the README can cite it.
    """
    chunks: list[Chunk] = []
    for doc in documents:
        for index, piece in enumerate(_paragraph_chunks(doc.text)):
            chunks.append(
                Chunk(
                    text=piece,
                    source=doc.source,
                    index=index,
                    produced_by="chunker.py::split_documents",
                )
            )
    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
