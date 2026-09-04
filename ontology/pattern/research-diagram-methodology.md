---
schema: pdca.asset/v1
id: ontology:pattern/research-diagram-methodology
type: pattern
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/research-diagram-methodology/1.0.0
summary: 调研图示方法论：架构师为主、多图mermaid inline、通用模板、每图溯源primary source
relations:
  specializes:
  - ontology:pattern
  guides:
  - ontology:concept/domain-entity
  - ontology:domain/skill-research
  relates_to:
  - ontology:concept/knowledge-provenance
  - ontology:pattern/ontology-modular-reference
  - ontology:concept/writing-for-agents
attributes:
- name: diagram_set
  desc: 多图集合（P0+P1）
  constraint: P0必含架构图C4 L2+逻辑图时序/流程+生命周期状态机；P1含数据流+部署+C4 L1，尽可能多
  testable_signal: 运行 grep -c 'mermaid' ontology/pattern/research-diagram-methodology.md
    检查≥3 且 grep -q 'C4 L2' 检查命中，且经 validate 通过
- name: mermaid_inline
  desc: mermaid inline于report
  constraint: 所有图为 mermaid 代码块 inline于 research-report.md，可 diff可渲染，grep mermaid 可检
  testable_signal: 运行 grep -c '```mermaid' templates/research-report.md 检查≥3 且经 validate
    通过
- name: architect_audience
  desc: 架构师为主
  constraint: 架构图C4 L2+模块依赖为主，兼术语表供新同学
  testable_signal: 检查本文件含 '架构师' 且含 'C4 L2' 且经 validate 通过 且运行 grep -q 'fix' ontology/pattern/research-diagram-methodology.md
    && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q
    'OK'
- name: universal_template
  desc: 通用模板
  constraint: 适用于所有research，非专于ZFS Crypto；ZFS为首个示范
  testable_signal: 检查 templates/research-report.md 含 mermaid占位且 grep -q 'research-diagram'
    可命中
- name: source_provenance
  desc: 每图溯源primary source
  constraint: 每mermaid图附1条Source源码行或官方doc链接可追溯
  testable_signal: 运行 grep -c 'Source:' ontology/pattern/research-diagram-methodology.md
    检查≥3 且经 validate 通过
---

# 调研图示方法论（Research Diagram Methodology）

> **准则**：所有 `research` 报告必含多图 `mermaid` inline，架构师一图建心智模型，ZFS Crypto为首个示范。

## 图集（尽可能多，mermaid）

### P0 必含（3图）

**1. 架构图 C4 L2（Container）**

```mermaid
graph TD
    A[ZFS Crypto] --> B[ZIO Layer]
    A --> C[DMU Layer]
    B --> D[Encryption Engine]
    C --> E[Key Management]
    %% Source: zfs.git/module/zfs/zio.c:120
```

*Source: `zfs.git/module/zfs/zio.c:120` + `OpenZFS docs`*

**2. 逻辑图 时序/流程**

```mermaid
sequenceDiagram
    participant App
    participant ZFS
    participant Crypto
    App->>ZFS: write()
    ZFS->>Crypto: encrypt()
    Crypto-->>ZFS: ciphertext
    %% Source: zfs.git/module/zfs/dmu.c:80
```

*Source: `dmu.c:80`*

**3. 生命周期图 状态机**

```mermaid
stateDiagram-v2
    [*] --> Unencrypted
    Unencrypted --> Encrypting
    Encrypting --> Encrypted
    Encrypted --> Decrypting
    %% Source: OpenZFS Crypto design doc
```

*Source: `OpenZFS Crypto Design`*

### P1 扩展（按需）

- **数据流图** `graph LR`（明文→加密→存储）
- **部署图** `graph TD`（Pool→Dataset→Key）
- **C4 L1 Context**（用户→ZFS→存储）

## 通用模板

`templates/research-report.md` 含上列6图 `mermaid` 占位，`grep -c '```mermaid'` ≥3 硬拦于 `skill-research` 门禁。

## 可验证性

每图 `Source:` 行必须为可复核 `primary source`（源码行 `file:line` 或官方doc URL），否则 `OOPS!` 式审查 `P08 missing provenance`。

## 门禁

`skill-research` 增加 `grep -c mermaid ≥3` 且每图含 `Source:`，`ci-ontology-gate` 可 `GATE OK`。
