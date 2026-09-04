---
schema: pdca.asset/v1
id: ontology:concept/deterministic-fixture
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/deterministic-fixture/1.0.0
summary: 确定性夹具：输入、预期输出和 pass/fail 信号均固定
relations:
  specializes:
  - ontology:concept/pdca-evidence
  relates_to:
  - ontology:domain/ai-efficiency-ai-friendliness-review-methodology
attributes:
- name: applicability
  desc: 适用于所有需要确定性验证的场景
  constraint: 见正文
  testable_signal: 检查夹具是否包含输入、预期输出和 pass/fail 信号
- name: input
  desc: 夹具输入
  constraint: 固定不变
  testable_signal: 检查输入是否可复现
- name: expected_output
  desc: 预期输出
  constraint: 固定不变
  testable_signal: 检查输出是否与预期一致
- name: pass_fail_signal
  desc: pass/fail 信号
  constraint: 二值可观察
  testable_signal: 检查信号是否明确
---

# Deterministic Fixture（确定性夹具）

输入、预期输出和 pass/fail 信号均固定，可在不调用 Agent 模型的情况下重复执行的测试场景。

## 三要素

1. **输入**：固定不变的测试输入
2. **预期输出**：固定不变的预期结果
3. **pass/fail 信号**：二值可观察的判定信号

## 原则

- 确定性夹具不依赖模型调用，可重复执行
- 失败路径使用固定夹具，失败必须得到预期错误码
- 夹具应构造保持标题不变但交换映射的反例，以验证 oracle 能拒绝契约漂移
- 引用故障必须删除实际被引用的受控文件，不能由测试分支直接返回预期错误码

## 验证

- 纯函数（解析 + 校验）四类边界 fixture：正常/缺失/不一致/无声明跳过
- 与 T0230 轮数模型测试、T0232 DAG 测试同构：确定性、无模型依赖、可回归
- 效果判定优先使用机器 pass/fail、明确错误码和相同输入的前后配对

## 边界

确定性流程夹具不能外推为真实 LLM 成功率。能力探测结果只对当前环境和会话有效。