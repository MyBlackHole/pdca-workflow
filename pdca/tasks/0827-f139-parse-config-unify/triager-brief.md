# Triage Brief — 0827-f139-parse-config-unify

- **category**: enhancement
- **scenario_type**: development
- **summary**: F-139 提交审查发现 parse_config 被 init_config / set_rpc_init_config / fsdeamon|fsclient_init_config 各自调用，运行期 fs_source/backup_helper/unix_server 还会再次调用，导致同一全局单例 _kv_store 被反复覆盖解析；且各模块 init 均携 config_file 参数自行解析。
- **current behavior**: 每个模块 init 与运行期 reload 都无条件调用 parse_config 重新解析并覆盖全局 _kv_store；各模块 init 均接收 config_file 参数用于自行解析。带来重复 IO、潜在 TOCTOU 不一致、调用关系不清晰。
- **desired behavior**: parse_config 仅由 init_config 调用；init_config 接收 config_file 加载 store；各模块 init 改为无参、仅从 store 读取；运行期重载统一走 init_config。
- **key interfaces**: rdb-config 解析与参数注册表（sec_get_*）、各模块 init 入口、运行期 reload 路径。
- **acceptance criteria**:
  - 运行 init_config + 各模块 init 后，全局 store 内容与单次 init_config 后一致（无重复解析副作用）
  - 各模块 init 签名不再含 config_file 参数，且内部不再调用 parse_config
  - 重载走 init_config 后 store 与模块参数反映最新文件
  - 配置缺失时各模块仍保留默认且行为与重构前一致
- **out of scope**: 全局 store 在 reload 与并发读取间的无锁竞态（独立问题，另立 task）。
- **information gaps**: 各模块 reload 后模块结构（各 *_config 全局）的刷新机制需在 Do 阶段细化。
- **dedup results**: 与 0826-cleanup-rdb-config-deadcode(T3984) 互补（其将双缓冲简化为单例 store，未做 parse 调用去重）；与 0823-rdbcfg-config-audit 审计任务独立。无重复。
- **recommended next steps**: 写完整 PRD 并拆解子任务；Do 阶段先改 rdb-config.c 收敛 parse_config 调用面，再适配 rpc/fs-backup 调用方去参，最后补行为测试。
