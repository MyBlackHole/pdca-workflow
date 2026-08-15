# PDCA 体系健康度自我审查报告

- 异常总数: 77

## 汇总

| 维度 | 计数 |
|------|------|
| event_mismatch | 5 |
| exemption | 5 |
| id_collision | 23 |
| legacy_no_gate | 7 |
| record_mismatch | 20 |
| schema | 8 |
| seam | 9 |

| 严重度 | 计数 |
|--------|------|
| blocking | 23 |
| integrity | 42 |
| noise | 12 |

| 根因 | 计数 |
|------|------|
| external-project | 9 |
| legacy | 63 |
| real-defect | 5 |

## 门禁覆盖率

- receipts 82.2% (125/152)，verdict 80.9%，rejected receipts 10 条

## 问题明细（按严重度）

### 阻断门禁 (23)

| task_id | slug | 类别 | 根因 | 明细 |
|---------|------|------|------|------|
| T0142 | 0728-clean-invalid-active-history / 0729-vmcore-analysis | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0163 | 0731-nbu-dte-enforced-mechanism / 0731-pg-mysql-parquet-poc | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0214 | 0804-cdm-report-center-analyse / T0214-0804-rpc-epoll-industrial-align | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0215 | T0215-0804-report-subscheme-docs / T0215-0804-rpc-epoll-multireactor | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0216 | 0805-rpc-epoll-worker-supply-followup / T0216-0804-report-db-adapter | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0217 | 0805-rpc-serialization-hardening / T0217-0804-cdm-data-cli | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0218 | 0806-buf-layer-endianness / 0808-backup-server-architecture / T0218-0804-collection-service | id_collision | legacy | 同一 task_id 出现在 3 个目录 |
| T0219 | 0806-rpc-arm-interop-verify / T0219-0804-report-web | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0220 | 0806-rpc-benchmark-review / T0220-0804-report-templates-query-export | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0221 | 0806-aio-speed-link-fix / T0221-0804-deployment-install | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0222 | 0806-epoll-business-callback-fsm / T0222-0804-acceptance-perf | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0224 | 0808-bwlimit-poc / T0224-0804-async-export | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0225 | 0807-xtrabackup-incremental-tech / 0808-core-tech-poc | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0228 | 0808-seda-pipeline / 0807-roach-gm-encrypt-support | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0229 | 0808-core-tech-poc-2 / T0229-0810-ob-backup-gm-encrypt-verify | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0244 | 0809-pdca-flow-impl-review / 0812-rpc-metadata-analysis | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0246 | 0813-small-writer-pool / T0246-0810-backup-gm-transport-encryption | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0247 | 0813-small-writer-pool-round61 / T0247-0811-backup-doc-optimize | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0248 | 0813-lmdb-tree-resume-round62 / T0248-0812-openssh-src-unpack | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0249 | 0814-lmdb-no-mmap-round63 / T0249-0812-kernel-nfs-gm-research | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0250 | 0814-lmdb-vl32-followup-round64 / 0813-mysql-parquet-physical | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0251 | 0814-oss-xmake-integration / 0814-production-observability-round65 | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0252 | 0814-tree-checkpoint-paged-round66 / 0814-inih-hide-symbols | id_collision | legacy | 同一 task_id 出现在 2 个目录 |

### 数据完整性 (42)

