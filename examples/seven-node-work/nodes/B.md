---
schema: pdca.work-node/v3
example_only: true
state: example
work_id: EXAMPLE-BOUNDED-WRITE
tree_revision: tree-2
node_id: B
node_revision: '1'
parent_node_id: R
children:
- B1
- B2
definition_refs: []
test_suites:
  ontology_modeling: ../scene-tests.md
  ontology_projection: ../scene-tests.md
  ontology_conformance_verification: ../scene-tests.md
---

# B：有界写入引擎

## 目标与组合

给定N=state长度、整数offset与非空bytes，先B1范围检查，OK后才B2原子应用；拒绝保持原块且B2调用数为0。

B1/B2真实版本组合；E_TYPE/E_DOMAIN/E_BOUNDS按B1，注入应用失败为E_APPLY。

必须AC：输入/输出及错误语义符合上述合同；授权范围内无额外副作用。此示例只说明任务边界，真实冻结前仍需填NODE-01完整接口与suite，不可把本教学片段直接当生产完整基线。

## 执行测试具体样本

正例输入：state=00×16,offset=15,data=[255]。预期：OK，末字节FF。

反例输入：state=00×16,offset=15,data=[255,255]。预期：E_BOUNDS，原块不变；B2_call_count=0。

判定：固定初始对象，调用当前节点，精确比较返回/输出/前后状态；组合节点追踪真实孩子调用及版本；异常、环境错误或缺日志不能当PASS。测试后先固定证据再清理沙箱。

## 三场景

建模以当前父seed/用户目标检验合同覆盖；执行检验上述行为；独立审查以正确/故意违例实现样本测试审查能力，再核对真实实现。详细场景用例与21任务顺序见场景文件。
