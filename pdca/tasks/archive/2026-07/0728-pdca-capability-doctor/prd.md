# 实现环境 doctor、能力协议与技能索引生成

## 问题陈述

入口存在断链，`PDCA_HOME` 和运行依赖缺少统一诊断；flow/skill 硬编码 `task()`、`pdca context` 等平台接口，在能力缺失时行为不确定。

## 解决方案

- 定义 required/optional/fallback 能力协议。
- 实现当前环境探测和主会话降级，不扩展为多平台 SDK。
- doctor 检查仓库发现、权威入口、本地引用、运行依赖和能力结果。
- 从 flow/skill frontmatter 生成单一 Markdown 技能索引。
- 缺失必需能力 fail-closed；缺失可选能力显示并验证 fallback。

## 验收标准

- [ ] `PDCA_HOME` 未设时能按仓库规则解析并给出配置提示。
- [ ] 所有权威入口本地引用可解析，断链数为 0。
- [ ] 缺少 agent.spawn、context.retrieve 时走已声明 fallback。
- [ ] 核心 flow/skill 不再硬编码平台专用子代理调用。
- [ ] 索引生成两次字节一致，重复 ID、缺必填 frontmatter 或断链均失败。

## 范围外

- 所有第三方 Agent 平台适配器。
- 完整产品级 `pdca` CLI。
- 将能力探测结果当作跨会话授权。
