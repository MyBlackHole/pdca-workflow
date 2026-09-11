---
schema: pdca.asset/v2
id: ontology:domain/skill-tdd
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 用真实失败和通过验证实现
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:concept/pdca-execution-contract
  - ontology:concept/pdca-evidence
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 用真实失败和通过验证实现

## 适用条件

当前执行契约包含本动作时按需读取；本技能不拥有阶段转换或授权权力。

## 动作与判据

在契约范围内先写或定位体现目标行为的测试，实际运行并观察预期失败；再做最小实现，运行同一测试和影响范围回归，最后必要重构。

区分环境/依赖失败与测试证明的行为失败；跳过、未运行、空测试集不算绿色。保存命令、源码版本、退出状态与原始输出。没有运行工具时交付测试设计并明确not_run，不假称完成TDD。

## 失败处理

缺必需输入、来源或工具时报告具体缺项及影响；未执行与未知结果不得写成成功。
