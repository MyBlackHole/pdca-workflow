#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MySQL 8.0 数据准备（T0250 InnoDB 侧）
生成 poc_orders 1M + poc_boundary，用 innodb_fast_shutdown=1 完整关闭后由
container stop 固化，供 .ibd 物理直读。
"""
import subprocess
import sys

client = ["podman", "exec", "t0250-mysql8", "mysql", "-uroot", "-ptest", "poct25"]

def run(sql):
    r = subprocess.run(client + ["-e", sql], capture_output=True, text=True)
    if r.returncode != 0:
        print("[FAIL]", sql[:60], "\n", r.stderr, file=sys.stderr)
        sys.exit(1)
    return r.stdout

run("USE poct25;")


DDL = """CREATE TABLE poc_orders (
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

# 1M 行用递归 CTE（每步 1M 行，避免 recursion limit — 用 seed 0..999999 + row 直接插入）
rows = sys.argv[1] if len(sys.argv) > 1 else "1000000"
print(f"[mysql] 灌入 {rows} 行 poc_orders ...")
INS = f"""INSERT INTO poc_orders
WITH RECURSIVE seq AS (
  SELECT 0 AS g
  UNION ALL
  SELECT g + 1 FROM seq WHERE g < {int(rows) - 1}
)
SELECT
  g + 1,
  (g % 1000) + 1,
  ROUND((g % 100000) / 100.0, 2),
  TIMESTAMP('2026-01-01 00:00:00') + INTERVAL (g + 1) SECOND,
  ELT((g % 4) + 1, 'new', 'paid', 'shipped', 'closed'),
  CONCAT(MD5(g + 1), REPEAT('x', 32)),
  (g % 2 = 0)
FROM seq;"""
run("SET SESSION cte_max_recursion_depth = 1100000; " + INS)
out = run("USE poct25; SELECT COUNT(*) AS cnt FROM poc_orders;")
print(out)

# 边界表
run("DROP TABLE IF EXISTS poc_boundary;")
run("""CREATE TABLE poc_boundary (
  id BIGINT PRIMARY KEY,
  n_null INT,
  s_empty TEXT,
  d_extreme DECIMAL(12,2),
  b_large TEXT,
  u_emoji TEXT,
  t_ts DATETIME(6),
  act TINYINT(1)
) ENGINE=InnoDB;""")
run("""INSERT INTO poc_boundary VALUES
  (1, NULL, '', 9999999999.99, REPEAT('x', 9000), 'emoji: 😀🚀é中', '2026-01-01 00:00:00', 1),
  (2, NULL, '', -9999999999.99, REPEAT('y', 7000), 'plain ascii', '2026-12-31 23:59:59', 0),
  (3, 42, '   ', 0.00, 'tiny', 'b', '1999-06-15 12:30:00', 1);""")
print("[mysql] boundary ok")

# 统计表大小与文件位置
print("== 校验 ==")
print(run("""USE poct25; SELECT COUNT(*) cnt, COUNT(DISTINCT id) ids,
                 MIN(amount) min_a, MAX(amount) max_a, COUNT(DISTINCT status) st,
                 SUM(active) act_t FROM poc_orders;"""))
print("== 表空间文件 ==")
print(run("""SELECT name FROM information_schema.innodb_tablespaces
             WHERE name IN ('poct25/poc_orders','poct25/poc_boundary');"""))