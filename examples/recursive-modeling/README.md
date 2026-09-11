# 复用定义、递归实例、入库履行

[八节点示意](hierarchy.md)展示F孩子继续拆孙节点，以及N/S/U同时只读复用相同业务定义。不是固定参考答案，不要求真实工作长成八节点。

## 正确的建模输出位置

- ontology/concept/audit/*：本版可复用实体定义，描述职责/接口/约束/测试，不带用户任务运行身份。
- ontology/pattern/audit/project-review-composition.md：参数化组成角色，孩子默认继续评估。
- tests/audit-contracts/*：固定正反期望；真实run不存这里。
- records/works/.../nodes：某次工作实例与局部参数/差异。
- records/<task-id>/artifacts/candidates：尚未获准的共享新定义或修订。
- records/<task-id>/tests/runs：本次actual与失败；不搬进实体定义。

仅文件编辑并交付仓库，不创建EVOLVE真实发布回执。部署时按授权固定baseline_snapshot，或在实际宿主完成独立审查与精确发布流程。已有定义够用时，reuse而不是强制造新文件。

## 何时正常结束，何时仍未完成

父建模完成自己的定义、子seed、测试语义和真实本地验证，可以完整归档；后代再独立建模。所有后代完成后冻结tree-spec/manifest。若声明shared_required，本地候选可以交付，但工作知识目标在真实发布前仍未完成。发布不是自动续写旧任务，也不复用旧确认。

[返工演练](../../tests/modeling-regression/rework-walkthrough.md)与[K案例](../../tests/modeling-regression/README.md)用于识别之前records的错误路径。
