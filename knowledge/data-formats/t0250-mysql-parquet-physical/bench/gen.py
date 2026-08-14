# 统一评测框架 — 数据生成与校验（PG 18 / MySQL 5.6~8.4 同构）
#
# 7 列模型（与 T0163 同口径）:
#   id BIGINT PK, customer_id INT, amount DECIMAL(12,2), created_at TIMESTAMP,
#   status VARCHAR(16), payload VARCHAR(96), active BOOLEAN/TINYINT
#
# 用法:
#   python3 bench/gen.py --engine pg|mysql --rows 1000000 --outdir data/gen
import argparse
import os
import subprocess
import sys

PG_DSN = dict(host="127.0.0.1", port=5433, user="test", dbname="poct25")
MYSQL_ARGS = dict(host="127.0.0.1", user="root", password="test")


def pg_exec(sql, db="poct25"):
    env = dict(os.environ, PGPASSWORD="")
    cmd = ["podman", "exec", "t0216-pg", "bash", "-lc",
           f"psql -U test -d {db} -v ON_ERROR_STOP=1 -c {_quote(sql)}"]
    subprocess.run(cmd, check=True, capture_output=True)


def _quote(s):
    return "'" + s.replace("'", "'\\''") + "'"


def pg_script(ddl, db="poct25"):
    """向容器内 psql 传递多语句脚本（通过 stdin）"""
    cmd = ["podman", "exec", "-i", "t0216-pg", "bash", "-lc",
           f"psql -U test -d {db} -v ON_ERROR_STOP=1"]
    subprocess.run(cmd, input=ddl.encode(), check=True)


def mysql_exec(sql, port=3306, version="8.0"):
    """容器内 mysql 客户端执行（容器名由 version 推导）"""
    cname = f"t0250-mysql-{version}"
    cmd = ["podman", "exec", "-i", cname, "bash", "-lc",
           f"mysql -uroot -ptest -h127.0.0.1 -P{port} {_quote(sql)}"]
    subprocess.run(cmd, check=True, capture_output=True)


def mysql_script(ddl, port=3306, version="8.0"):
    cname = f"t0250-mysql-{version}"
    cmd = ["podman", "exec", "-i", cname, "bash", "-lc",
           f"mysql -uroot -ptest -h127.0.0.1 -P{port}"]
    subprocess.run(cmd, input=ddl.encode(), check=True)


PG_DDL = """
DROP TABLE IF EXISTS poc_orders;
CREATE TABLE poc_orders (
  id BIGINT PRIMARY KEY,
  customer_id INTEGER NOT NULL,
  amount NUMERIC(12,2) NOT NULL,
  created_at TIMESTAMP NOT NULL,
  status TEXT NOT NULL,
  payload TEXT NOT NULL,
  active BOOLEAN NOT NULL
);
INSERT INTO poc_orders
SELECT
  g AS id,
  (g % 100000)::integer AS customer_id,
  round(((g % 100000)::numeric / 100), 2) AS amount,
  timestamp '2026-01-01 00:00:00' + (g || ' seconds')::interval AS created_at,
  CASE g % 4 WHEN 0 THEN 'new' WHEN 1 THEN 'paid' WHEN 2 THEN 'shipped' ELSE 'closed' END AS status,
  md5(g::text) || repeat('x', 32) AS payload,
  (g % 2 = 0) AS active
FROM generate_series(1, {rows}) AS g;
"""

PG_BOUNDARY_DDL = """
DROP TABLE IF EXISTS poc_boundary;
CREATE TABLE poc_boundary (
  id BIGINT PRIMARY KEY,
  n_null INTEGER,
  s_empty TEXT,
  d_extreme NUMERIC(12,2),
  b_large TEXT,
  u_emoji TEXT,
  t_ts TIMESTAMP,
  act BOOLEAN
);
INSERT INTO poc_boundary VALUES
  (1, NULL, '', 9999999999.99, repeat('x', 9000), 'emoji: 😀🚀é中', '2026-01-01 00:00:00', true),
  (2, NULL, '', -9999999999.99, repeat('y', 7000), 'plain ascii', '2026-12-31 23:59:59', false),
  (3, 42, '   ', 0.00, 'tiny', 'b', '1999-06-15 12:30:00', true);
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", choices=["pg", "mysql"], required=True)
    ap.add_argument("--rows", type=int, default=1000000)
    ap.add_argument("--mode", choices=["orders", "boundary", "all"], default="all")
    args = ap.parse_args()

    if args.engine == "pg":
        if args.mode in ("orders", "all"):
            pg_script(PG_DDL.format(rows=args.rows))
            print(f"[pg] poc_orders {args.rows} 行已灌入")
        if args.mode in ("boundary", "all"):
            pg_script(PG_BOUNDARY_DDL)
            print("[pg] poc_boundary 边界表已灌入")
    elif args.engine == "mysql":
        print("[mysql] 依赖 MySQL 容器就绪，稍后执行")


if __name__ == "__main__":
    main()


MYSQL_DDL = """
DROP TABLE IF EXISTS poc_orders;
CREATE TABLE poc_orders (
  id BIGINT NOT NULL,
  customer_id INT NOT NULL,
  amount DECIMAL(12,2) NOT NULL,
  created_at DATETIME(6) NOT NULL,
  status VARCHAR(16) NOT NULL,
  payload VARCHAR(96) NOT NULL,
  active TINYINT(1) NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB;
INSERT INTO poc_orders
SELECT
  g,
  (g % 1000),
  ROUND((g %% 100000) / 100.0, 2),
  TIMESTAMP('2026-01-01 00:00:00') + INTERVAL g SECOND,
  CASE g %% 4 WHEN 0 THEN 'new' WHEN 1 THEN 'paid' WHEN 2 THEN 'shipped' ELSE 'closed' END,
  CONCAT(MD5(g), REPEAT('x', 32)),
  (g %% 2 = 0)
FROM (SELECT 1 AS g) AS dummy
WHERE FALSE;
"""
