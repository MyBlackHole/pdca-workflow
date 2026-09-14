# 每次正式消息／阶段／恢复的共同入口

本页是恢复与分流方法，不创建授权。只读取当前任务所需内容，勿通读整个资源库。

1. **根与项目。** 安装入口明确的 PDCA_ROOT 与既有任务绑定优先；从集中 `records/projects/<project>/workspaces/<workspace>/project-context.md` 读取固定根及协议引用。新项目仅在用户同意后集中登记；不能转到 TARGET_ROOT/.pdca。根冲突、多个绑定或多个候选任务时询问，不选最新。
2. **原任务。** 读取自己的 task、dispatch 原生身份、最后完整事件、run 与待请求。阶段 Skill 收到调用但当前会话不是该执行者时，只路由真实用户操作至原实例并停止本地执行；不可路由就阻断，不重新 spawn、不由父 Agent 代做。
3. **版本。** `protocol_baseline_ref` 所在快照是本任务规则根。已采用的版本或摘要与当前入口不同，只用本入口定位，读取固定版本对应方法，不混用新规则。没有原快照就停止，不能从全局最新版猜步骤。
4. **本次授权。** 核对 request/原始用户 response/消费、task/attempt/phase/run/subject 和撤销；加载 Skill、状态 running、上阶段 PASS 均不代替授权。重复回应不启动新 run；目标或输入变动先重新沟通。
5. **资源。** 按 [RESOURCE](../ontology/concept/resource-ownership.md)核对集中预约与真实后端作用域。记录和模型写入也有拥有者，不能把集中根当全局可写区。结果未知保留占用，只对账原操作。

| 事件 | 下一方法 | 停止条件 |
|---|---|---|
| 新工作明确创建 | [TASK](../ontology/concept/pdca-task.md)、[CAP](../ontology/concept/capability-protocol.md)、[派发](dispatch-guide.md) | 新 Agent 展示 Plan 目标后等待，不把创建授权当阶段批准 |
| 启动一个阶段 | [CONFIRM](../ontology/concept/pdca-ai-friendly-confirmation.md)、[GATE](../ontology/concept/pdca-gate.md)、对应阶段 Skill | 任何不匹配、能力不足或撤权则阻断 |
| 阶段完成 | 保存真实产物与完成事件，报告下一目标 | 保持最后实际阶段，awaiting_confirmation；不自动切换 |
| 恢复／压缩／重启 | [RECOVERY](../ontology/concept/pdca-recovery.md) | 原身份、状态、输入与资源不能恢复则停止 |
| 停止／取消 | [CONTROL](../ontology/concept/task-control.md)及 RESOURCE | 优先止损和结清；不需要父 Agent 循环监工 |

阶段动作与场景方法在 [八入口索引](../skills/README.md)。读场景的方法段不会再次创建任务。相同固定规则已读可复用；变化的状态、授权和实际资源必须重核。没有自动重载的宿主需显式调用入口，不能以文件存在承诺永不遗忘。
