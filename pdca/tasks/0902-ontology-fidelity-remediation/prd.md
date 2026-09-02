# PRD — 本体保真度治理：消除“为写而写”，实现可复现的完备本体

> 任务：T0534 / 0902-ontology-fidelity-remediation / scenario: development / phase: plan

## 背景与问题

生产本体（`ontology/` 276节点，manifest 276条）名义上是“语义引擎”（README SSOT v3），承担知识权威、验证契约、关系树驱动任务分解三职责。

实测存量（2026-09-02抽样）：

- **domain 210个**：182个（86.7%）`testable_signal`为泛化短语 `检查本文件…且经 validate`，不可派生真实测试；仅4个含 `grep -q` 可执行动词；均行66行，大量叶节点20-65行空洞，仅承载一句话+迁移索引。
- **entity 55个**：23个含具体signal，平均79行；但 `backup-system` 等0 attributes，`evidence-*` 等无门禁；质量两极分化（`zfs-arc` 170行4图可实现 vs 凑数节点）。
- **门禁**：`ontology-validate.py` 仅校验 type/非空悬/无环/非空signal，未拒绝泛化signal与空正文；`production-ontology-gate.py` 仅对 ZFS/bcachefs等少数system节点生效，未覆盖全量domain。

结果：本体“为写而写”，无法通过本体信息独立复现原始领域的各种属性/特性，违背SSOT“属性即测试点”与“可实现完备性”初衷。

## 目标

将本体从“分类法+文档”升级为**可复现的技术规格**：任一核心领域的本体，第三方仅凭本体即可写出符合原始特性的实现，且偏离可被 `testable_signal` 自动证伪。

## 非目标

- 不重写全部276节点一次性到位；本任务先**立标准+示范+加固门禁**，存量分批修复按路线图推进。
- 不改变 PDCA 元本体（concept/process）结构；仅治理 `domain`/`entity`/`pattern` 等业务本体与校验脚本。

## 术语

- **保真度（fidelity）**：本体“说出的”与真实系统“做到的”一致程度。
- **完备性（completeness）**：对给定实体的本体，能否通过其 `attributes+约束+关系+时序/状态机/正反例` 独立写出实现并通过 `testable_signal` 自检。
- **泛化signal**：形如 `检查本文件完整性且经 validate` 的不可执行、不可证伪短语。
- **可实现节点**：具备 ≥3 `attributes`（每条含 `grep -q`/`gate.py`/`scaffold.py` 动词且双源可回归）+ C4/时序/状态机/决策树/正反例/门禁八段，且 `ontology_test_scaffold.py` 可产。

## 方案方向（已Grill确认 2026-09-02）

经两轮Grill（Q1-Q11全按推荐确认），决策树已收敛：

1. **范围**：全量一视同仁 — 全部类型（domain/entity/pattern/principle/pitfall/fact/concept/process）纳入完整性硬标准，不设类型豁免。
2. **完整性定义**：自我审查七项清单逐本体判定 — ①概念定义 ②属性完备（含约束与可测信号）③关系闭环（specializes/guides/composed_of）④行为可视化（C4/时序/状态机/决策树）⑤正反例 ⑥门禁溯源（Source行号）⑦可scaffold；缺一项即不完整需补充，不允许泛化signal。
3. **门禁策略**：增量零容忍 + 存量限期清零 — 新提交本体含泛化signal直接被 `ontology-validate` 拒（`[ATTR_GENERIC]`），存量审计列豁免清单分P0/P1/P2限期清零（P0两周），CI每日播报剩余。
4. **示范验收**：AI可复现为金标准 — 新AI仅读本体即能产出通过 `testable_signal` 的实现；必要条件 `ontology_test_scaffold.py` 可产且pytest可收集，充分条件人工盲测抽检。
5. **定点**：先审计后定点 — 按“高频复用×空洞严重”排序推荐首个示范域（预判 core 或 ai-efficiency 空洞叶）。

实施五件套：定义（fidelity-criterion）→ 审计（audit-report + fidelity score）→ 示范（1域重做至可实现）→ 门禁（validate/gate加固+本体rule_spec锚定）→ 分批修复（P0≥5节点首批可验证）。

## 验收标准

### 验收标准
- [ ] AC-1 完整性定义可执行：新增 `ontology:concept/ontology-fidelity-criterion.md` 明确“完整”八段与四类空洞拒绝规则，且 `production-ontology-gate.py --check fidelity` 可执行并对示范域PASS、泛化节点FAIL
- [ ] AC-2 存量审计可复现：产出 `records/T0534-0902-ontology-fidelity-remediation/audit-report.md`，含全量276节点四类空洞统计表（泛化/空正文/无Source/不可scaffold）与致命/严重/一般分级及Top20修复清单，且脚本可回归（`python3 scripts/audit-ontology-fidelity.py`）
- [ ] AC-3 示范域可实现：选定1个示范域（待Grill定）按完整标准重做后，`attributes≥3`且每条`testable_signal`含可执行动词、`mermaid≥2`且每图1 Source行号、正反例与门禁齐全、`ontology_test_scaffold.py --node <示范> --out /tmp/x.py` 可产且pytest可收集
- [ ] AC-4 门禁硬阻断：提交含泛化signal或正文<阈值的本体被 `ontology-validate.py` 与 `ci-ontology-gate.py` 拒绝（非0退出含 `[ATTR_GENERIC]`/`[BODY_TOO_SHORT]` 等码），CI workflow复现
- [ ] AC-5 分批修复路径可验证：产出 `remediation-roadmap.md` 含批次/优先级/工时估算，且首批≥5节点按新标准修复后 `ontology-validate` 0 issues 且 `production-ontology-gate --all` 不因存量空洞而FAIL（或明确豁免清单）
- [ ] AC-6 收敛可验证：Do产出已登记（`evidence/manifest.jsonl` ≥3条 `fidelity-*`）且 `convergence map` 逐条回链AC-1..5，`validate-convergence valid:true`

## 约束

- 全量零容忍但分“增量硬拒绝+存量限期豁免”落地：`ontology-validate --check fidelity` 独立开关，存量豁免清单由审计报告产出，P0两周清零，避免立门禁即全红阻塞归档。
- 所有新增门禁须有 `rule_spec` 本体锚定（`ontology:concept/ontology-rule-fidelity-generic` 等），符合README §9“本体为门禁权威”。
- 示范域选择须与现有 `zfs-arc`/`zfs-zio`/`bcachefs-btree` 等高质量实体互补，优先选当前空洞（fidelity score低）且高频复用的域。
- 七项清单逐项可机检：审计脚本 `audit-ontology-fidelity.py` 对每本体打分并给出致命/严重/一般分级。

## 风险

- 全量门禁过严导致历史任务无法归档 → 通过独立check与豁免清单缓解。
- “完整”定义过细导致编写成本过高 → 通过Grill校准阈值（mermaid/Source/行数）与分级（致命vs一般）缓解。

## 开放问题

Grill两轮（Q1-Q11）已闭环，无开放问题；待用户 `final_confirmation` 后进Do。
