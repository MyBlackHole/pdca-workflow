"""api/router 层：FastAPI 应用与 TODO CRUD 端点。

测试接缝 seam: tests/test_api.py -> app/main.py
依赖 service 层业务逻辑。
"""

from __future__ import annotations

from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .service import TodoNotFoundError, TodoService, TodoValidationError
from .storage import create_session

app = FastAPI(title="Todo FastAPI 验证应用", version="0.1.0")


def make_db_session():
    """Session 工厂，测试可 monkeypatch 替换为临时 DB。"""
    return create_session()


class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    completed: Optional[bool] = None


class TodoOut(BaseModel):
    id: int
    title: str
    completed: bool

    model_config = {"from_attributes": True}


def get_db() -> Session:
    session = make_db_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _service(db: Session) -> TodoService:
    return TodoService(db)


@app.post("/todos", response_model=TodoOut, status_code=201)
def create_todo_endpoint(body: TodoCreate, db: Session = Depends(get_db)):
    try:
        return _service(db).create(body.title)
    except TodoValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/todos", response_model=list[TodoOut])
def list_todos_endpoint(db: Session = Depends(get_db)):
    return _service(db).list()


@app.get("/todos/{todo_id}", response_model=TodoOut)
def get_todo_endpoint(todo_id: int, db: Session = Depends(get_db)):
    try:
        return _service(db).get(todo_id)
    except TodoNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.put("/todos/{todo_id}", response_model=TodoOut)
def update_todo_endpoint(todo_id: int, body: TodoUpdate, db: Session = Depends(get_db)):
    try:
        return _service(db).update(todo_id, title=body.title, completed=body.completed)
    except TodoNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except TodoValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo_endpoint(todo_id: int, db: Session = Depends(get_db)):
    try:
        _service(db).delete(todo_id)
    except TodoNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
