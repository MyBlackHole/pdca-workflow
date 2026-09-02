# 本体保真度审计报告 — T0534

> 七项清单：概念定义/属性完备/关系闭环/行为可视化/正反例/门禁溯源/可scaffold；fidelity score 0-100；致命/严重/一般三级。金标准：AI仅读本体可复现实现。

**审计时间**：`audit-ontology-fidelity.py` 全量 `413` 节点（`ontology/` 409 md，`ontology-validate` 扫描一致）

## 汇总

| 分级 | 数量 | 占比 |
|------|------|------|
| fatal 致命 | 227 | 55.0% |
| serious 严重 | 19 | 4.6% |
| minor 一般 | 36 | 8.7% |
| pass 通过 | 131 | 31.7% |
| **合计** | 413 | 100% |

### 按类型

| type | 总数 | fatal | serious | minor | pass | 均分 |
|------|------|-------|---------|-------|------|------|
| concept | 109 | 5 | 0 | 19 | 85 | 12.9 |
| domain | 210 | 188 | 16 | 0 | 6 | 18.9 |
| entity | 55 | 29 | 3 | 0 | 23 | 48.6 |
| fact | 1 | 0 | 0 | 1 | 0 | 23.0 |
| pattern | 24 | 5 | 0 | 10 | 9 | 35.0 |
| pitfall | 5 | 0 | 0 | 3 | 2 | 36.8 |
| principle | 4 | 0 | 0 | 3 | 1 | 30.5 |
| process | 5 | 0 | 0 | 0 | 5 | 13.6 |

### 四类空洞量化

- 泛化signal（含`检查本文件`）：115 节点（27.8%）— 零容忍致命
- 无mermaid：377 节点（91.3%）
- 无Source溯源：375 节点（90.8%）
- 正文<60行：320 节点（77.5%）
- 缺正反例：376 节点（91.0%）

## Top20 待修复（按score升序，致命优先）

| # | score | 分级 | id | 病症 | 路径 |
|---|-------|------|----|------|------|
| 1 | 8 | fatal | ontology:fact | MISSING_CONCEPT | ontology/concept/fact.md |
| 2 | 8 | fatal | ontology:pattern | MISSING_CONCEPT | ontology/concept/pattern.md |
| 3 | 8 | fatal | ontology:pitfall | MISSING_CONCEPT | ontology/concept/pitfall.md |
| 4 | 8 | fatal | ontology:concept/process | MISSING_CONCEPT | ontology/concept/process.md |
| 5 | 8 | fatal | ontology:concept/round | MISSING_CONCEPT | ontology/concept/round.md |
| 6 | 8 | fatal | ontology:domain/bcachefs | MISSING_ATTRIBUTES,MISSING_DIAGRAM,MISSING_EXAMPLES | ontology/domain/bcachefs.md |
| 7 | 8 | fatal | ontology:entity/exec-stdin-pump | MISSING_ATTRIBUTES,MISSING_DIAGRAM,MISSING_EXAMPLES | ontology/entity/exec-stdin-pump.md |
| 8 | 8 | fatal | ontology:entity/mtls-handshake | MISSING_ATTRIBUTES,MISSING_DIAGRAM,MISSING_EXAMPLES | ontology/entity/mtls-handshake.md |
| 9 | 8 | fatal | ontology:entity/ontology-deep-integration-knowledge | MISSING_ATTRIBUTES,MISSING_DIAGRAM,MISSING_EXAMPLES | ontology/entity/ontology-deep-integration-knowledge.md |
| 10 | 8 | fatal | ontology:entity/ontology-deep-integration-split | MISSING_ATTRIBUTES,MISSING_DIAGRAM,MISSING_EXAMPLES | ontology/entity/ontology-deep-integration-split.md |
| 11 | 8 | fatal | ontology:entity/ontology-deep-integration-test | MISSING_ATTRIBUTES,MISSING_DIAGRAM,MISSING_EXAMPLES | ontology/entity/ontology-deep-integration-test.md |
| 12 | 8 | fatal | ontology:entity/ontology-deep-integration-tree | MISSING_ATTRIBUTES,MISSING_DIAGRAM,MISSING_EXAMPLES | ontology/entity/ontology-deep-integration-tree.md |
| 13 | 8 | fatal | ontology:entity/ontology-deep-integration | MISSING_ATTRIBUTES,MISSING_DIAGRAM,MISSING_EXAMPLES | ontology/entity/ontology-deep-integration.md |
| 14 | 8 | fatal | ontology:entity/phase-act | MISSING_ATTRIBUTES,MISSING_DIAGRAM,MISSING_EXAMPLES | ontology/entity/phase-act.md |
| 15 | 8 | fatal | ontology:entity/phase-archive | MISSING_ATTRIBUTES,MISSING_DIAGRAM,MISSING_EXAMPLES | ontology/entity/phase-archive.md |
| 16 | 8 | fatal | ontology:entity/phase-check | MISSING_ATTRIBUTES,MISSING_DIAGRAM,MISSING_EXAMPLES | ontology/entity/phase-check.md |
| 17 | 8 | fatal | ontology:entity/phase-do | MISSING_ATTRIBUTES,MISSING_DIAGRAM,MISSING_EXAMPLES | ontology/entity/phase-do.md |
| 18 | 8 | fatal | ontology:entity/phase-plan | MISSING_ATTRIBUTES,MISSING_DIAGRAM,MISSING_EXAMPLES | ontology/entity/phase-plan.md |
| 19 | 8 | fatal | ontology:entity/tls-configuration | MISSING_ATTRIBUTES,MISSING_DIAGRAM,MISSING_EXAMPLES | ontology/entity/tls-configuration.md |
| 20 | 8 | fatal | ontology:entity/tls-session | MISSING_ATTRIBUTES,MISSING_DIAGRAM,MISSING_EXAMPLES | ontology/entity/tls-session.md |

