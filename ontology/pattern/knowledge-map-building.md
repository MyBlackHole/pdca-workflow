---
schema: pdca.asset/v2
id: ontology:pattern/knowledge-map-building
type: pattern
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-10
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/knowledge-map-building/3.1.0
summary: 知识地图构建方法论：05主03辅骨架、版本化目录布局、§〇版本路由、孤岛裁决、三项实证
relations:
  guides:
  - ontology:domain/skill-research
  relates_to:
  - ontology:concept/pdca-task
  - ontology:pattern/research-diagram-methodology
  instance_of:
  - ontology:pattern
attributes:
- name: skeleton_05_primary
  desc: 05为主骨架
  constraint: 每分册必含能力总览表（能力→代码→使用方）+ 复用扩展指南 + 影响范围表 + 不该放入的边界；吸收03任务链写法与实证铁律
  testable_signal: 运行 grep -l '能力总览' /home/black/Public/aio/rdb-skills/skills/rdb-tools-design/references/*/6.2.0.0.md
    检查命中4份能力分册且 grep -q '产物清单' 构建分册 且经 validate 通过
  evidence_level: structure
- name: versioned_layout
  desc: 版本化目录布局
  constraint: 分册各为目录，每版本一文件 `<tag>.md`；00-index 含 §〇 三步选版本 + 向下取底 + 已建版本清单；SKILL 先定版本流程
  testable_signal: 运行 ls /home/black/Public/aio/rdb-skills/skills/rdb-tools-design/references/ 检查5个分册目录存在且 grep
    -q '版本路由' references/00-index.md 且经 validate 通过
  evidence_level: structure
- name: island_triage
  desc: 孤岛裁决清单
  constraint: SKILL 含孤岛与废弃裁决速查 + 落码原则禁区；每分册有孤岛/冗余章节；命中孤岛即停
  testable_signal: 运行 grep -q '孤岛' /home/black/Public/aio/rdb-skills/skills/rdb-tools-design/SKILL.md 且各分册 grep
    -c '孤岛' 均≥1 且经 validate 通过
  evidence_level: structure
- name: evidence_discipline
  desc: 三项实证纪律
  constraint: 每条路径过存在/现行链路/逐字一致三项实证；无法确认即标记不猜测；文档滞后以代码为准并记录差异
  testable_signal: 运行 grep -q '三项实证' /home/black/Public/aio/rdb-skills/skills/rdb-tools-design/SKILL.md 且 grep -q
    '无法确认' 各分册至少一处诚实标记样例或差异清单 且经 validate 通过
  evidence_level: structure
- name: contract_check
  desc: 契约核对表
  constraint: 跨模块隐式契约逐字核对表（常量发送方 = 接收分发方）；定位结论含契约核对结果
  testable_signal: 运行 grep -q '契约核对' /home/black/Public/aio/rdb-skills/skills/rdb-tools-design/SKILL.md 检查命中且经 validate
    通过
  evidence_level: structure
revision: 3.1.0
authority: reference
semantic_kind: individual
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
validation:
  claim_status: unverified
  adoption: claim_review_required
---

# 知识地图构建方法论（Knowledge Map Building）

> **准则**：为存量代码库建「需求 → 代码路径」导航时，以「能力 → 代码 → 使用方」为主骨架，以版本化目录承载多版本，以孤岛裁决防引用错误实现，以三项实证保每条路径真实。首个示范：`rdb-tools-design`（T2154）。

## 骨架选择（05 主 03 辅）

- 工具/能力型代码库（无业务体系划分）→ 05 骨架：能力总览表 + 使用方统计 + 复用/扩展判断 + 影响范围 + 不该放入的边界 + 项目级机制。
- 业务编排型代码库（有体系 × 生命周期）→ 03 骨架：领域表 + 分体系实现地图 + 统一阶段链路。
- 无论何种骨架，均吸收：任务链写法（入口 → 分发 → 核心实现 → 回写）+ 三项实证铁律 + 新旧边界裁决清单。

## 版本化布局

```
<skill>/references/00-index.md          ← §〇 版本路由 + 路由矩阵（行号以最新版为基准）
<skill>/references/NN-<模块>-knowledge-map/<tag>.md   ← 每版本一文件，章节编号跨版本一致
```

- §〇 三步选版本：取基线 tag → 向下取底 → 无更低/高于最新读最新并注明以代码为准。
- 定位结论开头注明 `<子系统> @ <基线版本> → <版本文件>`。
- 同一章节跨版本编号不漂移；该版本未引入的能力保留章节并注明「该版本未引入」。

## 孤岛裁决

- 勘测期即用引用计数区分现行/孤岛/冗余拷贝/疑似废弃四类。
- SKILL 设裁决速查 + 落码原则（新代码只许落现行目录）；分册设孤岛章节；路由流程含「命中孤岛即停」关卡。

## 实证纪律

- 先路由，再验证，后输出；文档是地图，代码是事实。
- 每条路径：存在（ls/Read）→ 现行（grep 调用方）→ 逐字一致（符号/常量逐字核对）。
- 无法确认就标记，写明缺什么信息，不猜测。

## 来源

- 示范任务：T2154（record `T2154-0910-aio-tools-knowledge-map`，verdict confirmed）。
- 对标基线：`rdb-feature-design`（00-index §〇 + 03/04/05 版本化目录，6.2.0.0）。
- 沉淀理由：方法论可复用（下次为他项目建知识地图直接套用）；内容知识留外部 skill 单一事实源，避免双写漂移（C4 决策）。
