---
schema: pdca.asset/v2
id: ontology:concept/capability-protocol
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
status: active
authority: normative
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-14'
summary: CAP-01：能力核验与执行授权分离
---

# CAP-01：能力核验与执行授权分离

正式任务必需：真实独立 Agent、新上下文初始化、可与用户双向交互、等待后原会话继续、私有记录写入、获准业务工具与可核查的用户消息来源。任一未知或不可用，不能以父 Agent模拟补齐。

环境级核验记录宿主／工具版本、记忆与初始化设置、权限、原生创建／恢复语义及测试证据。适用范围内可复用；受影响变化后重核。没有相关证据标 NOT_RUN／unknown，不生成虚假已通过。

每次创建和继续仍检查实际参数、输入、返回身份、状态、控制和资源资格。环境旧 PASS 不证明本次成功；新 ID 不证明没继承历史，同 ID 不证明状态连续。

能调用 Agent 与能让用户直接沟通该 Agent 不同；能新建与能恢复不同；并发与身份隔离不同；独立会话与文件／网络安全隔离不同。逐项报告，不用一个“支持”遮盖。

不要求另写 adapter。使用宿主原生能力，按需读 bootstrap/native-agent-notes.md；工具参数从现场 schema 核对。能力声明不是阶段启动授权。
