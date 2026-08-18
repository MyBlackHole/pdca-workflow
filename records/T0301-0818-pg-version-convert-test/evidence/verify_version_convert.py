#!/usr/bin/env python3
# T0300 版本转换测试 — 逐版本全量对照（parquet vs SQL）
#
# 用法:
#   python3 bench/verify_version_convert.py <ver> <parquet> <sql_tsv>
#
# 对照内容（全量 1M 行 × 7 列）:
#   1) 行数一致
#   2) 逐字段规范化文本对照（差异数必须 = 0）
#   3) 聚合对照（count / SUM(amount) / distinct status / active=true / id 范围）
#
# 序列化约定（与 mysql -N -B 导出一致）:
#   amount        DECIMAL(12,2) -> 固定 2 位小数文本（如 4999999.99）
#   created_at    DATETIME(6)   -> %Y-%m-%d %H:%M:%S.%f（如 2026-01-01 00:00:01.000000）
#   active        TINYINT(1)    -> 1 / 0
#   NULL          一律为 "NULL" 文本（-N -B 的 NULL 显示）
import argparse
import sys
from decimal import Decimal

import pyarrow.parquet as pq


COLS = ["id", "customer_id", "amount", "created_at", "status", "payload", "active"]


def norm_parquet_row(rec):
    idv = "NULL" if rec["id"] is None else str(rec["id"])
    cid = "NULL" if rec["customer_id"] is None else str(rec["customer_id"])
    amt = rec["amount"]
    amt_s = "NULL" if amt is None else format(amt, "f")
    dt = rec["created_at"]
    dt_s = "NULL" if dt is None else dt.strftime("%Y-%m-%d %H:%M:%S.%f")
    st = "NULL" if rec["status"] is None else rec["status"]
    pl = "NULL" if rec["payload"] is None else rec["payload"]
    ac = rec["active"]
    ac_s = "NULL" if ac is None else ("1" if ac else "0")
    return (idv, cid, amt_s, dt_s, st, pl, ac_s)


def norm_sql_line(line):
    return tuple(line.rstrip("\n").split("\t"))


def agg(rows):
    # rows: iterable of tuples (id, cid, amt_s, dt_s, status, payload, active_s)
    count = 0
    sum_amount = Decimal("0")
    statuses = set()
    active_true = 0
    min_id = None
    max_id = None
    for r in rows:
        count += 1
        if r[2] != "NULL":
            sum_amount += Decimal(r[2])
        if r[4] != "NULL":
            statuses.add(r[4])
        if r[6] == "1":
            active_true += 1
        if r[0] != "NULL":
            v = int(r[0])
            min_id = v if min_id is None else min(min_id, v)
            max_id = v if max_id is None else max(max_id, v)
    return {
        "count": count,
        "sum_amount": str(sum_amount),
        "distinct_status": sorted(statuses),
        "active_true": active_true,
        "id_min": min_id,
        "id_max": max_id,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ver", help="版本标识，如 56/57/80/84")
    ap.add_argument("parquet", help="mysqlbin 输出的 parquet 路径")
    ap.add_argument("sql_tsv", help="mysql -N -B 导出的全量基准 tsv")
    args = ap.parse_args()

    table = pq.read_table(args.parquet)
    parquet_rows = table.to_pylist()
    n_pq = len(parquet_rows)

    # mysqlbin 按物理页序输出，不保证与主键序一致；
    # 以 id 为键排序后再与 SQL（ORDER BY id）逐行对照，全量且顺序无关
    parquet_rows = sorted(parquet_rows, key=lambda r: r["id"])

    with open(args.sql_tsv, "r", encoding="utf-8") as f:
        sql_lines = [l for l in f if l.strip()]
    n_sql = len(sql_lines)

    print(f"[{args.ver}] rows: parquet={n_pq} sql={n_sql}")

    diffs = 0
    diff_by_col = {c: 0 for c in COLS}
    samples = []
    if n_pq != n_sql:
        print(f"[{args.ver}] FAIL: 行数不一致 {n_pq} vs {n_sql}")
        sys.exit(1)

    limit = min(n_pq, n_sql)
    for i in range(limit):
        pr = norm_parquet_row(parquet_rows[i])
        sr = norm_sql_line(sql_lines[i])
        if pr != sr:
            diffs += 1
            if len(samples) < 10:
                samples.append((i, pr, sr))
            for c, a, b in zip(COLS, pr, sr):
                if a != b:
                    diff_by_col[c] += 1

    # 聚合对照
    pa = agg(norm_parquet_row(r) for r in parquet_rows)
    sa = agg(norm_sql_line(l) for l in sql_lines)
    agg_ok = pa == sa

    print(f"[{args.ver}] 全量逐字段差异: {diffs} (必须=0)")
    if diffs:
        print(f"[{args.ver}] 差异列分布: {diff_by_col}")
        for i, pr, sr in samples:
            print(f"  row {i}: parquet={pr}")
            print(f"           sql    ={sr}")
    print(f"[{args.ver}] 聚合对照: {'PASS' if agg_ok else 'FAIL'}")
    print(f"[{args.ver}]   count={pa['count']} sum_amount={pa['sum_amount']} "
          f"distinct_status={pa['distinct_status']} active_true={pa['active_true']} "
          f"id=[{pa['id_min']},{pa['id_max']}]")

    if diffs == 0 and agg_ok and n_pq == n_sql:
        print(f"[{args.ver}] RESULT: PASS")
        sys.exit(0)
    print(f"[{args.ver}] RESULT: FAIL")
    sys.exit(1)


if __name__ == "__main__":
    main()