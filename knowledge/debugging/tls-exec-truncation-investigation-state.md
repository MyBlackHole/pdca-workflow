# TLS exec stdin 偶发截断——调查状态与已知事实（T0347 输入）

来源：T0345（2026-08-22，partial，跟进任务 T0347 承接修复）

## 已确证事实

1. **现象**：TLS exec 大流量 stdin（32MiB）偶发短少 8KB~1.9MB（随机量级），远端 wc 提前收到 EOF 并输出截断计数。plain（非 TLS）模式 15/15 稳定。
2. **agent 接收侧无丢弃**：DIAG 显示 FT_EOF 到达时 stdin_queue 残留=0；exec_close_stdin 全部 residual=0。agent 把收到的字节全部写入 child 管道。
3. **client Reactor 发送侧提前 EOF**：决定性证据 `DIAGRX client eof sent=61440`（应发 32MiB）时 agent received 同步短少。sent=61440 ≈ 初始 credit 量级，疑第二窗口更新到达前泵误判流终结。
4. **排除项**：端口协作锁、证书路径冲突、agent 队列丢弃、socket 层（writev_all 为全写语义）。

## 关键代码位置

- client 泵：`client_exec_reactor.cpp` 的 `reactor_exec_try_pump`（stdin_credit / stdin_eof_pending / stdin_eof_sent 状态机）
- agent 接收：`agent_exec_runtime.cpp` 1115 行起 FT_DATA FF_STDIN 入队与 rx_paused 流控
- 复现工具：`tests/tls_exec_stress.sh [BUILD] [MAX_ROUNDS]`（≤5 轮稳定复现，失败现场保留于 TLS_STRESS_LOG）

## 诊断方法（可快速重加）

printf 打点三处：client EOF 发送处累计 sent；agent eof_frame 处累计 received + 队列残留；agent close_stdin 处残留。双端按 exec 实例对齐（注意多实例交错，需 channel-id 关联升级）。

## T0347 修复方向

1. WINDOW_UPDATE 到达时的 stdin 泵唤醒路径审查（credit 刷新后是否重新调度读）
2. `stdin_credit == 0` 且未 EOF 时泵的挂起/恢复语义
3. 验收基线：tls_exec_stress.sh ≥50 轮零截断

## 适用边界

结论仅覆盖 loopback TLS + 32MiB 单向 stdin 场景；full-duplex 与其他流量形态未单独验证。
