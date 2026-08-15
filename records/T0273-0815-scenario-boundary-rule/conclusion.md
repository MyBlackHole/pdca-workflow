# T0273 结论：模式边界判定规则

## 判定结论

**CONFIRMED** — 模式边界判定规则已实现并验证通过。

## 验收标准逐项

| AC | 描述 | 结果 | 证据 |
|----|------|------|------|
| AC-1 | 新增 `scripts/scenario-boundary-check.py`，输出场景归属判定 | ✅ PASSED | ac1-v2（scenario-boundary-check-v2.py） |
| AC-2 | 判定规则：可测试代码产出→development；纯结论→research | ✅ PASSED | ac1-v2 |
| AC-3 | 历史错配 T0268-T0272 判定为 development | ✅ PASSED | ac3-fixtures.md |
| AC-4 | 纯 research 任务（T0249/T0225/T0260）判定为 research | ✅ PASSED | ac4-research.md |
| AC-5 | 判定脚本接入校验器链 | ✅ PASSED | ac5-validator-chain.md |
| AC-6 | 测试覆盖判定规则含边界用例，全量无回归 | ✅ PASSED | ac6 + regression.md |

**6/6 AC Passed**

## 关键发现

1. **规则验证有效**：T0268-T0272（元审查系列）判定为 development，符合其实际产出（脚本+测试+全量回归）。
2. **额外发现 T0163**：`0731-pg-mysql-parquet-poc` 标 research 但含 `pg_poc.py`、`mysql_poc.py`、`duckdb_poc.py` 等 POC 代码，判定为 development——同一边界问题在更早任务中已存在。
3. **全量回归 272 passed / 4 failed**：4 个失败均为既有（2 harness + 2 doctor seam），无新增回归。新增 7 个测试全部通过。
4. **triager-brief 基线提升**：从 93→94 brief，核心覆盖率 57.0%→57.4%，evidence 79.6%→79.8%（新增 brief 采用标准格式）。

## 影响与范围

- 新增：`scripts/scenario-boundary-check.py`、`tests/test_scenario_boundary_check.py`（7 测试）
- 修改：`tests/test_triage_brief.py`（基线 94 brief）、T0273 自身 PRD/brief
- 未改：历史任务 scenario_type（按用户确认，仅作回归夹具）

## 建议（Act 阶段知识处置）

- 将判定规则写入 `skills/triage-work/SKILL.md` 分类表，作为 triage 阶段机械判定依据。
- 后续新任务的 triage 应运行 `scenario-boundary-check.py --judge` 校验场景归属。
