# 跟进：审计 docs/adr/ 并全量迁移/删除（PDCA 元工作流 ADR → 本体；子系统 ADR → 删除；引用改写）

## 问题陈述

T0418 收尾时发现：`docs/adr/` 中 ADR-0032~0036 的决策已可被本体节点忠实表示，遂迁移进本体并删除。用户进一步指出 `docs/adr/` 整体多余。审计结论：目录内 31 个 ADR 分两类——

- **A 组（8 个，PDCA 元工作流相关）**：0001（决策记录机制）、0002（严格任务合约）、0003（convergence 证据门禁）、0004（flow issue 不可变事件）、0017（to-tickets DAG/ready-set）、0024（task/record identity 原子事务）、0030（知识归并 ontology）、0031（本体存储选型）。其决策多数已对应本体节点，少数需新建节点承载。
- **B 组（23 个，外部子系统相关）**：rpc/report/lmdb/small-file/backup/handshake 等项目的架构决策，本仓库仅作归档位，**无对应本体节点**，但被 README/AGENTS/CONTEXT/多个 skills/templates/任务 PRD 引用为 ADR 权威写入位置。

若只删文件不改引用，会留下死链接与失效的 ADR 写入流程。故本任务：A 组迁移进本体并删除原文件、B 组删除、并改写全仓引用使删除自洽。

## 目标

- 将 A 组 8 个 ADR 的决策沉淀进本体（已存在节点追加「决策背景」段，或新建对应概念节点），随后删除原 ADR 文件。
- 删除 B 组 23 个子系统 ADR 文件与 `docs/adr/` 目录。
- 改写全仓对 `docs/adr/` 的引用与"写 ADR"机制说明，改为"决策记录本体化"，消除自相矛盾。

## 用户故事

- 作为 PDCA 维护者，我希望架构决策统一由本体承载而非散落 ADR 文件，以便事实单一、可机读、可演进。
- 作为技能作者，我希望技能/模板/README 不再指向已删除的 `docs/adr/`，以免误导用户向不存在的目录写决策。

## 方案

1. **A 组迁移映射**（决策载入本体节点「决策背景」段；缺节点的新建概念节点，specializes 既有节点并通过 ontology-validate）：
   - 0001 → `ontology-asset`（跨任务决策现由本体承载，原 ADR 机制退役）
   - 0002 → `pdca-task`（严格合约 + 能力适配边界）
   - 0003 → `pdca-evidence`（convergence map 作为 Do→Check 硬门禁）
   - 0004 → `pdca-continuous-improvement`（flow issue 独立不可变事件文件）
   - 0017 → `pdca-task`（to-tickets 显式依赖边/DAG 与 ready-set 术语；或新建 `task-decomposition` 概念节点）
   - 0024 → `task-record-identity`（已建，追加背景）
   - 0030 → `ontology-creation-gate`（知识资产物理归并至 ontology/）
   - 0031 → `pdca-ontology-ready`（本体存储选型 md 优先 + 图升级路径）
2. **B 组删除**：直接 `git rm` 23 个子系统 ADR，删除空目录 `docs/adr/`。
3. **引用改写**（grep `docs/adr` 命中点）：README.md、AGENTS.md、pdca/CONTEXT.md（术语表 ADR 定义 + ADR-0017 引用）、flows/flow-plan/SKILL.md、skills/grilling、skills/domain-modeling-work、skills/improve-codebase-architecture、skills/tdd 的 SKILL.md、templates/to-spec/SPEC.md、相关任务 PRD（0808/0820/0821/0823/0829 等）。统一改为"架构决策记录于本体（ontology/），不可逆非显然决策写入对应本体节点"，并移除"扫描 docs/adr/ 找最大编号建 ADR"等机制说明。

## 实现/测试决策

- 复用 T0418 的"迁移后删除"与"本体承载背景"模式，不新建校验机制。
- 新本体节点须满足既有 ontology-validate 约束（type==父目录、specializes 既有、relations 受控键、无环、无悬空）。
- 引用改写以 grep 零残留为完成判据（records/ 不可变记录中的历史引用例外保留）。

## 范围外

- 不把 B 组决策迁移到其它项目仓库（仅删除本仓库副本）。
- 不改动 ontology-validate / 校验机制本身。
- 不影响 `records/` 下既有的不可变历史记录（其引用按例外保留）。

## 验收标准

- [ ] AC-1: A 组 8 个 ADR（0001-0004/0017/0024/0030/0031）的决策均在本体中有承载（已存在节点追加「决策背景」段，或新建对应概念节点），原 ADR 文件已删除。
- [ ] AC-2: B 组全部 23 个子系统 ADR 文件已删除。
- [ ] AC-3: `docs/adr/` 目录已删除。
- [ ] AC-4: 全仓对 `docs/adr/` 的引用（README.md、AGENTS.md、pdca/CONTEXT.md、flows/flow-plan/SKILL.md、skills/grilling、skills/domain-modeling-work、skills/improve-codebase-architecture、skills/tdd 的 SKILL.md、templates/to-spec/SPEC.md、相关任务 PRD）已改写为"决策记录本体化"并移除"写 ADR"机制说明；grep 确认 `scripts/SKILL/flows/docs/templates` 中无 `docs/adr` 残留（仅 `records/` 不可变记录例外）。
- [ ] AC-5: `ontology-validate.py` 通过（退出码 0、无悬空引用、无环、islands=0），全部新节点合规。
- [ ] AC-6: 登记证据（ADR 迁移清单、引用改写审计报告、本体校验输出）并写入收敛映射，`validate-convergence.py` 通过。

## 关联本体节点

```
ontology:concept/ontology-asset
ontology:concept/pdca-task
ontology:concept/pdca-evidence
ontology:concept/pdca-continuous-improvement
ontology:concept/task-record-identity
ontology:concept/ontology-creation-gate
ontology:concept/pdca-ontology-ready
```

## 备注

- 本任务由 T0418 收尾发现触发，是用户确认的"开新任务审计 docs/adr/"（选项 A）的落地；用户进一步确认"审计+执行迁移""B 组删除""一并改写引用"。
- `pdca/CONTEXT.md` 术语表目前定义"ADR | 架构决策记录，存于 docs/adr/"并引用 ADR-0017，须随 AC-4 一并更新。
