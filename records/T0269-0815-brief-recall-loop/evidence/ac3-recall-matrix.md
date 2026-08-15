# AGENT-BRIEF 决策兑现回读矩阵（T0269，第五轮）

样本: round62（T0248，check，do-evidence+convergence）、round66（T0252，do，design.md）、round67（T0253，plan，design.md）

兑现判定口径（用户确认 G1）: 兑现 = 决策进入实施产出（样本进行中无最终 verdict，结果验证标注待任务完成）

总决策数: 21 | fulfilled: 19 | partial: 2 | not-fulfilled: 0 | unknown: 0

兑现率（fulfilled+partial 进入产出）: 100.0%（21/21）| 直接兑现率: 90.5%（19/21）

---

# 决策兑现回读矩阵：0813-lmdb-tree-resume-round62

任务: `0813-lmdb-tree-resume-round62` | brief: `triager-brief.md` | 决策数: 9

兑现状态: fulfilled=决策已进入实施产出 | partial=部分采纳/进行中 | not-fulfilled=未采纳或推翻 | unknown=无法判定

| # | 类型 | 决策 | 命中提示 | 兑现状态 | 依据 |
|---|------|------|---------|---------|------|
| 1 | verified_issue | `src/metadata_store.cpp` already contains an optional LMDB backend and `auto` selects it when compiled, but the normal integration suite assumes the cache is SQLite and fails against an LMDB-default binary with `file is not a database`. | do-evidence-round62.md(31) | fulfilled | do-evidence-round62.md:2-7 双后端集成 PASS（lmdb+sqlite） |
| 2 | verified_issue | `tests/benchmark_metadata_index.sh` can run both backends; one 20,000-entry probe measured unchanged scan at `0.0667s` LMDB versus `0.0741s` SQLite, but this is one unpaired sample and is not production evidence. | do-evidence-round62.md(42) | fulfilled | do-evidence-round62.md:17-20 五对 100k 基准 benchmark-metadata-100k.log |
| 3 | verified_issue | `--incremental-local` persists metadata only after `TREE_END`; the source walk and transfer have no durable per-batch checkpoint contract that can be validated after process interruption. | do-evidence-round62.md(17) | fulfilled | do-evidence-round62.md:10-13 checkpoint resume 测试 N=100000 |
| 4 | verified_issue | Existing resume coverage proves large regular-file partial PUT/GET resume, not a massive recursive TREE interrupted after confirmed batches. | do-evidence-round62.md(8) | fulfilled | do-evidence-round62.md:11 确定性中断 skipped=67071/resent=32929 |
| 5 | verified_issue | T0247 covered small-file pack streaming decode and did not add metadata checkpoint state or TREE transfer recovery. | do-evidence-round62.md(17) | fulfilled | do-evidence-round62.md:10 本任务新增 checkpoint 覆盖 |
| 6 | verified_issue | Existing metadata tasks cover the local SQLite/LMDB abstraction and generation correctness, but no active or archived task covers a resumable TREE checkpoint protocol. | do-evidence-round62.md(34) | fulfilled | do-evidence-round62.md:10 本任务即可恢复 TREE checkpoint 协议 |
| 7 | recommendation | checkpoint 的安全边界：推荐“逐批确认 + 每项 fingerprint 校验”，不推荐仅按路径游标盲跳。 | do-evidence-round62.md(5) | fulfilled | do-evidence-round62.md:16 排空队列+截断 tail+突变内容校验 |
| 8 | recommendation | backend 默认：推荐 `auto` 在编译含 LMDB 时继续选择 LMDB，显式 `sqlite` 保留回退，不做静默格式转换。 | do-evidence-round62.md(19) | fulfilled | do-evidence-round62.md:2-7 sqlite/lmdb 双后端 + auto 保留 |
| 9 | recommendation | 兼容策略：推荐新 capability 可选，旧 peer 无 checkpoint 时走现有路径，不修改旧 peer 的既有语义。 | do-evidence-round62.md(7) | fulfilled | do-evidence-round62.md:16 old peers 不协商可选 capability |
---

# 决策兑现回读矩阵：0814-tree-checkpoint-paged-round66

任务: `0814-tree-checkpoint-paged-round66` | brief: `triager-brief.md` | 决策数: 3

