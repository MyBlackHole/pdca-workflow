# T0159 架构设计

## 设计目标

建立可重放、可追溯、AI 不需猜测写入方式、且不能自行获得流程修改权限的反馈系统。

## 领域对象

```text
Flow Issue Occurrence (immutable fact)
        │ deterministic projection
        ▼
Flow Issue (rebuildable view)
        │ user-confirmed decision
        ▼
Improvement Candidate (immutable proposal version)
        │ promotion decision
        ▼
Improvement Task (strict PDCA task)
        │ deploy receipt + observation
        ▼
Effectiveness Verdict
        ├── improved  → verified decision
        ├── neutral   → re-triage / observe
        └── regressed → rollback candidate
```

## 写入边界

```text
report CLI ──exclusive create──> flow-events/<event-id>.json
decision CLI ─exclusive create─> flow-improvements/decisions/<decision-id>.json
candidate CLI ─exclusive create> flow-improvements/candidates/<candidate-id>.json
effect CLI ───exclusive create─> flow-improvements/effectiveness/<verdict-id>.json

aggregator ──atomic replace──> pdca/improvements/backlog.json
query CLI ───read only───────> compact JSON
```

事实与治理回执均不可覆盖；只有 backlog 是可重新生成的视图。

## CLI 合约

所有 CLI：

- stdout 只输出单个 JSON 对象；
- stderr 只输出诊断；
- 成功/unchanged 返回 0，拒绝返回非零；
- 错误含稳定 `error` code、字段 path 和可操作 message；
- 接受显式 `--root`，不依赖当前目录猜测；
- 路径解析后必须限制在各自根目录；
- 写入采用临时文件、fsync、独占创建或原子 replace。

## 一致性与幂等

- event ID 从 `record_id + idempotency_key` 派生，调用方负责稳定 key。
- 同 key、同规范化内容：`unchanged`。
- 同 key、不同内容：`IDEMPOTENCY_CONFLICT`。
- decision/candidate/verdict 使用相同模式。
- 聚合输入摘要覆盖排序后的事件相对路径与内容 digest。
- projection 输出排除生成时间等非确定字段，保证相同输入同 digest。

## 权限模型

| 动作 | AI 可直接执行 | 用户确认 |
|---|---:|---:|
| 上报 occurrence | 是 | 否 |
| 重建/查询 backlog | 是 | 否 |
| 生成 triage/candidate dry-run | 是 | 否 |
| false-positive / accepted-risk / close | 否 | 是 |
| impact 晋级 | 否 | 是 |
| 创建 Improvement Task | 否 | 是 |
| 修改权威流程 | 否 | 正常 PDCA P6 |
| 生成 effectiveness verdict | 是，基于冻结输入 | verdict 进入 Check |
| 回滚 | 否 | 是 |

## Cutover

- 既有 `flow-audit/v1` 文件与已登记摘要不变。
- 新版本发布时写入 cutover receipt，记录 commit、schema version、fingerprint version 和起始时间。
- 聚合器默认只读取 cutover 后的 `flow-events/`。
- 如需分析 v1，使用独立离线导入报告，不向事实存储写伪造事件。

## 故障模型

- 部分写入：临时文件未晋级，不出现事件。
- 并发同 key：一个创建成功，另一个比较内容后 unchanged 或 conflict。
- 单个损坏事件：聚合 fail-closed，报告具体路径，不跳过。
- projection 损坏：可从事实事件重建。
- 确认引用失效：治理动作拒绝。
- candidate 评测退化：不晋级或生成回滚候选。

## P4 拆解决策

不创建子任务。各模块共享事件合约、确认引用和端到端验收链，只有作为单一纵向能力才可独立验收。内部实现使用多轮 TDD 切片，不把未完成部分外包为独立生命周期。
