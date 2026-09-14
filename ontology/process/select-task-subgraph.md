---
schema: pdca.asset/v2
id: ontology:process/select-task-subgraph
type: process
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 4.0.0-rc.2
dcterms_modified: '2026-09-14'
summary: CONTEXT-01：只读当前动作需要的事实
---

# CONTEXT-01：只读当前动作需要的事实

每次从集中records中的具名项目context、自己的task／事件／请求开始；按目标阶段读方法，按SCENE读产物规则，遇到能力／资源／恢复事件再读对应权威。相同规则版本已读可复用，可变任务状态和用户操作必须重核。

不递归加载全ontology、legacy、所有模板或兄弟记录。全局Skill八入口只作方法选择，阶段入口不换执行者；读取场景方法不重新创建场景任务。集中资源冲突查询只需作用域及owner等最小元数据，不需要其他任务完整会话。任务输入显式列公共规则、需求、定义、产物和来源；参考资产先做适用性核验，不把旧normative字段当当前授权。关系存在不代表必须追读整图。

压缩摘要只留项目／task／attempt／Agent绑定、当前阶段、固定对象指针、未决操作与待用户事项。恢复读取这些原始记录，不能只信摘要；缺必要内容阻断，不重新解释目标。

评估上下文成本需含初次、重复读取、恢复重查与返工，不以字数减少宣称效果。独立输入不等于禁止共享固定允许的模型，但禁止未选择的活动对话和共享记忆。
