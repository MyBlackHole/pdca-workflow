# PDCA 体系健康度自我审查报告

- 异常总数: 116

## 汇总

| 维度 | 计数 |
|------|------|
| event_mismatch | 5 |
| exemption | 5 |
| gate_incomplete | 6 |
| id_collision | 26 |
| legacy_no_gate | 13 |
| record_mismatch | 17 |
| schema | 8 |
| seam | 36 |

| 严重度 | 计数 |
|--------|------|
| blocking | 32 |
| integrity | 66 |
| noise | 18 |

| 根因 | 计数 |
|------|------|
| external-project | 9 |
| legacy | 62 |
| real-defect | 45 |

## 门禁覆盖率

- receipts 80.8% (240/297)，verdict 76.8%，rejected receipts 251 条

## 问题明细（按严重度）

### 阻断门禁 (32)

| task_id | slug | 类别 | 根因 | 明细 |
|---------|------|------|------|------|
| T0216 | 0805-rpc-epoll-worker-supply-followup / T0216-0804-report-db-adapter | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0218 | 0806-buf-layer-endianness / 0808-backup-server-architecture / T0218-0804-collection-service | id_collision | legacy | 同一 task_id 出现在 3 个目录 |
| T0219 | 0806-rpc-arm-interop-verify / T0219-0804-report-web | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0220 | 0806-rpc-benchmark-review / T0220-0804-report-templates-query-export | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0221 | 0806-aio-speed-link-fix / T0221-0804-deployment-install | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0222 | 0806-epoll-business-callback-fsm / T0222-0804-acceptance-perf | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0228 | 0808-seda-pipeline / 0807-roach-gm-encrypt-support | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0229 | 0808-core-tech-poc-2 / T0229-0810-ob-backup-gm-encrypt-verify | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0248 | 0813-lmdb-tree-resume-round62 / T0248-0812-openssh-src-unpack | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0250 | 0814-lmdb-vl32-followup-round64 / 0813-mysql-parquet-physical | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0252 | 0814-tree-checkpoint-paged-round66 / 0814-inih-hide-symbols | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0253 | 0814-resume-production-architecture-round67 / 0814-sbt-transfer-encryption | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0254 | 0814-resumable-enumerator-segments-round67a / 0814-tls-cert-gmssl-backend | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0255 | 0814-durable-segment-protocol-round67b / 0814-tls-keygen-sm2 | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0256 | 0814-resume-rollout-benchmark-round67c / 0814-security-encrypt-config | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0257 | 0814-dmsbtex-sbt-encryption / 0814-immutable-object-manifest-store-round67d | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0258 | 0814-generation-publish-gc-restore-round67e / 0814-libobk-sbt-encryption | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0259 | 0814-backup-catalog-restore-round67f / 0814-oss-https-support | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0260 | 0817-rpc-handshake-negotiation / 0814-self-improvement-effectiveness-audit | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0300 | 0818-mysql-version-convert-test / 0820-backupstream-arch-diagram | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0323 | 0819-fsdeamon-snapshot-socket-leak / 0819-tool-mtls-cli-args-final | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0333 | 0820-backup-log-recovery / 0820-tls-cli-override-timing | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0335 | 0820-tls-session-integration-test | gate_incomplete | real-defect | gate_incomplete:no-act-to-archive |
| T0336 | 0821-tls-cert-ssl-free / 0820-pgwrecover-incremental-scope | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0336 | 0820-pgwrecover-incremental-scope | gate_incomplete | real-defect | gate_incomplete:no-act-to-archive |
| T0337 | 0821-tls-cert-ssl-wrapper / 0821-pgwrecover-btree-varlena-wal16 | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0338 | 0821-pgwrecover-btree-replay | gate_incomplete | real-defect | gate_incomplete:no-act-to-archive |
| T0339 | 0821-tls-keygen-cleanup / 0821-pgwrecover-btree-p1 | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0348 | 0822-rpc-cert-review / T0348-0822-mtls-state-alg-review | id_collision | real-defect | 同一 task_id 出现在 2 个目录 |
| T0350 | 0823-hs-frame-check-rollout | gate_incomplete | real-defect | gate_incomplete:no-act-to-archive |
| T0351 | 0823-remove-libs-rpc-handshake | gate_incomplete | real-defect | gate_incomplete:no-act-to-archive |
| T0398 | 0827-s3tools-rdb-config-integrate | gate_incomplete | real-defect | gate_incomplete:no-verdict |

