#!/usr/bin/env python3
# T0301 — PG 三版本容器独立灌数 poc_orders 1M 行
#
# 用法: python3 bench/gen_pg_versions.py
# 对 t0301-pg96(9.6)/t0301-pg11(11)/t0216-pg(18) 各执行:
#   建表 poc_orders(7 列, 与 PG18 基线同构) + generate_series 灌数 1,000,000 行
# 数据口径: id=1..1M, customer_id=(g%1000)+1, amount=g*0.01 精确 2 位,
#   created_at=2026-01-01 起 +g 秒, status=4 态轮转, payload=md5+48x, active=(g%2==0)
import subprocess
import sys

CONTAINERS = [
    ("96", "t0301-pg96"),
    ("11", "t0301-pg11"),
    ("18", "t0216-pg"),
]

CREATE = r"""
DROP TABLE IF EXISTS poc_orders;
CREATE TABLE poc_orders (
  id bigint NOT NULL,
  customer_id integer NOT NULL,
  amount numeric(12,2) NOT NULL,
  created_at timestamp NOT NULL,
  status text NOT NULL,
  payload text NOT NULL,
  active boolean NOT NULL,
  PRIMARY KEY (id)
);
INSERT INTO poc_orders
SELECT g,
       (g % 1000) + 1,
       (g * 0.01)::numeric(12,2),
       '2026-01-01 00:00:01'::timestamp + (g || ' seconds')::interval,
       (ARRAY['new','paid','shipped','closed'])[1 + (g % 4)],
       md5(g::text) || repeat('x', 48),
       (g % 2) = 0
FROM generate_series(1, 1000000) g;
"""


def main():
    failed = 0
    for ver, c in CONTAINERS:
        print(f"[{ver}] {c}: 灌数中...")
        r = subprocess.run(
            ["podman", "exec", c, "psql", "-U", "test", "-d", "poct25",
             "-v", "ON_ERROR_STOP=1", "-c", CREATE],
            capture_output=True, text=True)
        if r.returncode != 0:
            print(f"[{ver}] FAIL: {r.stderr[-400:]}")
            failed += 1
            continue
        cnt = subprocess.run(
            ["podman", "exec", c, "psql", "-U", "test", "-d", "poct25",
             "-tAc", "SELECT count(*) FROM poc_orders;"],
            capture_output=True, text=True)
        print(f"[{ver}] count={cnt.stdout.strip()}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()