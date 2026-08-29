---
schema: pdca.asset/v1
id: T0414-0829-ontology-full-lifecycle-gate
phase: check
source_ids: [ev-test-1, ev-test-2, ev-test-3, ev-test-4, ev-test-5, ev-review-1, ev-adr-1, ev-reg-1, ev-gate-1, ev-gate-2, ev-trans-1, ev-ci-1, ev-hook-1, ev-verdict-rej-1, ev-verdict-par-1, ev-act-skill-1, ev-act-skill-2, ev-ont-readme-1, ev-guide-1, convergence-map]
---

## 上下文
PDCA 元本体经 T0412（门禁节点）、T0413（validator 运行时读 rule_spec）后已"创建时"本体制化，但审查发现尚未全流程闭环：证据/结论未锚定本体、archive 无本体自检、无 CI/git hook 硬门禁。本任务（T0414）补齐上述三类缺口。

## 假设与结果
- 假设：把证据 `--kind` 锚定到 `pdca-evidence` 子类型、把 `verdict.outcome` 锚定到 `pdca-verdict` 三态、在 archive 转换时跑本体自检、并以 `ci-ontology-gate` 落地 CI/hook 硬门禁，可形成提交级全阶段闭环，且不破坏既有提交行为。
- 结果：六项 AC 全部达成，本体相关既有测试通过，ontology-validate OK、无孤岛，ci-gate OK。

## 分析
- **AC-1** ✅ register-evidence 从 pdca-evidence 子类型派生允许 kind 表，命中写 evidence_type_ref 且引用可解析，未知 kind 报错（ev-test-1, ev-reg-1）
- **AC-2** ✅ 新增 verdict-rejected/partial 节点（specializes pdca-verdict）；verdict_anchor_issues 在 check/act/archive 校验 outcome 映射（ev-gate-1, ev-test-2, ev-verdict-rej-1, ev-verdict-par-1）
- **AC-3** ✅ transition-phase 到 archive 时跑 archive_ontology_ready_issues（ontology-validate + 孤岛检查），本体不合法则拒（ev-trans-1, ev-gate-2, ev-test-3, ev-act-skill-1）
- **AC-4** ✅ ci-ontology-gate.py 共享逻辑 + install-git-hook.sh（可选装 pre-commit）+ .github/workflows/ontology-gate.yml 远端复跑（ev-ci-1, ev-hook-1, ev-test-4）
- **AC-5** ✅ ADR-0036、ontology/README.md §10、docs/ONTOLOGY_GUIDE.md §13、flow-act SKILL Ac8 更新闭环+硬门禁说明（ev-adr-1, ev-ont-readme-1, ev-guide-1, ev-act-skill-2, ev-review-1）
- **AC-6** ✅ 本体相关既有测试（test_ontology_reason/induction/pdca_ontology_correct/meta_ontology/ontology_validator_from_nodes）全通过；ontology-validate OK、无孤岛、ci-gate OK（ev-test-5）

## 失败原因
无（全部 ✅）。

## 适用边界
- plan/do/check/act 的本体"消费"保持顾问式（不阻断），仅创建门禁、证据/结论锚定、archive 自检、CI/hook 为硬门禁，避免 YAGNI 与吞吐损失。
- git hook 为可选安装，不静默改动用户 `.git/hooks`。
- 已知债：`tests/test_ontology_validate.py` 3 例因 T0413 节点化后临时本体缺 rule 节点而失败，不在本任务 AC-6 清单，待另立任务修复。

## 下一轮建议
- 修复 `test_ontology_validate.py` 使其提供 6 个 rule 节点（或整本体种子），消除 T0413 遗留债。
- 可选在 CI 中增加 ontology_graph island 趋势监控。