### 数据完整性 (66)

| task_id | slug | 类别 | 根因 | 明细 |
|---------|------|------|------|------|
| 0805-rpc-epoll-worker-supply-followup | 0805-rpc-epoll-worker-supply-followup | schema | real-defect | SCHEMA_INVALID |
| 0806-aio-speed-link-fix | 0806-aio-speed-link-fix | schema | real-defect | SCHEMA_INVALID |
| 0806-buf-layer-endianness | 0806-buf-layer-endianness | schema | real-defect | SCHEMA_INVALID |
| 0806-rpc-arm-interop-verify | 0806-rpc-arm-interop-verify | schema | real-defect | SCHEMA_INVALID |
| 0806-rpc-benchmark-review | 0806-rpc-benchmark-review | schema | real-defect | SCHEMA_INVALID |
| ? | 0822-rpc-hs-err-exit-code | seam | real-defect | 测试文件缺失: rpc/tests/mixed_mtls.cpp |
| T0135 | 0728-ai-friendliness-hardening | record_mismatch | legacy | record=R0135-ai-friendliness-hardening 期望=T0135-0728-ai-friendliness-hardening |
| T0136 | 0728-pdca-state-contract | record_mismatch | legacy | record=R0136-pdca-state-contract 期望=T0136-0728-pdca-state-contract |
| T0137 | 0728-pdca-capability-doctor | record_mismatch | legacy | record=R0137-pdca-capability-doctor 期望=T0137-0728-pdca-capability-doctor |
| T0138 | 0728-skill-content-audit | record_mismatch | legacy | record=R0138-skill-content-audit 期望=T0138-0728-skill-content-audit |
| T0139 | 0728-ai-friendliness-harness | record_mismatch | legacy | record=R0139-ai-friendliness-harness 期望=T0139-0728-ai-friendliness-harness |
| T0140 | 0728-agent-workflow-landscape | record_mismatch | legacy | record=R0140-agent-workflow-landscape 期望=T0140-0728-agent-workflow-landscape |
| T0141 | 0728-convergence-validator | record_mismatch | legacy | record=R0141-convergence-validator 期望=T0141-0728-convergence-validator |
| T0142 | 0728-clean-invalid-active-history | record_mismatch | legacy | record=R0142-clean-invalid-active-history 期望=T0142-0728-clean-invalid-active-history |
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
| T0226 | 0807-rpc-conn-idle-implement | record_mismatch | legacy | record=2026-08-07-rpc-conn-idle-implement 期望=T0226-0807-rpc-conn-idle-implement |
| T0227 | 0807-rpc-socket-reuse-idle-reclaim | record_mismatch | legacy | record=2026-08-07-rpc-idle-reclaim 期望=T0227-0807-rpc-socket-reuse-idle-reclaim |
| T0248 | 0813-lmdb-tree-resume-round62 | seam | external-project | 测试文件缺失: tests/metadata_backend_integration.sh; 测试文件缺失: tests/benchmark_metadata_index.sh; 测试文件缺失: tests/tls_tree_checkpoint_resume_integration.sh |
| T0252 | flow-events | event_mismatch | legacy | 目录 record=T0252-0814-inih-hide-symbols payload=T0252 |
| T0252 | flow-events | event_mismatch | legacy | 目录 record=T0252-0814-inih-hide-symbols payload=T0252 |
| T0252 | flow-events | event_mismatch | legacy | 目录 record=T0252-0814-inih-hide-symbols payload=T0252 |
| T0252 | flow-events | event_mismatch | legacy | 目录 record=T0252-0814-inih-hide-symbols payload=T0252 |
| T0252 | flow-events | event_mismatch | legacy | 目录 record=T0252-0814-inih-hide-symbols payload=T0252 |
| T0252 | 0814-tree-checkpoint-paged-round66 | seam | external-project | 测试文件缺失: tests/tls_tree_checkpoint_resume_integration.sh; 测试文件缺失: tests/tree_checkpoint_paged_benchmark.sh; 测试文件缺失: tests/unit.cpp |
| T0253 | 0814-resume-production-architecture-round67 | seam | external-project | 测试文件缺失: tests/tls_tree_checkpoint_resume_integration.sh; 测试文件缺失: tests/tls_tree_checkpoint_resume_integration.sh; 测试文件缺失: tests/tree_checkpoint_paged_benchmark.sh |
| T0253 | 0814-sbt-transfer-encryption | seam | real-defect | 测试文件缺失: libs/tests/tls_cert_test.c; 测试文件缺失: libs/tls_cert.c; 测试文件缺失: dmsbtex/network.c |
| T0254 | 0814-resumable-enumerator-segments-round67a | seam | external-project | 测试文件缺失: tests/tls_tree_checkpoint_resume_integration.sh; 测试文件缺失: tests/tree_checkpoint_paged_benchmark.sh; 测试文件缺失: tests/unit.cpp |
| T0255 | 0814-durable-segment-protocol-round67b | seam | external-project | 测试文件缺失: tests/tls_tree_checkpoint_resume_integration.sh |
| T0256 | 0814-resume-rollout-benchmark-round67c | seam | external-project | 测试文件缺失: tests/tls_tree_checkpoint_resume_integration.sh; 测试文件缺失: tests/tls_tree_checkpoint_resume_integration.sh; 测试文件缺失: tests/tree_checkpoint_paged_benchmark.sh |
| T0257 | 0814-immutable-object-manifest-store-round67d | seam | external-project | 测试文件缺失: tests/tree_checkpoint_paged_benchmark.sh; 测试文件缺失: tests/unit.cpp |
| T0258 | 0814-generation-publish-gc-restore-round67e | seam | external-project | 测试文件缺失: tests/tls_tree_checkpoint_resume_integration.sh; 测试文件缺失: tests/tls_tree_checkpoint_resume_integration.sh |
| T0259 | 0814-backup-catalog-restore-round67f | seam | external-project | 测试文件缺失: tests/tls_tree_checkpoint_resume_integration.sh; 测试文件缺失: tests/tls_tree_checkpoint_resume_integration.sh |
| T0260 | 0817-rpc-handshake-negotiation | seam | real-defect | 测试文件缺失: rpc/tests/rpc_negotiate_test.cpp; 测试文件缺失: rpc/tests/rpc_negotiate_test.cpp; 测试文件缺失: libs/tests/tls_cert_test.c |
| T0288 | 0815-backupstream-optimize | seam | real-defect | 测试文件缺失: tests/gate_warnings.sh; 测试文件缺失: tests/benchmark_control_plane.sh; 测试文件缺失: tests/benchmark_data_path.sh |
| T0289 | 0815-gate-werror | seam | real-defect | 测试文件缺失: tests/gate_warnings.sh |
| T0290 | 0815-perf-baseline | seam | real-defect | 测试文件缺失: tests/benchmark_control_plane.sh; 测试文件缺失: tests/benchmark_data_path.sh |
| T0293 | 0815-v81-cp-perf | seam | real-defect | 测试文件缺失: tests/benchmark_control_plane.sh; 测试文件缺失: tests/v81_control_frame_integration.sh; 测试文件缺失: tests/benchmark_data_path.sh |
| T0303 | 0818-unified-first-stage-protocol | seam | real-defect | 测试文件缺失: rpc/tests/rpc_rdbcomm_negotiate_test.cpp |
| T0304 | 0818-rpc-handshake-time-adapter | seam | real-defect | 测试文件缺失: rpc/tests/rpc_rdbcomm_negotiate_test.cpp |
| T0305 | 0818-rdbcomm-handshake-time-adapter | seam | real-defect | 测试文件缺失: rdbcomm/tests/rdbcomm_negotiate_test.c; 测试文件缺失: rdbcomm/tests/rdbcomm_time_test.c |
| T0306 | 0818-rpc-rdbcomm-protocol-integration | seam | real-defect | 测试文件缺失: rpc/tests/rpc_rdbcomm_negotiate_test.cpp; 测试文件缺失: rdbcomm/tests/rdbcomm_negotiate_test.c |
| T0313 | 0818-rpc-rdbcomm-sm2-app-frame-followup | seam | real-defect | 测试文件缺失: `libs/tests/tls_cert_test.c` |
| T0319 | 0818-tool-mtls-config | seam | real-defect | 测试文件缺失: `libs/tests/rpc_handshake_test.c` |
| T0320 | 0818-help-algorithm-constants | seam | real-defect | 测试文件缺失: `libs/tests/rpc_handshake_test.c`; 测试文件缺失: `libs/tests/rdb_config_test.c` |
| T0321 | 0819-tool-mtls-cli-args | seam | real-defect | 测试文件缺失: `libs/tests/rpc_handshake_test.c` |
| T0322 | 0819-tool-mtls-cli-args-v2 | seam | real-defect | 测试文件缺失: `libs/tests/rpc_handshake_test.c` |
| T0326 | 0819-centralize-all-ini-parameters | seam | real-defect | 测试文件缺失: `libs/tests/rdb_config_test.c` |
| T0327 | 0819-no-app-config-intervention | seam | real-defect | 测试文件缺失: `libs/tests/rdb_config_test.c` |
| T0328 | 0819-dmsbtex-libobk-mtls | seam | real-defect | 测试文件缺失: libs/tests/sbt_transport_test.c; 测试文件缺失: dmsbtex/network.c; 测试文件缺失: libobk/lib/logic/oracleCmdTbl.c |
| T0330 | 0819-sbt-rpc-session | seam | real-defect | 测试文件缺失: `libs/tests/rpc_handshake_test.c` |
| T0331 | 0819-sbt-mtls-simplify | seam | real-defect | 测试文件缺失: `libs/tests/rdb_config_test.c` |
| T0335 | 0820-tls-session-integration-test | seam | real-defect | 测试文件缺失: dmsbtex/test/session_test.c; 测试文件缺失: libobk/test/session_test.c |
| T0368 | 0823-oss-https-cert | seam | real-defect | 测试文件缺失: oss/cmd/oss_https_test.go |
| T0381 | 0823-async-object-lifecycle | seam | real-defect | 测试文件缺失: tests/callback_reactor_integration.sh; 测试文件缺失: tests/work_pool_init_integration.cpp |
| T0382 | 0823-async-lifecycle-tls-migrate | seam | real-defect | 测试文件缺失: tests/tls_reactor_state_machine.cpp |
| T0384 | 0823-async-lifecycle-runtime-converge | seam | real-defect | 测试文件缺失: tests/plain_restore_reactor_integration.sh; 测试文件缺失: tests/tls_tree_reactor_integration.sh |
| T0387 | 0826-rdb-config-f9-path-validation | seam | real-defect | 测试文件缺失: libs/tests/param_registry_test.c |

