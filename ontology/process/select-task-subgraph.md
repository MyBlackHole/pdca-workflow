---
schema: pdca.asset/v2
id: ontology:process/select-task-subgraph
type: process
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 4.0.0-rc.3
dcterms_modified: '2026-09-25'
summary: CONTEXT-01：只读当前动作需要的事实
---

# CONTEXT-01：只读当前动作需要的事实

每次从集中 records 中的具名项目 context、自己的 task/事件/请求开始；按目标阶段读方法，
按 SCENE 读产物规则，遇到能力、资源、恢复事件再读对应权威。
相同规则版本已读可复用，可变任务状态和用户操作必须重核。

不递归加载全 ontology、legacy、所有模板或兄弟记录。
**全局 Skill 九入口**只作运行方法选择，阶段入口不换执行者；读取场景方法不重新创建场景任务。
同仓库未列入 `skills/catalog.json` 的工程参考 Skill 不属于全局运行入口。

集中资源冲突查询只需作用域及 owner 等最小元数据，不需要其他任务完整会话。
任务输入显式列公共规则、需求、定义、产物和来源；参考资产先做适用性核验，
不把旧 normative 字段当当前授权。关系存在不代表必须追读整图。

Do-only Work Unit 只读取其 Contract 声明的 minimum sufficient context 与共享不变量，
不继承父任务或兄弟 Work Unit 的完整活动历史。

压缩摘要只留项目/task/attempt/Agent 绑定、当前阶段、固定对象指针、当前 Work Unit Contract、
未决操作与待用户事项。恢复读取原始记录，不能只信摘要；缺必要内容阻断，不重新解释目标。

评估上下文成本需含初次、重复读取、恢复重查与返工，不以字数减少宣称效果。
独立输入不等于禁止共享固定允许的模型，但禁止未选择的活动对话和共享记忆。
