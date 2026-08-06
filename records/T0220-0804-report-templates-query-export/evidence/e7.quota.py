"""Report DB 读池逻辑配额（§8.4/§8.5）。

Report DB 读池共 20 条连接，按用途拆分逻辑配额：
  - Query  最多 16 条（页面查询）
  - Export 最多 2 条（CSV/PDF 导出）
  - Metric 最多 2 条（健康指标）

配额耗尽时立即抛 ExportBusyError / QueryBusyError（429），不排队、不借用写池。
本模块只做信号量协调；实际的 `statement_timeout`/`lock_timeout` 由 Read Adapter 设置。
"""

from __future__ import annotations

import threading

from .errors import ExportBusyError, QueryBusyError


class ReadPoolQuota:
    """读池逻辑配额：三个独立的 BoundedSemaphore，区分 Query/Export/Metric。"""

    def __init__(
        self,
        query: int = 16,
        export: int = 2,
        metric: int = 2,
    ) -> None:
        self._query = threading.BoundedSemaphore(max(query, 1))
        self._export = threading.BoundedSemaphore(max(export, 1))
        self._metric = threading.BoundedSemaphore(max(metric, 1))

    # ---------- Query ----------

    def query_guard(self):
        """Query 配额上下文管理器；耗尽抛 QUERY_BUSY。"""
        return _SemaphoreGuard(self._query, QueryBusyError, "查询配额已满")

    # ---------- Export ----------

    def export_guard(self):
        """Export 配额上下文管理器；耗尽抛 EXPORT_BUSY。"""
        return _SemaphoreGuard(self._export, ExportBusyError, "导出配额已满")

    # ---------- Metric ----------

    def metric_guard(self):
        """Metric 配额上下文管理器；耗尽抛 MetricBusy。"""
        return _SemaphoreGuard(self._metric, QueryBusyError, "指标读取配额已满")


class _SemaphoreGuard:
    """基于 BoundedSemaphore 的上下文管理器：非阻塞 acquire，失败抛 busy 错误。"""

    def __init__(self, sem: threading.BoundedSemaphore, error_cls, message: str) -> None:
        self._sem = sem
        self._error_cls = error_cls
        self._message = message
        self._acquired = sem.acquire(blocking=False)
        if not self._acquired:
            raise error_cls(message)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._acquired:
            self._sem.release()
            self._acquired = False
        return False

    def release(self) -> None:
        if self._acquired:
            self._sem.release()
            self._acquired = False
