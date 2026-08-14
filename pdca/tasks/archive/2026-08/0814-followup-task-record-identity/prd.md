# 跟进：task/record identity 冲突根因与修复方案验证

## 问题陈述

- **现状**: T0260 发现 23 个 task ID 被不同 slug 使用，5 个 occurrence 的目录与 payload record_id 不一致，导致全量 backlog 重建返回 `EVENT_PATH_MISMATCH`。
- **目标**: 用历史来源、分配路径和并发复现验证根因，形成可证伪、不可变历史安全的 P0 修复方案。
- **差距**: 当前只确认冲突与阻断事实，尚未证明 ID 分配器、复制/迁移或 record 生命周期中的哪一环是唯一根因。

## 解决方案

保持 research 范围：枚举所有任务创建路径和 ID 分配方式，按时间/git 历史区分旧迁移、复制、普通 Plan 创建、Improvement Candidate 晋级和 record 生命周期行为；构造并发分配及 record 路径不变量复现。至少比较全局原子 ID 分配器与“不可变 record identity 为主、task ID 为显示编号”两类方案。经独立 development 任务终审前不修改现有任务、record、事件或聚合器。

自我审查本身不作为证据。每个根因判断必须由审查结论之外的 oracle 支持：真实历史路径、可执行复现、跨文件不变量、负对照或用户确认。无法获得独立支持时结论标记 `inconclusive`，不得晋级候选。

## Seam 分析

research 场景不声明开发测试 seam；方案若晋级为 development Improvement Task，必须另行确认 seam。

## 用户故事

1. 作为流程维护者，我想知道身份冲突的确切产生路径，以便不靠猜测修复。
2. 作为记录消费者，我想保证 event 目录与 payload identity 恒等，以便完整投影可重建。
3. 作为历史记录维护者，我想保留不可变事实，以便修复不会篡改既有证据。

## 实现决策

- 本任务只做根因验证与修复方案，不直接修复。
- 本任务不重复泛化的“自我审查准确率”评估；T0260 已给出首轮 partial 结论，本轮只验证 P0 identity 根因。
- T0260 的 baseline 为：冲突 task ID=23、path mismatch event=5、全量聚合失败。
- 必须区分旧数据迁移问题与当前并发分配问题。
- 历史 task、record 和 occurrence 保持不可变；方案通过新写入不变量、派生投影或显式兼容边界处理历史事实。
- 本轮输出 Improvement Candidate 草案，但不创建治理系统中的正式 candidate/decision，也不晋级 development 任务。
- 同一代理撰写的分析与摘要不是独立复核；确定性工具结果也只能证明其实际覆盖的不变量。

## 测试决策

- 对每个 ID 创建入口建立可重复的顺序与并发复现。
- 对 event path、payload record_id 和 task meta.record 建立跨文件不变量检查。
- 方案必须包含相同输入的修复前失败/修复后通过设计。
- 加入至少一个已知正常创建路径作为负对照，防止检查器把所有历史差异都误报为 identity 缺陷。
- 在读取候选方案收益判断前冻结根因假设与预测；实际结果不符合预测时必须降级或推翻假设。
- 若当前真实创建路径均不能复现冲突或漂移，则结论为历史问题、当前根因 `inconclusive`，并停止提出代码修复。

## 验收标准

- [ ] AC-1: 列出全部 task ID/record ID 创建路径及其原子性、锁和失败语义。
- [ ] AC-2: 对 23 个冲突 ID 和 5 个 mismatch event 给出来源分类，证据可回溯到路径与时间。
- [ ] AC-3: 至少构造一个可重复复现当前冲突或路径漂移的真实代码路径；若不可复现，明确排除过的假设。
- [ ] AC-4: 至少比较“全局原子 ID 分配器”与“不可变 record identity 为主、task ID 为显示编号”两类方案，说明并发、安全、失败恢复、迁移和不可变历史权衡。
- [ ] AC-5: 推荐方案冻结 baseline、前后配对指标、观察窗口、回滚条件、development seam 草案和 Improvement Candidate 草案。
- [ ] AC-6: 不修改既有 task、record、occurrence 或正式 backlog。
- [ ] AC-7: 每个根因结论均绑定至少一种独立 oracle，并包含正常路径负对照；无独立支持的判断标记 inconclusive，不进入候选草案。
- [ ] AC-8: 对冻结的 H1–H4 逐项给出 supported、rejected 或 inconclusive，实际结果与预测不符时保留反证并降级结论。

## 范围外

- 不实施 identity 修复。
- 不重命名或删除历史记录。
- 不推进 backlog 消费、AI 遥测或 burst 归并候选。

## 备注

- 来源：T0260 partial verdict 的 P0 跟进。
- 进入 Do 前仍需完整 Grill、方向确认和 final confirmation。
- P4 拆解判断：根因入口、历史分类、复现和方案比较共用同一身份矩阵，保持单一 research task，不创建子任务。
