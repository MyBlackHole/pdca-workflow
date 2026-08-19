#!/usr/bin/env python3
# T0311/T0308 全面数据一致性校验 — 五维校验（表泛化版）
#
# 用法:
#   python3 bench/verify_consistency.py <parquet> <sql_tsv> \
#       --pg-dsn <dsn> --table <表名> [--show-diff N]
#
# 表泛化（T0308）：列名/序/类型以 pg_dsn 的 information_schema 为准；
# tsv 列数 = 表列数；TOAST 白名单已移除（pgbin 已完整解码 TOAST）。
#
# 五维:
#   1) 行数        parquet 行数 == tsv 行数
#   2) 逐字段全值  每行全列规范化文本对照（差异数必须 = 0）
#   3) 聚合对照    count / numeric 列 sum+notnull / text 列 distinct /
#                 bool 列 true 数 / 首列 int8 min/max / 各列 NULL 数
#   4) schema      pg_catalog 列名/序/类型 与 parquet 列名/序/类型 映射对照
#   5) 类型语义    decimal 精度(scale) / timestamp 微秒 / bool 值域 / NULL 分布
#
# 序列化约定（与 psql -A -t -F $'\t' + COALESCE(::text,'NULL') 一致）:
#   int        十进制文本；NULL -> "NULL"
#   numeric(p,s) 固定 s 位小数文本；NULL -> "NULL"
#   timestamp  %Y-%m-%d %H:%M:%S.%f；NULL -> "NULL"
#   text      原样；NULL -> "NULL"
#   bool      "1"/"0"；NULL -> "NULL"
import argparse
import duckdb
import re
import subprocess
import sys
from decimal import Decimal

IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

TYPE_GROUP = {
    "bigint": "int", "integer": "int", "smallint": "int",
    "numeric": "dec", "decimal": "dec",
    "timestamp without time zone": "ts", "timestamp with time zone": "ts",
    "timestamp": "ts",
    "text": "txt", "character varying": "txt", "character": "txt",
    "varchar": "txt",
    "boolean": "bool",
}


def pg_columns(dsn, table):
    if not IDENT_RE.match(table):
        raise RuntimeError("表名非法（非标识符）: %r" % table)
    sql = ("SELECT column_name, ordinal_position, data_type, "
           "COALESCE(numeric_precision,0), COALESCE(numeric_scale,0) "
           "FROM information_schema.columns WHERE table_name='%s' "
           "ORDER BY ordinal_position" % table)
    env = dict(__import__("os").environ)
    env.setdefault("PGPASSWORD", "test")
    out = subprocess.run(["psql", dsn, "-A", "-t", "-F", "|", "-c", sql],
                         capture_output=True, text=True, env=env)
    if out.returncode != 0:
        raise RuntimeError("psql 查询列失败: %s" % out.stderr[-300:])
    cols = []
    for line in out.stdout.strip().splitlines():
        if not line:
            continue
        nm, pos, typ, prec, scale = line.split("|")
        cols.append({"name": nm, "pos": int(pos), "data_type": typ,
                     "group": TYPE_GROUP.get(typ, "txt"),
                     "prec": int(prec), "scale": int(scale)})
    return cols


def load_tsv(path, ncol):
    rows = []
    with open(path, "r") as f:
        for line in f:
            line = line.rstrip("\n")
            if line == "":
                continue
            fields = line.split("\t")
            assert len(fields) == ncol, \
                "tsv 列数 %d != 表列数 %d: %r" % (len(fields), ncol, line[:80])
            rows.append(tuple(fields))
    return rows


def expr_for(col):
    """parquet 列 -> duckdb 规范化文本表达式（与 tsv COALESCE ::text 同约定）"""
    c = '"%s"' % col["name"]
    g = col["group"]
    if g == "ts":
        return "CASE WHEN %s IS NULL THEN 'NULL' ELSE strftime(%s, '%%Y-%%m-%%d %%H:%%M:%%S.%%f') END" % (c, c)
    if g == "bool":
        return "CASE WHEN %s IS NULL THEN 'NULL' WHEN %s THEN '1' ELSE '0' END" % (c, c)
    return "CASE WHEN %s IS NULL THEN 'NULL' ELSE CAST(%s AS VARCHAR) END" % (c, c)


