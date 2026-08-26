# pgwrecover 多索引集成测试从跳过改为可运行 — 规格文档

## 问题陈述

- **现状**: `test_multi_index_mixed` 是唯一覆盖"一张表同时挂 Btree+GIN+GiST+BRIN+HASH 5 种索引 + heap，在一次重放中协同正确"的测试，但它被 `skipif(not _multi_sample_available())` 门禁，仅在设置 `PGW_MULTI_DIR` 时运行。CI 默认跳过，该关键场景从未真正回归。
- **目标**: 测试自带紧凑/原规模样本（入库 fixtures），无需任何环境变量即可运行并断言全部产物与 PG 最终态语义一致。
- **差距**: 当前缺少可入库的多索引样本（WAL+pg_control+基线 heap+各索引期望态），且测试逻辑依赖外部路径。

## 解决方案

将样本生成方法固化为 fixtures 入库；改写 `test_multi_index_mixed`，使其默认从 `tests/fixtures/` 解压样本运行，同时保留 `PGW_MULTI_DIR` 作为可选本地覆盖。测试断言全部 6 个产物（heap + 5 索引）非空且与 PG 最终态语义一致。

## Seam 分析

### 测试接缝
- 边界层：pytest 集成测试通过 subprocess 驱动 `build/pgwrecover` 二进制，输入样本目录，输出 heap 文件、clog、index 目录；再用 `verify_consistency.py` 比对 PG 最终态。
- 已有覆盖：单索引测试（btree/hash/gin/spgist/gist/brin/freeze）均已从 fixtures 运行；本任务补齐"多索引同遍"这一组合场景的自动化。
- 隔离策略：样本全部来自 fixtures（bz2 压缩），无外部 DB/网络依赖；`PGW_MULTI_DIR` 仅作可选覆盖，默认不读取。

### 声明的测试接缝
- seam: tests/pgwrecover/test_btree_e2e.py::test_multi_index_mixed -> src/pg/pg_replay.c（WAL 重放引擎，含各索引 redo 模块）

### 验收可测性
- 每个 AC 均可独立 pass/fail，且有无环境变量两种路径可构造。
- 端到端：从样本重放 → 比对期望态，是对外行为的黑盒验证。

## 用户故事

1. 作为 CI 维护者，我想要多索引集成测试在每次提交自动运行，以便及早发现各索引 redo 在组合场景下的回归。
2. 作为本地开发者，我想要 `PGW_MULTI_DIR` 仍能指向大负载样本做复现，以便调试罕见组合问题。

## 实现决策

- 新增/修改模块：集成测试入口、fixtures 生成与解压辅助。
- 接口定义：fixtures 解压辅助 `_decompress` 已存在，复用；新增多索引样本 fixtures（WAL 段序列、pg_control、基线 heap、各索引期望态）。
- 技术澄清：原 `MULTI_RELS` 中 `heap=1946810` 与已提交 `expected_multi_1946834` 的 relfilenode 不一致；Do 阶段重新生成一致样本，统一 relfilenode。
- 架构决策：样本采用原规模复刻（用户裁定），fixture 增量可接受；env 保留为可选覆盖。

## 测试决策

- 被测模块：WAL 重放引擎整体（含全部索引 redo 路径）。
- 现有先例：单索引测试 `test_*_index_official` 已确立"解压 fixtures → 重放 → verify_consistency PASS"范式，本任务沿用。

## 验收标准

- [ ] AC-1: 在无 `PGW_MULTI_DIR` 环境下运行 `pytest tests/pgwrecover/test_btree_e2e.py::test_multi_index_mixed` 得到退出码 0 且结果为 PASS（非 skipped）。
- [ ] AC-2: 测试默认从 `tests/fixtures/` 解压多索引样本，不读取任何环境变量或仓库外路径（代码中无 `os.environ.get('PGW_MULTI_DIR')` 作为默认路径来源）。
- [ ] AC-3: 全部 6 个产物（heap + pkey/gin/gist/brin/hash 5 索引）均非空，且 `verify_consistency.py` 对每一产物输出 PASS。
- [ ] AC-4: 重放统计 `incremental_applied` 达到原规模阈值（> 9000），证明多索引负载被实际重放。
- [ ] AC-5: 设置 `PGW_MULTI_DIR` 指向本地样本时，测试改用本地样本且仍 PASS（可选覆盖路径未被破坏）。
- [ ] AC-6: 新增 fixtures 压缩后总增量受控，且仓库 `tests/fixtures/` 体积在可接受范围（复刻原规模，用户已裁定接受增大）。

## 范围外

- 不改动重放引擎逻辑本身；不新增索引类型；不扩展至崩溃恢复/部分记录/TORN 页边界；不处理事务可见性（commit/abort）语义。

## 备注

- 样本生成方法见 `journal/2026-08-24.md`（原多索引样本构造记录），Do 阶段据此复刻原规模。
- 既有已提交 `expected_multi_*.bin.bz2` 中 relfilenode 与当前测试不一致，Do 阶段统一重生成。

---
*由 to-spec 流程合成。术语表见 `pdca/CONTEXT.md`，架构决策见 `docs/adr/`。*
