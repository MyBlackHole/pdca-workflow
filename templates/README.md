# 4.x当前模板

仅采用下表；其他原模板为历史指针，不能混用schema或旧自动转换。

| 用途 | 模板 |
|---|---|
| 项目与任务 | [context](project-task-context.md)、[task](task.md)、[assignment](agent-assignment.md)、[dispatch](dispatch.md)、[capability](capability-check.md) |
| 计划与授权 | [baseline](baseline.md)、[request](request.md)、[response](response.md)、[decision](request-decision.md) |
| 阶段与证据 | [transition](transition.md)、[evidence](evidence.md)、[conclusion](conclusion.md)、[delivery](delivery.md) |
| 模型与对应检查 | [ontology-revision](ontology-revision.md)、[conformance-review](conformance-review.md) |

复用现有记录用途，schema升级到v4只为表达每阶段启动、run与项目本地数据；不增加平行Goal／Phase／EvidenceContract。空值是真正未取得的事实，不把模板变成默认成功。

plan.md与投影mapping.md可按已批准任务直接编写，不要求每项都再生成一种表单。projection mapping至少有需求／模型对象或约束／目标位置／规则／验证及未知。
