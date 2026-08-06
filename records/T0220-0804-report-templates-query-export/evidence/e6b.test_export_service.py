"""导出服务测试（T0220 AC-5/AC-9 相关：CSV 流式、PDF 分页、截断保护）。"""

from __future__ import annotations

import csv
import io
from pathlib import Path

import pytest

from report_web.report.export_service import ExportConfig, ExportService
from report_web.report.query_handlers import ReportQueryHandlerRegistry
from report_web.report.query_service import QueryService
from report_web.report.template_registry import TemplateRegistry

TEMPLATE_ROOT = Path(__file__).parent.parent / "report_web" / "data" / "templates"


@pytest.fixture(scope="module")
def export_svc(factory):
    registry = TemplateRegistry.load(str(TEMPLATE_ROOT))
    handlers = ReportQueryHandlerRegistry()
    qsvc = QueryService(factory, registry, handlers)
    return ExportService(
        qsvc,
        ExportConfig(csv_max_rows=12, pdf_table_rows_per_page=4, pdf_max_tabular_rows=12),
    )


def _seed_domain(factory, did, name):
    with factory.write_connection() as conn:
        conn.execute(
            "INSERT INTO rpt_backup_domain (id, domain_name, web_ip, web_port, rpc_port, username, password, "
            "collection_enabled, is_deleted, created_at, updated_at) VALUES (%s,%s,'x',1,6611,'u','p',TRUE,FALSE,now(),now()) "
            "ON CONFLICT (id) DO UPDATE SET collection_enabled=TRUE, is_deleted=FALSE",
            (did, name),
        )


def _ensure_task_partitions(factory, weeks):
    """为测试数据补充 dwd_task_run 周分区（conftest 只保留当前周+下一周）。"""
    with factory.write_connection() as conn:
        for start_ts, end_ts in weeks:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS dwd_task_run_20260817 PARTITION OF dwd_task_run "
                f"FOR VALUES FROM ('{start_ts}'::timestamptz) TO ('{end_ts}'::timestamptz)"
            )


def _seed_collection_success(factory, did, topic):
    import uuid

    with factory.write_connection() as conn:
        conn.execute(
            "INSERT INTO rpt_collection_task (task_id, backup_domain_id, topic, status, created_at, updated_at) "
            "VALUES (%s,%s,%s,'SUCCESS',now(),now()) ON CONFLICT DO NOTHING",
            (uuid.uuid4(), did, topic),
        )


def _seed_task(factory, did, run_key, task_time, scene="backup", status="success"):
    with factory.write_connection() as conn:
        conn.execute(
            "INSERT INTO dwd_task_run (task_time, backup_domain_id, task_run_key, protection_object_key, "
            "protection_object_name, db_type, task_scene, task_type, task_status, start_time, end_time, "
            "duration_seconds, data_size_kb, task_num, initiator, execute_type, sub_task_count, "
            "success_sub_task_count, failed_sub_task_count, running_sub_task_count, canceled_sub_task_count, "
            "error_summary, aggregation_version, source_create_time, source_update_time, etl_create_time, etl_update_time) "
            "VALUES (%s,%s,%s,%s,%s,'oracle',%s,'full',%s,%s,%s,10,1024,'t1','u','manual',1,1,0,0,0,'',"
            "'v1',now(),now(),now(),now()) ON CONFLICT DO NOTHING",
            (task_time, did, run_key, f"{did}:plan:1", f"obj{did}", scene, status,
             task_time, task_time),
        )


class TestExportCsv:
    def test_csv_rows_within_limit(self, factory, export_svc):
        _seed_domain(factory, 1, "d1")
        _seed_collection_success(factory, 1, "task")
        for i in range(5):
            _seed_task(factory, 1, f"1:run:{i}", f"2026-08-{4 + i:02d}T10:00:00+00:00")
        res = export_svc.export_csv(
            "backup_success_detail", filters={"domain_ids": [1]}, view="table",
        )
        assert res.format == "csv"
        assert res.content_type == "text/csv; charset=utf-8"
        assert res.truncated is False
        assert res.row_count == 5
        assert res.columns[0] == "task_time"
        rows = list(csv.reader(io.StringIO(res.content.decode("utf-8"))))
        assert len(rows) == 6  # header + 5
        assert rows[0][2] == "task_run_key"

    def test_csv_truncated(self, factory, export_svc):
        _seed_domain(factory, 1, "d1")
        _seed_collection_success(factory, 1, "task")
        _ensure_task_partitions(factory, [("2026-08-17T00:00:00+00:00", "2026-08-24T00:00:00+00:00")])
        for i in range(20):
            _seed_task(factory, 1, f"1:run:{i}", f"2026-08-{4 + i:02d}T10:00:00+00:00")
        res = export_svc.export_csv(
            "backup_success_detail", filters={"domain_ids": [1]}, view="table",
        )
        assert res.truncated is True
        assert res.row_count == 12  # csv_max_rows
        assert res.row_limit == 12
        rows = list(csv.reader(io.StringIO(res.content.decode("utf-8"))))
        assert len(rows) == 13  # header + 12


class TestExportPdf:
    def test_pdf_bytes_and_pagination(self, factory, export_svc):
        _seed_domain(factory, 1, "d1")
        _seed_collection_success(factory, 1, "task")
        for i in range(10):
            _seed_task(factory, 1, f"1:run:{i}", f"2026-08-{4 + i:02d}T10:00:00+00:00")
        res = export_svc.export_pdf(
            "backup_success_detail", filters={"domain_ids": [1]}, view="table",
        )
        assert res.format == "pdf"
        assert res.content_type == "application/pdf"
        assert res.truncated is False
        assert res.row_count == 10
        assert res.content.startswith(b"%PDF")
        assert b"/Type /Page" in res.content
        assert b"TRUNCATED" not in res.content

    def test_pdf_truncated_marker(self, factory, export_svc):
        _seed_domain(factory, 1, "d1")
        _seed_collection_success(factory, 1, "task")
        _ensure_task_partitions(factory, [("2026-08-17T00:00:00+00:00", "2026-08-24T00:00:00+00:00")])
        for i in range(20):
            _seed_task(factory, 1, f"1:run:{i}", f"2026-08-{4 + i:02d}T10:00:00+00:00")
        res = export_svc.export_pdf(
            "backup_success_detail", filters={"domain_ids": [1]}, view="table",
        )
        assert res.truncated is True
        assert res.row_count == 12
        assert res.content.startswith(b"%PDF")
