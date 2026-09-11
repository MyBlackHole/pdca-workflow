# T2179 经验记录

## 来源

- 当前任务：`T2179-0911-independent-pdca-ticket-gate-projection`
- 本体锚点：`ontology:concept/pdca-task`
- 有效证据：`t2179-gate-runtime-c1`、`t2179-ticket-tests-c1`、`t2179-research-tests-c1`、`t2179-verification-report-c1`

## 可复用经验

- 删除显式 `TICKETS_MISSING` 不足以解除任务耦合；所有使用任务关系或其他任务状态影响当前阶段准入的路径都必须纳入符合性审查。
- 独立任务门禁测试应覆盖三个专业职责，并把其他 Plan 条件构造成有效输入，避免因早期 Schema 错误产生假通过。
- 研究证据属于当前任务自身的持久化输入；关联任务的 archive 状态不能代理当前任务满足准入条件。

## 纠偏

首次 Do 证据仍保留跨任务研究遍历，符合性审查失败后由同一一对一子 Agent 修正，并通过 evidence replacement 保留完整证据演进。
