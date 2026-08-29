# T0414 Do 阶段自审

## 实现摘要
- AC-1 证据锚定：register-evidence 从 pdca-evidence 子类型派生允许 kind 表，命中写 evidence_type_ref，未知 kind 报错。
- AC-2 结论锚定：新增 verdict-rejected/partial 节点（specializes pdca-verdict）；verdict_anchor_issues 在 check/act/archive 校验 outcome 映射。
- AC-3 archive 自检：archive_ontology_ready_issues 跑 ontology-validate + 孤岛检查；transition-phase 到 archive 时阻断。
- AC-4 硬门禁：ci-ontology-gate.py 共享逻辑；install-git-hook.sh 可选装 pre-commit；.github/workflows/ontology-gate.yml 远端复跑。
- AC-5 文档：ADR-0036、ontology/README.md §10、docs/ONTOLOGY_GUIDE.md §13、flow-act SKILL Ac8 更新。
- AC-6 回归：本体相关既有测试全通过，ontology-validate OK、无孤岛、ci-gate OK。

## 风险
- test_ontology_validate.py 3 例失败为 T0413 节点化遗留债（临时本体缺 rule 节点），不在本任务 AC-6 清单，待另立任务修复。
- git hook 默认不安装（可选），避免惊扰提交行为。
