# PDCA 门禁合规审计（T0270，第六轮）

扫描根: `pdca/tasks` | 任务数: 154

## 覆盖率

| 要素 | 覆盖数 | 覆盖率 |
|---|---:|---:|
| transition receipts（成功） | 125 | 81.2% |
| verdict | 122 | 79.2% |
| convergence 非空 | 147 | 95.5% |
| final_confirmation | 130 | 84.4% |
| rejected receipts（拒收留痕） | 0 | - |

## 阶段分布

| 阶段 | 任务数 |
|---|---:|
| act | 6 |
| archive | 118 |
| check | 2 |
| do | 10 |
| plan | 18 |

## 异常清单

### id 撞车

组数: 25

- `T0142`: archive/2026-07/0728-clean-invalid-active-history/task.json; archive/2026-07/0729-vmcore-analysis/task.json
- `T0163`: archive/2026-07/0731-nbu-dte-enforced-mechanism/task.json; archive/2026-07/0731-pg-mysql-parquet-poc/task.json
- `T0174`: archive/0801-btree-split-proptest/0801-btree-split-proptest/task.json; archive/0801-btree-split-proptest/task.json
- `T0175`: archive/0801-trans-enomem-restart/0801-trans-enomem-restart/task.json; archive/0801-trans-enomem-restart/task.json
- `T0214`: active/0804-cdm-report-center-analyse/task.json; archive/2026-08/0804-cdm-report-center-analyse/task.json; archive/2026-08/T0214-0804-rpc-epoll-industrial-align/task.json
- `T0215`: active/T0215-0804-report-subscheme-docs/task.json; archive/2026-08/T0215-0804-report-subscheme-docs/task.json; archive/2026-08/T0215-0804-rpc-epoll-multireactor/task.json
- `T0216`: active/0805-rpc-epoll-worker-supply-followup/task.json; archive/2026-08/T0216-0804-report-db-adapter/task.json
- `T0217`: archive/2026-08/0805-rpc-serialization-hardening/task.json; archive/2026-08/T0217-0804-cdm-data-cli/task.json
- `T0218`: active/0806-buf-layer-endianness/task.json; active/0808-backup-server-architecture/task.json; archive/2026-08/T0218-0804-collection-service/task.json
- `T0219`: active/0806-rpc-arm-interop-verify/task.json; archive/2026-08/T0219-0804-report-web/task.json
- `T0220`: active/0806-rpc-benchmark-review/task.json; archive/2026-08/T0220-0804-report-templates-query-export/task.json
- `T0221`: active/0806-aio-speed-link-fix/task.json; archive/2026-08/T0221-0804-deployment-install/task.json
- `T0222`: active/0806-epoll-business-callback-fsm/task.json; active/T0222-0804-acceptance-perf/task.json
- `T0224`: archive/2026-08/0808-bwlimit-poc/task.json; archive/2026-08/T0224-0804-async-export/task.json
- `T0225`: archive/2026-08/0807-xtrabackup-incremental-tech/task.json; archive/2026-08/0808-core-tech-poc/task.json
- `T0228`: active/0808-seda-pipeline/task.json; archive/2026-08/0807-roach-gm-encrypt-support/task.json
- `T0229`: active/0808-core-tech-poc-2/task.json; archive/2026-08/T0229-0810-ob-backup-gm-encrypt-verify/task.json
- `T0244`: archive/2026-08/0809-pdca-flow-impl-review/task.json; archive/2026-08/0812-rpc-metadata-analysis/task.json
- `T0246`: archive/2026-08/0813-small-writer-pool/task.json; archive/2026-08/T0246-0810-backup-gm-transport-encryption/task.json
- `T0247`: archive/2026-08/0813-small-writer-pool-round61/task.json; archive/2026-08/T0247-0811-backup-doc-optimize/task.json
- `T0248`: 0813-lmdb-tree-resume-round62/task.json; archive/2026-08/T0248-0812-openssh-src-unpack/task.json
- `T0249`: archive/2026-08/0814-lmdb-no-mmap-round63/task.json; archive/2026-08/T0249-0812-kernel-nfs-gm-research/task.json
- `T0250`: 0814-lmdb-vl32-followup-round64/task.json; active/0813-mysql-parquet-physical/task.json
- `T0251`: archive/2026-08/0814-oss-xmake-integration/task.json; archive/2026-08/0814-production-observability-round65/task.json
- `T0252`: 0814-tree-checkpoint-paged-round66/task.json; archive/2026-08/0814-inih-hide-symbols/task.json

### 归档不一致（重复归档 / active 残留）

重复归档组数: 2 | active 残留组数: 2

- `0801-btree-split-proptest` 重复归档: archive/0801-btree-split-proptest/0801-btree-split-proptest/task.json; archive/0801-btree-split-proptest/task.json
- `0801-trans-enomem-restart` 重复归档: archive/0801-trans-enomem-restart/0801-trans-enomem-restart/task.json; archive/0801-trans-enomem-restart/task.json
- `0804-cdm-report-center-analyse` active 残留: active/0804-cdm-report-center-analyse/task.json; archive/2026-08/0804-cdm-report-center-analyse/task.json
- `T0215-0804-report-subscheme-docs` active 残留: active/T0215-0804-report-subscheme-docs/task.json; archive/2026-08/T0215-0804-report-subscheme-docs/task.json

### 门禁要素异常（按任务）

