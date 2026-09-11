---
schema: pdca.work-node/v3
example_only: true
state: example
work_id: EXAMPLE-BOUNDED-WRITE
tree_revision: tree-2
node_id: R
node_revision: '1'
parent_node_id: null
children:
- A
- B
definition_refs: []
test_suites:
  ontology_modeling: ../scene-tests.md
  ontology_projection: ../scene-tests.md
  ontology_conformance_verification: ../scene-tests.md
---

# R：块覆盖服务

## 目标与组合

输入现有16字节块、严格十进制偏移文本和十六进制载荷；先A规范化再B执行；成功仅覆盖指定字节，任何拒绝/注入失败原块不变。

A1解析偏移、A2解码数据由A组合；B1校验与B2原子应用由B组合；R测试真实A/B版本。

必须AC：输入/输出及错误语义符合上述合同；授权范围内无额外副作用。此示例只说明任务边界，真实冻结前仍需填NODE-01完整接口与suite，不可把本教学片段直接当生产完整基线。

## 执行测试具体样本

正例输入：offset="15",data="FF",state=00×16。预期：state=00×15+FF，OK。

反例输入：offset="15",data="FFFF",state=00×16。预期：E_BOUNDS，state仍00×16且B2未被调用。

判定：固定初始对象，调用当前节点，精确比较返回/输出/前后状态；组合节点追踪真实孩子调用及版本；异常、环境错误或缺日志不能当PASS。测试后先固定证据再清理沙箱。

## 三场景

建模以当前父seed/用户目标检验合同覆盖；执行检验上述行为；独立审查以正确/故意违例实现样本测试审查能力，再核对真实实现。详细场景用例与21任务顺序见场景文件。
