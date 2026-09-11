---
schema: pdca.asset/v2
id: ontology:domain/skill-chinese-environment
name: chinese-environment
summary: Set up projects for Chinese-speaking developers with all output in Chinese.
description: Use when setting up a project for Chinese-speaking developers, or when all output (docs, comments,
  commits) should be in Chinese
invocation: manual
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/skill-chinese-environment/3.1.0
relations:
  relates_to:
  - ontology:concept/writing-for-agents
  - ontology:concept/knowledge-artifact
  - ontology:concept/pdca-task
  instance_of:
  - ontology:concept/knowledge-artifact
revision: 3.1.0
authority: reference
validation:
  structural_checks:
  - 递归解析本节点身份及关系列表；目标 ID 必须可定位。引用数量不作为行为验证。
  claim_status: unverified
  adoption: claim_review_required
semantic_kind: individual
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
---

---
name: chinese-environment
description: Use when setting up a project for Chinese-speaking developers, or when all output (docs, comments, commits) should be in Chinese
---

# Chinese Environment（中文环境）

## Core Rules

1. **AI 思考过程使用简体中文** — 内部推理、分析、规划、调试、代码审查等所有思考过程均使用简体中文
2. **AI → user 沟通使用简体中文**
3. **项目文档使用简体中文** — README、API 文档、changelog、spec、design docs
4. **代码保持英文** — 变量名、函数名、类名、类型名、API 签名保持英文
5. **代码注释用中文** — 使用 `// 备注:` 前缀；同时加载 `code-comments` 处理注释格式细节；保留原始英文注释
6. **Commit message 用中文** — 遵循 conventional commits 格式：`类型: 中文描述`
7. **项目 locale** — `zh_CN.UTF-8`，时区 `Asia/Shanghai`，编码 `UTF-8`

## Verification Checklist
- [ ] AI 思考/推理全程使用简体中文
- [ ] 所有文档为简体中文
- [ ] 所有代码标识符为英文
- [ ] Commit message 格式 `类型: 中文描述`
- [ ] 代码注释引用 `code-comments` 或使用 `// 备注:` 前缀
- [ ] 保留代码中原始英文注释
- [ ] locale 和时区设置为中国标准

## 已知坑

- 全中文环境勿在文档/注释/提交中混入未定义的英文术语；命名与术语表保持一致。