### 仅统计噪音 (18)

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
| T0336 | 0821-tls-cert-ssl-free | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T0337 | 0821-tls-cert-ssl-wrapper | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T0337 | 0821-pgwrecover-btree-varlena-wal16 | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T0339 | 0821-pgwrecover-btree-p1 | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T0340 | 0821-pgwrecover-btree-p2 | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T0348 | 0822-rpc-cert-review | legacy_no_gate | legacy | 机制前任务无 transition receipts |

## 修复候选清单（不执行，另立任务）

- **[high] ID 撞车清理**: 26 组 task_id 重复（跨目录），identity 歧义影响可追溯性 → 建议范围: 为每组冲突决定保留/重命名，更新依赖引用与记录
- **[high] 真违规门禁修复**: 6 项 gate_incomplete 非豁免（缺失 verdict/final_confirmation 等） → 建议范围: 按 T0271 remediate 模式补全或如实豁免
- **[medium] schema 一致性修复**: 8 项 schema/时序不一致任务 → 建议范围: 区分机制前遗留与真缺陷，对齐 states/receipts 时间序
- **[medium] record 派生一致性修复**: 17 项 record 字段与派生规则不符 → 建议范围: 按 identity 派生规则修正 task.json meta.record
- **[medium] seam 契约补齐**: 36 项声明的测试接缝与实际测试不一致 → 建议范围: 补齐缺失测试文件或修正 seam 声明（外部项目需确认测试位置）