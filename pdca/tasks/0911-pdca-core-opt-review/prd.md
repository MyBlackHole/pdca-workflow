# PDCA设计核心 B/A/C 命名适配性复核 ontology:concept/pdca

## 背景

T2153 已完成“PDCA 流程本体优化空间全库调研”，结论为 P0 已处理，P1/P2 候选已沉淀到 `ontology:decision/t2153-opt-backlog`。
用户进一步收窄并修正目标：复核 `ontology:concept/pdca` 中“设计核心：本体树驱动（B→A→C）”的 A、B、C 是否应成为核心场景划分；不保留六个 `scenario_type` 作为核心场景，六个具体场景只作为不同 tool/skill 的选择方式处理。

当前权威文本使用：

- B：建树，走知识产出路径
- A：按树实现，走代码变更路径
- C：逐项校验，走评审校验路径

潜在问题是叙述顺序为 B→A→C，但核心路由仍以六个 `scenario_type` 与路径 A/B/C 混合表达，可能把“任务大类”和“执行工具选择”耦合在一起。
本任务调研是否推荐将核心场景收敛为 A/B/C，并给出六场景下沉到 tool/skill 选择层的候选方案与迁移边界；不直接修改权威本体正文。

## 范围

聚焦设计核心命名：

- `ontology:concept/pdca`
- `ontology:process/flow-do`
- `ontology:decision/t2153-opt-backlog`
- `meta.scenario_type` 六值与 skill/tool 路由相关脚本
- 历史任务中引用“路径 A/B/C”“B→A→C”“建树/按树实现/逐项校验”“scenario_type”的证据

排除范围：

- 不逐节点深审领域子树（bcachefs/zfs/core 等）
- 本任务不直接实施 `scenario_type` 结构迁移或权威流程正文修改
- 不处理 T2153 backlog 中与命名无关的候选项

## 方法

1. 语义诊断：检查 A/B/C 是否比六个 `scenario_type` 更适合作为核心场景划分。
2. 分层评估：区分核心任务大类、执行路径、tool/skill 选择三层职责，判断六场景是否应下沉到 tool/skill 层。
3. 候选设计：给出至少两组方案，例如“保留六场景”“核心 A/B/C + skill 子类型”“A/B/C 重命名为语义名”。
4. 迁移边界建议：若推荐收敛为 A/B/C，说明 task schema、flow-do、transition gate 和 skill 路由的后续 Improvement Task 边界；不设计旧六场景兼容层。

## 验收标准

- [ ] AC-1: 明确判断核心场景是否推荐从六个 `scenario_type` 收敛为 A/B/C，并区分“必须改”“建议改”“不建议改”
- [ ] AC-2: 至少给出两组候选方案，逐项比较语义准确性、顺序一致性、迁移成本和 skill/tool 路由可行性
- [ ] AC-3: 若建议收敛为 A/B/C，输出后续 Improvement Task 边界：task schema、flow-do、transition gate、skill/tool 选择机制和验证方式；明确不保留旧六场景兼容层；若不建议，给出保留六场景的理由和消歧建议
- [ ] AC-4: research 产物可追溯到本仓库权威文件或既有 record，且不直接修改权威流程正文

## 关联本体节点

```
ontology:concept/pdca
ontology:process/flow-do
ontology:decision/t2153-opt-backlog
```

## 拆分映射

- A/B/C 核心场景诊断 -> ontology:concept/pdca
- flow-do 路由与 skill/tool 分层检查 -> ontology:process/flow-do
- T2153 关联候选复核 -> ontology:decision/t2153-opt-backlog
