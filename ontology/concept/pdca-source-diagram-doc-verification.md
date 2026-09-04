---
schema: pdca.asset/v1
id: ontology:concept/pdca-source-diagram-doc-verification
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/pdca-source-diagram-doc-verification/1.0.0
summary: 源码图解文档验证流程（函数级前置分析、mermaid 语法硬门禁、源码引用存在性核验、图例规范）
relations:
  specializes:
  - ontology:concept/pdca-acceptance-criterion
  relates_to:
  - ontology:concept/pdca-acceptance-criterion
---

# 源码图解文档验证流程（pdca-source-diagram-doc-verification）

来源：T0300（基于 backupstream 171.0.0 源码绘制 60 张 Mermaid 图后的沉淀）。

## 适用场景

为大型 C++/Go 代码库产出以图表为主的分析文档（架构图/流程时序图/状态机图），需保证图表可渲染、引用真实、覆盖完整。

## 关键流程

1. **函数级前置分析**：探索子代理按模块分批做函数级结构分析，记录关键枚举值、状态机状态数、函数行号；交叉核验枚举定义与 README/docs 行为描述互相印证。
2. **全部图表语法校验（硬门禁）**：提取文档所有 ` ```mermaid ` 块逐张用 mmdc 渲染校验；输出文件必须以 `.svg/.png/.md` 结尾。
3. **源码引用存在性核验**：正则提取文档中 `src/xxx.cpp` 引用逐一 `os.path.exists` 校验；缺失即写文档时用了猜测文件名，须改为真实文件名后复验（T0300 修正了 8 个）。
4. **Mermaid 语法易错点**：subgraph/节点标签避免裸 `,`/`(`/`)`/`:`；边标签用 `A -->|标签| B`；`A -- > text --> B` 会被误解析。
5. **覆盖率与图例规范**：每张图含中文节点标签 + 一行 `**图例**：...`；`grep -c '```mermaid'` 与 `grep -c '图例'` 须相等。

## 边界

只面向源码快照，不承诺跟踪未来版本；无性能断言；mmdc 逐图渲染 60 图约 1-2 分钟，适合 Do 阶段末尾一次性校验。

## 来源

- `（原知识层）source-diagram-doc-verification.md`
