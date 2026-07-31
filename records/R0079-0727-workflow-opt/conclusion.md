---
schema: pdca.asset/v1
id: R0079-0727-workflow-opt
phase: check
source_ids: [E01, E02, E03, E04, E05, E06]
---

## 上下文
参照 mattpocock/skills 设计模式对 PDCA 工作流核心改进。包括双轴 code-review、disable-model-invocation 标记、to-spec 标准化模板、残留清理。

## 假设与结果
- **假设**：双轴审查能更好区分"编码合规但功能错误"和"功能正确但编码违规"两类问题 → **确认**：skills/code-review/SKILL.md 重写为双轴并行子代理模式
- **假设**：标记 disable-model-invocation 能防止 AI 不适时触发交互式技能 → **确认**：grill + domain-modeling 已加标记，AGENTS.md 新增约定
- **假设**：to-spec 标准化模板能提高 Plan 产出一致性 → **确认**：模板就位且 flow-plan 引用

## 分析
四个子任务全部完成。核心改动影响 skills/、flows/、AGENTS.md、templates/ 四个目录。

## 适用边界
- 目标项目仍无 Rust/toml 等已清理语言文件
- 新技能（triage/wayfinder/prototype）尚未实现，属后续范围

## 下一轮建议
1. 实现 triage 技能（作为 Plan 前置步骤，参考 mattpocock 的状态机模式）
2. 实现 wayfinder 技能（Act→Plan 多 session 规划桥接）
3. 考虑用新工作流启动一个真实业务任务，端到端验证流程