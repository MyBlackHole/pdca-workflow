"""storage 层：SQLAlchemy TODO 模型 + 数据访问。

测试接缝 seam: tests/test_storage.py -> app/storage.py
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator, Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.sql import func

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///todo.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    completed = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


def create_session() -> Session:
    """创建独立 Session（测试与请求共用入口）。"""
    Base.metadata.create_all(bind=engine)
    return SessionLocal()


@contextmanager
def get_session() -> Iterator[Session]:
    """上下文管理器，自动提交/回滚/关闭。"""
    session = create_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_todo(session: Session, title: str) -> Todo:
    todo = Todo(title=title, completed=False)
    session.add(todo)
    session.flush()
    return todo


def get_todo(session: Session, todo_id: int) -> Optional[Todo]:
    return session.get(Todo, todo_id)


def list_todos(session: Session) -> list[Todo]:
    return session.query(Todo).order_by(Todo.id).all()


def update_todo(session: Session, todo: Todo, title: Optional[str] = None,
                completed: Optional[bool] = None) -> Todo:
    if title is not None:
        todo.title = title
    if completed is not None:
        todo.completed = completed
    session.flush()
    return todo


def delete_todo(session: Session, todo: Todo) -> None:
    session.delete(todo)
    session.flush()
