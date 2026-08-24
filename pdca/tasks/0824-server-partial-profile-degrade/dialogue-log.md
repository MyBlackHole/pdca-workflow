## Do → Check (2026-08-24)

- 实现：init_server 尽力收集语义（失败 profile 跳过+日志，slot_count==0 才整体失败）；保守实现保持直接写目标槽（tmp_slot 中转版曾致 mtls_handshake 行为漂移，已弃用）。
- 插曲：git checkout 误回滚测试文件（应先 add）；sed 双点误替换破损 RUN_TEST 行，均已修复。
- 验证：tls_cert_test 全绿含 partial_degrade；回归绿；实机 setsid 重启后 plain only 消失、国密握手成功。
## Check → Act (2026-08-24) verdict=confirmed
