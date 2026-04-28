from pathlib import Path
from orka.rag.chunker import chunk_file
from orka.rag.vectorstore import get_db
import uuid

BATCH_SIZE = 32


def index_project(root: str = "."):
    collection = get_db()
    files = list(Path(root).rglob("**/*.py"))
    all_chunks = []

    for file in files:
        if should_ignore(file):
            continue

        if file.stat().st_size > 200_000:  # 200kb
            continue

        chunks = chunk_file(file)
        all_chunks.extend(chunks)

    if not all_chunks:
        return

    for i in range(0, len(all_chunks), BATCH_SIZE):
        batch = all_chunks[i : i + BATCH_SIZE]

        collection.add(
            documents=[chunk["content"] for chunk in batch],
            metadatas=[chunk["metadata"] for chunk in batch],
            ids=[str(uuid.uuid4()) for _ in batch],
        )

        print(f"Indexed batch {i} → {i + len(batch)}")

def should_ignore(path: Path) -> bool:
    ignore = [".venv", ".git", "__pycache__", "node_modules", ".mypy_cache"]
    return any(part in path.parts for part in ignore)