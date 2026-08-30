# T0421 PRD：清理活动机制文件中的已删 ADR 悬空引用

## 背景
T0419/T0420 已删除 `docs/adr/` 并清理 knowledge/ 引用，但最终全仓扫描发现 3 个活动机制文件仍含不带路径前缀的已删 ADR 引用（CONTEXT.md 的 ADR-0018/0029、ontology-validate.py 的 ADR-0030 注释、skill-content-baseline.json 的 ADR-0007）。消除这些悬空引用，保持全仓无 ADR 悬空引用的一致性。

## 目标
改写/移除上述 3 个文件的已删 ADR 引用，不改本体、不删文件、不改变脚本行为。

## 验收标准
- [ ] AC-1：`pdca/CONTEXT.md` 的 ADR-0018 / ADR-0029 引用改写为历史注记（"已随 docs/adr/ 退役删除"），去除文件链接。
- [ ] AC-2：`scripts/ontology-validate.py` 的 ADR-0030 注释改为指向 `ontology:concept/ontology-creation-gate` 决策背景。
- [ ] AC-3：`pdca/skill-content-baseline.json` 的 "Initial ADR-0007 baseline" 去 ADR 引用（改为 "Initial baseline"）。
- [ ] AC-4：全仓活动文件（排除 records/journal/tasks/health-audit.md）grep 无 `docs/adr` 前缀及已删 ADR 悬空引用；仅保留本体节点「原 ADR-XXXX」历史归属注记。
- [ ] AC-5：`ontology-validate.py` 通过、islands=0；登记证据 + 收敛映射，`validate-convergence.py` valid:true。

## 关联本体节点
- ontology:concept/ontology-creation-gate（ADR-0030 决策背景）
