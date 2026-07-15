from sqlmodel import Session, col, select

from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL
from database.connection import engine
from database.models import ConversationLog, UserPreference
from memory.vector_store import VectorMemory


class VektorAgent:
    def __init__(self, model: str = OPENROUTER_MODEL) -> None:
        self.model = model
        self.memory = VectorMemory()

    def chat(self, user_input: str) -> str:
        import httpx

        with Session(engine) as session:
            prefs = _get_user_preferences(session)
            recent = _get_chronological_context(session)
            memories = self.memory.query_memories(user_input)

        system_parts = [
            "You are Vektor, a persistent local AI assistant.",
            "You are technical, concise, and precise. Short answers.",
        ]
        if prefs:
            system_parts.append("User preferences:\n" + "\n".join(f"  {k}: {v}" for k, v in prefs.items()))
        docs = memories.get("documents", [[]])[0]
        if docs:
            system_parts.append("Related context:\n" + "\n".join(f"- {d}" for d in docs))

        messages = [{"role": "system", "content": "\n\n".join(system_parts)}]
        for msg in recent:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": user_input})

        resp = httpx.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            json={"model": self.model, "messages": messages},
            timeout=60,
        )
        resp.raise_for_status()
        reply = resp.json()["choices"][0]["message"]["content"]

        with Session(engine) as session:
            session.add(ConversationLog(role="user", content=user_input))
            session.add(ConversationLog(role="assistant", content=reply))
            session.commit()
            last_id = _last_conversation_id(session)

        self.memory.add_memory(last_id - 1, f"User: {user_input}")
        self.memory.add_memory(last_id, f"Assistant: {reply}")

        return reply


def _get_chronological_context(session: Session, limit: int = 5) -> list[ConversationLog]:
    stmt = select(ConversationLog).order_by(col(ConversationLog.timestamp).desc()).limit(limit)
    results = session.exec(stmt).all()
    return list(reversed(results))


def _get_user_preferences(session: Session) -> dict[str, str]:
    return {p.key: p.value for p in session.exec(select(UserPreference)).all()}


def _last_conversation_id(session: Session) -> int:
    result = session.exec(select(ConversationLog.id).order_by(ConversationLog.id.desc()).limit(1)).one_or_none()
    return result or 0
