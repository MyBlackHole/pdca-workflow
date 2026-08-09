"""service 层：TODO 业务逻辑与校验。

测试接缝 seam: tests/test_service.py -> app/service.py
依赖 storage 层数据访问。
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from .storage import Todo, create_todo, delete_todo, get_todo, list_todos, update_todo


class TodoNotFoundError(LookupError):
    """请求的 TODO 不存在。"""


class TodoValidationError(ValueError):
    """TODO 业务校验失败。"""


MAX_TITLE_LEN = 200


class TodoService:
    """TODO 业务服务：封装校验规则并委托 storage 层。"""

    def __init__(self, session: Session) -> None:
        self._session = session

    def _validate_title(self, title: str) -> str:
        title = title.strip()
        if not title:
            raise TodoValidationError("title 不能为空")
        if len(title) > MAX_TITLE_LEN:
            raise TodoValidationError(f"title 超长（最多 {MAX_TITLE_LEN} 字符）")
        return title

    def create(self, title: str) -> Todo:
        clean = self._validate_title(title)
        return create_todo(self._session, clean)

    def get(self, todo_id: int) -> Todo:
        todo = get_todo(self._session, todo_id)
        if todo is None:
            raise TodoNotFoundError(f"TODO {todo_id} 不存在")
        return todo

    def list(self) -> list[Todo]:
        return list_todos(self._session)

    def update(self, todo_id: int, title: Optional[str] = None,
               completed: Optional[bool] = None) -> Todo:
        todo = self.get(todo_id)
        if title is not None:
            clean = self._validate_title(title)
            todo = update_todo(self._session, todo, title=clean)
        if completed is not None:
            todo = update_todo(self._session, todo, completed=completed)
        return todo

    def delete(self, todo_id: int) -> None:
        todo = self.get(todo_id)
        delete_todo(self._session, todo)
