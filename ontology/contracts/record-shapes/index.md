---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.4
authority: normative
status: active
---

# 4.x 当前记录格式

下表中的记录契约是当前格式的唯一权威，字段与完整示例在各自契约中。其他旧格式不适用，不能混用 schema 或旧自动转换。

## Schema major and protocol revision

`pdca.* /v4` 表示**记录格式 major**；`protocol_revision` 表示该当前 active contract/template 所属的 **PDCA protocol 语义版本**。两者不是同一个版本轴。

当前 protocol 为 `4.0.0-rc.3`，因此本目录所有 active current contract 及其示例都必须声明 `protocol_revision: 4.0.0-rc.4`。未来 protocol 升级若仍兼容 schema v4，可以继续使用 `/v4`，但 active template 的 `protocol_revision` 应随当前协议更新。

**已有历史 record 不自动迁移。** task/attempt 已固定的旧 record 保留原字节与原 `protocol_revision`，恢复时按 RECOVERY-01 结合其原始 Git 来源/固定 refs 判断是否仍可解释；不能为了“对齐当前版本”批量重写活动或历史记录。

| 用途 | 记录契约 |
|---|---|
| 项目与任务 | [context](project-task-context.md)、[task](task.md)、[assignment](agent-assignment.md)、[dispatch](dispatch.md)、[capability](capability-check.md) |
| 计划与授权 | [baseline](baseline.md)、[request](request.md)、[response](response.md)、[decision](request-decision.md) |
| 阶段与证据 | [transition](transition.md)、[evidence](evidence.md)、[conclusion](conclusion.md)、[delivery](delivery.md) |
| 集中资源与操作 | [resource-reservation](resource-reservation.md)、[operation](operation.md) |
| 模型与对应检查 | [ontology-revision](ontology-revision.md)、[conformance-review](conformance-review.md) |

复用现有记录用途，schema升级到v4只为表达每阶段启动、run与明确绑定；不增加平行Goal／Phase／EvidenceContract。空值是真正未取得的事实，不把示例变成默认成功。

plan.md与投影mapping.md可按已批准任务直接编写，不要求每项都再生成一种表单。projection mapping至少有需求／模型对象或约束／目标位置／规则／验证及未知。
