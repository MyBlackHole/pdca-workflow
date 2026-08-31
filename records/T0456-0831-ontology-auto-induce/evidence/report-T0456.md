# T0456 自动反哺机制实现报告

## 实现内容

### F1 EvidenceAdapter
- 新增 `EvidenceAdapter` 类于 `scripts/ontology_induction.py:66-130`
- 实现 `parse(path: Path) -> list[RawDraft]`，扫描 `manifest.jsonl`，按 `evidence_type_ref/kind` 去重生成 draft
- 扩展 `induce(source, ontology_dir, adapter="knowledge"|"evidence")` 支持 `--adapter evidence`
- 新增 CLI 参数 `--adapter`，默认 `knowledge`
- 验证：`python3 scripts/ontology_induction.py --adapter evidence --source records/T0454.../evidence/manifest.jsonl --out print` 成功产出 3 候选，其中 `evidence-convergence-map` 命中 `ontology:entity/evidence-convergence-map` guides

### F2 FlowIssue 自动触发
- 新增 `ontology_gate.auto_induce_flow_issues(root, threshold=3)` 于 `scripts/ontology_gate.py:182-220`
- 读取 `pdca/improvements/flow-issue-backlog.json`，阈值可配置，`occurrence_count >= threshold` 且无 candidate 时提示 `AUTO_FLOW_INDUCE_CANDIDATE`
- 防刷屏：单次最多 3 条
- 验证：阈值 3 命中 5 次的 issue，阈值 6 不命中

### F3 Act 阶段自动检查
- 新增 `ontology_gate.auto_induce_evidence(task, root)` 于 `scripts/ontology_gate.py:130-180`
- Act/Archive 阶段扫描 `records/<record>/evidence/manifest.jsonl`，对 `kind ∈ LEGACY_SUPPORT_KINDS` 且 `evidence_type_ref` 为空的知识型 evidence 提示 `AUTO_INDUCE_CANDIDATE`
- 顾问式不阻断，携带可执行指引
- 集成至 `scripts/transition-phase.py:188-199`，转换至 act/archive 时 stderr 输出提示

### 本体节点
- 新增 `ontology/concept/auto-induce-evidence.md` specializes pdca-continuous-improvement relates_to pdca-evidence/self-optimization-loop/knowledge-provenance
- 新增 `ontology/concept/auto-induce-flow-trigger.md` specializes pdca-continuous-improvement relates_to self-optimization-loop/pdca-evidence
- 验证：`ontology-validate.py` 0 issues，`ontology_graph.py` islands 0，nodes 346→346

## 测试
- 新增 `tests/test_ontology_auto_induce.py` 16 用例全部通过
- 覆盖：Adapter 存在性、解析、去重、induce 产物类型合法、guides 命中、CLI、幂等、auto_induce_evidence Act 触发/非 Act 空、缺 manifest 空、flow 阈值、flow code、节点存在性、validate/graph

## 证据锚定
- 通过 `register-evidence --kind test-result` / `convergence-map` / `document` 等登记

## 对应 AC
- AC-1  EvidenceAdapter 可运行
- AC-2  auto_induce_flow_issues 阈值可配置
- AC-3  auto_induce_evidence Act 调用
- AC-4  ontology-validate 通过
- AC-5  islands 0
- AC-6  测试覆盖