## 豁免清单（存量限期，P0两周）

本报告 `fatal` 列表即豁免清单基线；门禁 `--check fidelity` 对以下路径增量零容忍，存量按 P0/P1/P2 限期清零：

```
ontology:concept/process  # ontology/concept/process.md score=8 ['MISSING_CONCEPT']
ontology:concept/round  # ontology/concept/round.md score=8 ['MISSING_CONCEPT']
ontology:domain/ai-efficiency  # ontology/domain/ai-efficiency.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/ai-efficiency-ai-friendliness-review-methodology  # ontology/domain/ai-efficiency-ai-friendliness-review-methodology.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/ai-efficiency-mattpocock-skills-enhancement-mechanisms  # ontology/domain/ai-efficiency-mattpocock-skills-enhancement-mechanisms.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/ai-efficiency-skills-candidate-review  # ontology/domain/ai-efficiency-skills-candidate-review.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/ai-efficiency-unified-entrypoint-discipline  # ontology/domain/ai-efficiency-unified-entrypoint-discipline.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/ai-efficiency-uplift-assessment-before-adoption  # ontology/domain/ai-efficiency-uplift-assessment-before-adoption.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/ai-efficiency-writing-for-agents-levers  # ontology/domain/ai-efficiency-writing-for-agents-levers.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/backup  # ontology/domain/backup.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/backup-crypto  # ontology/domain/backup-crypto.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/backup-gs-roach-gm-encrypt-support  # ontology/domain/backup-gs-roach-gm-encrypt-support.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/backup-ob-backup-gm-encrypt-support  # ontology/domain/backup-ob-backup-gm-encrypt-support.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/backup-xtrabackup-incremental-schemes  # ontology/domain/backup-xtrabackup-incremental-schemes.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/bcachefs  # ontology/domain/bcachefs.md score=8 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/benchmark  # ontology/domain/benchmark.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/benchmark-build-profile-baseline-matching  # ontology/domain/benchmark-build-profile-baseline-matching.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/benchmark-paired-comparison-noise  # ontology/domain/benchmark-paired-comparison-noise.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/benchmark-small-pack-streaming-decode  # ontology/domain/benchmark-small-pack-streaming-decode.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/benchmark-small-writer-pool-parallelism  # ontology/domain/benchmark-small-writer-pool-parallelism.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/build-config  # ontology/domain/build-config.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/cli-help  # ontology/domain/cli-help.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/control-plane-nonblocking-ingress  # ontology/domain/control-plane-nonblocking-ingress.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/control-plane-nonblocking-ingress-v81-control-frame-nonblocking  # ontology/domain/control-plane-nonblocking-ingress-v81-control-frame-nonblocking.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/control-plane-nonblocking-ingress-v81-control-plane-perf-fastpath  # ontology/domain/control-plane-nonblocking-ingress-v81-control-plane-perf-fastpath.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/core  # ontology/domain/core.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/core-btree-node-rewrite-key-extent-contract  # ontology/domain/core-btree-node-rewrite-key-extent-contract.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/core-btree-random-op-consistency-proptest-pattern  # ontology/domain/core-btree-random-op-consistency-proptest-pattern.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/core-btree-split-proptest-enomem-restart-pattern  # ontology/domain/core-btree-split-proptest-enomem-restart-pattern.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/core-combined-op-domain-model  # ontology/domain/core-combined-op-domain-model.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/core-concurrent-combined-commit-log  # ontology/domain/core-concurrent-combined-commit-log.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/core-derived-state-validator-recovery-gate  # ontology/domain/core-derived-state-validator-recovery-gate.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/core-deterministic-interleave  # ontology/domain/core-deterministic-interleave.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/core-device-bucket-geometry-pointer-contract  # ontology/domain/core-device-bucket-geometry-pointer-contract.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/core-discard-boundary-guards  # ontology/domain/core-discard-boundary-guards.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/core-discard-worker-fifo-fairness  # ontology/domain/core-discard-worker-fifo-fairness.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/core-file-metadata-management-via-lmdb  # ontology/domain/core-file-metadata-management-via-lmdb.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/core-foreground-merge-mount-semantics  # ontology/domain/core-foreground-merge-mount-semantics.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/core-fsck-repair-fault-injection  # ontology/domain/core-fsck-repair-fault-injection.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/core-fsck-repair-mode  # ontology/domain/core-fsck-repair-mode.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/core-fsck-style-cli-healthcheck  # ontology/domain/core-fsck-style-cli-healthcheck.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/core-journal-key-layout-validation  # ontology/domain/core-journal-key-layout-validation.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/core-journal-reclaim-proptest-pattern  # ontology/domain/core-journal-reclaim-proptest-pattern.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/core-model-guard-decision-injection  # ontology/domain/core-model-guard-decision-injection.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/core-open-bucket-lifecycle-and-device-rw  # ontology/domain/core-open-bucket-lifecycle-and-device-rw.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/core-persistent-concurrency-crash-recovery  # ontology/domain/core-persistent-concurrency-crash-recovery.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/core-physical-pointer-derived-state-recovery-boundary  # ontology/domain/core-physical-pointer-derived-state-recovery-boundary.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/core-pointer-trigger-derived-chain  # ontology/domain/core-pointer-trigger-derived-chain.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/core-project-goal  # ontology/domain/core-project-goal.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/core-public-guard-assertions  # ontology/domain/core-public-guard-assertions.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/core-recovery-derived-state-publication-gate  # ontology/domain/core-recovery-derived-state-publication-gate.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/core-recovery-fault-matrix-public-validation  # ontology/domain/core-recovery-fault-matrix-public-validation.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/core-snapshot-table-lifecycle-filter-semantics  # ontology/domain/core-snapshot-table-lifecycle-filter-semantics.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/core-tech-poc  # ontology/domain/core-tech-poc.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/core-tech-poc-aead-auth-encryption  # ontology/domain/core-tech-poc-aead-auth-encryption.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/core-tech-poc-bloom-filter-dedup  # ontology/domain/core-tech-poc-bloom-filter-dedup.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/core-tech-poc-frame-multiplexing  # ontology/domain/core-tech-poc-frame-multiplexing.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/core-tech-poc-hash-selection  # ontology/domain/core-tech-poc-hash-selection.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/core-tech-poc-reed-solomon-erasure  # ontology/domain/core-tech-poc-reed-solomon-erasure.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/core-tech-poc-zero-copy-transfer  # ontology/domain/core-tech-poc-zero-copy-transfer.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/core-transactional-pointer-runner-publication  # ontology/domain/core-transactional-pointer-runner-publication.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/core-trigger-audit-derived-state-boundary  # ontology/domain/core-trigger-audit-derived-state-boundary.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/core-verify-all-aggregate-pattern  # ontology/domain/core-verify-all-aggregate-pattern.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/core-worker-verify-checkpoint-pattern  # ontology/domain/core-worker-verify-checkpoint-pattern.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/data-formats  # ontology/domain/data-formats.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/data-formats-backup-tools-serialization-practice  # ontology/domain/data-formats-backup-tools-serialization-practice.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/data-formats-mysql-innodb-physical-read-notes  # ontology/domain/data-formats-mysql-innodb-physical-read-notes.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/data-formats-parquet-technical-reference  # ontology/domain/data-formats-parquet-technical-reference.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/data-formats-pg-consistency-verification-method  # ontology/domain/data-formats-pg-consistency-verification-method.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/data-formats-pg-heap-null-bitmap  # ontology/domain/data-formats-pg-heap-null-bitmap.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/data-formats-pg-heap-physical-read-notes  # ontology/domain/data-formats-pg-heap-physical-read-notes.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/data-formats-pg-to-parquet-path-benchmark  # ontology/domain/data-formats-pg-to-parquet-path-benchmark.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/data-formats-t0250-mysql-parquet-physical-evidence-ac1-four-versions  # ontology/domain/data-formats-t0250-mysql-parquet-physical-evidence-ac1-four-versions.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/data-formats-t0250-mysql-parquet-physical-evidence-ac10-pg-100m-frozen-fix  # ontology/domain/data-formats-t0250-mysql-parquet-physical-evidence-ac10-pg-100m-frozen-fix.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/data-formats-t0250-mysql-parquet-physical-evidence-ac5-benchmark  # ontology/domain/data-formats-t0250-mysql-parquet-physical-evidence-ac5-benchmark.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/data-formats-t0250-mysql-parquet-physical-evidence-ac7-100m-benchmark  # ontology/domain/data-formats-t0250-mysql-parquet-physical-evidence-ac7-100m-benchmark.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/data-formats-t0250-mysql-parquet-physical-evidence-evidence  # ontology/domain/data-formats-t0250-mysql-parquet-physical-evidence-evidence.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/data-formats-t0250-mysql-parquet-physical-evidence-research-report  # ontology/domain/data-formats-t0250-mysql-parquet-physical-evidence-research-report.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/data-formats-t0300-mysql-version-convert-test  # ontology/domain/data-formats-t0300-mysql-version-convert-test.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/data-formats-t0301-pg-version-convert-test  # ontology/domain/data-formats-t0301-pg-version-convert-test.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/debugging  # ontology/domain/debugging.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/debugging-c-buffer-api-size-t-frame-validation  # ontology/domain/debugging-c-buffer-api-size-t-frame-validation.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/debugging-rpc-epoll-blocking-fd-trap  # ontology/domain/debugging-rpc-epoll-blocking-fd-trap.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/debugging-stream-frame-integration-traps  # ontology/domain/debugging-stream-frame-integration-traps.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/editor-config  # ontology/domain/editor-config.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/editor-config-neovim-config-audit  # ontology/domain/editor-config-neovim-config-audit.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/kernel-debugging  # ontology/domain/kernel-debugging.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/kernel-debugging-device-mapper-blk-mq-uaf-vmcore-method  # ontology/domain/kernel-debugging-device-mapper-blk-mq-uaf-vmcore-method.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/linux-epoll-eventloop  # ontology/domain/linux-epoll-eventloop.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/linux-epoll-eventloop-backupstream-v65-v101-arch-evolution  # ontology/domain/linux-epoll-eventloop-backupstream-v65-v101-arch-evolution.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/linux-epoll-eventloop-dynamic-deadline-wakeup  # ontology/domain/linux-epoll-eventloop-dynamic-deadline-wakeup.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/linux-epoll-eventloop-event-loop-time-conservation  # ontology/domain/linux-epoll-eventloop-event-loop-time-conservation.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/linux-epoll-eventloop-multireactor-so-reuseport  # ontology/domain/linux-epoll-eventloop-multireactor-so-reuseport.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/linux-epoll-eventloop-rpc-conn-idle-reclaim  # ontology/domain/linux-epoll-eventloop-rpc-conn-idle-reclaim.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/linux-epoll-eventloop-transport-ownership-model  # ontology/domain/linux-epoll-eventloop-transport-ownership-model.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/lmdb  # ontology/domain/lmdb.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/mysql  # ontology/domain/mysql.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/mysql-backup-recovery-consistency  # ontology/domain/mysql-backup-recovery-consistency.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/mysql-normal-shutdown-visibility-scope  # ontology/domain/mysql-normal-shutdown-visibility-scope.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/mysql-schema-nullable-contract  # ontology/domain/mysql-schema-nullable-contract.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/nbu  # ontology/domain/nbu.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/nbu-nbu-dte-architecture  # ontology/domain/nbu-nbu-dte-architecture.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/network-bandwidth-control  # ontology/domain/network-bandwidth-control.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/network-bandwidth-control-backup-bw-limit-algo-selection  # ontology/domain/network-bandwidth-control-backup-bw-limit-algo-selection.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/observability  # ontology/domain/observability.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/observability-structured-logging-jsonl-rotation  # ontology/domain/observability-structured-logging-jsonl-rotation.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/ontology-hybrid-methodology  # ontology/domain/ontology-hybrid-methodology.md score=30 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/out-of-scope  # ontology/domain/out-of-scope.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/pg  # ontology/domain/pg.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/pg-backup-recovery-wal-replay  # ontology/domain/pg-backup-recovery-wal-replay.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/pg-pgwrecover-implementation  # ontology/domain/pg-pgwrecover-implementation.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/pg-toast-compressed-varlena-layout  # ontology/domain/pg-toast-compressed-varlena-layout.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/pg-visibility-clog-infomask  # ontology/domain/pg-visibility-clog-infomask.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/rdb-config  # ontology/domain/rdb-config.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/rdb-config-audit-findings  # ontology/domain/rdb-config-audit-findings.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/rdb-config-optim-roadmap  # ontology/domain/rdb-config-optim-roadmap.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/rdb-config-wire-tool-config-to-registry  # ontology/domain/rdb-config-wire-tool-config-to-registry.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/report-center  # ontology/domain/report-center.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/report-center-async-export-distributed-quota-patterns  # ontology/domain/report-center-async-export-distributed-quota-patterns.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/report-center-auth-rpc-compensation-patterns  # ontology/domain/report-center-auth-rpc-compensation-patterns.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/report-center-db-adapter-pg-practices  # ontology/domain/report-center-db-adapter-pg-practices.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/report-center-deployment-assembly-patterns  # ontology/domain/report-center-deployment-assembly-patterns.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/report-center-report-center-decomposition-index  # ontology/domain/report-center-report-center-decomposition-index.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/report-center-report-web-report-sql-patterns  # ontology/domain/report-center-report-web-report-sql-patterns.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/reporting  # ontology/domain/reporting.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/reporting-report-graphical-transformation  # ontology/domain/reporting-report-graphical-transformation.md score=30 ['ATTR_GENERIC', 'MISSING_EXAMPLES', 'MISSING_SOURCE_LINE']
ontology:domain/rpc-rdbcomm  # ontology/domain/rpc-rdbcomm.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/rpc-rdbcomm-internal-dead-code-vs-public-abi  # ontology/domain/rpc-rdbcomm-internal-dead-code-vs-public-abi.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-advance-phase  # ontology/domain/skill-advance-phase.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-ask-matt  # ontology/domain/skill-ask-matt.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/skill-bug-analysis  # ontology/domain/skill-bug-analysis.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-bug-commit-format  # ontology/domain/skill-bug-commit-format.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-build-config  # ontology/domain/skill-build-config.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-chinese-environment  # ontology/domain/skill-chinese-environment.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-code-comments  # ontology/domain/skill-code-comments.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/skill-code-review  # ontology/domain/skill-code-review.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-code-review-checklist  # ontology/domain/skill-code-review-checklist.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-codebase-design  # ontology/domain/skill-codebase-design.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-commit-format  # ontology/domain/skill-commit-format.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-context-orchestration  # ontology/domain/skill-context-orchestration.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-context-retrieval  # ontology/domain/skill-context-retrieval.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-design-it-twice  # ontology/domain/skill-design-it-twice.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/skill-diagnosing-bugs  # ontology/domain/skill-diagnosing-bugs.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/skill-domain-modeling  # ontology/domain/skill-domain-modeling.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-domain-modeling-work  # ontology/domain/skill-domain-modeling-work.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/skill-feature-commit-format  # ontology/domain/skill-feature-commit-format.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-grill  # ontology/domain/skill-grill.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-grilling  # ontology/domain/skill-grilling.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/skill-handoff  # ontology/domain/skill-handoff.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-handoff-work  # ontology/domain/skill-handoff-work.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-implement  # ontology/domain/skill-implement.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-improve-codebase-architecture  # ontology/domain/skill-improve-codebase-architecture.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/skill-ontology-check  # ontology/domain/skill-ontology-check.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-project-goal  # ontology/domain/skill-project-goal.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-prototype  # ontology/domain/skill-prototype.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-register-evidence  # ontology/domain/skill-register-evidence.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-research  # ontology/domain/skill-research.md score=38 ['MISSING_ATTRIBUTES', 'MISSING_EXAMPLES', 'MISSING_SOURCE_LINE']
ontology:domain/skill-resolving-merge-conflicts  # ontology/domain/skill-resolving-merge-conflicts.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/skill-secure-coding  # ontology/domain/skill-secure-coding.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-tdd  # ontology/domain/skill-tdd.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/skill-teach  # ontology/domain/skill-teach.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-testing-strategy  # ontology/domain/skill-testing-strategy.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/skill-to-questionnaire  # ontology/domain/skill-to-questionnaire.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-to-spec  # ontology/domain/skill-to-spec.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-to-tickets  # ontology/domain/skill-to-tickets.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/skill-triage  # ontology/domain/skill-triage.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-triage-work  # ontology/domain/skill-triage-work.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/skill-verify-convergence  # ontology/domain/skill-verify-convergence.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/skill-wait-wait  # ontology/domain/skill-wait-wait.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-wayfinder  # ontology/domain/skill-wayfinder.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-wayfinding-chart  # ontology/domain/skill-wayfinding-chart.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/skill-wayfinding-work  # ontology/domain/skill-wayfinding-work.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-web-research  # ontology/domain/skill-web-research.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-wizard  # ontology/domain/skill-wizard.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-write-conclusion  # ontology/domain/skill-write-conclusion.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-write-journal  # ontology/domain/skill-write-journal.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/skill-writing-great-skills  # ontology/domain/skill-writing-great-skills.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/tdd-mocking  # ontology/domain/tdd-mocking.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/tdd-tests  # ontology/domain/tdd-tests.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/tls  # ontology/domain/tls.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/tls-cert-dual-format-and-path-unify  # ontology/domain/tls-cert-dual-format-and-path-unify.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/tls-handshake-dup-impl-length-contract  # ontology/domain/tls-handshake-dup-impl-length-contract.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/tls-handshake-reject-frame-consistency  # ontology/domain/tls-handshake-reject-frame-consistency.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/tool-production-readiness  # ontology/domain/tool-production-readiness.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE']
ontology:domain/tooling  # ontology/domain/tooling.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/tooling-cpp-api-style-mechanical-refactor-pitfalls  # ontology/domain/tooling-cpp-api-style-mechanical-refactor-pitfalls.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/tooling-layered-checker-shortcircuit-alignment  # ontology/domain/tooling-layered-checker-shortcircuit-alignment.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/workflow  # ontology/domain/workflow.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/workflow-code-review-dual-axis  # ontology/domain/workflow-code-review-dual-axis.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:domain/workflow-skill-invocation-convention  # ontology/domain/workflow-skill-invocation-convention.md score=15 ['ATTR_GENERIC', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:entity/backup-crypto-entity  # ontology/entity/backup-crypto-entity.md score=28 ['MISSING_CONCEPT', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:entity/backup-system  # ontology/entity/backup-system.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_CONCEPT', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:entity/evidence-convergence-map  # ontology/entity/evidence-convergence-map.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:entity/evidence-review  # ontology/entity/evidence-review.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_CONCEPT', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:entity/evidence-test-result  # ontology/entity/evidence-test-result.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:entity/exec-stdin-pump  # ontology/entity/exec-stdin-pump.md score=8 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:entity/mtls-handshake  # ontology/entity/mtls-handshake.md score=8 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:entity/ontology-deep-integration  # ontology/entity/ontology-deep-integration.md score=8 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:entity/ontology-deep-integration-knowledge  # ontology/entity/ontology-deep-integration-knowledge.md score=8 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:entity/ontology-deep-integration-split  # ontology/entity/ontology-deep-integration-split.md score=8 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:entity/ontology-deep-integration-test  # ontology/entity/ontology-deep-integration-test.md score=8 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:entity/ontology-deep-integration-tree  # ontology/entity/ontology-deep-integration-tree.md score=8 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:entity/phase-act  # ontology/entity/phase-act.md score=8 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:entity/phase-archive  # ontology/entity/phase-archive.md score=8 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:entity/phase-check  # ontology/entity/phase-check.md score=8 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:entity/phase-do  # ontology/entity/phase-do.md score=8 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:entity/phase-plan  # ontology/entity/phase-plan.md score=8 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:entity/report-center-system  # ontology/entity/report-center-system.md score=15 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:entity/tls-configuration  # ontology/entity/tls-configuration.md score=8 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:entity/tls-session  # ontology/entity/tls-session.md score=8 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:entity/tls-test-harness  # ontology/entity/tls-test-harness.md score=8 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:entity/transition-act-archive  # ontology/entity/transition-act-archive.md score=8 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:entity/transition-check-act  # ontology/entity/transition-check-act.md score=8 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:entity/transition-do-check  # ontology/entity/transition-do-check.md score=8 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:entity/transition-plan-do  # ontology/entity/transition-plan-do.md score=8 ['MISSING_ATTRIBUTES', 'MISSING_CONCEPT', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:entity/verdict-confirmed  # ontology/entity/verdict-confirmed.md score=8 ['MISSING_ATTRIBUTES', 'MISSING_CONCEPT', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:entity/verdict-partial  # ontology/entity/verdict-partial.md score=8 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:entity/verdict-rejected  # ontology/entity/verdict-rejected.md score=8 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:entity/x509-certificate  # ontology/entity/x509-certificate.md score=8 ['MISSING_ATTRIBUTES', 'MISSING_DIAGRAM', 'MISSING_EXAMPLES', 'MISSING_SOURCE', 'BODY_TOO_SHORT']
ontology:fact  # ontology/concept/fact.md score=8 ['MISSING_CONCEPT']
ontology:pattern  # ontology/concept/pattern.md score=8 ['MISSING_CONCEPT']
ontology:pattern/research-diagram-methodology  # ontology/pattern/research-diagram-methodology.md score=55 ['ATTR_GENERIC']
ontology:pattern/scientific-research-arc42  # ontology/pattern/scientific-research-arc42.md score=15 ['ATTR_GENERIC']
ontology:pattern/scientific-research-c4  # ontology/pattern/scientific-research-c4.md score=15 ['ATTR_GENERIC']
ontology:pattern/scientific-research-diataxis  # ontology/pattern/scientific-research-diataxis.md score=15 ['ATTR_GENERIC']
ontology:pattern/scientific-research-lifecycle  # ontology/pattern/scientific-research-lifecycle.md score=15 ['ATTR_GENERIC']
ontology:pitfall  # ontology/concept/pitfall.md score=8 ['MISSING_CONCEPT']
```

## 复现

```bash
python3 scripts/audit-ontology-fidelity.py --ontology-dir ontology --out records/T0534-0902-ontology-fidelity-remediation/audit-report.md --jsonl /tmp/fidelity.jsonl
python3 scripts/audit-ontology-fidelity.py --check fidelity --ontology-dir ontology  # 致命门禁
```

Source: `ontology/concept/ontology-fidelity-criterion.md` 七项清单 + `scripts/audit-ontology-fidelity.py`
