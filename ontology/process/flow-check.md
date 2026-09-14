---
schema: pdca.asset/v2
id: ontology:process/flow-check
type: process
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
status: active
authority: normative
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-14'
summary: Check：按固定依据核对，不自动修业务对象
---

# Check：按固定依据核对，不自动修业务对象

## 进入前

用户明确启动当前Check run，绑定最新Do产物、模型、映射、原需求及AC/oracle。同Agent保持原绑定。检查对象变化使旧请求失效；不能复用旧PASS证明新文件。

## 本阶段自主执行

逐AC核验对象→执行→actual／expected→反证→结论。对可疑问题追踪实际路径及上游保护；不能仅搜索失败即断言不存在。区分确定违例、缺证据unknown与建议；置信度不是证明。

SCENE的必需模型与映射是验收底线。结构／链接／hash通过仍须检查需求覆盖、语义与行为。正确发现违例可完成审查任务，但subject_conformance仍fail；未运行记not_run。

不改冻结业务产物、模型目标或oracle。确实是检查工具／环境／夹具问题时，可在本次明确授权的测试写域内修复并保存前后证据；预期及业务对象不变。否则先沟通，不用“修测试”掩盖业务修改。

## 完成与等待

保存含反证与局限的结论，列出接受、返修、延期或失败归档的建议。向用户说明Act将做什么、是否发布／更新知识，然后停止。用户选择返修时先形成新Do目标请求，不自动回Do。用户接受不把违例改为PASS。
