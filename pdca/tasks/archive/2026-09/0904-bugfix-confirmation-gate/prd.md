# Bug修复流程增加修复前用户确认门禁并修正根因模板

## 背景

当前 `diagnosing-bugs`（Phase 3-5）与 `bug-analysis` 在 Do 阶段可直接进入“最小修复/改代码”，仅有 `Show to user if present` 软约束，无强制用户确认。`flow-do` bugfix 路径与 `ai-execution-contract` 均无“确认修复方案”标记，`clarification.schema.json` 与 `append-confirmation.py` 无 `fix_confirmation` 类型，`flow_audit` 与 `pdca_core.gate_issues` 均不审计 Do 内修复确认，违背 HITL。

同时 `bug-analysis` 与 `bug-commit-format` 的根因模板表述不准确（与诊断结论、commit 格式未对齐），需一并修正。

> 关联本体节点
```
ontology:domain/skill-diagnosing-bugs
ontology:domain/skill-bug-analysis
ontology:domain/skill-bug-commit-format
ontology:process/flow-do
ontology:concept/pdca-task
```

## 目标

在 Do 内增加“诊断完成→修复前用户确认”可审计门禁（档 B：文本约束 + fix_confirmation 落盘 + audit WARN），并修正根因模板使三处一致（诊断假设→根因分析→提交格式）。

## 方案（档 B）

1. **Schema**：`schemas/clarification.schema.json` 新增 `fix_confirmation` 分支（response: confirmed/rejected）
2. **CLI**：`scripts/append-confirmation.py` 支持 `fix_confirmation`
3. **Skill 文本**：
   - `skill-diagnosing-bugs.md` Phase 4→5 间插入 Phase 4.5 Fix Approval，要求展示 已验证假设/根因/修复方案/回归测试计划/影响范围/回滚策略 并获 `fix_confirmation:confirmed`（captured:true）方可进入 Phase 5
   - `skill-bug-analysis.md` 步骤 6 后增加确认要求，输出需含现象/复现/证据/假设/实验/根因/修复方向/验证标准 并获确认
   - `skill-bug-commit-format.md` 修正根因表述：根因≠现象，需追到代码/配置/流程层面，与上游诊断结论一致
4. **Flow & Contract**：`ontology/process/flow-do.md` 路径 B 增加“确认修复方案”行；`pdca/ai-execution-contract.json` bugfix phases 在 `minimal-change` 前插入 `fix-approval`；`pdca/ai-friendliness-route-contract.json` 同步（如需）
5. **审计**：`scripts/flow_audit.py:_do_checks` 增加 `fix-confirmation` 检查（缺失记 WARN/issue，不阻断存量）；`pdca/skill-content-baseline.json` 更新
6. **测试**：`tests/test_diagnosing_bugs_enhance.py` 新增 2 条契约测试（fix-approval 文本、fix_confirmation 示例）；新增 `tests/test_fix_confirmation_gate.py` 校验 schema/CLI/audit 链路

## 验收标准

- [ ] AC-1 诊断到修复的确认门禁已落地且可审计：`grep -q "确认修复方案" ontology/process/flow-do.md` 命中；`grep -q "fix_confirmation" schemas/clarification.schema.json` 命中；`grep -q "fix_confirmation" scripts/append-confirmation.py` 命中；`grep -q "fix-approval" pdca/ai-execution-contract.json` 命中；`grep -q "fix-confirmation" scripts/flow_audit.py` 命中
- [ ] AC-2 根因模板已修正且与诊断结论一致：`skill-bug-analysis.md` 与 `skill-bug-commit-format.md` 的根因表述均含“根因≠现象”且区分假设/实现/流程三类；`skill-diagnosing-bugs.md` 含 Phase 4.5 且要求展示根因+方案+影响范围+回滚；`grep -q "fix_confirmation" ontology/domain/skill-diagnosing-bugs.md` 命中
- [ ] AC-3 全量门禁与契约测试通过：`python3 -m pytest tests/test_diagnosing_bugs_enhance.py tests/test_fix_confirmation_gate.py -q` 通过；`python3 scripts/ontology-validate.py --ontology-dir ontology` 通过；`python3 scripts/resolve-ai-execution-contract.py --verify-document --root .` 通过

## 非目标

- 不对 `do→check` 增加强阻断（存量任务兼容，audit 仅 WARN）
- 不改变 `plan→do` 的 `final_confirmation` 语义

## 拆分映射

- PRD 本体 -> ontology:domain/skill-diagnosing-bugs
- 根因模板修正 -> ontology:domain/skill-bug-analysis
- 提交格式对齐 -> ontology:domain/skill-bug-commit-format
- 执行契约 -> ontology:process/flow-do

### 声明的测试接缝

- seam: tests/test_fix_confirmation_gate.py -> schemas/clarification.schema.json
- seam: tests/test_fix_confirmation_gate.py -> scripts/append-confirmation.py
- seam: tests/test_fix_confirmation_gate.py -> scripts/flow_audit.py
- seam: tests/test_diagnosing_bugs_enhance.py -> ontology/domain/skill-diagnosing-bugs.md
