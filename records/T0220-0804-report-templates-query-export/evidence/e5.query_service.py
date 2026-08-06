"""查询编排（§8.3/§8.4：QuerySpec、权限收敛、Keyset 分页、多域归并、data_state）。

- 服务端从模板推导 resolved_sort/列集合/Handler；请求不能指定表/列/排序/SQL。
- 单域任务明细按 (task_time DESC, backup_domain_id DESC, task_run_key DESC)
  Keyset 查询；多域用 DOMAIN_TOPN_MERGE 归并，禁止多域全局 OFFSET/无界全局排序。
- data_state 区分 NO_MATCH / INSUFFICIENT_COLLECTION_COVERAGE / COVERED。
"""

from __future__ import annotations

from typing import Any, Optional

from .errors import QueryTimeoutError, ReportError
from .query_handlers import ReportQueryHandlerRegistry
from .template_registry import Template, TemplateRegistry

# 任务类模板按 topic 判定覆盖
_TOPIC_OF_TEMPLATE = {
    "data_source_count": "resource",
    "data_source_inventory": "resource",
    "backup_plan_count": "resource",
    "backup_plan_inventory": "resource",
    "backup_success_rate": "task",
    "backup_task_count": "task",
    "backup_task_count_trend": "task",
    "backup_data_size": "task",
    "backup_data_size_trend": "task",
    "backup_success_detail": "task",
    "backup_failure_detail": "task",
    "mount_success_rate": "task",
    "mount_success_detail": "task",
    "mount_failure_detail": "task",
    "storage_worker_usage": "capacity",
    "storage_capacity_trend": "capacity",
}


class QueryResult:
    def __init__(
        self,
        records: list[dict],
        columns: list[str],
        next_cursor: Optional[str],
        has_more: bool,
        data_state: str,
    ) -> None:
        self.records = records
        self.columns = columns
        self.next_cursor = next_cursor
        self.has_more = has_more
        self.data_state = data_state

    def to_dict(self) -> dict:
        return {
            "records": self.records,
            "columns": self.columns,
            "next_cursor": self.next_cursor,
            "has_more": self.has_more,
            "data_state": self.data_state,
        }


