#!/usr/bin/env python3
import argparse
import json
import platform
import resource
import time
from pathlib import Path

import duckdb


def bytes_size(path):
    return path.stat().st_size if path.exists() else 0


def max_rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=55432)
    parser.add_argument("--dbname", default="poc")
    parser.add_argument("--user", default="postgres")
    parser.add_argument("--password", default="postgres")
    parser.add_argument("--rows", type=int, default=1_000_000)
    parser.add_argument("--out", type=Path, default=Path("poc-output/pg-duckdb"))
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    csv_path = args.out.parent / "pg" / "pg_orders.csv"
    d1_path = args.out / "pg_duckdb_from_csv.parquet"
    d2_path = args.out / "pg_duckdb_from_pg.parquet"
    metrics_path = args.out / "pg_duckdb_metrics.json"
    report_path = args.out / "pg_duckdb_report.md"

    for path in (d1_path, d2_path, metrics_path, report_path):
        if path.exists():
            path.unlink()

    metrics = {
        "database": "PostgreSQL",
        "duckdb": duckdb.__version__,
        "rows_target": args.rows,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "stages": {},
        "files": {},
        "validation": {},
    }

    con = duckdb.connect()

    def run_path(key, sql, parquet_path, rows):
        started = time.perf_counter()
        con.execute(sql)
        seconds = time.perf_counter() - started
        metrics["stages"][f"{key}_seconds"] = seconds
        metrics["stages"][f"{key}_throughput_rows_per_second"] = rows / seconds
        metrics["files"][f"{key}_parquet_bytes"] = bytes_size(parquet_path)
        try:
            count = con.execute(
                f"SELECT count(*) FROM read_parquet('{parquet_path}')"
            ).fetchone()[0]
            metrics["validation"][f"{key}_parquet_rows"] = count
            metrics["validation"][f"{key}_row_count_match"] = count == rows
            schema = con.execute(
                f"DESCRIBE SELECT * FROM read_parquet('{parquet_path}')"
            ).fetchall()
            metrics["validation"][f"{key}_schema"] = [
                {"name": row[0], "type": str(row[1])} for row in schema
            ]
        except Exception as exc:
            metrics["validation"][f"{key}_parquet_rows"] = f"error: {exc}"
            metrics["validation"][f"{key}_row_count_match"] = False

    conn_str = (
        f"host={args.host} port={args.port} dbname={args.dbname} "
        f"user={args.user} password={args.password}"
    )

    con.execute("INSTALL postgres_scanner")
    con.execute("LOAD postgres_scanner")

    started_total = time.perf_counter()

    run_path(
        "d1_csv",
        f"""
        COPY (
          SELECT
            CAST(id AS BIGINT) AS id,
            CAST(customer_id AS INTEGER) AS customer_id,
            CAST(amount AS DECIMAL(12,2)) AS amount,
            CAST(created_at AS TIMESTAMP) AS created_at,
            CAST(status AS VARCHAR) AS status,
            CAST(payload AS VARCHAR) AS payload,
            CAST(active AS BOOLEAN) AS active
          FROM read_csv('{csv_path}', header = true,
                        columns = {{'id': 'BIGINT', 'customer_id': 'INTEGER',
                                    'amount': 'VARCHAR', 'created_at': 'VARCHAR',
                                    'status': 'VARCHAR', 'payload': 'VARCHAR',
                                    'active': 'VARCHAR'}})
        ) TO '{d1_path}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """,
        d1_path,
        args.rows,
    )

    run_path(
        "d2_pg",
        f"""
        COPY (
          SELECT id, customer_id, amount, created_at, status, payload, active
          FROM postgres_scan_pushdown('{conn_str}', 'public', 'poc_orders')
        ) TO '{d2_path}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """,
        d2_path,
        args.rows,
    )

    try:
        row = con.execute(
            f"""
            SELECT count(*), max(amount) FROM postgres_scan_pushdown(
                '{conn_str}', 'public', 'poc_orders')
            """
        ).fetchone()
        metrics["validation"]["source_rows"] = row[0]
    except Exception as exc:
        metrics["validation"]["source_rows"] = f"error: {exc}"

    metrics["total_seconds"] = time.perf_counter() - started_total
    metrics["max_rss_mb"] = max_rss_mb()
    con.close()

    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(
        "\n".join(
            [
                "# PostgreSQL DuckDB 转换 POC 报告",
                "",
                "## 调研目标",
                "",
                "用 DuckDB 补测两条路径，对照 pandas/psycopg2 路径：",
                "1. D1: DuckDB 读既有 COPY CSV 转 Parquet（转换引擎替换，对照 pandas 转换层）。",
                "2. D2: DuckDB postgres_scanner 直读 PG 表转 Parquet（端到端直转，对照 psycopg2 直转）。",
                "",
                "## 方法",
                "",
                f"- DuckDB {duckdb.__version__}，COMPRESSION ZSTD，数据源为既有 poc_orders 表（{args.rows} 行）。",
                f"- D1 输入: `poc-output/pg/pg_orders.csv`（112.7 MB，COPY CSV HEADER 产物）。",
                f"- D2 输入: `postgres_scan_pushdown('{conn_str}', 'public', 'poc_orders')`。",
                "",
                "## 发现",
                "",
                f"- D1（CSV→Parquet）耗时: {metrics['stages']['d1_csv_seconds']:.3f}s，吞吐 {metrics['stages']['d1_csv_throughput_rows_per_second']:.2f} rows/s",
                f"- D1 Parquet 大小: {metrics['files']['d1_csv_parquet_bytes']} bytes",
                f"- D2（PG→Parquet）耗时: {metrics['stages']['d2_pg_seconds']:.3f}s，吞吐 {metrics['stages']['d2_pg_throughput_rows_per_second']:.2f} rows/s",
                f"- D2 Parquet 大小: {metrics['files']['d2_pg_parquet_bytes']} bytes",
                f"- 两路径合计耗时: {metrics['total_seconds']:.3f}s",
                f"- 峰值 RSS: {metrics['max_rss_mb']:.2f} MiB",
                f"- D1 行数校验: {metrics['validation']['d1_csv_parquet_rows']} rows, match={metrics['validation']['d1_csv_row_count_match']}",
                f"- D2 行数校验: {metrics['validation']['d2_pg_parquet_rows']} rows, match={metrics['validation']['d2_pg_row_count_match']}",
                f"- D2 schema: {json.dumps(metrics['validation']['d2_pg_schema'], ensure_ascii=False)}",
                "",
                "## 结论与建议",
                "",
                "- 对照结果见总报告 research-report.md 第 6 节（四路径对照表）。",
                "",
                "## 参考资料",
                "",
                "- 本任务 PRD: `prd.md`",
                "- 原始指标: `pg_duckdb_metrics.json`",
                "- 总报告: `../../research-report.md`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
