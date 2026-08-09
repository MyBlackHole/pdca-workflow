"""service 层测试（seam: tests/test_service.py -> app/service.py）。

验证业务校验规则、404 语义以及与 storage 的集成。
"""

from __future__ import annotations

import os
import tempfile

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.service import TodoNotFoundError, TodoService, TodoValidationError
from app.storage import Base


@pytest.fixture()
def service():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    engine = create_engine(f"sqlite:///{tmp.name}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    s = Session()
    yield TodoService(s)
    s.close()
    os.unlink(tmp.name)


def test_create_validates_trimmed_title(service):
    todo = service.create("  写代码  ")
    assert todo.title == "写代码"


def test_create_rejects_empty_title(service):
    with pytest.raises(TodoValidationError):
        service.create("   ")


def test_create_rejects_oversized_title(service):
    with pytest.raises(TodoValidationError):
        service.create("长" * 201)


def test_get_returns_existing(service):
    todo = service.create("查我")
    assert service.get(todo.id).title == "查我"


def test_get_missing_raises_not_found(service):
    with pytest.raises(TodoNotFoundError):
        service.get(9999)


def test_update_flip_completed(service):
    todo = service.create("做一件事")
    service.update(todo.id, completed=True)
    assert service.get(todo.id).completed is True


def test_update_invalid_title_rejected(service):
    todo = service.create("有效标题")
    with pytest.raises(TodoValidationError):
        service.update(todo.id, title="")
    assert service.get(todo.id).title == "有效标题"


def test_delete_removes(service):
    todo = service.create("删除我")
    service.delete(todo.id)
    with pytest.raises(TodoNotFoundError):
        service.get(todo.id)


def test_delete_missing_raises_not_found(service):
    with pytest.raises(TodoNotFoundError):
        service.delete(9999)


def test_list_returns_created(service):
    service.create("一")
    service.create("二")
    assert len(service.list()) == 2