兑现状态: fulfilled=决策已进入实施产出 | partial=部分采纳/进行中 | not-fulfilled=未采纳或推翻 | unknown=无法判定

| # | 类型 | 决策 | 命中提示 | 兑现状态 | 依据 |
|---|------|------|---------|---------|------|
| 1 | risk | 只把 map 换成另一种内存容器不会满足生产目标。 | design.md(7) | fulfilled | design.md:5-9 模块边界 + design.md:38-43 Alternatives rejected |
| 2 | risk | 仅依赖 SQLite WAL 而不处理旧 journal 的尾部截断、重放偏移和远端 ACK 后本地落盘窗口，可能破坏断点续传安全性。 | design.md(51) | fulfilled | design.md:29 journal_offset 重放/截断/ACK 落盘窗口 |
| 3 | risk | 只跑 100k 会掩盖每路径内存增长；必须加入 1M 和 RSS 基线比较。 | design.md(2) | fulfilled | design.md:36 peak RSS + design.md:43 1M + design.md:57 吞吐预算 |
---

# 决策兑现回读矩阵：0814-resume-production-architecture-round67

任务: `0814-resume-production-architecture-round67` | brief: `triager-brief.md` | 决策数: 9

兑现状态: fulfilled=决策已进入实施产出 | partial=部分采纳/进行中 | not-fulfilled=未采纳或推翻 | unknown=无法判定

| # | 类型 | 决策 | 命中提示 | 兑现状态 | 依据 |
|---|------|------|---------|---------|------|
| 1 | verified_issue | rsync 使用 partial/partial-dir 保留单文件临时结果，现代版本可原地更新 partial 文件；它不要求每个文件完成时同步一个全局数据库。 | design.md(49); research.md(17); implement.md(1) | fulfilled | design.md:7,88 partial+offset+digest+原子发布（rsync 语义） |
| 2 | verified_issue | restic 在中断后重新扫描源树，依靠已持久化的内容索引复用已上传 blob；索引周期更新，允许有限进度重做，而不是每个文件都做强同步。 | design.md(1) | fulfilled | design.md:22-23 content-addressed 幂等 + 未引用 pack 回收 |
| 3 | verified_issue | restic 的存储顺序是先写不可变 pack，再写索引，最后写 snapshot；崩溃时未被 snapshot 引用的 pack 是可清理的孤儿数据，不破坏已提交快照。 | design.md(13); research.md(13); implement.md(2) | fulfilled | design.md:23 manifest generation 引用/孤儿可回收 |
| 4 | verified_issue | Borg 使用周期性 checkpoint archive，恢复依靠重新执行并复用已存在的数据，而非要求每条扫描记录都同步提交。 | design.md(15); research.md(7); implement.md(2) | fulfilled | design.md:17,80 durable cursor 重启最多重做一 batch |
| 5 | recommendation | 单文件：保留 `.partial`、源指纹、offset、最终校验和原子 rename；不要引入全局 TREE checkpoint lookup。 | design.md(76); research.md(33); implement.md(8) | fulfilled | design.md:7,51 原子 rename + partial 绑定路径/大小/指纹，无全局 lookup |
| 6 | recommendation | 海量目录：改为批量/不可变 block ledger 或批量 manifest checkpoint；远端数据提交幂等，checkpoint 按时间或字节阈值落盘，允许声明范围内的重复发送。若继续使用 SQLite，只能作为批量索引/恢复工具，不能逐文件 `fsync`/COMMIT。 | design.md(65); research.md(23); implement.md(8) | fulfilled | design.md:15-16,23,26 幂等 batch + SQLite 仅批量索引 + manifest generation |
| 7 | information_gap | 需要在 tmpfs、SSD、旋转盘或网络盘上分别测量当前方案与候选方案。 | design.md(2) | partial | design.md:43 tmpfs/SSD/network 各一组；旋转盘未列 |
| 8 | information_gap | 需要明确可接受的重复发送窗口和断电后最多重做的数据量。 | - | partial | design.md:50,80 重复发送/重做机制明确；量化窗口与数据量未声明 |
| 9 | information_gap | 需要注入 ACK 后、journal fsync 后、索引提交中断三类故障，验证 fail-closed 和幂等恢复。 | design.md(53); research.md(17); implement.md(3) | fulfilled | design.md:44,49,15 四故障点注入 + fail-closed + 幂等 receipt |