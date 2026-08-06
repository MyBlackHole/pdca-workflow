"""固定查询 Handler 注册表（§8.2/§8.3）。

每个 Handler 使用服务端硬编码的固定参数化 SQL，请求只提供绑定参数值，
不能指定表/列/排序/SQL。SQL 模板的唯一来源是本模块常量表，用户输入
经筛选器校验后仅作为绑定参数插入，杜绝注入。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .errors import ReportError, TemplateValidationError
from .template_registry import Template

# ---------------------------------------------------------------------------
# 固定读模型映射（§8.2.2）：模板 code → 读表/JOIN/谓词/投影/排序。
# 这些是唯一的 SQL 模板来源，不接受任何运行时表名/列名/排序表达式。
# ---------------------------------------------------------------------------


@dataclass
class FieldSpec:
    """单列投影：逻辑列名 → SQL 表达式（白名单）。"""

    name: str
    sql: str


@dataclass
class HandlerSpec:
    """读模型映射：唯一允许的固定查询构造。"""

    code: str
    from_sql: str
    where_sql: str  # 固定谓词（不含用户值；用户值走 filters 绑定）
    keyset_order: list[str]  # Keyset 排序列 SQL
    key_cols: list[str]  # Keyset 并列键取值列
    fields: list[FieldSpec]
    group_by: Optional[list[str]] = None
    domain_col: str = "backup_domain_id"  # 域过滤物理列（多表 JOIN 时消除歧义）


def _f(name: str, sql: str) -> FieldSpec:
    return FieldSpec(name=name, sql=sql)


def _domain_name(alias: str = "d") -> str:
    return f"{alias}.domain_name"


# ----- 数据源（1/2） -----
DS_COUNT = HandlerSpec(
    code="data_source_count",
    from_sql="dim_data_source ds JOIN rpt_backup_domain d ON d.id = ds.backup_domain_id",
    where_sql="ds.is_deleted = false",
    domain_col="ds.backup_domain_id",
    keyset_order=[],
    key_cols=[],
    group_by=["ds.backup_domain_id", "ds.db_type", "d.domain_name"],
    fields=[
        _f("domain_name", _domain_name()),
        _f("db_type", "ds.db_type"),
        _f("count", "COUNT(DISTINCT ds.data_source_key)"),
    ],
)

DS_INVENTORY = HandlerSpec(
    code="data_source_inventory",
    from_sql="dim_data_source ds JOIN rpt_backup_domain d ON d.id = ds.backup_domain_id",
    where_sql="ds.is_deleted = false",
    domain_col="ds.backup_domain_id",
    keyset_order=["(d.id) ASC", "ds.data_source_key ASC"],
    key_cols=["d.domain_name", "ds.data_source_key"],
    fields=[
        _f("domain_name", _domain_name()),
        _f("data_source_name", "ds.data_source_name"),
        _f("db_type", "ds.db_type"),
        _f("data_source_type", "ds.data_source_type"),
        _f("host_address", "ds.host_address"),
        _f("service_port", "ds.service_port"),
        _f("status", "ds.status"),
    ],
)

# ----- 备份计划（3/4） -----
PLAN_COUNT = HandlerSpec(
    code="backup_plan_count",
    from_sql="dim_protection_object po JOIN rpt_backup_domain d ON d.id = po.backup_domain_id",
    where_sql="po.is_deleted = false AND po.protection_object_type = 'backup_plan'",
    domain_col="po.backup_domain_id",
    keyset_order=[],
    key_cols=[],
    group_by=["po.backup_domain_id", "po.db_type", "d.domain_name"],
    fields=[
        _f("domain_name", _domain_name()),
        _f("db_type", "po.db_type"),
        _f("count", "COUNT(DISTINCT po.protection_object_key)"),
    ],
)

PLAN_INVENTORY = HandlerSpec(
    code="backup_plan_inventory",
    from_sql=(
        "dim_protection_object po JOIN rpt_backup_domain d ON d.id = po.backup_domain_id "
        "LEFT JOIN rel_protection_policy rpp ON rpp.protection_object_key = po.protection_object_key "
        "AND rpp.backup_domain_id = po.backup_domain_id AND rpp.is_deleted = false "
        "LEFT JOIN dim_policy p ON p.policy_key = rpp.policy_key AND p.is_deleted = false "
        "AND p.backup_domain_id = po.backup_domain_id"
    ),
    where_sql="po.is_deleted = false AND po.protection_object_type = 'backup_plan'",
    domain_col="po.backup_domain_id",
    keyset_order=["po.backup_domain_id ASC", "po.protection_object_key ASC"],
    key_cols=["d.domain_name", "po.protection_object_key"],
    fields=[
        _f("domain_name", _domain_name()),
        _f("protection_object_name", "po.protection_object_name"),
        _f("db_type", "po.db_type"),
        _f("data_size_kb", "po.data_size_kb"),
        _f("policy_name", "p.policy_name"),
        _f("policy_type", "p.policy_type"),
        _f("schedule_summary", "p.schedule_summary"),
        _f("retention_days", "p.retention_days"),
    ],
)

# ----- 任务聚合（5/6/7/8/9/14） -----
def _agg_from() -> str:
    return "agg_task_daily a JOIN rpt_backup_domain d ON d.id = a.backup_domain_id"


def _agg_where(scene: str) -> str:
    return f"a.task_scene = '{scene}'"


SUCCESS_RATE = HandlerSpec(
    code="backup_success_rate",
    from_sql=_agg_from(),
    where_sql=_agg_where("backup"),
    domain_col="a.backup_domain_id",
    keyset_order=[],
    key_cols=[],
    group_by=["a.backup_domain_id", "a.db_type", "a.task_type", "d.domain_name"],
    fields=[
        _f("domain_name", _domain_name()),
        _f("db_type", "a.db_type"),
        _f("task_type", "a.task_type"),
        _f("finished_count", "SUM(a.finished_count)"),
        _f("success_count", "SUM(a.success_count)"),
        _f(
            "success_rate",
            "CASE WHEN SUM(a.finished_count) = 0 THEN 0 "
            "ELSE ROUND(SUM(a.success_count) * 100.0 / SUM(a.finished_count), 2) END",
        ),
    ],
)

TASK_COUNT = HandlerSpec(
    code="backup_task_count",
    from_sql=_agg_from(),
    where_sql=_agg_where("backup"),
    domain_col="a.backup_domain_id",
    keyset_order=[],
    key_cols=[],
    group_by=["a.backup_domain_id", "a.db_type", "a.task_type", "d.domain_name"],
    fields=[
        _f("domain_name", _domain_name()),
        _f("db_type", "a.db_type"),
        _f("task_type", "a.task_type"),
        _f("total_count", "SUM(a.total_count)"),
        _f("success_count", "SUM(a.success_count)"),
        _f("failed_count", "SUM(a.failed_count)"),
        _f("running_count", "SUM(a.running_count)"),
        _f("canceled_count", "SUM(a.canceled_count)"),
    ],
)

DATA_SIZE = HandlerSpec(
    code="backup_data_size",
    from_sql=_agg_from(),
    where_sql=_agg_where("backup"),
    domain_col="a.backup_domain_id",
    keyset_order=[],
    key_cols=[],
    group_by=["a.backup_domain_id", "a.db_type", "a.task_type", "d.domain_name"],
    fields=[
        _f("domain_name", _domain_name()),
        _f("db_type", "a.db_type"),
        _f("task_type", "a.task_type"),
        _f("success_data_size_kb", "SUM(a.success_data_size_kb)"),
    ],
)

# 趋势模板用 <time_bucket> 列（时间桶函数表达式），由 Handler 注入
MOUNT_SUCCESS_RATE = HandlerSpec(
    code="mount_success_rate",
    from_sql=_agg_from(),
    where_sql=_agg_where("mount"),
    domain_col="a.backup_domain_id",
    keyset_order=[],
    key_cols=[],
    group_by=["a.backup_domain_id", "a.db_type", "d.domain_name"],
    fields=[
        _f("domain_name", _domain_name()),
        _f("db_type", "a.db_type"),
        _f("finished_count", "SUM(a.finished_count)"),
        _f("success_count", "SUM(a.success_count)"),
        _f(
            "success_rate",
            "CASE WHEN SUM(a.finished_count) = 0 THEN 0 "
            "ELSE ROUND(SUM(a.success_count) * 100.0 / SUM(a.finished_count), 2) END",
        ),
    ],
)

# ----- 任务明细（10/11/15/16） -----
def _task_from() -> str:
    return (
        "dwd_task_run t JOIN rpt_backup_domain d ON d.id = t.backup_domain_id "
        "LEFT JOIN LATERAL (SELECT 1) x ON true"
    )


_TASK_DETAIL_FIELDS = [
    _f("task_time", "t.task_time"),
    _f("backup_domain_id", "t.backup_domain_id"),
    _f("task_run_key", "t.task_run_key"),
    _f("domain_name", _domain_name()),
    _f("protection_object_name", "t.protection_object_name"),
    _f("db_type", "t.db_type"),
    _f("task_type", "t.task_type"),
    _f("task_num", "t.task_num"),
    _f("start_time", "t.start_time"),
    _f("end_time", "t.end_time"),
    _f("duration_seconds", "t.duration_seconds"),
    _f("data_size_kb", "t.data_size_kb"),
    _f("initiator", "t.initiator"),
    _f("execute_type", "t.execute_type"),
    _f("sub_task_count", "t.sub_task_count"),
]
_TASK_KEYSET = ["t.task_time DESC", "t.backup_domain_id DESC", "t.task_run_key DESC"]
_TASK_KEY_COLS = ["t.task_time", "t.backup_domain_id", "t.task_run_key"]


def _task_detail_spec(code: str, scene: str, status_sql: str, extra_fields=()) -> HandlerSpec:
    return HandlerSpec(
        code=code,
        from_sql=_task_from(),
        where_sql=f"t.task_scene = '{scene}' AND t.task_status {status_sql}",
        keyset_order=_TASK_KEYSET,
        key_cols=_TASK_KEY_COLS,
        domain_col="t.backup_domain_id",
        fields=list(_TASK_DETAIL_FIELDS) + list(extra_fields),
    )


TASK_SUCCESS_DETAIL = _task_detail_spec("backup_success_detail", "backup", "= 'success'")
TASK_FAILURE_DETAIL = _task_detail_spec(
    "backup_failure_detail",
    "backup",
    "IN ('failed', 'failed_uncleaned')",
    [FieldSpec(name="failure_reason", sql="t.failure_reason"),
     FieldSpec(name="error_summary", sql="t.error_summary")],
)
MOUNT_SUCCESS_DETAIL = _task_detail_spec("mount_success_detail", "mount", "= 'success'")
MOUNT_FAILURE_DETAIL = _task_detail_spec(
    "mount_failure_detail",
    "mount",
    "IN ('failed', 'failed_uncleaned')",
    [FieldSpec(name="failure_reason", sql="t.failure_reason"),
     FieldSpec(name="error_summary", sql="t.error_summary")],
)

# ----- 容量（12/13） -----
WORKER_USAGE = HandlerSpec(
    code="storage_worker_usage",
    from_sql=(
        "dwd_storage_worker_capacity_daily c "
        "JOIN dim_storage_worker sw ON sw.storage_worker_key = c.storage_worker_key "
        "AND sw.backup_domain_id = c.backup_domain_id "
        "JOIN rpt_backup_domain d ON d.id = c.backup_domain_id"
    ),
    where_sql="sw.is_deleted = false",
    domain_col="c.backup_domain_id",
    keyset_order=[],
    key_cols=[],
    fields=[
        _f("domain_name", _domain_name()),
        _f("storage_worker_name", "sw.storage_worker_name"),
        _f("storage_worker_key", "c.storage_worker_key"),
        _f("total_capacity_bytes", "c.total_capacity_bytes"),
        _f("used_capacity_bytes", "c.used_capacity_bytes"),
        _f("available_bytes", "c.total_capacity_bytes - c.used_capacity_bytes"),
        _f(
            "usage_rate",
            "CASE WHEN c.total_capacity_bytes = 0 THEN 0 "
            "ELSE ROUND(c.used_capacity_bytes * 100.0 / c.total_capacity_bytes, 2) END",
        ),
    ],
)


# 趋势类 Handler（时间桶、分组模式）
def _bucket_expr(granularity: str, date_col: str = "a.stat_date") -> str:
    mapping = {
        "day": f"date_trunc('day', {date_col})",
        "week": f"date_trunc('week', {date_col})",
        "month": f"date_trunc('month', {date_col})",
    }
    return mapping.get(granularity, mapping["day"])


TASK_COUNT_TREND = HandlerSpec(
    code="backup_task_count_trend",
    from_sql=_agg_from(),
    where_sql=_agg_where("backup"),
    domain_col="a.backup_domain_id",
    keyset_order=[],
    key_cols=[],
    group_by=["time_bucket", "a.backup_domain_id", "a.db_type", "a.task_type", "d.domain_name"],
    fields=[
        _f("time_bucket", "%(time_bucket_expr)s"),
        _f("domain_name", _domain_name()),
        _f("db_type", "a.db_type"),
        _f("task_type", "a.task_type"),
        _f("total_count", "SUM(a.total_count)"),
    ],
)

DATA_SIZE_TREND = HandlerSpec(
    code="backup_data_size_trend",
    from_sql=_agg_from(),
    where_sql=_agg_where("backup"),
    domain_col="a.backup_domain_id",
    keyset_order=[],
    key_cols=[],
    group_by=["time_bucket", "a.backup_domain_id", "a.db_type", "a.task_type", "d.domain_name"],
    fields=[
        _f("time_bucket", "%(time_bucket_expr)s"),
        _f("domain_name", _domain_name()),
        _f("db_type", "a.db_type"),
        _f("task_type", "a.task_type"),
        _f("success_data_size_kb", "SUM(a.success_data_size_kb)"),
    ],
)

STORAGE_CAPACITY_TREND = HandlerSpec(
    code="storage_capacity_trend",
    from_sql=(
        "dwd_storage_worker_capacity_daily c "
        "JOIN dim_storage_worker sw ON sw.storage_worker_key = c.storage_worker_key "
        "AND sw.backup_domain_id = c.backup_domain_id "
        "JOIN rpt_backup_domain d ON d.id = c.backup_domain_id"
    ),
    where_sql="sw.is_deleted = false",
    domain_col="c.backup_domain_id",
    keyset_order=[],
    key_cols=[],
    group_by=["time_bucket", "group_key"],
    fields=[
        _f("time_bucket", "%(time_bucket_expr)s"),
        _f("group_key", "%(group_key_expr)s"),
        _f("total_capacity_bytes", "SUM(c.total_capacity_bytes)"),
        _f("used_capacity_bytes", "SUM(c.used_capacity_bytes)"),
        _f("available_bytes", "SUM(c.total_capacity_bytes - c.used_capacity_bytes)"),
    ],
)


_SPECS: dict[str, HandlerSpec] = {
    spec.code: spec
    for spec in (
        DS_COUNT,
        DS_INVENTORY,
        PLAN_COUNT,
        PLAN_INVENTORY,
        SUCCESS_RATE,
        TASK_COUNT,
        DATA_SIZE,
        MOUNT_SUCCESS_RATE,
        TASK_SUCCESS_DETAIL,
        TASK_FAILURE_DETAIL,
        MOUNT_SUCCESS_DETAIL,
        MOUNT_FAILURE_DETAIL,
        WORKER_USAGE,
        TASK_COUNT_TREND,
        DATA_SIZE_TREND,
        STORAGE_CAPACITY_TREND,
    )
}

_TREND_HANDLERS = {
    "backup_task_count_trend",
    "backup_data_size_trend",
    "storage_capacity_trend",
}

# ---------------------------------------------------------------------------
# 执行器：把 HandlerSpec 编译为固定参数化 SQL，绑定用户筛选值。
# ---------------------------------------------------------------------------

# 用户筛选器 → 物理列/参数绑定的白名单映射（值只作绑定参数，不拼接 SQL）
_FILTER_COLUMN = {
    "database_types": ("ds.db_type", "a.db_type", "po.db_type", "t.db_type", "sw.storage_type"),
    "backup_types": ("t.task_type", "a.task_type"),
    "data_source_types": ("ds.data_source_type",),
}

_AGG_DATE_COLUMN = "a.stat_date"
_TASK_TIME_COLUMN = "t.task_time"
_CAPACITY_DATE_COLUMN = "c.stat_date"


class HandlerExecutionError(ReportError):
    code = "REPORT_QUERY_EXECUTION_ERROR"


def _time_range_predicate(filters: dict, date_col: str) -> tuple[str, list]:
    """time_range 筛选 → (SQL 片段, 参数)。UTC 半开区间 [start_at, end_at)。"""
    tr = (filters or {}).get("time_range")
    if not tr:
        return "", []
    if isinstance(tr, dict) and tr.get("mode") == "custom":
        start = tr.get("start_date")
        end = tr.get("end_date")
        if not start or not end:
            return "", []
        return f"{date_col} >= %s AND {date_col} < %s", [str(start), str(end)]
    return "", []


def _domain_predicate(domain_ids, domain_col: str = "backup_domain_id") -> tuple[str, list]:
    if not domain_ids:
        return "", []
    ids = [int(d) for d in domain_ids]
    return f"{domain_col} = ANY(%s)", [ids]


def _enum_predicate(filters, keys, spec: HandlerSpec) -> tuple[list[str], list]:
    """枚举筛选 → 条件列表。列名从 _FILTER_COLUMN 白名单按需选择。"""
    clauses: list[str] = []
    params: list = []
    for key in keys:
        values = (filters or {}).get(key)
        if not values:
            continue
        candidates = _FILTER_COLUMN.get(key, ())
        # 从 spec 的表别名推断适用列：按字段出现顺序选第一个存在列
        col = _pick_filter_column(candidates, spec)
        if col is None:
            continue
        clauses.append(f"{col} = ANY(%s)")
        params.append([str(v) for v in values])
    return clauses, params


def _pick_filter_column(candidates, spec: HandlerSpec):
    """根据 spec 的 from_sql 推断可用列。

    用 `别名.` 断言（单词边界）判断表别名是否存在，避免 `t` 命中
    `agg_task_daily` 之类含该字母的子串误判。
    """
    from_sql = spec.from_sql
    for cand in candidates:
        prefix = cand.split(".")[0]
        # 别名引用形如 `a.`/`ds.`；注意 SQL 别名声明也可能拼成前缀，故再查表名特例
        if f"{prefix}." in from_sql or (
            prefix == "ds" and "dim_data_source" in from_sql
        ):
            return cand
    return None


def _granularity_value(filters) -> str:
    g = (filters or {}).get("granularity")
    return g if g in ("day", "week", "month") else "day"


def _group_mode_expr(mode: str) -> str:
    return {
        "overall": "'overall'",
        "domain": "d.domain_name",
        "worker": "sw.storage_worker_name",
    }.get(mode, "'overall'")


def _compile_time_bucket(spec: HandlerSpec, filters: dict) -> Optional[str]:
    """趋势类模板：把 %(time_bucket_expr)s 替换为具体时间桶表达式。"""
    names = {f.name for f in spec.fields}
    if "time_bucket" not in names:
        return None
    g = _granularity_value(filters)
    if spec.code == "storage_capacity_trend":
        return _bucket_expr(g, _CAPACITY_DATE_COLUMN)
    return _bucket_expr(g, _AGG_DATE_COLUMN)


def _build_sql(
    spec: HandlerSpec,
    domain_ids,
    filters: dict,
    page_size: int,
    cursor: Optional[dict],
) -> tuple[str, list]:
    """编译固定 SQL + 绑定参数。cursor 为 keyset 并列键 dict。"""
    where = [spec.where_sql]
    params: list = []

    dclause, dparams = _domain_predicate(domain_ids, spec.domain_col)
    if dclause:
        where.append(dclause)
        params.extend(dparams)

    date_col = _AGG_DATE_COLUMN
    if spec.code in ("backup_success_detail", "backup_failure_detail",
                     "mount_success_detail", "mount_failure_detail"):
        date_col = _TASK_TIME_COLUMN
    elif spec.code in ("storage_worker_usage", "storage_capacity_trend"):
        date_col = _CAPACITY_DATE_COLUMN
    tclause, tparams = _time_range_predicate(filters, date_col)
    if tclause:
        where.append(tclause)
        params.extend(tparams)

    enum_keys = ("database_types", "backup_types", "data_source_types")
    eclauses, eparams = _enum_predicate(filters, enum_keys, spec)
    if eclauses:
        where.extend(eclauses)
        params.extend(eparams)

    time_bucket = _compile_time_bucket(spec, filters)
    group_key = None
    if spec.code == "storage_capacity_trend":
        mode = (filters or {}).get("group_mode") or "overall"
        group_key = _group_mode_expr(mode)

    # Keyset 游标条件（任务明细：task_time DESC, domain DESC, run_key DESC）
    if cursor and spec.keyset_order:
        # 通用 keyset：按 key_cols 顺序构造复合条件
        cols = spec.key_cols
        # 构造 (k1,k2,k3) < (%s,%s,%s) 词典序条件
        placeholders = ", ".join(["%s"] * len(cols))
        comp = "(" + ", ".join(cols) + ")"
        where.append(f"{comp} < ({placeholders})")
        params.extend([cursor.get(c.split(".")[-1]) for c in cols])

    select_cols = []
    for f in spec.fields:
        expr = f.sql
        if time_bucket and f.name == "time_bucket":
            expr = time_bucket
        if group_key and f.name == "group_key":
            expr = group_key
        select_cols.append(f"{expr} AS {f.name}")

    sql = f"SELECT {', '.join(select_cols)} FROM {spec.from_sql} WHERE {' AND '.join(where)}"
    if spec.group_by:
        gb = []
        for col in spec.group_by:
            if col == "time_bucket":
                gb.append(time_bucket)
            elif col == "group_key":
                # group_mode=overall 时 group_key 是常量 'overall'，常量不入 GROUP BY
                if group_key and not group_key.startswith("'"):
                    gb.append(group_key)
            else:
                gb.append(col)
        if gb:
            sql += " GROUP BY " + ", ".join(gb)
    if spec.keyset_order:
        sql += " ORDER BY " + ", ".join(spec.keyset_order)
    sql += f" LIMIT %s"
    params.append(int(page_size) + 1)
    return sql, params


class HandlerResult:
    """Handler 查询结果。"""

    def __init__(self, records: list[dict], columns: list[str], has_more: bool,
                 next_cursor: Optional[dict], keyset_cols: list[str]) -> None:
        self.records = records
        self.columns = columns
        self.has_more = has_more
        self.next_cursor = next_cursor
        self.keyset_cols = keyset_cols


class ReportQueryHandlerRegistry:
    """16 个固定 Handler 注册表。SQL 模板来源唯一为本模块 _SPECS。"""

    def __init__(self, specs: Optional[dict[str, HandlerSpec]] = None) -> None:
        self._specs = dict(_SPECS if specs is None else specs)

    def has(self, code: str) -> bool:
        return code in self._specs

    def spec(self, code: str) -> HandlerSpec:
        if code not in self._specs:
            raise TemplateValidationError(f"无此查询 Handler: {code}")
        return self._specs[code]

    def execute(
        self,
        conn,
        template: Template,
        *,
        domain_ids,
        filters: dict,
        view: str,
        page_size: int,
        cursor: Optional[dict],
    ) -> HandlerResult:
        spec = self.spec(template.query_handler)
        sql, params = _build_sql(spec, domain_ids, filters, page_size, cursor)
        try:
            rows = conn.execute(sql, params).fetchall()
        except Exception as exc:
            raise HandlerExecutionError(str(exc)) from exc
        limit = page_size
        has_more = len(rows) > limit
        rows = rows[:limit]
        records = [dict(r) for r in rows]
        next_cursor = None
        if has_more and records and spec.key_cols:
            last = records[-1]
            next_cursor = {
                c.split(".")[-1]: last.get(c.split(".")[-1])
                for c in spec.key_cols
            }
        columns = [f.name for f in spec.fields]
        return HandlerResult(records, columns, has_more, next_cursor, spec.key_cols)
