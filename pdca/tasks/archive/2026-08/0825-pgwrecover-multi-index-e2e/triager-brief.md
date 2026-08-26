# Triage Brief — 0825-pgwrecover-multi-index-e2e

- **category**: enhancement
- **scenario_type**: development
- **summary**: 将 `test_multi_index_mixed` 从依赖 `PGW_MULTI_DIR` 环境变量的跳过状态，改为基于已入库 fixtures 的可运行集成测试。
- **current behavior**: 多索引混合场景（一张表同时挂 Btree+GIN+GiST+BRIN+HASH 5 种索引 + heap）的重放验证仅在设置 `PGW_MULTI_DIR` 时运行；CI 中默认跳过。该场景是唯一覆盖"多索引在同一次重放中协同正确"的测试，当前并未真正回归。
- **desired behavior**: 测试从 `tests/fixtures/` 解压紧凑版多索引样本（WAL + pg_control + 基线 heap + 各索引期望态），无需任何环境变量即可运行，并断言全部产物与 PG 最终态语义一致。
- **key interfaces**: WAL 重放引擎（pg_replay）、各索引 redo 模块、语义一致性校验器（verify_consistency.py）、pytest 集成测试入口。
- **acceptance criteria**:
  - 运行 `pytest tests/pgwrecover/test_btree_e2e.py::test_multi_index_mixed` 在无 `PGW_MULTI_DIR` 环境下得到 PASS（退出 0，无 skip）。
  - 测试自行从 fixtures 解压样本，不读取任何环境变量或外部路径。
  - 全部 6 个产物（heap + 5 索引）非空且与 PG 最终态语义一致（verify_consistency PASS）。
  - 新增 fixture 压缩后总增量控制在合理范围（目标 < 60MB，可比对现有 117MB fixtures 体量）。
- **out of scope**: 不改动重放引擎逻辑本身；不新增索引类型；不扩展至崩溃恢复/部分记录边界。
- **information gaps**:
  - 现有已提交 fixture `expected_multi_1946834` 与测试 `MULTI_RELS['heap']=1946810` 的 relfilenode 不一致，需 Do 阶段重新生成一致样本并统一。
  - "体积过大不入库"为旧注释；实测现有 fixtures 已 117MB，紧凑样本入库可行，但需控制规模。
- **dedup results**: 活跃/归档任务无同概念重复；out-of-scope 概念检查无命中；knowledge 无相关条目。
- **recommended next steps**: Do 阶段生成紧凑多索引样本（降行数至数百级），提交 WAL+pg_control+基线+期望态 fixtures，改写测试去掉 env 门槛并断言一致性；Check 阶段用 pytest 实际运行确认无 skip 且 PASS。