| task_id | slug | 类别 | 根因 | 明细 |
|---------|------|------|------|------|
| 0805-rpc-epoll-worker-supply-followup | 0805-rpc-epoll-worker-supply-followup | schema | real-defect | SCHEMA_INVALID |
| 0806-aio-speed-link-fix | 0806-aio-speed-link-fix | schema | real-defect | SCHEMA_INVALID |
| 0806-buf-layer-endianness | 0806-buf-layer-endianness | schema | real-defect | SCHEMA_INVALID |
| 0806-rpc-arm-interop-verify | 0806-rpc-arm-interop-verify | schema | real-defect | SCHEMA_INVALID |
| 0806-rpc-benchmark-review | 0806-rpc-benchmark-review | schema | real-defect | SCHEMA_INVALID |
| T0135 | 0728-ai-friendliness-hardening | record_mismatch | legacy | record=R0135-ai-friendliness-hardening 期望=T0135-0728-ai-friendliness-hardening |
| T0136 | 0728-pdca-state-contract | record_mismatch | legacy | record=R0136-pdca-state-contract 期望=T0136-0728-pdca-state-contract |
| T0137 | 0728-pdca-capability-doctor | record_mismatch | legacy | record=R0137-pdca-capability-doctor 期望=T0137-0728-pdca-capability-doctor |
| T0138 | 0728-skill-content-audit | record_mismatch | legacy | record=R0138-skill-content-audit 期望=T0138-0728-skill-content-audit |
| T0139 | 0728-ai-friendliness-harness | record_mismatch | legacy | record=R0139-ai-friendliness-harness 期望=T0139-0728-ai-friendliness-harness |
| T0140 | 0728-agent-workflow-landscape | record_mismatch | legacy | record=R0140-agent-workflow-landscape 期望=T0140-0728-agent-workflow-landscape |
| T0141 | 0728-convergence-validator | record_mismatch | legacy | record=R0141-convergence-validator 期望=T0141-0728-convergence-validator |
| T0142 | 0728-clean-invalid-active-history | record_mismatch | legacy | record=R0142-clean-invalid-active-history 期望=T0142-0728-clean-invalid-active-history |
| T0142 | 0729-vmcore-analysis | record_mismatch | legacy | record=R0142-vmcore-analysis 期望=T0142-0729-vmcore-analysis |
| T0143 | 0729-vmcore-deep | record_mismatch | legacy | record=R0143 期望=T0143-0729-vmcore-deep |
| T0150 | 0730-parquet-format-research | record_mismatch | legacy | record=T0150 期望=T0150-0730-parquet-format-research |
| T0158 | 0801-pdca-process-audit | record_mismatch | legacy | record=T0158 期望=T0158-0801-pdca-process-audit |
| T0159 | 0801-pdca-self-optimization-loop | record_mismatch | legacy | record=T0159 期望=T0159-0801-pdca-self-optimization-loop |
| T0160 | 0730-ai-friendliness-evaluation-hardening | record_mismatch | legacy | record=R0160 期望=T0160-0730-ai-friendliness-evaluation-hardening |
| T0161 | 0731-execution-contract-hardening | record_mismatch | legacy | record=R0161 期望=T0161-0731-execution-contract-hardening |
| T0164-0731-gm-tls-benchmark | T0164-0731-gm-tls-benchmark | schema | legacy | CONFIRMATION_AFTER_PLAN_TO_DO; STATE_TIME_ORDER |
| T0182 | 0802-transaction-trigger-runner-pointer-dispatch | record_mismatch | legacy | record=T0182 期望=T0182-0802-transaction-trigger-runner-pointer-dispatch |
| T0210b-0806-btree-root-driven-recovery | T0210b-0806-btree-root-driven-recovery | schema | legacy | SCHEMA_INVALID |
| T0222-0804-acceptance-perf | T0222-0804-acceptance-perf | schema | legacy | STATE_TIMESTAMP_MISSING |
| T0225 | 0807-xtrabackup-incremental-tech | record_mismatch | legacy | record=T0225 期望=T0225-0807-xtrabackup-incremental-tech |
| T0226 | 0807-rpc-conn-idle-implement | record_mismatch | legacy | record=2026-08-07-rpc-conn-idle-implement 期望=T0226-0807-rpc-conn-idle-implement |
| T0227 | 0807-rpc-socket-reuse-idle-reclaim | record_mismatch | legacy | record=2026-08-07-rpc-idle-reclaim 期望=T0227-0807-rpc-socket-reuse-idle-reclaim |
| T0244 | 0812-rpc-metadata-analysis | record_mismatch | legacy | record=R0244-rpc-metadata-analysis 期望=T0244-0812-rpc-metadata-analysis |
| T0248 | 0813-lmdb-tree-resume-round62 | seam | external-project | 测试文件缺失: tests/metadata_backend_integration.sh; 测试文件缺失: tests/benchmark_metadata_index.sh; 测试文件缺失: tests/tls_tree_checkpoint_resume_integration.sh |
| T0252 | flow-events | event_mismatch | legacy | 目录 record=T0252-0814-inih-hide-symbols payload=T0252 |
| T0252 | flow-events | event_mismatch | legacy | 目录 record=T0252-0814-inih-hide-symbols payload=T0252 |
| T0252 | flow-events | event_mismatch | legacy | 目录 record=T0252-0814-inih-hide-symbols payload=T0252 |
| T0252 | flow-events | event_mismatch | legacy | 目录 record=T0252-0814-inih-hide-symbols payload=T0252 |
| T0252 | flow-events | event_mismatch | legacy | 目录 record=T0252-0814-inih-hide-symbols payload=T0252 |
| T0252 | 0814-tree-checkpoint-paged-round66 | seam | external-project | 测试文件缺失: tests/tls_tree_checkpoint_resume_integration.sh; 测试文件缺失: tests/tree_checkpoint_paged_benchmark.sh; 测试文件缺失: tests/unit.cpp |
| T0253 | 0814-resume-production-architecture-round67 | seam | external-project | 测试文件缺失: tests/tls_tree_checkpoint_resume_integration.sh; 测试文件缺失: tests/tls_tree_checkpoint_resume_integration.sh; 测试文件缺失: tests/tree_checkpoint_paged_benchmark.sh |
| T0254 | 0814-resumable-enumerator-segments-round67a | seam | external-project | 测试文件缺失: tests/tls_tree_checkpoint_resume_integration.sh; 测试文件缺失: tests/tree_checkpoint_paged_benchmark.sh; 测试文件缺失: tests/unit.cpp |
| T0255 | 0814-durable-segment-protocol-round67b | seam | external-project | 测试文件缺失: tests/tls_tree_checkpoint_resume_integration.sh |
| T0256 | 0814-resume-rollout-benchmark-round67c | seam | external-project | 测试文件缺失: tests/tls_tree_checkpoint_resume_integration.sh; 测试文件缺失: tests/tls_tree_checkpoint_resume_integration.sh; 测试文件缺失: tests/tree_checkpoint_paged_benchmark.sh |
| T0257 | 0814-immutable-object-manifest-store-round67d | seam | external-project | 测试文件缺失: tests/tree_checkpoint_paged_benchmark.sh; 测试文件缺失: tests/unit.cpp |
| T0258 | 0814-generation-publish-gc-restore-round67e | seam | external-project | 测试文件缺失: tests/tls_tree_checkpoint_resume_integration.sh; 测试文件缺失: tests/tls_tree_checkpoint_resume_integration.sh |
| T0259 | 0814-backup-catalog-restore-round67f | seam | external-project | 测试文件缺失: tests/tls_tree_checkpoint_resume_integration.sh; 测试文件缺失: tests/tls_tree_checkpoint_resume_integration.sh |

