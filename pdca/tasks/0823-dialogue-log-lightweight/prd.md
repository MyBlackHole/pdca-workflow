# 改进：阶段边界对话摘要（轻量版过程存档）— PRD

## 来源

用户问询"交流信息如何记录/对话交流过程"后裁决：做轻量版，反对全量录制。

## 问题陈述

完整对话过程零持久化：推理路径、被否决的备选、用户即时反应随会话消失。跨 session 恢复时无法回答"当初为什么没选 B"。

## 方案（documentation 场景）

### 机制定义（handoff-work 单点权威）
handoff-work 新增「对话摘要存档」节：
- 触发：每个阶段转换前（Done when 处）
- 落点：任务目录 `dialogue-log.md` 追加式
- 每段 ≤2KB，含四要素：本阶段讨论要点（≤5条）/ 被否决的备选及理由 / 用户关键反应原话（呼应 captured:true）/ 未解决即跳过的疑点
- 明确不做：全量逐句、常规确认、工具输出

### flows 接线（指针，不重复定义）
flow-plan P7 / flow-do Z4 / flow-check Ch6 / flow-act Ac8 各加半句"转换前追加对话摘要（见 handoff-work）"

## 测试接缝声明

### 声明的测试接缝
- seam: 无独立测试——纯文档约定，验证为本任务自身按新机制产出首份 dialogue-log.md（自反）

## 验收标准

- [ ] AC-1: handoff-work 含对话摘要存档节（触发时机/落点/四要素/大小上限/不做清单）
- [ ] AC-2: flows 四处转换步骤各含指针句
- [ ] AC-3: 本任务自身产出首份 dialogue-log.md 且符合四要素格式（自反验证）
- [ ] AC-4: baseline 更新 audit 零 issue；evidence 齐备 convergence valid

## 范围外

- 全量逐句记录；平台 session 导出集成；历史任务回填
