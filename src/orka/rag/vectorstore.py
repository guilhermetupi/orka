import chromadb
from chromadb.utils import embedding_functions


def get_db():
    client = chromadb.PersistentClient(path=".orka/chroma")

    embedding = embedding_functions.OllamaEmbeddingFunction(
        model_name="mxbai-embed-large",
        url="http://localhost:11434",
    )

    collection = client.get_or_create_collection(
        name="orka",
        embedding_function=embedding,
    )

    return collection
