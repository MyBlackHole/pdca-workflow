# ID 撞车清理处置报告（T0274）

## 背景

`task_identity.py` 统一身份入口引入前，历史任务重复分配 task_id。doctor `identity.duplicate_task_ids` 报告 23 组撞车，每组同一 task_id 被 2-3 个真实独立任务占用。身份唯一性阻断体系健康度（valid=False）。

## 裁决原则

**主流方保留原 ID**，非主流方分配新 ID（T0275-T0286）：

1. 被其他任务作为 parent 引用（任务树主干）→ 保留原 ID。
2. 无引用时，record 格式规范（`Txxxx-slug`）优先；旧格式（`Rxxxx` 或裸 `Txxxx`）重分配。
3. 其余按创建时间早者保留。

## 12 组可处置重分配明细

| 重分配方 | 新 ID | 目录 | 原 record | 新 record | 引用改动 |
|---|---|---|---|---|---|
| T0142 0729-vmcore-analysis | T0275 | 0729-vmcore-analysis | R0142-vmcore-analysis | T0275-0729-vmcore-analysis | 0 |
| T0163 0731-nbu-dte-enforced-mechanism | T0276 | 0731-nbu-dte-enforced-mechanism | T0163-0731-nbu-dte-enforced-mechanism | T0276-0731-nbu-dte-enforced-mechanism | 0 |
| T0214 0804-cdm-report-center-analyse | T0277 | 0804-cdm-report-center-analyse | T0214-0804-cdm-report-center-analyse | T0277-0804-cdm-report-center-analyse | 2 |
| T0215 0804-report-subscheme-docs | T0278 | T0278-0804-report-subscheme-docs | T0215-0804-report-subscheme-docs | T0278-0804-report-subscheme-docs | 1 |
| T0217 0804-cdm-data-cli | T0279 | T0279-0804-cdm-data-cli | T0217-0804-cdm-data-cli | T0279-0804-cdm-data-cli | 1 |
| T0224 0808-bwlimit-poc | T0280 | 0808-bwlimit-poc | T0224-0808-bwlimit-poc | T0280-0808-bwlimit-poc | 0 |
| T0225 0807-xtrabackup-incremental-tech | T0281 | 0807-xtrabackup-incremental-tech | T0225 | T0281-0807-xtrabackup-incremental-tech | 0 |
| T0244 0812-rpc-metadata-analysis | T0282 | 0812-rpc-metadata-analysis | R0244-rpc-metadata-analysis | T0282-0812-rpc-metadata-analysis | 0 |
| T0246 0810-backup-gm-transport-encryption | T0283 | T0283-0810-backup-gm-transport-encryption | T0246-0810-backup-gm-transport-encryption | T0283-0810-backup-gm-transport-encryption | 0 |
| T0247 0811-backup-doc-optimize | T0284 | T0284-0811-backup-doc-optimize | T0247-0811-backup-doc-optimize | T0284-0811-backup-doc-optimize | 0 |
| T0249 0812-kernel-nfs-gm-research | T0285 | T0285-0812-kernel-nfs-gm-research | T0249-0812-kernel-nfs-gm-research | T0285-0812-kernel-nfs-gm-research | 0 |
| T0251 0814-oss-xmake-integration | T0286 | 0814-oss-xmake-integration | T0251-0814-oss-xmake-integration | T0286-0814-oss-xmake-integration | 0 |

**目录重命名**：5 个含旧 ID 前缀的目录同步更名（T0215-、T0217-、T0246-、T0247-、T0249- 前缀 → 新 ID 前缀）。

## 上下文感知引用替换（关键设计）

撞车组 T0214 存在 **CDM/报表树 与 RPC 树 纠缠**：两者子任务 parent 均指向 T0214，字符串级替换无法区分归属。按引用者 slug 上下文判定：

- **CDM/报表链特征**（slug 含 report/cdm/collection/deployment/acceptance 且非 rpc/worker）→ 引用指向重分配方，parent 改向 T0277。
- **RPC 链特征**（slug 含 rpc/worker/epoll）→ 引用指向保留方（rpc-epoll T0214），保持原 ID。

应用结果：
- CDM 链子任务 `0804-report-subscheme-docs`（→T0278）、`0804-cdm-data-cli`（→T0279）parent 改向 T0277。
- T0277（cdm）children 中 T0215→T0278、T0217→T0279 同步更新。
- RPC 链 `0804-rpc-epoll-multireactor`（保留 T0215）、`0805-worker-adaptation` 等 parent 保持 T0214 不变。
- 11 组含活跃任务的撞车（DEFERRED_IDS）整组未改写。

## 11 组待办（含活跃任务，跳过）

| 组 ID | 含活跃任务 | 待办原因 |
|---|---|---|
| T0216 | 0805-rpc-epoll-worker-supply-followup（active） | 活跃侧未归档，整组跳过 |
| T0218 | 0806-buf-layer-endianness 等（active） | 同上 |
| T0219 | active | 同上 |
| T0220 | active | 同上 |
| T0221 | active | 同上 |
| T0222 | active（含 T0222-0804-acceptance-perf） | 同上 |
| T0228 | active | 同上 |
| T0229 | active | 同上 |
| T0248 | 0813-lmdb-tree-resume-round62（active） | 同上 |
| T0250 | active | 同上 |
| T0252 | active | 同上 |

待其归档后另立任务处理。

## 验证结果

- doctor `identity.duplicate_task_ids`：**23 → 11 组**（仅剩活跃待办组，AC-5 达标）。
- doctor `identity.event_path_mismatches`：无新增（flow-events `record_id`/`task_id` 同步补全后恢复至既有 5 项基线）。
- `check-disposable`：12 组全部 archive，通过。
- `check-deferred`：11 组全部含活跃任务，通过。
- 幂等性：重复 apply 无二次改写（digest 一致）。
- 新 ID T0275-T0286 与既有 ID 无冲突。
- 引用链无新增悬空引用（既有 T0150→T0151-T0157 遗留除外）。

## flow-events 同步补全

records 目录重命名后，flow-events 内部 `record_id`/`task_id` 字段须同步为新值，否则 doctor `event_path_mismatches` 会新增。已同步 7 组 22 个 flow-events：

| 新记录 | 同步数 |
|---|---|
| T0276-0731-nbu-dte-enforced-mechanism | 16 |
| T0277-0804-cdm-report-center-analyse | 1 |
| T0280-0808-bwlimit-poc | 1 |
| T0281-0807-xtrabackup-incremental-tech | 1 |
| T0282-0812-rpc-metadata-analysis | 1 |
| T0283-0810-backup-gm-transport-encryption | 1 |
| T0286-0814-oss-xmake-integration | 1 |
