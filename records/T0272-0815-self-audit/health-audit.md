# PDCA 体系健康度自我审查报告

- 异常总数: 75

## 汇总

| 维度 | 计数 |
|------|------|
| gate_incomplete | 5 |
| id_collision | 57 |
| legacy_no_gate | 12 |
| seam | 1 |

| 严重度 | 计数 |
|--------|------|
| blocking | 62 |
| integrity | 1 |
| noise | 12 |

| 根因 | 计数 |
|------|------|
| legacy | 12 |
| real-defect | 63 |

## 门禁覆盖率

- receipts 80.3% (236/294)，verdict 83.0%，rejected receipts 333 条

## 问题明细（按严重度）

### 阻断门禁 (62)

| task_id | slug | 类别 | 根因 | 明细 |
|---------|------|------|------|------|
| T0428 | 0830-review-cleanup | gate_incomplete | real-defect | gate_incomplete:no-act-to-archive |
| T0444 | 0830-pdca-ai-eff-review-mapping | gate_incomplete | real-defect | gate_incomplete:no-final-confirmation |
| T0445 | 0830-pdca-ai-eff-review-gap | gate_incomplete | real-defect | gate_incomplete:no-final-confirmation |
| T0446 | 0830-pdca-ai-eff-review-plan | gate_incomplete | real-defect | gate_incomplete:no-final-confirmation |
| T0457 | 0831-ontology-fragment-scope / 0831-tls-keygen-followup-fix | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0468 | 0901-ontology-signal-completion | gate_incomplete | real-defect | gate_incomplete:no-act-to-archive |
| T0487 | 0901-ontology-closure-audit / 0905-bcachefs-versions | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0488 | 0901-research-project-issues / 0905-bcachefs-strengths | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0489 | 0902-wizard-domain-map / 0905-bcachefs-ontology | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0490 | 0902-p2-tdd-diagnose-wayfinder / 0906-bcachefs-deep-dive | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0491 | 0902-p2-teach-skill / 0906-bcachefs-kernel-sweep | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0492 | 0902-scenario-ontology-coverage / 0906-bcachefs-kernel-round4 | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0493 | 0902-exempt-hard-gate / 0906-bcachefs-kernel-round5 | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0494 | 0903-single-ontology-closure / 0906-bcachefs-kernel-round6 | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0495 | 0903-hybrid-ontology-methodology / 0906-bcachefs-kernel-round7 | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0496 | 0903-production-ontology-detail / 0906-bcachefs-kernel-round8 | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0497 | 0903-ontology-governance-principle / 0906-bcachefs-kernel-round9 | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0498 | 0903-ontology-evaluation-reuse / 0906-bcachefs-kernel-round10 | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0499 | 0903-ontology-metrics / 0906-bcachefs-kernel-round11 | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0500 | 0901-research-zfs-crypto / 0906-bcachefs-kernel-round12 | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0501 | 0901-research-methodology-diagrams / 0906-bcachefs-kernel-round13 | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0502 | 0903-scientific-research-methodology / 0906-userspace-mount | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0503 | 0903-research-zfs-implementation / 0906-userspace-recovery | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0504 | 0903-zfs-crypto-diagram-fill / 0906-userspace-devkey | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0505 | 0903-zfs-system-dev / 0906-pattern-concurrency | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0506 | 0903-zfs-dmu / 0906-pattern-consistency | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0507 | 0903-zfs-dsl / 0906-pattern-allocheal | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0508 | 0903-zfs-spa / 0906-principle-distill | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0509 | 0903-zfs-zio / 0906-signal-govern-1 | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0510 | 0903-zfs-zpl / 0906-signal-govern-2 | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0511 | 0903-zfs-arc / 0906-signal-govern-3 | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0512 | 0903-zfs-system-integrate / 0906-study-sixlock | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0513 | 0903-research-zfs-dmu / 0906-ontology-mandatory | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0514 | 0903-research-zfs-dsl / 0906-triple-check | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0515 | 0903-research-zfs-spa / 0906-study-journal | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0516 | 0903-research-zfs-zio / 0906-study-ec | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0517 | 0903-research-zfs-zpl / 0906-study-alloc | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0518 | 0903-research-zfs-arc / 0906-study-btreetrans | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0519 | 0903-bug-scenario-mismatch / 0906-study-snapshot | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0520 | 0903-review-research-dev-mismatch / 0906-study-userspace | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0521 | 0903-scenario-gate-hard / 0906-study-crypto | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0522 | 0903-research-zfs-checksum / 0906-study-observability | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0523 | 0903-research-zfs-compress / 0906-study-finale | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0524 | 0903-research-zfs-encrypt-transform / 0906-study-btreesearch | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0525 | 0906-study-writepath / 0902-review-zfs-production-ontology | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0526 | 0906-study-recovery / 0902-zfs-system-deepening | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0527 | 0906-study-btreegc / 0902-zfs-zil-entity | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0528 | 0906-study-reconcile / 0902-zfs-legacy-upgrade | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0529 | 0906-study-superblock / 0902-zfs-system-8leaf | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0530 | 0906-study-datamove / 0902-ci-production-gate | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0531 | 0906-study-quota / 0902-zfs-ddt-entity | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0532 | 0906-study-journalread / 0902-zfs-scrub-pattern | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0533 | 0902-research-bcachefs-tools / 0906-study-snapdelete | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0534 | 0902-ontology-fidelity-remediation / 0906-study-ecread | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0535 | 0902-gate-keyword-rationality / 0906-detail-batch1 | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0536 | 0902-fidelity-gate-calibration / 0906-detail-batch2 | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0537 | 0902-fidelity-p0-true-generic / 0906-detail-batch3 | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0538 | 0902-fidelity-p1-diagrams / 0906-lock-usage | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0539 | 0903-research-zfs-pcie-sm4 / 0906-study-btreegc2 | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0540 | 0903-fix-inc-mount-verify-eexist / 0906-three-conflicts | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0541 | 0903-analyze-inc-mount-verify-fail / 0906-pin-leak | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0542 | 0906-ec-lectures / 0906-journalread-add / 0904-bugfix-confirmation-gate | id_collision | real-defect | 同一 task_id 出现在 3 个目录 |

