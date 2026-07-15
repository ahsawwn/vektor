from memory.vector_store import VectorMemory as _VectorMemory

_store = _VectorMemory()


def add_memory(conversation_id: int, text: str) -> None:
    _store.add_memory(conversation_id, text)


def query_memories(query: str, limit: int = 5) -> list[str]:
    result = _store.query_memories(query, limit)
    return result.get("documents", [[]])[0]


def count() -> int:
    return _store.count()


def delete_all() -> None:
    _store.delete_all()
