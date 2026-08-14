#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AC-1 四版本灌数（5.6/5.7/8.0/8.4 通用，不依赖 WITH RECURSIVE）
通过 10 行 seed × 三表 CROSS JOIN 倍增 1M 行，仅用 INSERT..SELECT。
用法: python3 gen_mysql_versions.py <port> <table_suffix>
"""
import subprocess, sys

port, suffix = sys.argv[1], sys.argv[2] or ""
client = ["mysql", "--host=127.0.0.1", f"--port={port}", "-uroot", "-ptest"]

def run(sql, db=None):
    args = client + (["-e", sql] if db is None else [db, "-e", sql])
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        print("[FAIL]", sql[:80], "\n", r.stderr, file=sys.stderr); sys.exit(1)
    return r.stdout

run("CREATE DATABASE IF NOT EXISTS poct25;")
tb = f"poc_orders{suffix}"

# 行格式按版本差异验证 COMPACT vs DYNAMIC：
# 5.6 默认 COMPACT；5.7 默认 DYNAMIC；8.0/8.4 默认 DYNAMIC
DDL = f"""DROP TABLE IF EXISTS poct25.{tb};
CREATE TABLE poct25.{tb} (
  id BIGINT NOT NULL,
  customer_id INT NOT NULL,
  amount DECIMAL(12,2) NOT NULL,
  created_at DATETIME(6) NOT NULL,
  status VARCHAR(16) NOT NULL,
  payload VARCHAR(96) NOT NULL,
  active TINYINT(1) NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB;"""
run(DDL)
# 用持久表构造 10^6 组合
run("DROP TABLE IF EXISTS poct25._seq10; CREATE TABLE poct25._seq10 (n INT);")
run("INSERT INTO poct25._seq10 VALUES (0),(1),(2),(3),(4),(5),(6),(7),(8),(9);")
print(f"[{port}] 灌入 1M 行 {tb} ...")
INS = f"""INSERT INTO poct25.{tb}
SELECT
  h.n*100000 + k.n*10000 + t.n*1000 + x.n*100 + y.n*10 + z.n + 1,
  ((h.n*100000 + k.n*10000 + t.n*1000 + x.n*100 + y.n*10 + z.n) % 1000) + 1,
  ROUND(((h.n*100000 + k.n*10000 + t.n*1000 + x.n*100 + y.n*10 + z.n) % 100000) / 100.0, 2),
  TIMESTAMP('2026-01-01 00:00:00') + INTERVAL (h.n*100000 + k.n*10000 + t.n*1000 + x.n*100 + y.n*10 + z.n + 1) SECOND,
  ELT(((h.n*100000 + k.n*10000 + t.n*1000 + x.n*100 + y.n*10 + z.n) % 4) + 1, 'new','paid','shipped','closed'),
  CONCAT(MD5(h.n*100000 + k.n*10000 + t.n*1000 + x.n*100 + y.n*10 + z.n + 1), REPEAT('x',32)),
  ((h.n*100000 + k.n*10000 + t.n*1000 + x.n*100 + y.n*10 + z.n) % 2 = 0)
FROM poct25._seq10 h, poct25._seq10 k, poct25._seq10 t,
     poct25._seq10 x, poct25._seq10 y, poct25._seq10 z;"""
run(INS)
run("DROP TABLE IF EXISTS poct25._seq10;")
print(run("SELECT COUNT(*) AS cnt FROM poct25.%s;" % tb))
