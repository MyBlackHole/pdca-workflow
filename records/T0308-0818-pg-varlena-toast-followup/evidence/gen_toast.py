#!/usr/bin/env python3
# T0308 — 三版本 PG 转换 TOAST/4B 头 varlena 对照：poc_toast 灌数 + heap/toast/clog 固化 + tsv 基准导出
#
# 用法:
#   python3 bench/gen_toast.py --container t0216-pg --table poc_toast --rows 10000 [--out <dir>]
#
# 形态分桶（id % 200，实测 PG9.6/11/18 一致）:
#   id%200==0   -> md5||repeat('x',2470)  行内压缩 4B 头 varlena（pglz 解压路径）
#   id%200==50  -> 78×md5||repeat('x',2000) 4496B  TOAST external 压缩（extsize<rawsize-4）
#   id%200==100 -> 70×md5 拼接 2240B       TOAST external 未压缩
#   id%200==150 -> 80×md5 拼接 2560B       TOAST external 未压缩
#   id%7==0     -> NULL
#   id%100==0   -> repeat('x',480)         4B 头 varlena（未压缩，>127B）
#   其它        -> md5||repeat('x',48)     1B 头 varlena（≤127B）
#
# 输出（--out 默认 evidence/pg/toast/<ver>/）:
#   poc_toast_heap        主表 heap
#   poc_toast_toast_heap  TOAST 表 heap（reltoastrelid 的 relfilenode）
#   pg_xact | pg_clog     CLOG 目录（按版本）
#   poc_toast.tsv         SQL 基准（COALESCE ::text 规范化, NULL 字面量）
import argparse
import os
import subprocess
import sys

VERS = {"t0216-pg": ("18", "pg_xact"), "t0301-pg11": ("11", "pg_xact"),
        "t0301-pg96": ("96", "pg_clog")}

CREATE = """
DROP TABLE IF EXISTS {table};
CREATE TABLE {table} (
  id bigint NOT NULL,
  customer_id integer,
  amount numeric(12,2),
  created_at timestamp(6),
  status text,
  payload text,
  active boolean,
  PRIMARY KEY (id)
);
INSERT INTO {table}
SELECT g,
  (g%1000)+1,
  (g*0.01)::numeric(12,2),
  '2026-01-01 00:00:01'::timestamp + (g || ' microseconds')::interval,
  (ARRAY['new','paid','shipped','closed'])[1 + (g % 4)],
  CASE WHEN g%200=0 THEN md5(g::text)||repeat('x',2470)
       WHEN g%200=50 THEN (SELECT string_agg(md5(t||'c'||g::text),'') FROM generate_series(1,78) t)||repeat('x',2000)
       WHEN g%200=100 THEN (SELECT string_agg(md5(t||':'||g::text),'') FROM generate_series(1,70) t)
       WHEN g%200=150 THEN (SELECT string_agg(md5(t||'b'||g::text),'') FROM generate_series(1,80) t)
       WHEN g%7=0 THEN NULL
       WHEN g%100=0 THEN repeat('x',480)
       ELSE md5(g::text)||repeat('x',48)
  END,
  (g%2)=0
FROM generate_series(1, {rows}) g;
"""

SELECT_STATS = """
SELECT
  count(*) FILTER (WHERE length(payload) > 2000) AS external_sz,
  count(*) FILTER (WHERE payload IS NULL) AS null_cnt,
  count(*) FILTER (WHERE length(payload) > 127 AND length(payload) <= 2000) AS fourb,
  count(*) AS total
FROM {table};
"""


