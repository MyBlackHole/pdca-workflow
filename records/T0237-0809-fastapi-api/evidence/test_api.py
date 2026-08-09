"""api/router 层集成测试（seam: tests/test_api.py -> app/main.py）。

用 TestClient 走真实 HTTP 请求链路，验证全部 CRUD 端点。
"""

from __future__ import annotations

import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.storage import Base


@pytest.fixture()
def client(monkeypatch):
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    engine = create_engine(f"sqlite:///{tmp.name}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    import app.main as main_module

    def _make_session():
        return Session()

    monkeypatch.setattr(main_module, "make_db_session", _make_session)
    yield TestClient(app)
    os.unlink(tmp.name)


def test_create_todo(client):
    resp = client.post("/todos", json={"title": "买牛奶"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "买牛奶"
    assert body["completed"] is False
    assert body["id"] > 0


def test_create_rejects_empty_title(client):
    resp = client.post("/todos", json={"title": ""})
    assert resp.status_code in (422, 422)


def test_list_todos(client):
    client.post("/todos", json={"title": "一"})
    client.post("/todos", json={"title": "二"})
    resp = client.get("/todos")
    assert resp.status_code == 200
    assert [t["title"] for t in resp.json()] == ["一", "二"]


def test_get_todo(client):
    created = client.post("/todos", json={"title": "查我"}).json()
    resp = client.get(f"/todos/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "查我"


def test_get_missing_returns_404(client):
    resp = client.get("/todos/9999")
    assert resp.status_code == 404


def test_update_completed(client):
    created = client.post("/todos", json={"title": "做"}).json()
    resp = client.put(f"/todos/{created['id']}", json={"completed": True})
    assert resp.status_code == 200
    assert resp.json()["completed"] is True


def test_update_title(client):
    created = client.post("/todos", json={"title": "旧"}).json()
    resp = client.put(f"/todos/{created['id']}", json={"title": "新"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "新"


def test_update_missing_returns_404(client):
    resp = client.put("/todos/9999", json={"title": "x"})
    assert resp.status_code == 404


def test_delete_todo(client):
    created = client.post("/todos", json={"title": "删"}).json()
    resp = client.delete(f"/todos/{created['id']}")
    assert resp.status_code == 204
    assert client.get(f"/todos/{created['id']}").status_code == 404


def test_delete_missing_returns_404(client):
    resp = client.delete("/todos/9999")
    assert resp.status_code == 404


def test_full_workflow(client):
    created = client.post("/todos", json={"title": "全流程"}).json()
    tid = created["id"]
    client.put(f"/todos/{tid}", json={"completed": True})
    assert client.get(f"/todos/{tid}").json()["completed"] is True
    client.delete(f"/todos/{tid}")
    assert client.get(f"/todos/{tid}").status_code == 404
