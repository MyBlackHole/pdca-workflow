#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PG 可见性四场景数据准备（T0250 V2/V3/V4）

物理直读成功率 = count(visible元组) vs count(select可见) 差异为 0。
场景表固定 11 行 + 操作序列：
  V1 INSERT 基准确认（另表已验证 1M）
  V2 模拟删除/更新序列（制造死元组）：删除一半 + 更新一半 → 11→N 可见
  V3 批量 DELETE 造 delete-mark
  V4 回滚事务残留：两事务，一个 COMMIT 一个 ROLLBACK → 回滚的行不可见
"""
import subprocess
import sys

PSQL = ["podman", "exec", "t0216-pg", "psql", "-U", "test", "-d", "poct25", "-v", "ON_ERROR_STOP=1"]

SCENARIOS = {
    # 表定义: 每场景独立表避免互相干扰
    "v2": """
DROP TABLE IF EXISTS poc_scen_v2;
CREATE TABLE poc_scen_v2 (id BIGINT PRIMARY KEY, val INT, note TEXT);
INSERT INTO poc_scen_v2 VALUES
  (1,10,'a'),(2,20,'b'),(3,30,'c'),(4,40,'d'),(5,50,'e'),
  (6,60,'f'),(7,70,'g'),(8,80,'h'),(9,90,'i'),(10,100,'j'),(11,110,'k');
UPDATE poc_scen_v2 SET val = val + 1 WHERE id IN (1,3,5,7,9);
DELETE FROM poc_scen_v2 WHERE id IN (2,4,6,8,10);
SELECT 'v2_visible_should_be' AS k, count(*) FROM (SELECT DISTINCT ON (id) id FROM poc_scen_v2) s;
""",
    "v3": """
DROP TABLE IF EXISTS poc_scen_v3;
CREATE TABLE poc_scen_v3 (id BIGINT PRIMARY KEY, val INT, note TEXT);
INSERT INTO poc_scen_v3 VALUES
  (1,10,'a'),(2,20,'b'),(3,30,'c'),(4,40,'d'),(5,50,'e'),
  (6,60,'f'),(7,70,'g'),(8,80,'h'),(9,90,'i'),(10,100,'j');
DELETE FROM poc_scen_v3 WHERE id IN (1,2,3,4,5);
SELECT 'v3_visible_should_be' AS k, count(*) FROM (SELECT DISTINCT ON (id) id FROM poc_scen_v3) s;
""",
    "v4": """
DROP TABLE IF EXISTS poc_scen_v4;
CREATE TABLE poc_scen_v4 (id BIGINT PRIMARY KEY, val INT, note TEXT);
BEGIN;
INSERT INTO poc_scen_v4 VALUES (1,10,'x'),(2,20,'y');
COMMIT;
BEGIN;
INSERT INTO poc_scen_v4 VALUES (3,30,'z'),(4,40,'w');
ROLLBACK;
INSERT INTO poc_scen_v4 VALUES (5,50,'u'),(6,60,'v');
SELECT 'v4_visible_should_be' AS k, count(*) FROM (SELECT DISTINCT ON (id) id FROM poc_scen_v4) s;
""",
}

def run_sql(sql):
    r = subprocess.run(PSQL + ["-c", sql], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[FAIL] {sql[:60]}...\n{r.stderr}", file=sys.stderr)
        return None
    return r.stdout

if __name__ == "__main__":
    for name in ["v2", "v3", "v4"]:
        out = run_sql(SCENARIOS[name])
        if out is None:
            sys.exit(1)
        # 提取可见行数
        for line in out.splitlines():
            if "visible_should_be" in line or (name in out and line.strip().startswith(("1","2","3","4","5","6"))):
                pass
        # psql result table: last non-empty numeric reti value row
        rows_line = [l.split("|")[-1].strip() for l in out.splitlines() if l.strip() and "visible_should_be" in l or l.strip().startswith(("1","2","3","4","5","6","7","8","9","10"))]
        print(f"=== {name} ===")
        print(out)
        print(f"[info] {name} 场景 SQL 已执行")
    # checkpoint 固化
    print("== CHECKPOINT ==")
    print(run_sql("CHECKPOINT;"))