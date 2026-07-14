from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class UserPreference(SQLModel, table=True):
    __tablename__ = "user_preferences"

    id: int | None = Field(default=None, primary_key=True)
    key: str = Field(unique=True, index=True)
    value: str
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class ConversationLog(SQLModel, table=True):
    __tablename__ = "conversation_logs"

    id: int | None = Field(default=None, primary_key=True)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    role: str
    content: str
