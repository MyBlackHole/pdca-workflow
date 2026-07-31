## 当前状态

T0144 已获得 `confirmed` verdict 并进入 Act。根因分析、两次独立 crash transcript、源码
对应、逻辑闭环审查、非技术图和详细分析报告均位于本 record。可复用方法已经投影到
`knowledge/kernel-debugging/device-mapper-blk-mq-uaf-vmcore-method.md`。

## 未完成事项

本任务本身没有未完成的验收项。以下为需要另行授权的新周期候选：

- 将上游 guard 等价回移植到目标 3.10 内核；
- 构建并执行修复前后 A/B 并发压测；
- 如业务需要，补采 iSCSI 到 dm 状态转换的完整事件链。

详见 `improvement-backlog.md`。

## 已知约束

- 已闭合的是 request-based device-mapper blk-mq suspend/reload 竞态。
- iSCSI 直接触发已排除，间接促成关系仍为 `inconclusive`。
- 上游补丁的同源性和静态充分性已证明，但目标内核回移植尚未运行验证。
- record 中的指针地址、设备编号和主机信息属于本次案例，不能泛化。

## 推荐的下一步

若用户要求实施修复，应启动新的 Plan 任务，把“等价回移植 + 构建 + A/B 压测 + 回退方案”
作为独立验收范围。不要在已归档 T0144 中直接追加实施结论。

## 关键上下文文件列表

- `conclusion.md`
- `evidence/vmcore_analysis_report_detailed.md`
- `evidence/root-cause-proof.md`
- `evidence/proof-rerun-expanded.md`
- `evidence/patch-equivalence-proof.md`
- `evidence/logic-closure-review.md`
- `disposition.md`
- `improvement-backlog.md`
- `../../knowledge/kernel-debugging/device-mapper-blk-mq-uaf-vmcore-method.md`

## Suggested skills

- `flow-plan`：为回移植和 A/B 验证建立新任务。
- `grilling`：确认测试负载、停机边界和回退条件。
- `register-evidence`：登记构建产物、测试日志和对比结果。
- `write-conclusion`：对运行验证结果给出独立 verdict。