| id | phase | receipts | verdict | final_conf | issues |
|---|---|---:|---|---|---|
| T0142 | archive | 4 | Y | Y | id_collision |
| T0142 | archive | 4 | Y | Y | id_collision |
| T0146 | archive | 0 | Y | Y | legacy_no_gate |
| T0149 | archive | 1 | Y | N | gate_incomplete:no-final-confirmation |
| T0162 | archive | 0 | Y | Y | legacy_no_gate |
| T0163 | archive | 3 | Y | Y | id_collision |
| T0163 | archive | 4 | Y | Y | id_collision |
| T0173 | act | 0 | Y | Y | legacy_no_gate |
| T0174 | act | 0 | Y | N | id_collision; legacy_no_gate |
| T0174 | act | 0 | Y | Y | id_collision; legacy_no_gate |
| T0175 | act | 0 | Y | N | id_collision; legacy_no_gate |
| T0175 | act | 0 | Y | Y | id_collision; legacy_no_gate |
| T0176 | act | 0 | Y | N | legacy_no_gate |
| T0200 | archive | 2 | Y | Y | gate_incomplete:no-act-to-archive |
| T0203 | archive | 0 | Y | Y | legacy_no_gate |
| T0207 | archive | 1 | N | Y | gate_incomplete:no-verdict; gate_incomplete:no-act-to-archive |
| T0208 | archive | 1 | N | N | gate_incomplete:no-verdict; gate_incomplete:no-final-confirmation; gate_incomplete:no-act-to-archive |
| T0209 | archive | 2 | N | N | gate_incomplete:no-verdict; gate_incomplete:no-final-confirmation; gate_incomplete:no-act-to-archive |
| T0210b | do | 0 | N | N | legacy_no_gate |
| T0214 | archive | 4 | Y | Y | id_collision |
| T0214 | archive | 4 | Y | Y | id_collision |
| T0214 | archive | 4 | Y | Y | id_collision |
| T0215 | archive | 4 | Y | Y | id_collision |
| T0215 | archive | 4 | Y | Y | id_collision |
| T0215 | archive | 4 | Y | Y | id_collision |
| T0216 | plan | 0 | N | N | id_collision; legacy_no_gate |
| T0216 | archive | 4 | Y | Y | id_collision |
| T0217 | archive | 4 | Y | Y | id_collision |
| T0217 | archive | 4 | Y | Y | id_collision |
| T0218 | plan | 0 | N | N | id_collision; legacy_no_gate |
| T0218 | do | 0 | N | Y | id_collision; legacy_no_gate |
| T0218 | archive | 4 | Y | Y | id_collision |
| T0219 | plan | 0 | N | N | id_collision; legacy_no_gate |
| T0219 | archive | 4 | Y | Y | id_collision |
| T0220 | plan | 0 | N | N | id_collision; legacy_no_gate |
| T0220 | archive | 4 | Y | Y | id_collision |
| T0221 | plan | 0 | N | N | id_collision; legacy_no_gate |
| T0221 | archive | 4 | Y | Y | id_collision |
| T0222 | do | 1 | N | Y | id_collision |
| T0222 | plan | 0 | N | N | id_collision; legacy_no_gate |
| T0224 | archive | 4 | Y | Y | id_collision |
| T0224 | archive | 4 | Y | Y | id_collision |
| T0225 | archive | 4 | Y | Y | id_collision |
| T0225 | archive | 4 | Y | Y | id_collision |
| T0228 | do | 1 | N | Y | id_collision |
| T0228 | archive | 4 | Y | Y | id_collision |
| T0229 | do | 1 | N | Y | id_collision |
| T0229 | archive | 4 | Y | Y | id_collision |
| T0235 | plan | 0 | N | N | legacy_no_gate |
| T0236 | plan | 0 | N | N | legacy_no_gate |
| T0237 | plan | 0 | N | N | legacy_no_gate |
| T0244 | archive | 4 | Y | Y | id_collision |
| T0244 | archive | 4 | Y | Y | id_collision |
| T0246 | archive | 4 | Y | Y | id_collision |
| T0246 | archive | 4 | Y | Y | id_collision |
| T0247 | archive | 4 | Y | Y | id_collision |
| T0247 | archive | 4 | Y | Y | id_collision |
| T0248 | check | 2 | N | Y | id_collision; gate_incomplete:no-verdict |
| T0248 | archive | 4 | Y | Y | id_collision |
| T0249 | archive | 4 | Y | Y | id_collision |
| T0249 | archive | 4 | Y | Y | id_collision |
| T0250 | plan | 0 | N | N | id_collision; legacy_no_gate |
| T0250 | check | 2 | Y | Y | id_collision |
| T0251 | archive | 4 | Y | Y | id_collision |
| T0251 | archive | 4 | Y | Y | id_collision |
| T0252 | do | 1 | N | Y | id_collision |
| T0252 | archive | 3 | Y | Y | id_collision |
| T0253 | plan | 0 | N | N | legacy_no_gate |
| T0254 | plan | 0 | N | N | legacy_no_gate |
| T0255 | plan | 0 | N | N | legacy_no_gate |
| T0256 | plan | 0 | N | N | legacy_no_gate |
| T0257 | plan | 0 | N | N | legacy_no_gate |
| T0258 | plan | 0 | N | N | legacy_no_gate |
| T0259 | plan | 0 | N | N | legacy_no_gate |
| T0263 | plan | 0 | N | Y | legacy_no_gate |

## 结论

- 真违规候选（gate_incomplete）: 6 个；机制前任务（legacy_no_gate）: 29 个。
- 门禁拦截留痕（rejected receipts）: 0 次（transition 拒绝现可计数可审计）。
