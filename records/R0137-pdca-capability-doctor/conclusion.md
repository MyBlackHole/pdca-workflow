---
schema: pdca.asset/v1
id: R0137-pdca-capability-doctor
phase: check
source_ids: [doctor-result, skills-index]
---

## 上下文

检查环境诊断、抽象能力协议和技能索引是否减少 AI 的入口误判与无效工具调用。

## 假设与结果

- doctor 能定位仓库、必需能力和本地断链：通过，53 个引用无断链。
- 缺失可选能力时行为明确：通过，`agent.spawn` 降级主会话，`context.retrieve` 降级文件检索。
- 技能索引可重复生成：通过，共 41 个 flow/skill。

## 分析

活跃 flow/skill 中硬编码 `task()` 与 `pdca context` 的数量为 0。缺少可选能力不会伪装成功，必需能力缺失则 fail-closed。只保留有当前消费者的 Markdown 索引，删除了重复 JSON 索引。

## 适用边界

能力协议只覆盖当前执行环境，不宣称兼容所有 Agent 平台；探测结果不是跨会话授权。

## 下一轮建议

只有出现真实新运行环境且现有 fallback 失败时，才增加适配器。
