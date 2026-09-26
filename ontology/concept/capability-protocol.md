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
dcterms_modified: '2026-09-27'
summary: CAP-01：核验宿主是否能承载正式独立任务
---

# CAP-01：宿主能力资格

CAP-01 只回答：**当前宿主/配置是否具备承载正式 PDCA task 所需的原生能力。**
它不创建 task、不选择上下文、不执行 dispatch，也不产生 phase 授权。

## 必需能力

正式 task 需要能够核验：

| 能力 | 必须能证明的语义 |
|---|---|
| new | 创建真实新实例，并能观察/控制其初始上下文来源；新 ID 本身不证明 fresh |
| communicate | 用户消息能到达该实例，来源和路由可核查；父 Agent 转述不能冒充用户 |
| continue | 等待后继续原实例；同 ID 不足以证明状态连续，新 spawn 不能冒充 resume |
| suspend/control | 等待、取消、停止与继续不会由父 Agent 轮询监工或代替审批 |
| writes | task record scope、获准业务工具/写域和共享资源边界可落实；会话隔离不等于文件/网络沙箱 |
| events | 创建、完成、失败、取消等原生回执可核查，不能只依赖 Agent 自述 |

任一当前任务所需能力为 unknown / not_run / unavailable 时，正式创建或继续保持 blocked；
父 Agent、角色提示、摘要或额外 adapter 不能模拟补齐。

## 能力证据

环境级核验记录宿主/工具版本、配置、初始化/记忆设置、权限和原生语义。
在版本与相关配置未变化且适用范围相同的情况下可以复用；受影响变化后重新核验。

环境级 PASS 只证明“能力存在”，不证明某次创建/恢复实际成功。
具体 invocation 的参数、输入、返回身份和回执由 agent-dispatch / RECOVERY-01 记录。

工具名（如 fresh/fork/resume）没有跨宿主统一语义；按现场 schema 与真实行为判断，不猜等价调用。
[历史来源说明](../provenance/README.md)中的旧资料只作候选证据，不是当前参数承诺。

精确能力记录格式见 [capability-check](../contracts/record-shapes/capability-check.md)。
真实宿主验收未运行时保持 NOT_RUN/unknown，不以静态脚本或文档检查升级结论。