### 数据完整性 (1)

| task_id | slug | 类别 | 根因 | 明细 |
|---------|------|------|------|------|
| T0545 | 0906-conformance-audit | seam | real-defect | 测试文件缺失: scripts/audit-ontology-conformance.py |

### 仅统计噪音 (12)

| task_id | slug | 类别 | 根因 | 明细 |
|---------|------|------|------|------|
| T0431 | 0830-add-matt-pocock-concepts | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T0434 | 0830-pdca-ai-efficiency-review-2 | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T0435 | 0831-pdca-ai-efficiency-p0-fix | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T0436 | 0832-pdca-ai-efficiency-p1-integration | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T0437 | 0833-pdca-ai-efficiency-p2-fill | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T0440 | 0834-pdca-ai-efficiency-effectiveness | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T0441 | 0835-pdca-ai-efficiency-fixture-fix | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T0442 | 0836-pdca-ai-efficiency-archive-fix | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T0447 | 0831-old-arch-refs-audit | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T0539 | 0903-research-zfs-pcie-sm4 | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T2068 | 0907-ontology-prevention-gate | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T2070 | 0907-ontology-knowledge-fidelity | legacy_no_gate | legacy | 机制前任务无 transition receipts |

## 修复候选清单（不执行，另立任务）

- **[high] ID 撞车清理**: 57 组 task_id 重复（跨目录），identity 歧义影响可追溯性 → 建议范围: 为每组冲突决定保留/重命名，更新依赖引用与记录
- **[high] 真违规门禁修复**: 5 项 gate_incomplete 非豁免（缺失 verdict/final_confirmation 等） → 建议范围: 按 T0271 remediate 模式补全或如实豁免
- **[medium] seam 契约补齐**: 1 项声明的测试接缝与实际测试不一致 → 建议范围: 补齐缺失测试文件或修正 seam 声明（外部项目需确认测试位置）