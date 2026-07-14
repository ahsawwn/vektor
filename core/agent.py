from sqlmodel import Session, col, select

from config import OLLAMA_HOST, OLLAMA_MODEL
from database.connection import engine
from database.models import ConversationLog, UserPreference
from memory.vector_store import VectorMemory

try:
    import ollama
except ImportError:
    ollama = None


def _get_chronological_context(session: Session, limit: int = 5) -> list[ConversationLog]:
    stmt = (
        select(ConversationLog)
        .order_by(col(ConversationLog.timestamp).desc())
        .limit(limit)
    )
    results = session.exec(stmt).all()
    return list(reversed(results))


def _get_user_preferences(session: Session) -> dict[str, str]:
    stmt = select(UserPreference)
    results = session.exec(stmt).all()
    return {p.key: p.value for p in results}


def _format_conversation_context(messages: list[ConversationLog]) -> str:
    if not messages:
        return ""
    lines = []
    for msg in messages:
        label = "User" if msg.role == "user" else "Assistant"
        lines.append(f"[{label}]: {msg.content}")
    return "\n".join(lines)


def _format_memory_context(memories) -> str:
    docs = memories.get("documents", [[]])[0]
    if not docs:
        return ""
    lines = [f"- {d}" for d in docs]
    return "Related past context:\n" + "\n".join(lines)


def _preferences_to_text(prefs: dict[str, str]) -> str:
    if not prefs:
        return ""
    lines = [f"  {k}: {v}" for k, v in prefs.items()]
    return "User preferences:\n" + "\n".join(lines)


class VektorAgent:
    def __init__(
        self,
        model: str = OLLAMA_MODEL,
        host: str = OLLAMA_HOST,
    ) -> None:
        if ollama is None:
            msg = (
                "ollama package is not installed. "
                "Run: pip install ollama"
            )
            raise RuntimeError(msg)
        self.model = model
        self.client = ollama.Client(host=host)
        self.memory = VectorMemory()

    def chat(self, user_input: str) -> str:
        with Session(engine) as session:
            prefs = _get_user_preferences(session)
            recent = _get_chronological_context(session)
            memories = self.memory.query_memories(user_input)

        pref_text = _preferences_to_text(prefs)
        conv_text = _format_conversation_context(recent)
        mem_text = _format_memory_context(memories)

        system_parts = [
            "You are Vektor, a persistent local AI assistant.",
            "You are technical, concise, and precise.",
            "Respond with minimal fluff — short answers, dense information, code when appropriate.",
        ]
        if pref_text:
            system_parts.append(pref_text)
        if mem_text:
            system_parts.append(mem_text)

        system_prompt = "\n\n".join(system_parts)

        messages = [{"role": "system", "content": system_prompt}]

        if conv_text:
            messages.append(
                {"role": "user", "content": f"Recent conversation:\n{conv_text}"}
            )

        messages.append({"role": "user", "content": user_input})

        response = self.client.chat(model=self.model, messages=messages)
        reply = response["message"]["content"]

        with Session(engine) as session:
            session.add(ConversationLog(role="user", content=user_input))
            session.add(ConversationLog(role="assistant", content=reply))
            session.commit()
            last_id = _last_conversation_id(session)

        self.memory.add_memory(last_id - 1, f"User: {user_input}")
        self.memory.add_memory(last_id, f"Assistant: {reply}")

        return reply


def _last_conversation_id(session: Session) -> int:
    stmt = select(ConversationLog.id).order_by(ConversationLog.id.desc()).limit(1)
    result = session.exec(stmt).one_or_none()
    return result or 0
