# Triage Brief — 0825-rpc-net-time-test-fix

- **category**: bug
- **scenario_type**: bugfix
- **summary**: rpc_net_time_test 伪服务端按旧无前缀协议编写，与恢复后的 libs/rpc-net.c（4B 长度前缀+body，与服务端 rpc_send_io 一致）不匹配导致测试失败。
- **current behavior**: xmake run rpc_net_time_test 失败 status=512（伪服务端 _exit(2) 请求校验不过）；负路径用例"错误 mt 必拒"与恢复实现（只查 uiResult）语义冲突。
- **desired behavior**: 测试适配真实分帧协议；负路径改为 uiResult≠0 业务失败被拒；全绿。
- **key interfaces**: libs/rpc-net.c rpc_send/rpc_recv 分帧（4B htonl 前缀）；msg_get_time_resp_t 布局（uiMT/uiLEN/uiResult/timestamp）。
- **acceptance criteria**:
  - 运行 xmake run -D rpc_net_time_test 输出 PASS 且退出码 0。
  - grep 确认测试含 htonl(sizeof) 前缀收发、无直读直写残留。
  - e2e 场景矩阵 keygen 相关场景通过（恢复实现与真实服务端兼容）。
- **out of scope**: 给 rpc_get_time 加 uiMT 校验（属实现强化，另立任务）；改动 rpc-net.c。
- **information gaps**: 无。
- **dedup results**: 无同主题任务；T0353 为该测试初建任务。
- **recommended next steps**: 小任务直接执行：改 fake_server → 跑测试 → e2e 回归 → 提交。
