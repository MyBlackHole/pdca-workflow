# flow-events record_id 同步补全（T0274 补漏）

records 目录重命名后，flow-events 内部 `record_id`/`task_id` 字段未同步，导致 doctor `event_path_mismatches` 从 5 项新增至 27 项。补全 `_sync_record_flow_events` 后同步 7 组 22 个 flow-events，`event_path_mismatches` 恢复至 5 项基线（T0252 既有遗留）。

- T0276-0731-nbu-dte-enforced-mechanism: 16
- T0277-0804-cdm-report-center-analyse: 1
- T0280-0808-bwlimit-poc: 1
- T0281-0807-xtrabackup-incremental-tech: 1
- T0282-0812-rpc-metadata-analysis: 1
- T0283-0810-backup-gm-transport-encryption: 1
- T0286-0814-oss-xmake-integration: 1

doctor 验证：event_path_mismatches = 5（仅 T0252 既有），无新增回归。
