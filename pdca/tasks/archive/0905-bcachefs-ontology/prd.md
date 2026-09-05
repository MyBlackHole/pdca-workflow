# bcachefs 内核巧思本体沉淀

## 背景
T0488 产出 89 条内核巧思（records-only 未沉淀本体）。现将其精选为 5 个 `ontology:domain/core` 下的 domain 节点，与现有 30+ core-* 节点互补不重复。

## 目标
新建 5 个 domain 节点：并发（SIX/seq/环检测）、崩溃一致性（seq 黑名单/pin 分级/clean 段）、空间管理（WFQ/水位/预留）、自愈分级（AUTOFIX/调度/限流）、兼容审慎（FEATURE 位/stable 映射/X 宏）。

## 功能需求
1. 每节点 frontmatter 满足 pdca.asset/v1，type=domain，specializes ontology:domain/core
2. attributes 含 applicability/constraints/testable_signal，信号非泛化（含动词+对象+判定）
3. relates_to 指向相关现有 core-* 节点与 T0488 evidence，避免重复覆盖
4. 全量 `ontology-validate.py` 0 issues

## 非功能需求
- 不修改现有本体节点，只新增
- 引用全部使用本体 id

## 验收标准
- [ ] AC-1 5 个节点文件存在于 ontology/domain/core-*.md 且 frontmatter 合法
- [ ] AC-2 `python3 scripts/ontology-validate.py --ontology-dir ontology` 0 issues
- [ ] AC-3 每节点 attributes 非空且 testable_signal 含动词+对象+判定，无泛化短语
- [ ] AC-4 全部 relations 引用在 ontology/ 中存在，specializes 无环

### 声明的测试接缝
- seam: scripts/ontology-validate.py -> ontology/domain/core-*.md（新增 5 节点）

## 风险与对策
- 风险：与现有 core-* 节点主题重叠。对策：动笔前 Read 比对现有节点正文，relates_to 显式关联而非重复
- 风险：testable_signal 泛化被结算门禁拦截。对策：按动词+对象+判定结构编写，跑 check-research-ontology-settlement.py 自检
