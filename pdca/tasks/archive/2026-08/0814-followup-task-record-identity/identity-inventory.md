# Task / Record Identity Inventory

冻结时间：2026-08-14（T0261 Do）

## 汇总

- 扫描到 117 个 task ID。
- 23 个 task ID 对应多个不同 slug；共涉及 47 个不同 slug、49 份物理 `task.json`（其中 2 份是同 slug 的 active/archive 双份文件）。
- 扫描到 5 条 `EVENT_PATH_MISMATCH`，全部属于 task `T0252`：目录身份是 `T0252-0814-inih-hide-symbols`，事件载荷身份是 `T0252`。
- 23 个冲突 ID 中有 22 个没有 event path mismatch。因此 task ID 冲突不是 mismatch 的充分条件，只是会扩大引用歧义。
- 49 份物理 task 中 6 份在冻结时未被 Git 跟踪；其余条目可由 first-add commit 追溯。历史只证明“多个创建批次写入了重复 ID”，不能证明每一份文件由哪个具体命令或操作者创建。

## 创建路径与并发语义

| 路径 | 分配方式 | 锁 / 原子性 | 失败语义 | 判定 |
|---|---|---|---|---|
| `skills/to-tickets/SKILL.md` | 扫描 active + archive 取最大数字后加一 | 未规定共享锁；任务与 parent 更新不是一个事务 | 要求同 commit，但没有运行时回滚器 | 并发 scan→create 可复用同一 ID |
| `skills/triage-work/SKILL.md` / Plan 主会话 | 由代理生成 task skeleton | 未引用统一分配器或锁 | 依赖会话自行处理 | 可与其他会话竞态 |
| `flows/flow-act/SKILL.md` partial 跟进 | 直接创建新任务 | 未引用统一分配器或锁 | 未定义跨文件事务 | 可与其他会话竞态 |
| `scripts/flow_issues.py::promote_candidate` | `_next_task_id()` 扫描后加一 | `_promotion_lock()` 覆盖去重、分配和创建；文件用 `O_EXCL` | 同 slug 冲突拒绝；部分创建会清理目录 | 当前唯一有可执行并发保护的创建路径 |

## 冲突明细

