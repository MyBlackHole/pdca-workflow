# T0420 PRD：清理 knowledge/ 下对已删 ADR 的引用

## 背景
T0419 全量删除 `docs/adr/`（含 ADR-0030/0022/0016/0007 等），但 `knowledge/` 下 19 个文件仍含指向已删 ADR 的引用。为保持"决策记录本体化、无悬空 ADR 引用"的一致性，清理这些残留。

## 目标
消除 `knowledge/` 下所有 `ADR-[0-9]` 字面引用，改写为本体节点指向或任务号/records 溯源，不删文件、不改本体。

## 验收标准
- [ ] AC-1：16 个 A 类重定向桩中的"已按 ADR-0030 物理归并"改写为指向 `ontology:concept/ontology-creation-gate` 决策背景，删除 ADR-0030 字面引用。
- [ ] AC-2：`knowledge/linux-epoll-eventloop/rpc-conn-idle-reclaim.md` 移除对 ADR-0016 的字面引用（保留 records/ 溯源说明）。
- [ ] AC-3：`knowledge/lmdb/vl32-no-mmap-build-gate.md` 移除 "and ADR-0022"（保留 T0249 任务号溯源）。
- [ ] AC-4：`knowledge/ai-efficiency/skills-candidate-review.md` 移除对 ADR-0007 的字面引用。
- [ ] AC-5：`grep -rn "ADR-[0-9]" knowledge/` 无结果；`ontology-validate.py` 通过、islands=0。
- [ ] AC-6：登记 reference-cleanup 证据 + 收敛映射，`validate-convergence.py` 通过（valid:true）。

## 关联本体节点
- ontology:concept/ontology-creation-gate（ADR-0030 决策背景）
- ontology:concept/pdca-task（任务溯源约定）
