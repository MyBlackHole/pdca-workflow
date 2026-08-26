# pgwrecover 多索引混合样本生成与 fixture 协同验证

## 适用场景
为 pgwrecover 端到端测试构造"一张表同时挂多种索引"的样本，使重放引擎在同一次
重放中协同重建全部索引，并与 PG 最终态语义级一致。

## 样本生成范式（已验证可复现）
在 PG18.4 容器内：
1. 建表（**不含主键/索引**）→ `CHECKPOINT`，记录 redo LSN 与 heap relfilenode。
   此时 heap 文件为空，作为重放基线拷贝出来。
2. 在 CHECKPOINT 之后：`ALTER TABLE ADD PRIMARY KEY`（btree）、`CREATE INDEX`
   (GIN/GiST/BRIN/HASH)、`INSERT` 大量行 + `DELETE` 部分行 → `CHECKPOINT`。
   这样**所有索引创建与数据写入都落在 WAL 内**，pgwrecover 从 redo 起点从零
   构建全部索引（无需提供索引基线文件，只需 heap 基线）。
3. 干净停止，拷贝 `pg_control`（将其 `checkPoint` 与 `minRecoveryPoint` 偏移 32/40
   改写为 redo LSN）、`pg_wal/` 从 redo 段起的各段、以及 PG 最终态的 heap + 各索引
   relfile（作为期望态）。

## 关键陷阱
- **relfilenode 一致性**：测试代码 `MULTI_RELS` 的 relfilenode 必须与 fixture 的
  期望态文件名逐字一致。曾出现测试用 `1946810` 而已提交 fixture 为 `1946834` 的
  错位（样本被多次重建后 relfilenode 漂移）。每次重建样本必须统一重生成 fixtures，
  删除旧的不一致条目。
- **主键索引的坑**：若 `CREATE TABLE ... PRIMARY KEY` 内联主键，主键索引在
  CHECKPOINT 前已存在，不在 WAL 内，pgwrecover 找不到其基线→失败。必须把主键也
  放到 CHECKPOINT 之后建（见步骤 2），让所有索引都进 WAL。
- **env 覆盖语义**：`PGW_MULTI_DIR` 仅作重放**输入源**覆盖；一致性比对目标应固定为
  fixtures 中的期望态（输入样本是基线态，不能直接拿来当期望态比较）。

## 验收口径
- `incremental_applied` 需达原规模阈值（>9000 对应 ~2500 行 ×5 索引）。
- 全部产物用 `verify_consistency.py` 比对 PG 最终态，`结构性差异=0` 且 hint 位差异
  在允许集内（HEAP_XMIN_COMMITTED 不写 WAL 无法重放，属预期）。

## 复用指引
新增加密/新索引类型的端到端测试时，沿用本范式：CHECKPOINT 前只建表、CHECKPOINT 后
建全部索引与数据，基线只留 heap，期望态取自 PG 最终 relfile。
