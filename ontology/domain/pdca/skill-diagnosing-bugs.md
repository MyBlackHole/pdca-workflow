---
schema: pdca.asset/v2
id: ontology:domain/skill-diagnosing-bugs
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 证据驱动诊断
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:concept/pdca-evidence
  - ontology:concept/pdca-recovery
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 证据驱动诊断

## 适用条件

当前执行契约包含本动作时按需读取；本技能不拥有阶段转换或授权权力。

## 动作与判据

固定环境、版本与最小复现，保留原始错误和时间线。建立可证伪假设，每轮只改变必要变量；利用日志、调用链和真实观测淘汰假设，再验证最小修复及回归。

有副作用的实验先核对授权；未知外部结果不盲目重试。人工确认循环参考同目录diagnosing-bugs中的Markdown模板，不依赖自带shell脚本。

## 失败处理

缺必需输入、来源或工具时报告具体缺项及影响；未执行与未知结果不得写成成功。