### 仅统计噪音 (12)

| task_id | slug | 类别 | 根因 | 明细 |
|---------|------|------|------|------|
| T0146 | T0146-0730-rpc-ipv6-support | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T0149 | T0149-0801-design-md-review | exemption | legacy | 早期任务（T0149-0801-design-md-review）record=None 无 conclusion，缺 final_confirmation 属 |
| T0162 | 0731-nbu-dte-packet-capture | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T0173 | 0801-journal-reclaim-proptest | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T0174 | 0801-btree-split-proptest | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T0175 | 0801-trans-enomem-restart | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T0176 | 0801-journal-seq-overflow-boundary | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T0200 | 0802-fsck-repair-faults | exemption | legacy | 早期任务缺 act-to-archive receipt（仅 plan-to-do/check-to-act），无过渡记录依据，如实豁免不伪造 |
| T0203 | 0802-concurrent-combined-sequence | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T0207 | 0803-fsck-scrub-rewrite-followup | exemption | legacy | 补 verdict 完成；缺 final_confirmation/act-to-archive 属门禁机制建立前记录不全，conclusion 已含完整 Ve |
| T0208 | 0803-btree-random-op-consistency | exemption | legacy | 补 verdict 完成；缺 final_confirmation/act-to-archive 属门禁机制建立前记录不全，conclusion 已含完整 Ve |
| T0209 | 0803-snapshot-table-reload | exemption | legacy | 补 verdict 完成；缺 final_confirmation/act-to-archive 属门禁机制建立前记录不全，conclusion 已含完整 Ve |

## 修复候选清单（不执行，另立任务）

- **[high] ID 撞车清理**: 23 组 task_id 重复（跨目录），identity 歧义影响可追溯性 → 建议范围: 为每组冲突决定保留/重命名，更新依赖引用与记录
- **[medium] schema 一致性修复**: 8 项 schema/时序不一致任务 → 建议范围: 区分机制前遗留与真缺陷，对齐 states/receipts 时间序
- **[medium] record 派生一致性修复**: 20 项 record 字段与派生规则不符 → 建议范围: 按 identity 派生规则修正 task.json meta.record
- **[medium] seam 契约补齐**: 9 项声明的测试接缝与实际测试不一致 → 建议范围: 补齐缺失测试文件或修正 seam 声明（外部项目需确认测试位置）