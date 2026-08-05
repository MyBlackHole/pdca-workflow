# T0217 Handoff

## 当前状态

T0217（rpc 序列化补强：消息体就地化 + 小端字节序）PDCA 已走完 Do→Check
（verdict=confirmed，10 项 AC 全过）→ Act 阶段：Ac0-Ac5 已完成（Grill 确认
跳过知识沉淀、disposition=task_only 已记录、跟进项已登记 clarifications.jsonl）。
剩余 Ac6~Ac8（journal/提交/归档）待收尾。

## 未完成事项

- flow-act Ac6（journal）/ Ac7（git 提交）/ Ac8（归档）收尾
- 代码提交 c4549f4a 已完成于 release 仓库（6.1.1.0-release 分支）
- 跟进项已登记（详见 clarifications.jsonl，source=followup）：
  - 跟进-1: buf 层(rpc_conn_* 高层) 84 处 buf_put_u32/get_u32 字节序统一切小端（需协调 rdbcomm 共用方）
  - 跟进-2: ARM 节点实测跨机互通
  - 跟进-3: T0216 遗留基准复核（bench_download/bench_concurrent 量化就地化+小端净收益）
  - 跟进-4: aio-speed 链接问题（do_is_dir/do_batch_list_dir_tree 声明无定义，T0212 遗留）

## 已知约束

- 帧头 magic 'FSBC' 是字节序列常量，必须字节序无关直写（memcpy），
  不得用 put_u32_le/put_u32 数值化（初版写出 CBSF 导致全线 BAD_FRAME）
- 就地化覆盖 msg_* 消息体；file_stat/dir_tree 的 struct stat 打包仍跨缓冲（合理例外）
- buf 层 rpc_conn_* 高层 API 仍为大端（AC-6 设计不改动），仅协议层+帧头+STREAM INIT body 为小端
- 协议版本 3 要求两端同步升级，新旧混跑返回 RPC_ERR_PROTO_VERSION 而非错乱
- LSP 报 rpc-epoll.h/rpc.h not found 属 include 路径误报，以 xmake build 实际编译为准
- xmake build 只接受单 target；aio-speed 链接失败为 HEAD 预存问题（非 T0217 引入）

## 推荐的下一步

1. 完成 T0217 Ac6-Ac8 归档收尾
2. 归档后创建跟进任务（走 Plan 流程）：跟进-1 buf 层字节序统一优先级最高
   （用户已决策纳入后续任务），其次跟进-4 aio-speed 链接补齐

## 关键上下文文件列表

- ADR-0015: `docs/adr/ADR-0015-rpc-serialization-little-endian-inplace.md`（如已生成）
- 结论: `records/T0217-0805-rpc-serialization-hardening/conclusion.md`
- 证据: `records/T0217-0805-rpc-serialization-hardening/evidence/manifest.jsonl`（11 项 + convergence-map-v3）
- 实现: release 仓库 rpc/（rpc-protocol/rpc-msg/rpc-io/rpc-common/rpc-server/rpc-client）、libs/（misc LE 工具、rpc-net-protocol）
- 测试: rpc/tests/（protocol_roundtrip/frame_validation/io_partial/stream_blocks/scp_stream/rpc_server_epoll_integration/dir_tree）、libs/tests/misc_le_test.c
- 提交: `c4549f4a`（release 仓库 6.1.1.0-release 分支，26 文件）

## suggested skills

- flow-act、advance-phase（归档收尾）
- feature-commit-format（跟进任务提交时）
- test-driven-development（跟进任务 buf 层字节序统一时）
