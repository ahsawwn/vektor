from sqlmodel import Session, col, select

from config import SQLITE_PATH
from database.connection import engine, init_db
from database.models import ConversationLog, UserPreference

init_db()


def get_preferences() -> dict[str, str]:
    with Session(engine) as sess:
        rows = sess.exec(select(UserPreference)).all()
    return {p.key: p.value for p in rows}


def set_preference(key: str, value: str) -> None:
    with Session(engine) as sess:
        stmt = select(UserPreference).where(UserPreference.key == key)
        existing = sess.exec(stmt).one_or_none()
        if existing:
            existing.value = value
        else:
            sess.add(UserPreference(key=key, value=value))
        sess.commit()


def get_recent_messages(limit: int = 10) -> list[dict]:
    with Session(engine) as sess:
        stmt = (
            select(ConversationLog)
            .order_by(col(ConversationLog.timestamp).desc())
            .limit(limit)
        )
        rows = sess.exec(stmt).all()
    return [
        {"role": r.role, "content": r.content, "id": r.id}
        for r in reversed(rows)
    ]


def save_message(role: str, content: str) -> int:
    with Session(engine) as sess:
        msg = ConversationLog(role=role, content=content)
        sess.add(msg)
        sess.commit()
        sess.refresh(msg)
    return msg.id


def delete_all_conversations() -> None:
    with Session(engine) as sess:
        for r in sess.exec(select(ConversationLog)).all():
            sess.delete(r)
        sess.commit()
