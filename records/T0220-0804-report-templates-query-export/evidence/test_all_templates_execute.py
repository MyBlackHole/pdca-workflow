"""16 套模板全量 DB 执行冒烟测试（T0220 AC-3 补充：每套 Handler 在真实 PG schema 可执行）。"""

from __future__ import annotations

from pathlib import Path

import pytest

from report_web.report.query_handlers import ReportQueryHandlerRegistry
from report_web.report.query_service import QueryService
from report_web.report.template_registry import TemplateRegistry

TEMPLATE_ROOT = Path(__file__).parent.parent / "report_web" / "data" / "templates"


@pytest.fixture(scope="module")
def qsvc(factory):
    registry = TemplateRegistry.load(str(TEMPLATE_ROOT))
    handlers = ReportQueryHandlerRegistry()
    return QueryService(factory, registry, handlers)


def _seed_domain(factory, did, name):
    with factory.write_connection() as conn:
        conn.execute(
            "INSERT INTO rpt_backup_domain (id, domain_name, web_ip, web_port, rpc_port, username, password, "
            "collection_enabled, is_deleted, created_at, updated_at) VALUES (%s,%s,'x',1,6611,'u','p',TRUE,FALSE,now(),now()) "
            "ON CONFLICT (id) DO UPDATE SET collection_enabled=TRUE, is_deleted=FALSE",
            (did, name),
        )


def _seed_collection_success(factory, did, topic):
    import uuid

    with factory.write_connection() as conn:
        conn.execute(
            "INSERT INTO rpt_collection_task (task_id, backup_domain_id, topic, status, created_at, updated_at) "
            "VALUES (%s,%s,%s,'SUCCESS',now(),now()) ON CONFLICT DO NOTHING",
            (uuid.uuid4(), did, topic),
        )


def _seed_read_tables(factory, did):
    """填充各读表最小数据：dim_data_source/dim_protection_object/rel_protection_policy/"
    dim_policy/agg_task_daily/dwd_storage_worker_capacity_daily/dim_storage_worker。"""
    with factory.write_connection() as conn:
        conn.execute(
            "INSERT INTO dim_data_source (data_source_key, backup_domain_id, source_table, source_id, "
            "source_update_time, attribute, is_deleted, etl_create_time, etl_update_time, data_source_name, db_type, "
            "data_source_type, host_address, service_port, status) "
            "VALUES ('1:data_source:1',%s,'data_source',1,now(),'{}'::jsonb,FALSE,now(),now(),'ds1','oracle','oracle','h1',1521,'active') "
            "ON CONFLICT DO NOTHING",
            (did,),
        )
        conn.execute(
            "INSERT INTO dim_protection_object (protection_object_key, backup_domain_id, source_table, source_id, "
            "source_update_time, attribute, is_deleted, etl_create_time, etl_update_time, data_source_key, "
            "protection_object_name, db_type, protection_object_type, data_size_kb) "
            "VALUES ('1:protection_object:1',%s,'protection_object',1,now(),'{}'::jsonb,FALSE,now(),now(),"
            "'1:data_source:1','plan1','oracle','backup_plan',2048) "
            "ON CONFLICT DO NOTHING",
            (did,),
        )
        conn.execute(
            "INSERT INTO dim_policy (policy_key, backup_domain_id, source_table, source_id, source_update_time, "
            "attribute, is_deleted, etl_create_time, etl_update_time, policy_name, policy_type, schedule_summary, retention_days) "
            "VALUES ('1:policy:1',%s,'policy',1,now(),'{}'::jsonb,FALSE,now(),now(),'pol1','daily','0 2 * * *',7) "
            "ON CONFLICT DO NOTHING",
            (did,),
        )
        conn.execute(
            "INSERT INTO rel_protection_policy (backup_domain_id, protection_object_key, stage_key, policy_key, is_deleted, "
            "etl_create_time, etl_update_time) "
            "VALUES (%s,'1:protection_object:1','1:stage:1','1:policy:1',FALSE,now(),now()) ON CONFLICT DO NOTHING",
            (did,),
        )
        conn.execute(
            "INSERT INTO agg_task_daily (stat_date, backup_domain_id, db_type, task_scene, task_type, "
            "total_count, success_count, failed_count, running_count, canceled_count, finished_count, "
            "success_data_size_kb, etl_create_time, etl_update_time) "
            "VALUES ('2026-08-04'::date,%s,'oracle','backup','full',10,8,1,0,1,9,2048,now(),now()) "
            "ON CONFLICT DO NOTHING",
            (did,),
        )
        conn.execute(
            "INSERT INTO dim_storage_worker (storage_worker_key, backup_domain_id, source_table, source_id, "
            "source_update_time, attribute, is_deleted, etl_create_time, etl_update_time, storage_worker_name, storage_type) "
            "VALUES ('1:storage_worker:1',%s,'storage_worker',1,now(),'{}'::jsonb,FALSE,now(),now(),'worker1','pool') "
            "ON CONFLICT DO NOTHING",
            (did,),
        )
        conn.execute(
            "INSERT INTO dwd_storage_worker_capacity_daily (stat_date, backup_domain_id, storage_worker_key, "
            "total_capacity_bytes, used_capacity_bytes, collection_time, etl_create_time, etl_update_time) "
            "VALUES ('2026-08-04'::date,%s,'1:storage_worker:1',1024000,512000,now(),now(),now()) ON CONFLICT DO NOTHING",
            (did,),
        )


_ALL_TEMPLATES = [
    "data_source_count", "data_source_inventory",
    "backup_plan_count", "backup_plan_inventory",
    "backup_success_rate", "backup_task_count", "backup_task_count_trend",
    "backup_data_size", "backup_data_size_trend",
    "backup_success_detail", "backup_failure_detail",
    "mount_success_rate", "mount_success_detail", "mount_failure_detail",
    "storage_worker_usage", "storage_capacity_trend",
]


class TestAllTemplatesExecutable:
    def test_16_templates_execute(self, factory, qsvc):
        """AC-3 补充：每套模板在 seed fixture 上可执行且返回结构。"""
        _seed_domain(factory, 1, "d1")
        _seed_collection_success(factory, 1, "task")
        _seed_collection_success(factory, 1, "resource")
        _seed_collection_success(factory, 1, "capacity")
        _seed_read_tables(factory, 1)

        for code in _ALL_TEMPLATES:
            filters = {"domain_ids": [1]}
            # 趋势模板需要 time_range 才走聚合（否则仍可执行）
            tpl = qsvc._registry.get(code)
            res = qsvc.query(code, filters=filters, view=tpl.default_view, page_size=20)
            assert res.columns, f"{code}: 无列"
            assert res.data_state in (
                "COVERED", "NO_MATCH", "INSUFFICIENT_COLLECTION_COVERAGE",
            ), f"{code}: data_state 非法"

    def test_trend_templates_execute_with_range(self, factory, qsvc):
        """趋势模板带 time_range 执行。"""
        _seed_domain(factory, 1, "d1")
        _seed_collection_success(factory, 1, "task")
        _seed_collection_success(factory, 1, "resource")
        _seed_collection_success(factory, 1, "capacity")
        _seed_read_tables(factory, 1)
        for code in ("backup_task_count_trend", "backup_data_size_trend", "storage_capacity_trend"):
            tpl = qsvc._registry.get(code)
            res = qsvc.query(
                code,
                filters={
                    "domain_ids": [1],
                    "time_range": {"mode": "custom", "start_date": "2026-08-01", "end_date": "2026-08-10"},
                },
                view=tpl.default_view,
                page_size=20,
            )
            assert res.columns, f"{code}: 无列"
