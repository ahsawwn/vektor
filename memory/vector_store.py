from pathlib import Path

import chromadb
from chromadb.api.types import QueryResult

from config import CHROMA_PATH


class VectorMemory:
    _collection_name = "vektor_memories"

    def __init__(self, persist_dir: Path = CHROMA_PATH) -> None:
        self.client = chromadb.PersistentClient(path=str(persist_dir))
        self.collection = self.client.get_or_create_collection(
            name=self._collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_memory(self, conversation_id: int, text: str) -> None:
        self.collection.add(
            documents=[text],
            ids=[str(conversation_id)],
            metadatas=[{"conversation_id": conversation_id}],
        )

    def query_memories(self, query: str, limit: int = 5) -> QueryResult:
        return self.collection.query(
            query_texts=[query],
            n_results=limit,
        )

    def count(self) -> int:
        return self.collection.count()

    def delete_all(self) -> None:
        self.client.delete_collection(self._collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self._collection_name,
            metadata={"hnsw:space": "cosine"},
        )
