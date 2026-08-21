# AC-9 测试套件回归汇总 (2026-08-22)

## 通过项
- 编译型测试: metadata-scan / unit / exec-process / client-resource-lock / work-pool-init / reactor-group-start / signal-safe-errno / reactor_connect 全部 PASS
- 集成 shell 测试: integration / tree / catalog / backup_batching / catalog_safety / dirty_incremental / dirty_journal(+sparse) / tree_fence_pipeline / tree_dir_final_pipeline / durability_fault_injection / prepared_receipt_durability / final_only_replay_durability / catalog_restore / catalog_verify / directory_resume / directory_cursor / production(+readiness phase1-3) / agent_reactor_wiring / system_rpc / protocol_version / plain_ingress / plain_control_yield / exec_admission / plain_exec_event_pump / plain_exec_shared_reactor / plain_exec_shared_rx / event_backend / data_lane / callback_reactor / backup_observe(+diagnose) / backup_result_identity / immutable_ephemeral_state — 全部 PASS
- TLS 变体: tls_reactor_state_machine / catalog_tls / dirty_incremental_tls / directory_resume_tls — 全部 PASS
- CMake ctest 目标全部构建成功

## 存量失败甄别(HEAD 复现,与本次改动无关)
1. style_check 行数规则 x4: backup_agent 807/650、backupctl 2570/1800、agent_audit 268/135、client_resource_lock 193/190(init 提交即失配)
2. p1_closure_source_regression.sh: 2 个 grep 断言在 HEAD 即不命中
3. tree_small_metadata_order_integration.sh: 测试清理阶段 rm 只读目录报权限错误(HEAD 同样失败)
4. Makefile test 目标引用 2 个不存在的脚本(session_pool/plain_session_elastic_pidfd)

## 结论
本次重构未引入任何新测试失败;所有可运行测试通过。

## 补充: CMake ctest 全量运行 (2026-08-22)
120 项测试: 117 Passed / 3 Failed。
失败项均为存量问题(HEAD 同样失败): p1_closure_source_regression / tree_small_metadata_order_integration / style_check(行数规则)。
本次重构引入的新增失败: 0。
