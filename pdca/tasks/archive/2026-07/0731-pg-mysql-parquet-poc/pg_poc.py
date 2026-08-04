#!/usr/bin/env python3
import argparse
import json
import os
import platform
import resource
import shutil
import subprocess
import time
from pathlib import Path

import fastparquet
import pandas as pd
import psycopg2


def run(command):
    started = time.perf_counter()
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return {
        "command": command,
        "seconds": time.perf_counter() - started,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def connect(args):
    return psycopg2.connect(
        host=args.host,
        port=args.port,
        dbname=args.dbname,
        user=args.user,
        password=args.password,
    )


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
    parser.add_argument("--out", type=Path, default=Path("poc-output/pg"))
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    csv_path = args.out / "pg_orders.csv"
    parquet_path = args.out / "pg_orders.parquet"
    metrics_path = args.out / "pg_metrics.json"
    report_path = args.out / "pg_poc_report.md"

    for path in (csv_path, parquet_path, metrics_path, report_path):
        if path.exists():
            path.unlink()

    metrics = {
        "database": "PostgreSQL",
        "rows_target": args.rows,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "tools": {},
        "stages": {},
        "files": {},
        "validation": {},
    }

    for tool in ["podman", "psql"]:
        if shutil.which(tool):
            try:
                metrics["tools"][tool] = run([tool, "--version"])["stdout"]
            except Exception as exc:
                metrics["tools"][tool] = f"unavailable: {exc}"

    started_total = time.perf_counter()
    with connect(args) as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            metrics["tools"]["postgres_server"] = cursor.fetchone()[0]

            started = time.perf_counter()
            cursor.execute("DROP TABLE IF EXISTS poc_orders")
            cursor.execute(
                """
                CREATE TABLE poc_orders (
                  id BIGINT PRIMARY KEY,
                  customer_id INTEGER NOT NULL,
                  amount NUMERIC(12,2) NOT NULL,
                  created_at TIMESTAMP NOT NULL,
                  status TEXT NOT NULL,
                  payload TEXT NOT NULL,
                  active BOOLEAN NOT NULL
                )
                """
            )
            cursor.execute(
                """
                INSERT INTO poc_orders
                SELECT
                  g AS id,
                  (g %% 100000)::integer AS customer_id,
                  round(((g %% 100000)::numeric / 100), 2) AS amount,
                  timestamp '2026-01-01 00:00:00' + (g || ' seconds')::interval AS created_at,
                  CASE g %% 4
                    WHEN 0 THEN 'new'
                    WHEN 1 THEN 'paid'
                    WHEN 2 THEN 'shipped'
                    ELSE 'closed'
                  END AS status,
                  md5(g::text) || repeat('x', 32) AS payload,
                  (g %% 2 = 0) AS active
                FROM generate_series(1, %s) AS g
                """,
                (args.rows,),
            )
            metrics["stages"]["prepare_seconds"] = time.perf_counter() - started
            cursor.execute("SELECT count(*) FROM poc_orders")
            metrics["validation"]["source_rows"] = cursor.fetchone()[0]

        started = time.perf_counter()
        with connection.cursor() as cursor, csv_path.open("w", encoding="utf-8", newline="") as handle:
            cursor.copy_expert(
                """
                COPY (
                  SELECT id, customer_id, amount, created_at, status, payload, active
                  FROM poc_orders
                  ORDER BY id
                ) TO STDOUT WITH CSV HEADER
                """,
                handle,
            )
        metrics["stages"]["copy_export_seconds"] = time.perf_counter() - started

    metrics["files"]["csv_bytes"] = bytes_size(csv_path)

    started = time.perf_counter()
    dataframe = pd.read_csv(
        csv_path,
        parse_dates=["created_at"],
        true_values=["t"],
        false_values=["f"],
        dtype={
            "id": "int64",
            "customer_id": "int32",
            "amount": "float64",
            "status": "string",
            "payload": "string",
            "active": "boolean",
        },
    )
    metrics["stages"]["csv_read_seconds"] = time.perf_counter() - started

    started = time.perf_counter()
    dataframe.to_parquet(parquet_path, engine="fastparquet", compression="zstd", index=False)
    metrics["stages"]["parquet_write_seconds"] = time.perf_counter() - started
    metrics["files"]["parquet_bytes"] = bytes_size(parquet_path)

    parquet_file = fastparquet.ParquetFile(parquet_path)
    parquet_rows = sum(row_group.num_rows for row_group in parquet_file.fmd.row_groups)
    metrics["validation"]["parquet_rows"] = parquet_rows
    metrics["validation"]["row_count_match"] = parquet_rows == metrics["validation"]["source_rows"]
    metrics["validation"]["schema"] = str(parquet_file.schema)
    metrics["validation"]["sample"] = dataframe.head(3).astype(str).to_dict(orient="records")
    metrics["total_seconds"] = time.perf_counter() - started_total
    metrics["throughput_rows_per_second_total"] = args.rows / metrics["total_seconds"]
    metrics["throughput_rows_per_second_export"] = args.rows / metrics["stages"]["copy_export_seconds"]
    metrics["throughput_rows_per_second_convert"] = args.rows / (
        metrics["stages"]["csv_read_seconds"] + metrics["stages"]["parquet_write_seconds"]
    )
    metrics["compression_ratio_csv_to_parquet"] = metrics["files"]["csv_bytes"] / metrics["files"]["parquet_bytes"]
    metrics["max_rss_mb"] = max_rss_mb()

    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(
        "\n".join(
            [
                "# PostgreSQL 逻辑导出转换 Parquet POC 报告",
                "",
                "## 调研目标",
                "",
                "验证 PostgreSQL 使用逻辑 COPY 导出后转换为 Parquet 的本地端到端性能和数据校验结果。",
                "",
                "## 方法",
                "",
                f"- 使用 Podman 临时 PostgreSQL 实例，目标行数 {args.rows}。",
                "- 在 PostgreSQL 内用 `generate_series` 构造包含整数、NUMERIC、TIMESTAMP、TEXT、BOOLEAN 的测试表。",
                "- 使用 `COPY (...) TO STDOUT WITH CSV HEADER` 执行逻辑导出。",
                "- 使用 pandas + fastparquet 将 CSV 转为 ZSTD 压缩 Parquet。",
                "",
                "## 发现",
                "",
                f"- PostgreSQL 版本: `{metrics['tools']['postgres_server']}`",
                f"- 准备数据耗时: {metrics['stages']['prepare_seconds']:.3f}s",
                f"- COPY 导出耗时: {metrics['stages']['copy_export_seconds']:.3f}s",
                f"- CSV 读取耗时: {metrics['stages']['csv_read_seconds']:.3f}s",
                f"- Parquet 写入耗时: {metrics['stages']['parquet_write_seconds']:.3f}s",
                f"- 端到端耗时: {metrics['total_seconds']:.3f}s",
                f"- 端到端吞吐: {metrics['throughput_rows_per_second_total']:.2f} rows/s",
                f"- 导出吞吐: {metrics['throughput_rows_per_second_export']:.2f} rows/s",
                f"- 转换吞吐: {metrics['throughput_rows_per_second_convert']:.2f} rows/s",
                f"- CSV 大小: {metrics['files']['csv_bytes']} bytes",
                f"- Parquet 大小: {metrics['files']['parquet_bytes']} bytes",
                f"- CSV/Parquet 压缩比: {metrics['compression_ratio_csv_to_parquet']:.2f}x",
                f"- 峰值 RSS: {metrics['max_rss_mb']:.2f} MiB",
                f"- 行数校验: source={metrics['validation']['source_rows']}, parquet={metrics['validation']['parquet_rows']}, match={metrics['validation']['row_count_match']}",
                "",
                "## 结论与建议",
                "",
                "- PostgreSQL 逻辑 COPY 导出链路已完成端到端验证；本轮瓶颈以实际指标表为准。",
                "- 当前转换通过 CSV 中间态完成，NUMERIC 在 pandas 侧按 float64 读取，生产级工程化需要补测 Decimal 保真路径。",
                "- MySQL 对比尚未执行；应在 MySQL 镜像可用后按同口径补齐 AC-3/AC-4。",
                "",
                "## 参考资料",
                "",
                "- 本任务 PRD: `prd.md`",
                "- 原始指标: `pg_metrics.json`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
