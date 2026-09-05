---
schema: pdca.asset/v1
id: T0489-0905-bcachefs-ontology
phase: check
source_ids: [node-core-six-intent-seq-deadlock-free-locking, node-core-journal-seq-blacklist-pin-reclaim, node-core-allocator-wfq-watermark-reservation, node-core-fsck-autofix-graded-self-healing, node-core-format-compat-stable-evolution, validate-output, convergence-map]
---

## 上下文
用户要求创建本体：把 T0488 内核巧思沉淀为本体知识。Plan 查重发现已有 core 父节点 + 30+ core-* 子节点，推荐精选 5 个不重复 domain 节点并获确认。Do 阶段比对现有节点正文定边界，编写 5 节点，全量 validate 通过。

## 假设与结果
- 假设 1：5 主题与现有 core-* 不重复。结果：成立，动笔前 Read 比对 persistent-concurrency 与 fsck-repair-mode，边界为机制 vs 方法论/动作语义。
- 假设 2：testable_signal 可达非泛化标准。结果：成立，10 条信号全含运行/通读动词，无泛化短语。
- 假设 3：引用全部非空悬。结果：成立，validate 全量通过。

## 分析
- **AC-1** ✅ 5 个节点文件存在于 ontology/domain/core-*.md 且 frontmatter 合法（5 node 证据）
- **AC-2** ✅ ontology-validate.py 全量 0 issues（validate-output）
- **AC-3** ✅ 每节点 attributes 非空，10 条 testable_signal 全含动词+对象+判定，无泛化短语（5 node 证据）
- **AC-4** ✅ 全部 relations 引用现存节点，specializes 无环（validate 覆盖 + 5 node 证据）

关键结论：5 节点为 core-six-intent-seq-deadlock-free-locking、core-journal-seq-blacklist-pin-reclaim、core-allocator-wfq-watermark-reservation、core-fsck-autofix-graded-self-healing、core-format-compat-stable-evolution，全部 specializes ontology:domain/core。
复核途径：`python3 scripts/ontology-validate.py --ontology-dir ontology` 应输出 OK；逐节点 Read 核对正文与 T0488 报告对应关系。

## 适用边界
- 仅新增 5 节点，未动现有节点；EC/可观测主题因与现有节点重叠本次未建。
- 引用代码行号以当前 bcachefs main 快照为准，演进后可能漂移（函数名稳定）。

## 下一轮建议
- SKILLS-INDEX 由 generate-skills-index.py 从 frontmatter 生成，仅覆盖 skill 类型，本体 domain 节点无需更新索引。
- 如需补 EC/可观测主题，应先与现有 journal/EC 相关节点做更细的差分再立项。

verdict: {"outcome": "confirmed", "reason": "4 AC 全绿，validate 0 issues，证据链完整", "verdict_id": "vt0489-confirmed", "at": "2026-09-06T00:00:00+08:00"}
