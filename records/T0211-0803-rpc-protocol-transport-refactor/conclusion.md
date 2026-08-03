---
schema: pdca.asset/v1
id: T0211-0803-rpc-protocol-transport-refactor
phase: check
source_ids: [ev-frame-validation, ev-overlimit-reject, ev-roundtrip, ev-io-partial, ev-frame-flags, ev-max-conn-v2, ev-epoll-heartbeat-v2, ev-regression-baseline, ev-naming, ev-full-regression, ev-bench-throughput, ev-stream-sequence, ev-stream-memory-peak, ev-queue-full-v2, ev-init-timeout-ms, ev-heartbeat-pingpong, ev-error-code-detail]
---

## 上下文

rpc 协议与传输层工业级重构（T0211）：16B 帧头协议、流式块传输、应用层心跳、
标准化错误码、单 Reactor + 有界线程池调度层。Do 阶段按 8 模块 TDD 推进，
本次会话完成模块 ①-⑥ + ⑧（帧头/序列化/传输/流帧/心跳错误码/epoll 调度/吞吐基准）。

## 假设与结果

| 假设 | 结果 |
|------|------|
| 帧头校验顺序（magic→version→total_len 上限，先校验后分配）| 成立：frame_validation 13 断言，超限帧/坏 magic/版本不匹配均被拒 |
| 流帧 INIT→DATA→END + 4MB 块内存峰值 | 成立：stream_blocks 15 断言，peak ≤ block_size+64 |
| 错误帧原语（RESPONSE+ERROR flag）| 成立：heart_beat 17 断言，错误码+详情字符串往返一致 |
| epoll 调度：有界队列/连接上限/连接所有权/优雅关闭 | 成立：conn_limit 30 断言（含队列满 QUEUE_FULL、第 3 连接拒收、归还复用、Stop 清理）|
| 心跳 Ping/Pong + 无响应断开 | 成立：帧级往返 + 2×interval 断开断言 |
| 吞吐基线 | 成立：1GB 流式 514 MB/s（socketpair 本机）|

## 分析

1. **核心交付**：基础设施层全部就绪并有测试锁定。rpc-epoll 调度层实现 prd
   ADR-0011 全部语义（EPOLLONESHOT 连接所有权转移、队列容量=max_conn、
   max_conn 默认 8、心跳 tick 驱动 epoll_wait timeout）。
2. **TDD 意外收获**：`buf_get_string_direct` 的 size_t 输出参数以 uint32 接收
   造成栈溢出（release 优化下暴露 segfault，debug 不崩）——验证了 release
   模式回归测试的必要性；rpc-protocol.cpp:283 ntohl 误用 htonl 已修复。
3. **证据链**：16 项 test evidence + convergence-map 验证 valid: true，
   17 个 AC 全部有非 map 证据覆盖；全量回归 14/15（dir_utils_dir_copy_test
   为既有环境问题，改动前已失败，git stash 验证）。
4. **已提交**：35c5d376（模块①-⑥）、30d443fc（bench）、6eb82bde（AC-7 增强）。

## 失败原因

无（不适用）。

## 适用边界

1. **模块⑦业务流式化未做**：do_scp_upload/do_scp_download 仍走旧消息格式
   （512KB 块 + msg_scp_upload_t）。流帧原语已就绪但生产路径未接入；
   AC-15 的"服务端超时执行返回 RPC_ERR_TIMEOUT"依赖业务接入 INIT timeout_ms。
2. **AC-11 对比基准缺失**：无重构前基准数据，514 MB/s 仅为协议原语层新基线，
   供未来对比。
3. **AC-16 心跳断开语义**：断开阈值 2×interval 为实现选择，未在 prd 明确。
4. 下载路径为客户端拉模式状态机（opt_type open/read/close），流式化改造
   需独立会话，涉及断点续传回归。
5. 调度层（rpc-epoll）已独立验证，但 rpc-server.cpp 现有 RPCServiceThread
   尚未迁移到 rpc-epoll（thread-per-conn 仍在使用）。

## 下一轮建议

1. 模块⑦：do_scp_upload/download → STREAM 帧序列（客户端/服务端成对改造），
   完成后补 AC-15 服务端超时执行测试 + 业务层吞吐对比 AC-11。
2. rpc-server.cpp 迁移到 rpc-epoll 调度层（替换 thread-per-conn），
   以 max_conn/有界队列约束生产路径。
3. 既有 dir_utils_dir_copy_test 环境问题另立任务排查。