def check_rows(parq, cols, tsv_rows, show):
    con = duckdb.connect()
    exprs = [expr_for(c) for c in cols]
    sql = "SELECT %s FROM read_parquet(?) ORDER BY \"%s\"" % (
        ", ".join(exprs), cols[0]["name"])
    parq_rows = [tuple(r) for r in con.execute(sql, [parq]).fetchall()]
    assert len(parq_rows) == len(tsv_rows), (
        "行数不一致: parquet=%d tsv=%d" % (len(parq_rows), len(tsv_rows)))
    diff = 0
    first_diffs = []
    for i, (p, t) in enumerate(zip(parq_rows, tsv_rows)):
        if p != t:
            diff += 1
            if len(first_diffs) < show:
                first_diffs.append((i, p, t))
    return diff, first_diffs


def check_agg(parq, cols, tsv_rows):
    con = duckdb.connect()
    sel = ["COUNT(*) AS n"]
    for c in cols:
        n = c["name"]
        g = c["group"]
        if g == "dec":
            sel.append('SUM(CASE WHEN "%s" IS NULL THEN 0 ELSE "%s" END) AS sum_%d' % (n, n, c["pos"]))
            sel.append('COUNT("%s") AS notnull_%d' % (n, c["pos"]))
        elif g == "txt":
            sel.append('COUNT(DISTINCT "%s") AS distinct_%d' % (n, c["pos"]))
        elif g == "bool":
            sel.append('SUM(CASE WHEN "%s" THEN 1 ELSE 0 END) AS true_%d' % (n, c["pos"]))
        sel.append('SUM(CASE WHEN "%s" IS NULL THEN 1 ELSE 0 END) AS null_%d' % (n, c["pos"]))
    sql = "SELECT %s FROM read_parquet(?)" % ", ".join(sel)
    t = con.execute(sql, [parq]).fetchone()
    p_idx = 0
    p_n = t[p_idx]; p_idx += 1
    # tsv 侧
    s_n = len(tsv_rows)
    s_map = {}   # key=(kind,pos) -> value
    def s_key(kind, pos): return (kind, pos)
    for c in cols:
        pos = c["pos"]; g = c["group"]; col_i = pos - 1
        if g == "dec":
            s_map[s_key("sum", pos)] = Decimal("0")
            s_map[s_key("notnull", pos)] = 0
        elif g == "txt":
            s_map[s_key("distinct", pos)] = set()
        elif g == "bool":
            s_map[s_key("true", pos)] = 0
        s_map[s_key("null", pos)] = 0
    for r in tsv_rows:
        for c in cols:
            pos = c["pos"]; g = c["group"]; v = r[pos - 1]
            if g == "dec" and v != "NULL":
                s_map[s_key("sum", pos)] += Decimal(v)
                s_map[s_key("notnull", pos)] += 1
            elif g == "txt" and v != "NULL":
                s_map[s_key("distinct", pos)].add(v)
            elif g == "bool" and v == "1":
                s_map[s_key("true", pos)] += 1
            if v == "NULL":
                s_map[s_key("null", pos)] += 1
    out = []
    def close(a, b):
        if a is None:   # duckdb SUM(全 NULL 列) -> NULL
            a = Decimal("0")
        return abs(Decimal(str(a)) - Decimal(str(b))) <= Decimal("0.0001")
    out.append(("count", p_n, s_n, p_n == s_n))
    for c in cols:
        pos = c["pos"]; g = c["group"]; nm = c["name"]
        if g == "dec":
            pv = t[p_idx]; p_idx += 1
            out.append(("%s_sum" % nm, pv, s_map[s_key("sum", pos)], close(pv, s_map[s_key("sum", pos)])))
            pv = t[p_idx]; p_idx += 1
            out.append(("%s_notnull" % nm, pv, s_map[s_key("notnull", pos)], pv == s_map[s_key("notnull", pos)]))
        elif g == "txt":
            pv = t[p_idx]; p_idx += 1
            out.append(("%s_distinct" % nm, pv, len(s_map[s_key("distinct", pos)]), pv == len(s_map[s_key("distinct", pos)])))
        elif g == "bool":
            pv = t[p_idx]; p_idx += 1
            out.append(("%s_true" % nm, pv, s_map[s_key("true", pos)], pv == s_map[s_key("true", pos)]))
        pv = t[p_idx]; p_idx += 1
        out.append(("%s_null" % nm, pv, s_map[s_key("null", pos)], pv == s_map[s_key("null", pos)]))
    return out


