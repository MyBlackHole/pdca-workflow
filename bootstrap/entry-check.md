# 每次消息／阶段／恢复的动作入口

本页只导航，不创建授权。先查看项目 context，再按实际角色选择路径；不通读整个 ontology 库、旧索引或历史示例。

| 事件 | 最小读取与动作 | 停止条件 |
|---|---|---|
| 新工作明确启用 | USE-PDCA、项目绑定、[TASK](../ontology/concept/pdca-task.md)、[CAP](../ontology/concept/capability-protocol.md)、派发入口 | 未获准创建或能力未知只沟通，不开始 Plan |
| 新 task 已绑定 | [CONFIRM](../ontology/concept/pdca-ai-friendly-confirmation.md)、task、用户目标 | 提出 Plan 启动对象并等待 |
| 当前阶段获准 | 当前请求／真实响应／消费记录、原始输入摘要、[GATE](../ontology/concept/pdca-gate.md)、对应阶段方法 | 任一不匹配或有撤权就停止 |
| 阶段完成 | 保存产物、证据和完成事件；报告下一阶段目标 | task=awaiting_confirmation；不执行下一阶段 |
| 重复消息／压缩／重启 | [RECOVERY](../ontology/concept/pdca-recovery.md)、原会话、最后完整事件、未决操作与请求 | 不靠状态布尔值产生授权，不自动重放操作 |
| 停止／取消／撤权 | [CONTROL](../ontology/concept/task-control.md)、[RESOURCE](../ontology/concept/resource-ownership.md) | 先停止新增动作并结清，不伪造完整归档 |

对应阶段：[Plan](../ontology/process/flow-plan.md)、[Do](../ontology/process/flow-do.md)、[Check](../ontology/process/flow-check.md)、[Act](../ontology/process/flow-act.md)。场景对象见 [SCENE](../ontology/process/work-scenarios.md)。

记录最小实际观察：project/task/attempt、原生绑定、当前阶段、最后事件、待用户事项、本次允许动作及阻断原因。用户不需要看到长篇协议清单。保留同版本已读内容；新消息必须复核可变状态与授权，不重复全量规则加载。
