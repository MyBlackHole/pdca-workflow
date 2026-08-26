# 结论 — T3966 多索引集成测试从跳过改为可运行

## 实验回顾
- scenario_type: development
- 对照 PRD 验收标准逐条核查；变更见 git commit `fd9657e`。
- 实际变更：`tests/pgwrecover/test_btree_e2e.py` 中 `test_multi_index_mixed` 改为默认从 fixtures 解压样本运行；`PGW_MULTI_DIR` 仅作可选输入源覆盖；统一 relfilenode 并替换旧的不一致 fixtures。

## 验收判定

- **AC-1** ✅ 无 `PGW_MULTI_DIR` 环境下 `pytest tests/pgwrecover/test_btree_e2e.py::test_multi_index_mixed` 退出 0 且结果为 PASS（非 skipped）。证据 `evt-multi-default`。
- **AC-2** ✅ 测试默认从 `tests/fixtures/` 解压样本（`pg_control_multi` + `multi_wal_*` + `baseline_multi_heap_1946880`），代码中无 `os.environ.get('PGW_MULTI_DIR')` 作为默认路径来源（仅在可选覆盖分支读取）。证据 `evt-test-entry` `evt-fix-pgcontrol` `evt-fix-baseline`。
- **AC-3** ✅ 全部 6 产物（heap + pkey/gin/gist/brin/hash 5 索引）均非空，且 `verify_consistency.py` 对每一产物输出 PASS（语义级一致，结构性差异=0）。证据 `evt-multi-default` `evt-fix-baseline` `evt-fix-expected-gist`。
- **AC-4** ✅ 重放统计 `incremental_applied=14913 > 9000`，证明多索引负载被实际重放。证据 `evt-multi-default`。
- **AC-5** ✅ 设置 `PGW_MULTI_DIR` 指向本地样本（基线输入）时，测试改用本地样本且仍 PASS（覆盖路径未被破坏）。证据 `evt-multi-override`。
- **AC-6** ✅ 新增 fixtures 压缩后总增量受控：入库后 `tests/fixtures/` 168MB（较改动前 +51MB），复刻原规模已为用户 Plan 阶段裁定接受。证据 `evt-fix-ac6`。

## 结论
多索引混合场景（Btree(pkey)+GIN+GiST+BRIN+HASH 同遍重放）现具备自动化回归能力，CI 默认运行且全部产物与 PG 最终态语义级一致。原"体积过大不入库"的旧约束已被用户裁定解除，样本以原规模入库。

## 风险与边界
- 不改动重放引擎逻辑；本任务仅补齐"多索引协同"的自动化验证缺口。
- 事务可见性（commit/abort）语义、崩溃恢复/部分记录边界不在本任务范围内（PRD 范围外）。
