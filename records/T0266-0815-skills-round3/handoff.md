# T0266 Handoff — 第二轮可证明增量（out-of-scope / merge-conflicts intent / DEEPENING）

## 当前状态

T0266 已完成并确认 verdict=confirmed、disposition=projected，进入归档。

- `scripts/out-of-scope-manager.py`：add/check/list 状态机，概念级聚合（同概念追加已有文件、不同概念新建）、`--implemented` 反污染拒绝写入、check surfacing 历史理由。状态写 `knowledge/out-of-scope/<concept>.md`。
- `skills/triage-work/SKILL.md`：wontfix 分支升级为概念聚合 + Prior requests 追加 + dedup 前置检查（check/list）+ 仅 enhancement 写入 + durable reason 要求。
- `skills/resolving-merge-conflicts/SKILL.md`：重写为 intent-based 五步（状态/primary source/逐 hunk 保留意图/自动化检查/完成），含 never abort、preserve both intents 契约。
- `skills/design-it-twice/SKILL.md`：补 DEEPENING 深化测试策略（4 类依赖→测试策略决策表、deletion test、one/two-adapter seam 纪律、replace-don't-layer）。
- 新测试：`tests/test_out_of_scope.py`、`tests/test_merge_conflicts_intent.py`、`tests/test_deepening_policy.py` 共 14 测试全绿。
- evidence 已登记（AC-1..AC-8）、convergence-map valid: True、conclusion.md 已写、check_confirmation=confirmed、verdict=T0266-vd-001。

## 未完成事项

1. **进程级文件锁**：out-of-scope-manager 与 check-ticket-claims 均为轻量文件操作，无并发锁。
2. **merge fixture 扩展**：当前仅单文件 merge；多文件冲突 + rebase 场景未 fixture。
3. **out-of-scope 真实命中率统计**：知识库机制已就绪但 `knowledge/out-of-scope/` 仍空（.gitkeep），真实使用后才可统计 dedup surfacing 命中率。

## 已知约束

- 4 个全量测试失败均为既有状态：2 harness（`test_all_deterministic_fixtures_pass`、`test_public_harness_runs_real_lifecycle_success_and_transition_failures`）+ 2 doctor（`test_doctor_uses_explicit_fallbacks`、`test_doctor_reports_seam_contracts_segment`）；均因 round62-67 外部任务缺失，`git stash` 隔离验证非本轮回归。
- 本轮唯一真实回归是 SKILLS-INDEX.md 过期（改 3 skill 后未同步），已 `generate-skills-index.py` 重新生成修复（valid: True）。
- LSP 静态告警（`arch_review`/`pdca_core` import 无法解析）不影响运行时。
- git merge 产生冲突返回 1 是正常状态；测试用 `git_allow_failure()` 显式接受（勿误当失败）。

## 推荐的下一步

1. 为 out-of-scope-manager 与 check-ticket-claims 增加进程级文件锁（flock）。
2. 扩展 merge fixture 到多文件 + rebase 场景。
3. 真实 triage 时启用 out-of-scope 写入，累计后统计 dedup surfacing 命中率（机制效果二次证明）。
4. T0263（identity 观察）继续挂起等待观察窗，观察期满后出 effectiveness verdict。

## 关键上下文文件列表

- `pdca/tasks/0815-skills-round3/`：prd.md、task.json、clarifications.jsonl、implement.jsonl
- `records/T0266-0815-skills-round3/conclusion.md`、`evidence/`（含 convergence.json）
- `scripts/out-of-scope-manager.py`
- `skills/triage-work/SKILL.md`、`skills/resolving-merge-conflicts/SKILL.md`、`skills/design-it-twice/SKILL.md`
- `tests/test_out_of_scope.py`、`tests/test_merge_conflicts_intent.py`、`tests/test_deepening_policy.py`
- `knowledge/out-of-scope/`（机制就绪，待真实填充）
- `records/T0265-0815-skills-provable-increments/conclusion.md`（上轮方法论来源）

## Suggested Skills

- 文件锁实现：`memory-model-concurrency`
- merge fixture 扩展：`testing-strategy`
- out-of-scope 命中率统计设计：`testing-strategy`