def run(c, db, args, input_text=None):
    cmd = ["podman", "exec", c, "psql", "-U", "test", "-d", db, "-v", "ON_ERROR_STOP=1"]
    if input_text is not None:
        cmd += ["-A", "-t", "-F", "|", "-c", input_text]
        return subprocess.run(cmd, capture_output=True, text=True)
    cmd += ["-c", input_text]
    return subprocess.run(cmd, capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--container", default="t0216-pg")
    ap.add_argument("--db", default="poct25")
    ap.add_argument("--table", default="poc_toast")
    ap.add_argument("--rows", type=int, default=10000)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    ver, cl = VERS.get(args.container, ("18", "pg_xact"))
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    outdir = args.out or os.path.join(root, "evidence", "pg", "toast", ver)
    os.makedirs(outdir, exist_ok=True)

    c, db, t = args.container, args.db, args.table
    r = run(c, db, None, CREATE.format(table=t, rows=args.rows))
    if r.returncode != 0:
        print("灌数 FAIL:", r.stderr[-500:])
        sys.exit(1)
    print(f"[{c}] {t} 灌数完成")

    r = run(c, db, None, "CHECKPOINT;")
    rel = run(c, db, None,
              f"SELECT pg_relation_filepath('{t}');").stdout.strip().split("|")[0]
    t_rel = run(c, db, None,
                f"SELECT t2.relfilenode FROM pg_class c JOIN pg_class t2 ON t2.oid=c.reltoastrelid "
                f"WHERE c.relname='{t}';").stdout.strip().split("|")[0]
    dboid = rel.split("/")[1]
    print(f"  主表 relfilenode={rel.split('/')[-1]} toast表 relfilenode={t_rel} dboid={dboid}")

    src = subprocess.run(["podman", "inspect", c, "--format", "{{range .Mounts}}{{.Source}}{{end}}"],
                         capture_output=True, text=True).stdout.strip()
    pgdata = subprocess.run(["podman", "exec", c, "sh", "-c", 'echo "$PGDATA"'],
                            capture_output=True, text=True).stdout.strip()
    mntdest = subprocess.run(["podman", "inspect", c, "--format", "{{range .Mounts}}{{.Destination}}{{end}}"],
                             capture_output=True, text=True).stdout.strip()
    base = src + pgdata[len(mntdest):]
    main_rel = rel.split("/")[-1]

    subprocess.run(["podman", "unshare", "sh", "-c",
                    f"cp '{base}/base/{dboid}/{main_rel}' '{outdir}/poc_toast_heap' && "
                    f"cp '{base}/base/{dboid}/{t_rel}' '{outdir}/poc_toast_toast_heap' && "
                    f"rm -rf '{outdir}/{cl}' && cp -rT '{base}/{cl}' '{outdir}/{cl}' && "
                    f"chown -R 0:0 '{outdir}'"],
                   check=True)

    tsv = subprocess.run(
        ["podman", "exec", c, "psql", "-U", "test", "-d", db, "-A", "-t", "-F", "\t", "-c",
         f"SELECT id, "
         f"COALESCE(customer_id::text,'NULL'), "
         f"COALESCE(amount::text,'NULL'), "
         f"COALESCE(to_char(created_at,'YYYY-MM-DD HH24:MI:SS.US'),'NULL'), "
         f"COALESCE(status::text,'NULL'), "
         f"COALESCE(payload::text,'NULL'), "
         f"CASE WHEN active IS NULL THEN 'NULL' WHEN active THEN '1' ELSE '0' END "
         f"FROM {t} ORDER BY id;"],
        capture_output=True, text=True)
    if tsv.returncode != 0:
        print("tsv 导出 FAIL:", tsv.stderr[-300:])
        sys.exit(1)
    with open(os.path.join(outdir, "poc_toast.tsv"), "w") as f:
        f.write(tsv.stdout)
    n = len([l for l in tsv.stdout.splitlines() if l.strip()])
    print(f"  tsv 导出 {n} 行")

    stats = run(c, db, None, SELECT_STATS.format(table=t)).stdout.strip()
    print("  形态分布(external_sz|null|4b|total):", stats.replace("|", " "))
    print("  输出目录:", outdir)


if __name__ == "__main__":
    main()