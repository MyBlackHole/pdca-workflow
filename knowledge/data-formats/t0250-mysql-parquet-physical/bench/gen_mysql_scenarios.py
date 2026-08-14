#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MySQL InnoDB V2/V3/V4 场景数据准备（T0250，对标 PG 可见性场景）。

物理直读目标：过滤 delete-mark（REC_INFO_DELETED_FLAG 0x20）后
可见行 == SQL 可见行。

  V2  UPDATE 5 + DELETE 5（11 行 → 6 可见；更新行读最新值）
  V3  批量 DELETE 5（10 行 → 5 可见）
  V4  事务回滚（COMMIT 2 + ROLLBACK 2 + 再插入 2 → 4 可见）

注意：数据固化必须容器内 `mysqladmin shutdown`（podman stop 不刷 InnoDB 脏页，
BLOB / delete-mark 页可能缺失，见 evidence/mysql/EVIDENCE.md）。
"""
import subprocess
import sys

client = ["podman", "exec", "t0250-mysql8", "mysql", "-uroot", "-ptest", "poct25"]

def run(sql):
    r = subprocess.run(client + ["-e", sql], capture_output=True, text=True)
    if r.returncode != 0:
        print("[FAIL]", sql[:80].replace("\n", " "), "\n", r.stderr, file=sys.stderr)
        sys.exit(1)
    return r.stdout

V2 = """
DROP TABLE IF EXISTS poc_scen_v2;
CREATE TABLE poc_scen_v2 (id BIGINT PRIMARY KEY, val INT, note TEXT);
INSERT INTO poc_scen_v2 VALUES
 (1,10,'a'),(2,20,'b'),(3,30,'c'),(4,40,'d'),(5,50,'e'),
 (6,60,'f'),(7,70,'g'),(8,80,'h'),(9,90,'i'),(10,100,'j'),(11,110,'k');
UPDATE poc_scen_v2 SET val = val + 1 WHERE id IN (1,3,5,7,9);
DELETE FROM poc_scen_v2 WHERE id IN (2,4,6,8,10);
SELECT 'v2_visible' AS k, COUNT(*) FROM poc_scen_v2;
"""

V3 = """
DROP TABLE IF EXISTS poc_scen_v3;
CREATE TABLE poc_scen_v3 (id BIGINT PRIMARY KEY, val INT, note TEXT);
INSERT INTO poc_scen_v3 VALUES
 (1,10,'a'),(2,20,'b'),(3,30,'c'),(4,40,'d'),(5,50,'e'),
 (6,60,'f'),(7,70,'g'),(8,80,'h'),(9,90,'i'),(10,100,'j');
DELETE FROM poc_scen_v3 WHERE id IN (1,2,3,4,5);
SELECT 'v3_visible' AS k, COUNT(*) FROM poc_scen_v3;
"""

V4 = """
DROP TABLE IF EXISTS poc_scen_v4;
CREATE TABLE poc_scen_v4 (id BIGINT PRIMARY KEY, val INT, note TEXT);
START TRANSACTION;
INSERT INTO poc_scen_v4 VALUES (1,10,'x'),(2,20,'y');
COMMIT;
START TRANSACTION;
INSERT INTO poc_scen_v4 VALUES (3,30,'z'),(4,40,'w');
ROLLBACK;
INSERT INTO poc_scen_v4 VALUES (5,50,'u'),(6,60,'v');
SELECT 'v4_visible' AS k, COUNT(*) FROM poc_scen_v4;
"""

V5_UPDATE_LARGE = """
DROP TABLE IF EXISTS poc_scen_v5;
CREATE TABLE poc_scen_v5 (id BIGINT PRIMARY KEY, val INT, note TEXT);
INSERT INTO poc_scen_v5 VALUES (1,10,REPEAT('a',9000));
-- UPDATE 不改主键：若行内无 off-page 则 in-place（旧值进 undo，物理读新值）
UPDATE poc_scen_v5 SET val = 99 WHERE id = 1;
UPDATE poc_scen_v5 SET note = REPEAT('b',9000) WHERE id = 1;
SELECT 'v5_visible' AS k, COUNT(*), (SELECT val FROM poc_scen_v5 WHERE id=1), CHAR_LENGTH((SELECT note FROM poc_scen_v5 WHERE id=1)) FROM poc_scen_v5;
"""

if __name__ == "__main__":
    for name, sql in [("v2", V2), ("v3", V3), ("v4", V4), ("v5", V5_UPDATE_LARGE)]:
        print(f"=== {name} ===")
        print(run(sql))
    print("[mysql] scenarios ok")