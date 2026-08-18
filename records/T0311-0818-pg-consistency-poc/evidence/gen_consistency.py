#!/usr/bin/env python3
# T0311 — PG 转换一致性校验 POC：合成表 poc_consistency 灌数
#
# 用法: python3 bench/gen_consistency.py
# 对 PG18 容器 t0216-pg(库 poct25, user test) 建表并灌数 100,000 行。
#
# 设计(选项 A)：复用 pgbin 支持的 poc_orders 同构 7 列，但值形态做足，
# 聚焦校验方法的形态盲区：
#   - NULL 三形态(稀疏): customer_id(19%)/amount(23%)/created_at(29%)/
#     status(7%)/payload(13%)/active(17%)
#   - 文本形态: 空串/全空白/中文+emoji/超长 payload(>127B 触发 4B 头 varlena;
#     >2KB 触发 TOAST 仅登记)
#   - 数值边界: amount 0/0.00/负/最大精度(99999999.99); customer_id 0/负
#   - 时间边界: epoch 起, 微秒(6 位)、跨日、整秒
#   - bool 边界: 全部 false / true 轮转
import subprocess
import sys

CONTAINER = "t0216-pg"
ROWS = 100000

CREATE = r"""
DROP TABLE IF EXISTS poc_consistency;
CREATE TABLE poc_consistency (
  id bigint NOT NULL,
  customer_id integer,
  amount numeric(12,2),
  created_at timestamp(6),
  status text,
  payload text,
  active boolean,
  PRIMARY KEY (id)
);
-- 基础行 + 形态注入(按 id 取模分桶)
INSERT INTO poc_consistency
SELECT
  g,
  CASE
    WHEN g % 19 = 0 THEN NULL
    WHEN g % 997 = 0 THEN -1
    WHEN g % 991 = 0 THEN 0
    ELSE (g % 1000) + 1
  END,
  CASE
    WHEN g % 23 = 0 THEN NULL
    WHEN g % 983 = 0 THEN 0.00
    WHEN g % 977 = 0 THEN -123.45
    WHEN g % 971 = 0 THEN 99999999.99
    ELSE (g * 0.01)::numeric(12,2)
  END,
  CASE
    WHEN g % 29 = 0 THEN NULL
    WHEN g % 967 = 0 THEN '2026-01-01 00:00:00'::timestamp(6)
    WHEN g % 953 = 0 THEN '2026-01-02 23:59:59.999999'::timestamp(6)
    ELSE '2026-01-01 00:00:01'::timestamp(6) + (g || ' microseconds')::interval
  END,
  CASE
    WHEN g % 7 = 0 THEN NULL
    WHEN g % 947 = 0 THEN ''
    WHEN g % 941 = 0 THEN '   '
    WHEN g % 937 = 0 THEN '测试-中文-emoji-🚀'
    ELSE (ARRAY['new','paid','shipped','closed'])[1 + (g % 4)]
  END,
  CASE
    WHEN g % 13 = 0 THEN NULL
    WHEN g % 929 = 0 THEN ''
    WHEN g % 120 = 0 THEN md5(g::text) || repeat('长文', 80)   -- ~480B, 4B 头 varlena
    WHEN g % 500 = 0 THEN md5(g::text) || repeat('x', 2500)    -- ~2564B, TOAST(登记不判错)
    ELSE md5(g::text) || repeat('x', 48)
  END,
  CASE
    WHEN g % 17 = 0 THEN NULL
    WHEN g % 923 = 0 THEN false
    ELSE (g % 2) = 0
  END
FROM generate_series(1, 100000) g;
"""

SELECT_NULLS = """
SELECT
  count(*) FILTER (WHERE customer_id IS NULL) AS cid_null,
  count(*) FILTER (WHERE amount     IS NULL) AS amt_null,
  count(*) FILTER (WHERE created_at IS NULL) AS dt_null,
  count(*) FILTER (WHERE status     IS NULL) AS st_null,
  count(*) FILTER (WHERE payload    IS NULL) AS pl_null,
  count(*) FILTER (WHERE active     IS NULL) AS act_null,
  count(*) FILTER (WHERE length(payload) > 127) AS long4b,
  count(*) FILTER (WHERE length(payload) > 2000) AS toast,
  count(*) FILTER (WHERE status = '') AS empty_st,
  count(*) FILTER (WHERE amount = 0.00) AS amt_zero,
  count(*) FILTER (WHERE created_at IS NOT NULL AND created_at::time(6) = '23:59:59.999999') AS dt_us_max
FROM poc_consistency;
"""


def main():
    print(f"[{CONTAINER}] 建表+灌数 {ROWS} 行...")
    r = subprocess.run(
        ["podman", "exec", CONTAINER, "psql", "-U", "test", "-d", "poct25",
         "-v", "ON_ERROR_STOP=1", "-c", CREATE],
        capture_output=True, text=True)
    if r.returncode != 0:
        print(f"灌数 FAIL: {r.stderr[-500:]}")
        sys.exit(1)
    cnt = subprocess.run(
        ["podman", "exec", CONTAINER, "psql", "-U", "test", "-d", "poct25",
         "-tAc", "SELECT count(*) FROM poc_consistency;"],
        capture_output=True, text=True)
    print(f"count={cnt.stdout.strip()}")
    stats = subprocess.run(
        ["podman", "exec", CONTAINER, "psql", "-U", "test", "-d", "poct25",
         "-A", "-t", "-F", "|", "-c", SELECT_NULLS],
        capture_output=True, text=True)
    print("形态分布(列: NULL数/超长4B/TOAST/空串/零值/微秒末):")
    print(stats.stdout.strip())


if __name__ == "__main__":
    main()