---
schema: pdca.tree-readiness/v1
protocol_revision: 3.4.11
check_id: null
work_id: null
tree_revision: null
proposal_id: null
manifest_ref: null
manifest_digest: null
required_checks: []
checks: []
blocking_issue_refs: []
result: null
checker_ref: null
checked_at: null
time_source_ref: null
requirements_basis_ref: null
requirements_basis_digest: null
---

# 整树技术就绪核验

TREE-01：required_checks完整展开闭包/身份/三场景案例/subject成员/全场景图及check/终态/阻断issue/预算。每项checks有输入、原始观测、expected/actual和pass/fail/unknown；每个绑定ID实际解析、摘要重算，不接受all_match自述。

只在必需项全pass且无当前冻结阻断issue时ready；其他not_ready。check固定在manifest外，tree-confirmation-request绑定本check和manifest摘要。不是用户批准或发布事务；未知宿主身份/确认/资源证据不能由静态文件检查提升为pass。


requirements_basis固定适用权威、原请求/seed与当前要求来源；由核验入口独立选定，不能由候选自证。模板空值是草稿，不代表未知项通过。

## 任务完整性与测试覆盖不能由草稿代替

完整节点/场景集合来自requirements_basis，不由已有目录数推导。采用agent-dispatch.1时检查每个被采用交付的实际派发、独立身份/上下文、四阶段责任、原生确认来源、run与终态；来源缺失标unknown而非pass。草稿目录、阶段标题、`delivery_usable_as_draft`和“会话已确认”均不能替代。

当前建模 ME 的本地绑定和实际运行、Do产出的三个场景完整case语义、未来场景是否已运行，分别列结果；未来not_run合法不代表必需case可not_defined。身份使用真实root/node ID，不猜root别名。已知必需缺口形成带影响范围的issue并阻断相关采用；不把“需补证据”与“无issue”同时填写。

仅本地父seed交付时使用NODE本地合同，不预先要求全树readiness；本表在整树冻结边界核验。图/文字/约束同一事实的矛盾也须有实际检查与反例，不能仅凭文件齐全判通过。
