#!/usr/bin/env python3
import argparse
import json
import platform
import resource
import subprocess
import time
from pathlib import Path

import duckdb


def bytes_size(path):
    return path.stat().st_size if path.exists() else 0


def max_rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--heap", type=Path, default=Path("/tmp/opencode/pgfiledump-test/poc_orders_heap"))
    parser.add_argument("--pgfiledump", type=Path, default=Path("/tmp/opencode/pgfiledump-test/pg_filedump"))
    parser.add_argument("--rows", type=int, default=1_000_000)
    parser.add_argument("--out", type=Path, default=Path("poc-output/pg-filedump"))
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    tsv_path = args.out / "poc_orders_filedump.tsv"
    parquet_path = args.out / "pg_filedump.parquet"
    metrics_path = args.out / "pg_filedump_metrics.json"
    report_path = args.out / "pg_filedump_report.md"

    for path in (tsv_path, parquet_path, metrics_path, report_path):
        if path.exists():
            path.unlink()

    metrics = {
        "database": "PostgreSQL",
        "method": "pg_filedump direct heap file decode (physical path, no SQL server involvement)",
        "rows_target": args.rows,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "duckdb": duckdb.__version__,
        "heap_bytes": bytes_size(args.heap),
        "stages": {},
        "files": {},
        "validation": {},
    }

    started_total = time.perf_counter()

    started = time.perf_counter()
    with tsv_path.open("w", encoding="utf-8", newline="") as handle:
        completed = subprocess.run(
            [str(args.pgfiledump), "-D", "bigint,int,numeric,timestamp,text,text,bool", str(args.heap)],
            check=True,
            stdout=handle,
            stderr=subprocess.PIPE,
            text=True,
        )
    metrics["stages"]["filedump_decode_seconds"] = time.perf_counter() - started
    metrics["files"]["filedump_tsv_bytes"] = bytes_size(tsv_path)

    started = time.perf_counter()
    clean_path = args.out / "poc_orders_clean.tsv"
    with tsv_path.open("r", encoding="utf-8") as source, clean_path.open("w", encoding="utf-8", newline="") as target:
        for line in source:
            if line.startswith("COPY: "):
                target.write(line[len("COPY: ") :])
    metrics["stages"]["tsv_clean_seconds"] = time.perf_counter() - started
    metrics["files"]["clean_tsv_bytes"] = bytes_size(clean_path)

    con = duckdb.connect()
    started = time.perf_counter()
    con.execute(
        f"""
        COPY (
          SELECT
            CAST(column0 AS BIGINT) AS id,
            CAST(column1 AS INTEGER) AS customer_id,
            CAST(column2 AS DECIMAL(12,2)) AS amount,
            CAST(column3 AS TIMESTAMP) AS created_at,
            CAST(column4 AS VARCHAR) AS status,
            CAST(column5 AS VARCHAR) AS payload,
            CAST(column6 AS BOOLEAN) AS active
          FROM read_csv('{clean_path}', header = false, delim = '\\t',
                        columns = {{'column0': 'VARCHAR', 'column1': 'VARCHAR',
                                    'column2': 'VARCHAR', 'column3': 'VARCHAR',
                                    'column4': 'VARCHAR', 'column5': 'VARCHAR',
                                    'column6': 'VARCHAR'}})
        ) TO '{parquet_path}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """
    )
    metrics["stages"]["duckdb_convert_seconds"] = time.perf_counter() - started
    con.close()

    metrics["files"]["parquet_bytes"] = bytes_size(parquet_path)
    metrics["total_seconds"] = time.perf_counter() - started_total

    con = duckdb.connect()
    count = con.execute(f"SELECT count(*) FROM read_parquet('{parquet_path}')").fetchone()[0]
    schema = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{parquet_path}')").fetchall()
    metrics["validation"]["parquet_rows"] = count
    metrics["validation"]["row_count_match"] = count == args.rows
    metrics["validation"]["schema"] = [{"name": row[0], "type": str(row[1])} for row in schema]
    sample = con.execute(
        f"SELECT * FROM read_parquet('{parquet_path}') LIMIT 3"
    ).fetchall()
    metrics["validation"]["sample"] = [[str(v) for v in row] for row in sample]
    con.close()

    metrics["throughput_rows_per_second_total"] = args.rows / metrics["total_seconds"]
    metrics["throughput_rows_per_second_decode"] = args.rows / metrics["stages"]["filedump_decode_seconds"]
    metrics["throughput_rows_per_second_convert"] = args.rows / metrics["stages"]["duckdb_convert_seconds"]
    metrics["max_rss_mb"] = max_rss_mb()

    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(
        "\n".join(
            [
                "# PostgreSQL 数据文件直接转 Parquet POC 报告（物理路径）",
                "",
                "## 调研目标",
                "",
                "验证绕开 SQL 服务层的物理路径：用 pg_filedump 直接解析 PG heap 数据文件并转 Parquet，",
                "对照逻辑路径（COPY/查询流式）评估吞吐、可行性和限制。",
                "",
                "## 方法",
                "",
                f"- 源数据: `{args.heap}`（poc_orders 的 main fork，{metrics['heap_bytes']} bytes，CHECKPOINT 后从容器拷出）。",
                "- 解码: `pg_filedump -D bigint,int,numeric,timestamp,text,text,bool <heap>` → COPY 风格 TSV。",
                "- 预处理: 剥离每行 `COPY: ` 前缀。",
                f"- 转换: DuckDB read_csv(TSV) → PARQUET ZSTD（显式 Decimal128(12,2)）。",
                "",
                "## 发现",
                "",
                f"- pg_filedump 解码耗时: {metrics['stages']['filedump_decode_seconds']:.3f}s，吞吐 {metrics['throughput_rows_per_second_decode']:.2f} rows/s",
                f"- 解码 TSV 大小: {metrics['files']['filedump_tsv_bytes']} bytes",
                f"- 前缀清理耗时: {metrics['stages']['tsv_clean_seconds']:.3f}s",
                f"- DuckDB 转换耗时: {metrics['stages']['duckdb_convert_seconds']:.3f}s",
                f"- 端到端耗时: {metrics['total_seconds']:.3f}s，吞吐 {metrics['throughput_rows_per_second_total']:.2f} rows/s",
                f"- Parquet 大小: {metrics['files']['parquet_bytes']} bytes",
                f"- 峰值 RSS: {metrics['max_rss_mb']:.2f} MiB",
                f"- 行数校验: source=1000000, parquet={metrics['validation']['parquet_rows']}, match={metrics['validation']['row_count_match']}",
                f"- schema: {json.dumps(metrics['validation']['schema'], ensure_ascii=False)}",
                "",
                "## 结论与建议",
                "",
                "- 物理路径可行且不依赖运行中的 PG 服务（可用于冷备份/离线迁移场景）。",
                "- 吞吐与限制对照见总报告 research-report.md 第 6 节。",
                "",
                "## 参考资料",
                "",
                "- 本任务 PRD: `prd.md`",
                "- 原始指标: `pg_filedump_metrics.json`",
                "- 总报告: `../../research-report.md`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