class QueryService:
    def __init__(
        self,
        factory,
        registry: TemplateRegistry,
        handlers: ReportQueryHandlerRegistry,
        *,
        statement_timeout_ms: int = 2000,
    ) -> None:
        self._factory = factory
        self._registry = registry
        self._handlers = handlers
        self._statement_timeout_ms = statement_timeout_ms

    # ---------- 域 ----------

    def resolve_domains(self, domain_ids) -> list[int]:
        """domain_ids=[] → 全部活动域；否则校验存在性。"""
        if not domain_ids:
            with self._factory.read_connection() as conn:
                rows = conn.execute(
                    "SELECT id FROM rpt_backup_domain WHERE is_deleted = false "
                    "AND collection_enabled = true ORDER BY id"
                ).fetchall()
            return [r["id"] for r in rows]
        ids = [int(d) for d in domain_ids]
        with self._factory.read_connection() as conn:
            rows = conn.execute(
                "SELECT id FROM rpt_backup_domain WHERE id = ANY(%s) AND is_deleted = false",
                ([ids],),
            ).fetchall()
        found = {r["id"] for r in rows}
        unknown = [i for i in ids if i not in found]
        if unknown:
            raise ReportError(f"域不存在或已删除: {unknown}")
        return ids

    # ---------- 查询 ----------

    def query(
        self,
        template_code: str,
        *,
        filters: Optional[dict] = None,
        view: str = "table",
        page_size: int = 20,
        cursor_token: Optional[str] = None,
    ) -> QueryResult:
        tpl, merged = self._registry.resolve(template_code, filters, view, page_size)
        domain_ids = self.resolve_domains(merged.get("domain_ids") or [])
        cursor = _parse_cursor(cursor_token)

        if self._handlers.spec(tpl.query_handler).keyset_order:
            result = self._paged_keyset(tpl, merged, domain_ids, page_size, cursor)
        else:
            result = self._aggregated(tpl, merged, domain_ids, page_size, cursor)

        state = self._data_state(tpl.code, domain_ids, result.records)
        return QueryResult(
            records=result.records,
            columns=result.columns,
            next_cursor=_encode_cursor(result.next_cursor),
            has_more=result.has_more,
            data_state=state,
        )

    def _paged_keyset(self, tpl, merged, domain_ids, page_size, cursor):
        """任务明细：单域直接 Keyset；多域 K 路归并。"""
        if len(domain_ids) <= 1:
            return self._run(tpl, merged, domain_ids, page_size, cursor)
        return self._kway_merge(tpl, merged, domain_ids, page_size, cursor)

    def _run(self, tpl, merged, domain_ids, page_size, cursor):
        try:
            with self._factory.read_connection() as conn:
                _set_timeout(conn, self._statement_timeout_ms)
                return self._handlers.execute(
                    conn, tpl, domain_ids=domain_ids, filters=merged,
                    view=merged.get("view") or "table", page_size=page_size, cursor=cursor,
                )
        except ReportError:
            raise
        except Exception as exc:
            raise QueryTimeoutError(str(exc)) from exc

    def _kway_merge(self, tpl, merged, domain_ids, page_size, cursor):
        """DOMAIN_TOPN_MERGE：每域取 page_size 候选，K 路归并取全局 page_size。"""
        per_domain = page_size
        collected: list[dict] = []
        seen: set = set()
        # 多域归并用当前域集合（若 cursor 来自上一页，域集合不变）
        for did in domain_ids:
            part = self._run(tpl, merged, [did], per_domain, cursor)
            for rec in part.records:
                key = _record_key(rec, part.keyset_cols)
                if key in seen:
                    continue
                seen.add(key)
                collected.append(rec)
            if len(collected) >= page_size:
                break
        collected.sort(key=_sort_value, reverse=True)
        has_more = len(collected) > page_size
        records = collected[:page_size]
        next_cursor = None
        if has_more and records and _keyset_cols(tpl, self._handlers):
            cols = _keyset_cols(tpl, self._handlers)
            last = records[-1]
            next_cursor = {c.split(".")[-1]: last.get(c.split(".")[-1]) for c in cols}
        columns = list(_columns(tpl, self._handlers))
        return _ResultLike(records, columns, has_more, next_cursor)

    def _aggregated(self, tpl, merged, domain_ids, page_size, cursor):
        """图表聚合：全量查询（图表模板无分页）。"""
        return self._run(tpl, merged, domain_ids, 10000, cursor)

    # ---------- data_state ----------

    def _data_state(self, code: str, domain_ids: list[int], records: list) -> str:
        if records:
            return "COVERED"
        topic = _TOPIC_OF_TEMPLATE.get(code, "resource")
        covered = self._has_collection_coverage(topic, domain_ids)
        if not covered:
            return "INSUFFICIENT_COLLECTION_COVERAGE"
        return "NO_MATCH"

    def _has_collection_coverage(self, topic: str, domain_ids: list[int]) -> bool:
        if not domain_ids:
            return False
        try:
            with self._factory.read_connection() as conn:
                row = conn.execute(
                    "SELECT 1 FROM rpt_collection_task "
                    "WHERE backup_domain_id = ANY(%s) AND topic = %s AND status = 'SUCCESS' "
                    "LIMIT 1",
                    ([domain_ids], topic),
                ).fetchone()
            return row is not None
        except Exception:
            return False


# ---------------------------------------------------------------------------
# 辅助
# ---------------------------------------------------------------------------


def _parse_cursor(token: Optional[str]) -> Optional[dict]:
    if not token:
        return None
    try:
        from report_center_db.protocol.query import KeysetCursor

        c = KeysetCursor.from_token(token)
        return c.values if not c.is_empty else None
    except Exception:
        return None


def _encode_cursor(values: Optional[dict]) -> Optional[str]:
    if not values:
        return None
    from report_center_db.protocol.query import KeysetCursor

    return KeysetCursor(values=values).to_token()


def _set_timeout(conn, ms: int) -> None:
    conn.execute(f"SET statement_timeout = {int(ms)}")


def _keyset_cols(tpl: Template, handlers) -> list[str]:
    return handlers.spec(tpl.query_handler).key_cols


def _columns(tpl: Template, handlers) -> list[str]:
    return [f.name for f in handlers.spec(tpl.query_handler).fields]


def _record_key(rec: dict, key_cols: list[str]) -> tuple:
    return tuple(rec.get(c.split(".")[-1]) for c in key_cols)


def _sort_value(rec: dict) -> tuple:
    """归并排序键：按任务时间（ISO 字符串降序可比较）→ 域 → run_key。"""
    return (
        str(rec.get("task_time") or ""),
        int(rec.get("backup_domain_id") or 0),
        str(rec.get("task_run_key") or ""),
    )


class _ResultLike:
    """兼容 HandlerResult 的轻量包装。"""

    def __init__(self, records, columns, has_more, next_cursor):
        self.records = records
        self.columns = columns
        self.has_more = has_more
        self.next_cursor = next_cursor
        self.keyset_cols = []
