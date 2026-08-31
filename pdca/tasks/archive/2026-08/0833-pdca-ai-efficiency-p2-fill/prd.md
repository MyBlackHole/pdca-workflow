# 补齐 PDCA 本体 P2 差距

## 目标

收尾 T0434 识别的 4 项 P2 差距。

## 实施计划

### G7：setup-matt-pocock-skills 模式
- 新建 `ontology:concept/setup-skill` 概念节点
- specializes: `ontology:concept/skill-mechanics`
- 表示配置/设置类技能的通用模式

### G8：wizard/teach/to-questionnaire 模式
- 新建 `ontology:concept/wizard` 概念节点
- 新建 `ontology:concept/teach` 概念节点
- 新建 `ontology:concept/to-questionnaire` 概念节点
- 均 specializes `ontology:concept/skill-mechanics`

### G9：Context-pointer branch trigger
- 更新 `ontology/concept/context-pointer.md`
- 新增 `branch_trigger` attribute（分支触发条件列表）

### G10：SKILL-MECHANICS 等价文档
- 新建 `ontology:concept/skill-mechanics-detail` 概念节点
- 表示 SKILL-MECHANICS 等价的详细机制描述

## 验收标准
- AC-1~AC-5：所有概念节点通过 ontology-validate，收敛映射 valid:true