| task ID | slug | created_at | path | Git first-add |
|---|---|---|---|---|
| T0142 | 0728-clean-invalid-active-history | 2026-07-28T21:31:45+08:00 | `pdca/tasks/archive/2026-07/0728-clean-invalid-active-history/task.json` | 3070ede5067e |
| T0142 | 0729-vmcore-analysis | 2026-07-29T09:30:00+08:00 | `pdca/tasks/archive/2026-07/0729-vmcore-analysis/task.json` | ae5e488da92a |
| T0163 | 0731-nbu-dte-enforced-mechanism | 2026-07-31T11:20:00+08:00 | `pdca/tasks/archive/2026-07/0731-nbu-dte-enforced-mechanism/task.json` | ae5e488da92a |
| T0163 | 0731-pg-mysql-parquet-poc | 2026-07-31T10:13:00+08:00 | `pdca/tasks/archive/2026-07/0731-pg-mysql-parquet-poc/task.json` | ae5e488da92a |
| T0214 | 0804-cdm-report-center-analyse | 2026-08-04T16:36:00+08:00 | `pdca/tasks/active/0804-cdm-report-center-analyse/task.json` | ae5e488da92a |
| T0214 | 0804-cdm-report-center-analyse | 2026-08-04T16:36:00+08:00 | `pdca/tasks/archive/2026-08/0804-cdm-report-center-analyse/task.json` | 0ebc7ce11236 |
| T0214 | 0804-rpc-epoll-industrial-align | 2026-08-04T08:11:59+08:00 | `pdca/tasks/archive/2026-08/T0214-0804-rpc-epoll-industrial-align/task.json` | 95c15e9b8e95 |
| T0215 | 0804-report-subscheme-docs | 2026-08-04T16:55:00+08:00 | `pdca/tasks/active/T0215-0804-report-subscheme-docs/task.json` | ae5e488da92a |
| T0215 | 0804-report-subscheme-docs | 2026-08-04T16:55:00+08:00 | `pdca/tasks/archive/2026-08/T0215-0804-report-subscheme-docs/task.json` | 5a9a42ae6bca |
| T0215 | 0804-rpc-epoll-multireactor | 2026-08-04T21:00:00+08:00 | `pdca/tasks/archive/2026-08/T0215-0804-rpc-epoll-multireactor/task.json` | 2de6f66c51f9 |
| T0216 | 0805-rpc-epoll-worker-supply-followup | 2026-08-05T08:17:32+08:00 | `pdca/tasks/active/0805-rpc-epoll-worker-supply-followup/task.json` | ff28a791e69a |
| T0216 | 0804-report-db-adapter | 2026-08-04T16:55:00+08:00 | `pdca/tasks/archive/2026-08/T0216-0804-report-db-adapter/task.json` | 680c4851d34e |
| T0217 | 0805-rpc-serialization-hardening | 2026-08-05T00:00:00+08:00 | `pdca/tasks/archive/2026-08/0805-rpc-serialization-hardening/task.json` | b8934e4d14db |
| T0217 | 0804-cdm-data-cli | 2026-08-04T16:55:00+08:00 | `pdca/tasks/archive/2026-08/T0217-0804-cdm-data-cli/task.json` | 843a1258ff2b |
| T0218 | 0806-buf-layer-endianness | 2026-08-06T07:56:29.478481+08:00 | `pdca/tasks/active/0806-buf-layer-endianness/task.json` | 3e4618c46c22 |
| T0218 | 0808-backup-server-architecture | 2026-08-08T09:30:00+08:00 | `pdca/tasks/active/0808-backup-server-architecture/task.json` | untracked |
| T0218 | 0804-collection-service | 2026-08-04T16:55:00+08:00 | `pdca/tasks/archive/2026-08/T0218-0804-collection-service/task.json` | 10b42b7ecedd |
| T0219 | 0806-rpc-arm-interop-verify | 2026-08-06T07:57:07.089684+08:00 | `pdca/tasks/active/0806-rpc-arm-interop-verify/task.json` | 3e4618c46c22 |
| T0219 | 0804-report-web | 2026-08-04T16:55:00+08:00 | `pdca/tasks/archive/2026-08/T0219-0804-report-web/task.json` | 894dbab3d51e |
| T0220 | 0806-rpc-benchmark-review | 2026-08-06T07:57:07.089684+08:00 | `pdca/tasks/active/0806-rpc-benchmark-review/task.json` | 3e4618c46c22 |
| T0220 | 0804-report-templates-query-export | 2026-08-04T16:55:00+08:00 | `pdca/tasks/archive/2026-08/T0220-0804-report-templates-query-export/task.json` | 13485626d9c1 |
| T0221 | 0806-aio-speed-link-fix | 2026-08-06T07:57:07.089684+08:00 | `pdca/tasks/active/0806-aio-speed-link-fix/task.json` | 3e4618c46c22 |
| T0221 | 0804-deployment-install | 2026-08-04T16:55:00+08:00 | `pdca/tasks/archive/2026-08/T0221-0804-deployment-install/task.json` | 42e50ff16eac |
| T0222 | 0806-epoll-business-callback-fsm | 2026-08-06T08:05:18.313773+08:00 | `pdca/tasks/active/0806-epoll-business-callback-fsm/task.json` | 56cd1c34b9ad |
| T0222 | 0804-acceptance-perf | 2026-08-04T16:55:00+08:00 | `pdca/tasks/active/T0222-0804-acceptance-perf/task.json` | ae5e488da92a |
| T0224 | 0808-bwlimit-poc | 2026-08-08T17:41:00+08:00 | `pdca/tasks/archive/2026-08/0808-bwlimit-poc/task.json` | b6b51f3f8a2a |
| T0224 | 0804-async-export | 2026-08-06T12:06:00+08:00 | `pdca/tasks/archive/2026-08/T0224-0804-async-export/task.json` | 804f81840328 |
| T0225 | 0807-xtrabackup-incremental-tech | 2026-08-07T10:20:00+08:00 | `pdca/tasks/archive/2026-08/0807-xtrabackup-incremental-tech/task.json` | d9f7ab6e101a |
| T0225 | 0808-core-tech-poc | 2026-08-08T18:30:00+08:00 | `pdca/tasks/archive/2026-08/0808-core-tech-poc/task.json` | 5dfc8715d8b4 |
| T0228 | 0808-seda-pipeline | 2026-08-08T18:20:00+08:00 | `pdca/tasks/active/0808-seda-pipeline/task.json` | untracked |
| T0228 | 0807-roach-gm-encrypt-support | 2026-08-07T14:49:00+08:00 | `pdca/tasks/archive/2026-08/0807-roach-gm-encrypt-support/task.json` | f86aadab608d |
| T0229 | 0808-core-tech-poc-2 | 2026-08-08T20:00:00+08:00 | `pdca/tasks/active/0808-core-tech-poc-2/task.json` | untracked |
| T0229 | 0810-ob-backup-gm-encrypt-verify | 2026-08-10T10:33:17+08:00 | `pdca/tasks/archive/2026-08/T0229-0810-ob-backup-gm-encrypt-verify/task.json` | f86aadab608d |
| T0244 | 0809-pdca-flow-impl-review | 2026-08-09T17:50:00+08:00 | `pdca/tasks/archive/2026-08/0809-pdca-flow-impl-review/task.json` | f1876b6c36cd |
| T0244 | 0812-rpc-metadata-analysis | 2026-08-12T13:51:43+08:00 | `pdca/tasks/archive/2026-08/0812-rpc-metadata-analysis/task.json` | dd89df7df72c |
| T0246 | 0813-small-writer-pool | 2026-08-13T21:02:59+08:00 | `pdca/tasks/archive/2026-08/0813-small-writer-pool/task.json` | c85151da49b2 |
| T0246 | 0810-backup-gm-transport-encryption | 2026-08-10T14:18:25+08:00 | `pdca/tasks/archive/2026-08/T0246-0810-backup-gm-transport-encryption/task.json` | 280bb17d285a |
| T0247 | 0813-small-writer-pool-round61 | 2026-08-13T22:02:34+08:00 | `pdca/tasks/archive/2026-08/0813-small-writer-pool-round61/task.json` | 68221274265a |
| T0247 | 0811-backup-doc-optimize | 2026-08-11T12:27:10+08:00 | `pdca/tasks/archive/2026-08/T0247-0811-backup-doc-optimize/task.json` | cec44d671049 |
| T0248 | 0813-lmdb-tree-resume-round62 | 2026-08-13T22:40:03+08:00 | `pdca/tasks/0813-lmdb-tree-resume-round62/task.json` | untracked |
| T0248 | 0812-openssh-src-unpack | 2026-08-12T14:30:15+08:00 | `pdca/tasks/archive/2026-08/T0248-0812-openssh-src-unpack/task.json` | 0d8b01c6bc31 |
| T0249 | 0814-lmdb-no-mmap-round63 | 2026-08-14T06:34:26+08:00 | `pdca/tasks/archive/2026-08/0814-lmdb-no-mmap-round63/task.json` | f5df4be21c54 |
| T0249 | 0812-kernel-nfs-gm-research | 2026-08-12T15:09:38+08:00 | `pdca/tasks/archive/2026-08/T0249-0812-kernel-nfs-gm-research/task.json` | 5a1709dfc635 |
| T0250 | 0814-lmdb-vl32-followup-round64 | 2026-08-14T06:51:00+08:00 | `pdca/tasks/0814-lmdb-vl32-followup-round64/task.json` | 338e2a96eb67 |
| T0250 | 0813-mysql-parquet-physical | 2026-08-13T00:00:00+08:00 | `pdca/tasks/active/0813-mysql-parquet-physical/task.json` | dd89df7df72c |
| T0251 | 0814-oss-xmake-integration | 2026-08-14T10:00:00+08:00 | `pdca/tasks/archive/2026-08/0814-oss-xmake-integration/task.json` | ccb860efe1af |
| T0251 | 0814-production-observability-round65 | 2026-08-14T06:56:00+08:00 | `pdca/tasks/archive/2026-08/0814-production-observability-round65/task.json` | untracked |
| T0252 | 0814-tree-checkpoint-paged-round66 | 2026-08-14T07:26:02+08:00 | `pdca/tasks/0814-tree-checkpoint-paged-round66/task.json` | untracked |
| T0252 | 0814-inih-hide-symbols | 2026-08-14T10:45:37.630983+08:00 | `pdca/tasks/archive/2026-08/0814-inih-hide-symbols/task.json` | 13c8d238e219 |

## mismatch 明细

5 条事件都发生于 `2026-08-14T11:06:56+08:00`，issue code 分别是：

- `RECORD_MISSING`
- `CONVERGENCE_MAP_MISSING`
- `AC_COVERAGE_UNVERIFIABLE`
- `ACCEPTANCE_CRITERIA_MISSING`
- `EVIDENCE_INTEGRITY_UNVERIFIABLE`

同一 record 后续 16 条事件从 `11:07:19+08:00` 起使用完整 `record_id=T0252-0814-inih-hide-symbols`。Git commit `ccb860efe1af` 首次加入该 record 时，21 条事件已经共同位于完整 record 目录；commit `13c8d238e219` 随后只归档 task。当前历史没有保存移动命令或执行者，因此“发生过目录归并”有文件状态支持，“由哪个工具移动”保持 inconclusive。
