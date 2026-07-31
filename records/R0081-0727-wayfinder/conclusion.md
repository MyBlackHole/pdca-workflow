---
schema: pdca.asset/v1
id: R0081-0727-wayfinder
phase: check
source_ids: [E01]
---

## 上下文
实现 wayfinder 技能，支持多 session 大型规划的分票推进模式。

## 假设与结果
5 项验收标准全部通过。适配到文件系统（pdca/tasks/wayfinder-<name>/），无 issue tracker。

## 分析
方式与 triage 相同：一次实现，直接通过。核心是 MAP.md + ticket 文件 + 迷雾推进逻辑。

## 适用边界
- wayfinder 比 triage 复杂，建议配合真实大需求验证
- 暂未与 flow-plan/flow-act 集成，触发需用户显式调用
