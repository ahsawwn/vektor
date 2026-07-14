from collections.abc import Generator
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

from config import SQLITE_PATH


def get_engine(db_path: Path | str = SQLITE_PATH):
    url = f"sqlite:///{db_path}"
    connect_args = {"check_same_thread": False}
    return create_engine(url, connect_args=connect_args, echo=False)


engine = get_engine()


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
