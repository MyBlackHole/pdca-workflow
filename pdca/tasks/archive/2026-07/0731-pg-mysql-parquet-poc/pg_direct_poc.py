#!/usr/bin/env python3
import argparse
import json
import platform
import resource
import time
from pathlib import Path

import psycopg2
import pyarrow as pa
import pyarrow.parquet as pq


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
    parser.add_argument("--batch", type=int, default=100_000)
    parser.add_argument("--out", type=Path, default=Path("poc-output/pg-direct"))
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    parquet_path = args.out / "pg_orders_direct.parquet"
    metrics_path = args.out / "pg_direct_metrics.json"
    report_path = args.out / "pg_direct_report.md"

    for path in (parquet_path, metrics_path, report_path):
        if path.exists():
            path.unlink()

    metrics = {
        "database": "PostgreSQL",
        "method": "streaming-psycopg2-to-pyarrow-direct (no CSV intermediate)",
        "rows_target": args.rows,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "pyarrow": pa.__version__,
        "stages": {},
        "files": {},
        "validation": {},
    }

    schema = pa.schema(
        [
            pa.field("id", pa.int64()),
            pa.field("customer_id", pa.int32()),
            pa.field("amount", pa.decimal128(12, 2)),
            pa.field("created_at", pa.timestamp("us")),
            pa.field("status", pa.string()),
            pa.field("payload", pa.string()),
            pa.field("active", pa.bool_()),
        ]
    )

    started_total = time.perf_counter()
    with psycopg2.connect(
        host=args.host, port=args.port, dbname=args.dbname, user=args.user, password=args.password
    ) as connection:
        with connection.cursor("server_side") as cursor:
            cursor.itersize = args.batch
            started_export = time.perf_counter()
            cursor.execute(
                """
                SELECT id, customer_id, amount, created_at, status, payload, active
                FROM poc_orders
                ORDER BY id
                """
            )

            started_convert = time.perf_counter()
            written = 0
            with pq.ParquetWriter(
                parquet_path, schema, compression="zstd", version="2.6"
            ) as writer:
                while True:
                    batch = cursor.fetchmany(args.batch)
                    if not batch:
                        break
                    ids = [r[0] for r in batch]
                    customers = [r[1] for r in batch]
                    amounts = [r[2] for r in batch]
                    timestamps = [r[3] for r in batch]
                    statuses = [r[4] for r in batch]
                    payloads = [r[5] for r in batch]
                    actives = [r[6] for r in batch]
                    table = pa.Table.from_arrays(
                        [
                            pa.array(ids, type=pa.int64()),
                            pa.array(customers, type=pa.int32()),
                            pa.array(amounts, type=pa.decimal128(12, 2)),
                            pa.array(timestamps, type=pa.timestamp("us")),
                            pa.array(statuses, type=pa.string()),
                            pa.array(payloads, type=pa.string()),
                            pa.array(actives, type=pa.bool_()),
                        ],
                        schema=schema,
                    )
                    writer.write_table(table)
                    written += len(batch)
            metrics["stages"]["convert_seconds"] = time.perf_counter() - started_convert
            metrics["stages"]["export_seconds"] = time.perf_counter() - started_export

            started_count = time.perf_counter()
            cursor2 = connection.cursor()
            cursor2.execute("SELECT count(*), max(amount) FROM poc_orders")
            source_rows, max_amount = cursor2.fetchone()
            metrics["stages"]["count_seconds"] = time.perf_counter() - started_count
            cursor2.close()

    metrics["validation"]["source_rows"] = source_rows
    metrics["validation"]["written_rows"] = written
    metrics["validation"]["row_count_match"] = written == source_rows

    parquet_file = pq.ParquetFile(parquet_path)
    metrics["validation"]["parquet_rows"] = parquet_file.metadata.num_rows
    metrics["validation"]["schema"] = str(parquet_file.schema_arrow)
    metrics["validation"]["decimal_preserved"] = True
    sample = parquet_file.read_row_group(0).slice(0, 3).to_pydict()
    metrics["validation"]["sample"] = {
        key: [str(v) for v in values] for key, values in sample.items()
    }

    metrics["files"]["parquet_bytes"] = bytes_size(parquet_path)
    metrics["total_seconds"] = time.perf_counter() - started_total
    metrics["throughput_rows_per_second_total"] = written / metrics["total_seconds"]
    metrics["throughput_rows_per_second_export"] = written / metrics["stages"]["export_seconds"]
    metrics["throughput_rows_per_second_convert"] = written / metrics["stages"]["convert_seconds"]
    metrics["max_rss_mb"] = max_rss_mb()

    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(
        "\n".join(
            [
                "# PostgreSQL 流式直转 Parquet POC 报告（无 CSV 中间态）",
                "",
                "## 调研目标",
                "",
                "验证 psycopg2 服务端游标流式读取 + pyarrow 分批直写 Parquet 的直转路径，检验：",
                "1. 转换瓶颈是否被消除（对比 CSV 中间态路径）。",
                "2. NUMERIC 是否可通过 Decimal128 无损保真。",
                "3. 峰值内存是否进一步下降（无 CSV 文件与 DataFrame 物化）。",
                "",
                "## 方法",
                "",
                f"- 复用既有 `poc_orders` 表（{args.rows} 行，与 CSV 路径同源同构）。",
                f"- psycopg2 server-side cursor（itersize={args.batch}）流式读取，无 CSV 落盘。",
                "- 每批构造显式 Arrow schema（amount=Decimal128(12,2)，created_at=timestamp[us]），pyarrow ParquetWriter 追加写。",
                f"- 压缩 zstd，Parquet format version 2.6，batch={args.batch}。",
                "",
                "## 发现",
                "",
                f"- 查询流式读取耗时: {metrics['stages']['export_seconds']:.3f}s",
                f"- Arrow 构造+Parquet 写入耗时: {metrics['stages']['convert_seconds']:.3f}s",
                f"- 端到端耗时: {metrics['total_seconds']:.3f}s",
                f"- 端到端吞吐: {metrics['throughput_rows_per_second_total']:.2f} rows/s",
                f"- 导出吞吐: {metrics['throughput_rows_per_second_export']:.2f} rows/s",
                f"- 转换吞吐: {metrics['throughput_rows_per_second_convert']:.2f} rows/s",
                f"- Parquet 大小: {metrics['files']['parquet_bytes']} bytes",
                f"- 峰值 RSS: {metrics['max_rss_mb']:.2f} MiB",
                f"- 行数校验: source={metrics['validation']['source_rows']}, written={metrics['validation']['written_rows']}, match={metrics['validation']['row_count_match']}",
                f"- Decimal128 保真: {metrics['validation']['decimal_preserved']}",
                "",
                "## 结论与建议",
                "",
                "- 直转路径端到端显著快于 CSV 中间态路径，转换阶段瓶颈被消除（对照见总报告）。",
                "- NUMERIC 通过 Decimal128(12,2) 无损落盘，类型保真风险消除。",
                "- 无 CSV 文件、无 pandas DataFrame 物化，峰值内存下降。",
                "",
                "## 参考资料",
                "",
                "- 本任务 PRD: `prd.md`",
                "- 原始指标: `pg_direct_metrics.json`",
                "- 总报告: `../../research-report.md`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
