---
schema: pdca.work-node/v3
example_only: true
state: example
work_id: EXAMPLE-BOUNDED-WRITE
tree_revision: tree-2
node_id: A
node_revision: '1'
parent_node_id: R
children:
- A1
- A2
definition_refs: []
test_suites:
  ontology_modeling: ../scene-tests.md
  ontology_projection: ../scene-tests.md
  ontology_conformance_verification: ../scene-tests.md
---

# A：请求规范化

## 目标与组合

把合法十进制offset文本与偶数位十六进制data文本转成整数及非空bytes；不得隐式改用户单位。

固定A1/A2版本与错误传播；任一孩子失败不输出可交付规范化请求。

必须AC：输入/输出及错误语义符合上述合同；授权范围内无额外副作用。此示例只说明任务边界，真实冻结前仍需填NODE-01完整接口与suite，不可把本教学片段直接当生产完整基线。

## 执行测试具体样本

正例输入：offset="0",data="00FF"。预期：offset=0,data=[0,255],length=2。

反例输入：offset="0",data="F"。预期：E_HEX，不向B交付半个请求。

判定：固定初始对象，调用当前节点，精确比较返回/输出/前后状态；组合节点追踪真实孩子调用及版本；异常、环境错误或缺日志不能当PASS。测试后先固定证据再清理沙箱。

## 三场景

建模以当前父seed/用户目标检验合同覆盖；执行检验上述行为；独立审查以正确/故意违例实现样本测试审查能力，再核对真实实现。详细场景用例与21任务顺序见场景文件。
