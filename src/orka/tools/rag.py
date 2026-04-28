from orka.rag.vectorstore import get_db


def search(query: str, k: int = 5):
    collection = get_db()

    results = collection.query(query_texts=[query], n_results=k)

    docs = results["documents"][0]
    metadata = results["metadatas"][0]

    return [
        {
            "content": doc,
            "path": meta.get("path", "unknown"),
        }
        for doc, meta in zip(docs, metadata)
    ]
