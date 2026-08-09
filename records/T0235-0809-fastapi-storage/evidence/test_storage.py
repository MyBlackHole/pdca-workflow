"""storage 层测试（seam: tests/test_storage.py -> app/storage.py）。

用临时 SQLite 文件隔离，验证 CRUD round-trip 与数据一致性。
"""

from __future__ import annotations

import os
import tempfile

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.storage import Base, Todo, create_todo, delete_todo, get_todo, list_todos, update_todo


@pytest.fixture()
def session():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    engine = create_engine(f"sqlite:///{tmp.name}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    s = Session()
    yield s
    s.close()
    os.unlink(tmp.name)


def test_create_and_get_roundtrip(session):
    todo = create_todo(session, "写测试")
    assert todo.id is not None
    assert todo.completed is False
    got = get_todo(session, todo.id)
    assert got is not None
    assert got.title == "写测试"


def test_list_returns_ordered(session):
    create_todo(session, "第一个")
    create_todo(session, "第二个")
    todos = list_todos(session)
    assert [t.title for t in todos] == ["第一个", "第二个"]


def test_update_title_and_completed(session):
    todo = create_todo(session, "旧标题")
    updated = update_todo(session, todo, title="新标题", completed=True)
    assert updated.title == "新标题"
    assert updated.completed is True
    assert get_todo(session, todo.id).completed is True


def test_update_partial_keeps_other_fields(session):
    todo = create_todo(session, "标题")
    update_todo(session, todo, completed=True)
    assert todo.title == "标题"
    assert todo.completed is True


def test_delete_removes_record(session):
    todo = create_todo(session, "待删")
    delete_todo(session, todo)
    assert get_todo(session, todo.id) is None


def test_get_missing_returns_none(session):
    assert get_todo(session, 9999) is None
