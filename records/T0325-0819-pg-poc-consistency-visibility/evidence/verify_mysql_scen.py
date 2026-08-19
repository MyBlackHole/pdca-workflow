#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MySQL 场景表（poc_scen_v2..v5）可见性对照：mysqlbin parquet vs SQL 可见行 tsv。

通用 N 列对照：parquet 列集动态读取，按首列排序，NULL 规范化为 'NULL'，
bool 规范化为 1/0（对齐 verify_version_convert 约定）。用于 T0325 可见性矩阵。
"""
import sys
import pyarrow.parquet as pq


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: verify_mysql_scen.py <parquet> <sql_tsv>")
    parquet, tsv_path = sys.argv[1], sys.argv[2]
    tbl = pq.read_table(parquet)
    cols = tbl.column_names
    rows = sorted(tbl.to_pylist(), key=lambda r: r[cols[0]])

    def norm(v):
        if v is None:
            return "NULL"
        if isinstance(v, bool):
            return "1" if v else "0"
        if isinstance(v, (bytes, bytearray)):
            return v.decode("utf-8", "replace")
        return str(v)

    p_rows = [[norm(r[c]) for c in cols] for r in rows]
    tsv = [l.rstrip("\n").split("\t") for l in open(tsv_path, "r", encoding="utf-8") if l.strip()]
    if tsv and len(tsv[0]) != len(cols):
        sys.exit("tsv 列数 %d != parquet 列数 %d" % (len(tsv[0]), len(cols)))

    fail = 0
    for i, (p, s) in enumerate(zip(p_rows, tsv)):
        if p != s:
            fail += 1
            if fail <= 5:
                print("  row %d: parquet=%s" % (i, p))
                print("           sql    =%s" % (s,))
    print("rows: parquet=%d sql=%d 逐字段差异=%d" % (len(p_rows), len(tsv), fail))
    if len(p_rows) == len(tsv) and fail == 0:
        print("RESULT: PASS")
        sys.exit(0)
    print("RESULT: FAIL")
    sys.exit(1)


if __name__ == "__main__":
    main()
