# PDCA 体系健康度自我审查报告

- 异常总数: 56

## 汇总

| 维度 | 计数 |
|------|------|
| gate_incomplete | 1 |
| id_collision | 9 |
| legacy_no_gate | 2 |
| schema | 8 |
| seam | 36 |

| 严重度 | 计数 |
|--------|------|
| blocking | 10 |
| integrity | 44 |
| noise | 2 |

| 根因 | 计数 |
|------|------|
| external-project | 9 |
| legacy | 14 |
| real-defect | 33 |

## 门禁覆盖率

- receipts 45.6% (36/79)，verdict 17.7%，rejected receipts 46 条

## 问题明细（按严重度）

### 阻断门禁 (10)

| task_id | slug | 类别 | 根因 | 明细 |
|---------|------|------|------|------|
| T0218 | 0806-buf-layer-endianness / 0808-backup-server-architecture | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0222 | 0806-epoll-business-callback-fsm / T0222-0804-acceptance-perf | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0253 | 0814-resume-production-architecture-round67 / 0814-sbt-transfer-encryption | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0254 | 0814-resumable-enumerator-segments-round67a / 0814-tls-cert-gmssl-backend | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0255 | 0814-durable-segment-protocol-round67b / 0814-tls-keygen-sm2 | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0256 | 0814-resume-rollout-benchmark-round67c / 0814-security-encrypt-config | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0257 | 0814-dmsbtex-sbt-encryption / 0814-immutable-object-manifest-store-round67d | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0258 | 0814-generation-publish-gc-restore-round67e / 0814-libobk-sbt-encryption | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0259 | 0814-backup-catalog-restore-round67f / 0814-oss-https-support | id_collision | legacy | 同一 task_id 出现在 2 个目录 |
| T0335 | 0820-tls-session-integration-test | gate_incomplete | real-defect | gate_incomplete:no-act-to-archive |

### 数据完整性 (44)

| task_id | slug | 类别 | 根因 | 明细 |
|---------|------|------|------|------|
| 0805-rpc-epoll-worker-supply-followup | 0805-rpc-epoll-worker-supply-followup | schema | real-defect | SCHEMA_INVALID |
| 0806-aio-speed-link-fix | 0806-aio-speed-link-fix | schema | real-defect | SCHEMA_INVALID |
| 0806-buf-layer-endianness | 0806-buf-layer-endianness | schema | real-defect | SCHEMA_INVALID |
| 0806-rpc-arm-interop-verify | 0806-rpc-arm-interop-verify | schema | real-defect | SCHEMA_INVALID |
| 0806-rpc-benchmark-review | 0806-rpc-benchmark-review | schema | real-defect | SCHEMA_INVALID |
| ? | 0822-rpc-hs-err-exit-code | seam | real-defect | 测试文件缺失: rpc/tests/mixed_mtls.cpp |
| T0164-0731-gm-tls-benchmark | T0164-0731-gm-tls-benchmark | schema | legacy | CONFIRMATION_AFTER_PLAN_TO_DO; STATE_TIME_ORDER |
| T0210b-0806-btree-root-driven-recovery | T0210b-0806-btree-root-driven-recovery | schema | legacy | SCHEMA_INVALID |
| T0222-0804-acceptance-perf | T0222-0804-acceptance-perf | schema | legacy | STATE_TIMESTAMP_MISSING |
| T0248 | 0813-lmdb-tree-resume-round62 | seam | external-project | 测试文件缺失: tests/metadata_backend_integration.sh; 测试文件缺失: tests/benchmark_metadata_index.sh; 测试文件缺失: tests/tls_tree_checkpoint_resume_integration.sh |
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

### 仅统计噪音 (2)

| task_id | slug | 类别 | 根因 | 明细 |
|---------|------|------|------|------|
| T0336 | 0821-tls-cert-ssl-free | legacy_no_gate | legacy | 机制前任务无 transition receipts |
| T0337 | 0821-tls-cert-ssl-wrapper | legacy_no_gate | legacy | 机制前任务无 transition receipts |

## 修复候选清单（不执行，另立任务）

- **[high] ID 撞车清理**: 9 组 task_id 重复（跨目录），identity 歧义影响可追溯性 → 建议范围: 为每组冲突决定保留/重命名，更新依赖引用与记录
- **[high] 真违规门禁修复**: 1 项 gate_incomplete 非豁免（缺失 verdict/final_confirmation 等） → 建议范围: 按 T0271 remediate 模式补全或如实豁免
- **[medium] schema 一致性修复**: 8 项 schema/时序不一致任务 → 建议范围: 区分机制前遗留与真缺陷，对齐 states/receipts 时间序
- **[medium] seam 契约补齐**: 36 项声明的测试接缝与实际测试不一致 → 建议范围: 补齐缺失测试文件或修正 seam 声明（外部项目需确认测试位置）