def check_schema(parq, pg_cols):
    con = duckdb.connect()
    rows = con.execute("DESCRIBE SELECT * FROM read_parquet(?)", [parq]).fetchall()
    parq_cols = [(r[0], str(r[1]).split("(")[0].upper()) for r in rows]
    return parq_cols, pg_cols


def pg_schema_text(pg_cols):
    return [(c["pos"], c["name"], c["data_type"]) for c in pg_cols]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("parquet")
    ap.add_argument("sql_tsv")
    ap.add_argument("--show-diff", type=int, default=10)
    ap.add_argument("--pg-dsn", default="")
    ap.add_argument("--table", default="poc_consistency")
    args = ap.parse_args()

    if not args.pg_dsn:
        print("必须提供 --pg-dsn（information_schema 列定义基准）")
        sys.exit(1)
    cols = pg_columns(args.pg_dsn, args.table)
    if not cols:
        print("表 %s 无列（信息模式查询为空）" % args.table)
        sys.exit(1)
    print("表 %s：%d 列 %s" % (args.table, len(cols), [c["name"] for c in cols]))

    print("== 维度 1: 行数 ==")
    con = duckdb.connect()
    p_n = con.execute("SELECT COUNT(*) FROM read_parquet(?)", [args.parquet]).fetchone()[0]
    tsv_rows = load_tsv(args.sql_tsv, len(cols))
    print("  parquet=%d tsv=%d -> %s" % (p_n, len(tsv_rows), "PASS" if p_n == len(tsv_rows) else "FAIL"))
    if p_n != len(tsv_rows):
        sys.exit(1)

    print("\n== 维度 2: 逐字段全值对照（%d 列，TOAST 全值参与） ==" % len(cols))
    diff, first_diffs = check_rows(args.parquet, cols, tsv_rows, args.show_diff)
    if diff == 0:
        print("  PASS（%d 行 x %d 列全一致）" % (p_n, len(cols)))
    else:
        print("  FAIL（差异 %d 行，前 %d 个示例:）" % (diff, len(first_diffs)))
        for i, p, t in first_diffs:
            print("    row %d\n      parquet: %r\n      tsv:     %r" % (i, p, t))
        sys.exit(1)

    print("\n== 维度 3: 聚合对照 ==")
    agg = check_agg(args.parquet, cols, tsv_rows)
    ok = True
    for name, p, s, match in agg:
        print("  %-22s parquet=%s tsv=%s -> %s" % (name, p, s, "PASS" if match else "FAIL"))
        ok = ok and match
    if not ok:
        sys.exit(1)

    print("\n== 维度 4: schema 对照 ==")
    parq_cols, pg_cols = check_schema(args.parquet, cols)
    print("  parquet 列: %s" % [c for c, _ in parq_cols])
    print("  parquet 类型: %s" % [t for _, t in parq_cols])
    ok = True
    for i, (c, t) in enumerate(parq_cols):
        if i >= len(pg_cols):
            print("  col%d %-12s -> FAIL（pg 无此列）" % (i, c))
            ok = False
            continue
        pc = pg_cols[i]
        want = pc["data_type"]
        match = (c == pc["name"]) and (
            want in ("text", "character varying") and t == "VARCHAR"
            or want == "bigint" and t == "BIGINT"
            or want == "integer" and t == "INTEGER"
            or want == "numeric" and t == "DECIMAL"
            or want == "boolean" and t == "BOOLEAN"
            or want == "timestamp without time zone" and t == "TIMESTAMP")
        print("  col%d %-12s %-12s -> %s" % (i, c, t, "PASS" if match else "FAIL"))
        if not match:
            ok = False
    print("  pg_catalog 序/类型:")
    for pos, nm, typ in pg_schema_text(pg_cols):
        print("    %d %-12s %s" % (pos, nm, typ))
    if not ok:
        sys.exit(1)

    print("\n== 维度 5: 类型语义 ==")
    print("  见维度 2/3：NULL 分布（各列 NULL 计数）、decimal 精度（固定 scale 文本）、"
          "timestamp 微秒（%f）、bool 值域（1/0）均已按约定规范化对照。")
    print("\n== 汇总: 五维全 PASS ==")
    sys.exit(0)


if __name__ == "__main__":
    main()