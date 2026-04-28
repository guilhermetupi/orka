from pathlib import Path
from typing import Collection


def chunk_file(
    path: Path, chunk_size: int = 500, overlap: int = 50
) -> list[dict[str, Collection[str]]]:
    try:
        text = path.read_text(errors="ignore")
    except Exception:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        chunks.append(
            {
                "content": chunk,
                "metadata": {
                    "path": str(path),
                    "filename": path.name,
                },
            }
        )

        start += chunk_size - overlap

    return chunks
