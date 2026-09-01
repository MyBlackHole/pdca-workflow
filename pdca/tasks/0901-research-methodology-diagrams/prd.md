# 调研方法论：以ZFS Crypto为例补架构图逻辑图生命周期图使易理解

## 背景

T0500类ZFS Crypto研究难理解因缺图。Architect为主读者需快速建立心智模型，现有 `skill-research` 仅定 `research-report.md` 四段（目标/方法/发现/结论）未定图标准，`ontology/domain/skill-research.md` 无 mermaid 门禁，`knowledge-provenance` 未要求图溯源。

## 目标

- 沉淀 `ontology/pattern/research-diagram-methodology.md` 通用方法论：所有 `research` 报告必含多图（mermaid inline），架构师可一图建立心智模型
- ZFS Crypto为首个示范，产出架构图+逻辑图+生命周期图+数据流等可直接复用

## 范围

- 输入：ZFS Crypto源码/官方doc（primary source）、C4/Mermaid、现有research 15个
- 输出：1 pattern节点 + `research-report.md` 多图模板 + 全绿
- 不做：不改业务实体，不重写T0500全文

## 功能需求

1. 方法论文档：`ontology/pattern/research-diagram-methodology.md` 定义6图（P0架构图C4 L2+逻辑图时序/流程+生命周期状态机，P1数据流+部署+C4 L1上下文）均 mermaid inline，`grep mermaid` 可检，每图附1条primary source引证（源码行或官方doc链接）
2. 通用模板：`templates/research-report.md` 更新为7段：目标/方法/发现（含6图mermaid块）/结论/术语表/参考资料（primary source列表）
3. 门禁：`skill-research` 增加“无图阻断”校验（`grep -c mermaid research-report.md ≥3`）
4. 示范：为ZFS Crypto补3图示例（可空内容但含mermaid框架与引证占位）

## 非功能需求

- `islands:0`，`scaffold` 可产，`mermaid` 可渲染（`mermaid`语法 `bash -n` 级校验）

## 验收标准

- [ ] AC-1 方法论已沉淀：`research-diagram-methodology.md` 6图定义且 `validate` 通过且含 `mermaid`
- [ ] AC-2 模板已更新：`templates/research-report.md` 含6图mermaid占位且可 `grep mermaid` ≥3
- [ ] AC-3 架构师可用：P0三图（C4 L2+时序+状态机）齐且每图含 `Source:` 引证
- [ ] AC-4 通用可校验：`grep -c mermaid` 与 `validate` 双 `GATE OK`
- [ ] AC-5 收敛 valid:true

## 关联本体节点

```
ontology:pattern/research-diagram-methodology
ontology:domain/skill-research
ontology:concept/knowledge-provenance
ontology:pattern/ontology-modular-reference
```

## 拆分映射

- 方法论本体 -> ontology:pattern/research-diagram-methodology
- 模板与门禁 -> ontology:domain/skill-research
