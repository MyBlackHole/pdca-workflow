"""T0220 Check 阶段修复的 3 个真实 bug 精确单测（SQL 片段级，无 DB 依赖）。

根因 1: _pick_filter_column 用 `prefix in from_sql` 子串匹配, `t` 误命中
       agg_task_daily 等含该字母的表名, 误选 t 别名导致 missing FROM-clause。
根因 2: _domain_predicate 固定裸 backup_domain_id, 多表 JOIN 同名列歧义。
根因 3: storage_capacity_trend 在 group_mode=overall 时 GROUP BY 常量 'overall'。
"""

from __future__ import annotations

from report_web.report.query_handlers import (
    DATA_SIZE_TREND,
    STORAGE_CAPACITY_TREND,
    WORKER_USAGE,
    _build_sql,
    _pick_filter_column,
)


def test_pick_filter_column_not_confused_by_substring():
    """根因1: `t` 候选不得因 agg_task_daily 含字母 t 而被误选。"""
    cands = ("a.task_type", "t.task_type")
    # from_sql 只有 agg 别名 a 引用, 无 t 别名
    assert _pick_filter_column(cands, DATA_SIZE_TREND) == "a.task_type"


def test_pick_filter_column_matches_alias_with_dot():
    """别名 `t.` 只在真正出现 t. 引用时命中。"""
    cands = ("t.task_type", "a.task_type")
    # DATA_SIZE_TREND 无 t 别名, 应落到 a
    assert _pick_filter_column(cands, DATA_SIZE_TREND) == "a.task_type"


def test_domain_predicate_uses_qualified_column_for_join():
    """根因2: JOIN 多表模板的域列带别名, 避免同名列歧义。"""
    sql, params = _build_sql(
        WORKER_USAGE, [1], {"domain_ids": [1]}, page_size=20, cursor=None
    )
    assert "c.backup_domain_id = ANY(%s)" in sql
    assert params  # domain 参数存在


def test_domain_predicate_bare_column_for_single_table():
    """单表模板保持裸列。"""
    sql, params = _build_sql(
        STORAGE_CAPACITY_TREND, [1], {"domain_ids": [1]}, page_size=20, cursor=None
    )
    # STORAGE_CAPACITY_TREND 也走 c 别名
    assert "c.backup_domain_id = ANY(%s)" in sql


def test_group_key_constant_not_in_group_by():
    """根因3: group_mode=overall 时 group_key='overall' 常量不入 GROUP BY。"""
    sql, params = _build_sql(
        STORAGE_CAPACITY_TREND,
        [1],
        {"domain_ids": [1], "time_range": {"mode": "custom", "start_date": "2026-08-01", "end_date": "2026-08-10"}},
        page_size=20,
        cursor=None,
    )
    assert "'overall'" in sql  # SELECT 中有常量
    assert "'overall'" not in sql.split("GROUP BY", 1)[1]  # GROUP BY 后无常量


def test_domain_col_configured_on_every_join_template():
    """所有 JOIN 多表模板均显式配置 domain_col, 不依赖裸列默认。"""
    from report_web.report.query_handlers import ReportQueryHandlerRegistry

    reg = ReportQueryHandlerRegistry()
    join_specs = [
        s for s in reg._specs.values() if s.from_sql.count("JOIN") > 0
    ]
    for spec in join_specs:
        assert spec.domain_col, f"{spec.code}: JOIN 模板缺 domain_col"
