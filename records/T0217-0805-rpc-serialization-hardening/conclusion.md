---
schema: pdca.asset/v1
id: T0217-0805-rpc-serialization-hardening
phase: check
source_ids: [rt_inplace_v, rt_ac3_v, rpc_sep_v, le_residue_v, frame_validation_v, scp_stream_v, misc_le_test_v, io_common_v, protocol_roundtrip_rt, stream_blocks_v, io_partial_v, convergence-map-v3]
---

## 上下文

T0217 针对 T0216 审计发现的 rpc 协议序列化性能与跨机互通问题：
（1）host/net 双缓冲导致大块传输 data memcpy 冗余复制；（2）htonl/ntohl
大端转换在 x86 小端主机上产生额外字节交换开销；（3）协议版本未协商，
新旧节点混跑存在解析错乱风险。目标：消息体就地化 + 全链路小端字节序 +
版本提升，x86/ARM 跨机互通为硬需求。验收标准 10 条（AC-1~AC-10，含 AC-1b）。

## 假设与结果

| AC | 假设 | 验证结果 | 判定 |
|----|------|---------|------|
| AC-1 | 全部 msg_*_ntoh 就地化，签名 (msg, net_len)，就地转换+校验 | protocol_roundtrip_inplace：msg_base/msg_cmd/scp_download/download_block 等 14 个消息就地化往返逐字段字节级一致 | 通过 |
| AC-1b | 全部 msg_*_hton 就地化（单参），常规路径无 data memcpy | 同上：hton 单参就地，wire 往返无跨缓冲复制（仅 file_stat/dir_tree 内部字段 memcpy 属合理例外） | 通过 |
| AC-2 | 超长变长字段被拒绝，无越界读写 | io_partial 超限帧（8MB+1）分配前拒绝 RPC_ERR_FRAME_TOO_LARGE；protocol_roundtrip 新增 cmd_len 超长 + 截断 net_len 负向测试均 RPC_ERR_BAD_FRAME | 通过 |
| AC-3 | 服务端分发层校验 uiLEN ≤ 实际读入字节，不符拒绝 | process_single_request 用 msg_base_ntoh(实际读入 bytes) 预检 + 各消息 ntoh 传 msg_len 校验；rpc_server_epoll_integration 65 PASS 0 fail | 通过 |
| AC-4 | 协议层 htonl/ntohl/htonll/ntohll 全替换小端，无残留 | 静态扫描 rpc-protocol.cpp/rpc-msg.c/libs-rpc-net-protocol.c 大端调用 0 处；misc_le_test 验证 LE 工具 | 通过 |
| AC-5 | 帧头解析/组装切小端，magic 'FSBC' 跨机校验正确 | frame_validation：magic/version/total_len 上限/截断全过；magic 字节序无关 memcmp + 发送端 memcpy 直写对称 | 通过 |
| AC-6 | 错误帧 body 随协议切小端，buf 层不改动 | scp_stream 509 PASS（STREAM INIT 用 buf_put_u32_le）；misc_le_test 全过 | 通过 |
| AC-7 | rpc-io 长度前缀、rpc-common 目录树打包同步小端 | io_common_v diff 证据：rpc_recv le32toh / rpc_send htole32 对称，dir_tree 打包 htole32 | 通过 |
| AC-8 | RPC_FRAME_VERSION 提升至 3，混跑返回 PROTO_VERSION | frame_validation test_bad_version 实测 RPC_ERR_PROTO_VERSION | 通过 |
| AC-9 | protocol_roundtrip 全过（新小端 wire 字节级一致） | protocol_roundtrip all tests passed（含新增负向测试） | 通过 |
| AC-10 | 全量回归通过（含既有 rpc/tests 基线） | stream_blocks/scp_stream/rpc_server_epoll_integration 全过；aio-speed 链接失败为 HEAD 预存（T0212 遗留 do_is_dir/do_batch_list_dir_tree 无定义），与本任务无关 | 通过（含既有环境/遗留说明） |

## 分析

1. **帧头 magic 是字节序列，必须字节序无关直写**：初版实现用 put_u32_le(hdr,
   RPC_FRAME_MAGIC) 数值化写入，小端主机写出 "CBSF"，导致所有
   rpc_recv_frame/rpc_conn_recv_msg 返回 RPC_ERR_BAD_FRAME(-4)（rpc_server_
   epoll_integration/scp_stream 大面积失败暴露）。修复为 memcpy(hdr, "FSBC", 4)
   与解析侧 memcmp(data, "FSBC", 4) 对称。这是本任务最重要的工程教训：
   字节序列常量（magic/signature）不得参与字节序转换，应按字节数组直写。

2. **就地化测试策略**：protocol_roundtrip 覆盖 14 个消息的 host→hton(就地)→
   copy→ntoh(就地)→逐字段断言，net_len 用 le32toh(back->uiLEN) 取回，保证
   hton 后 uiLEN 已覆写为 wire 序的语义被测试锁定。

3. **变长字段越界防护双保险**：帧级（rpc_frame_parse 校验 total_len 上限
   8MB 在分配前拦截）+ 字段级（rpc_var_check 用 net_len - offsetof 界定
   wire 可用长度，len > avail 拒绝）。io_partial 覆盖帧级，protocol_roundtrip
   新增用例覆盖字段级。

4. **AC-3 判定依据**：epoll 路径 process_single_request 读入后先
   msg_base_ntoh(msg_base_net, bytes) 用实际读入字节数校验再分发，各消息
   ntoh 传 msg_len(=bytes)；测试服务端 scp_stream server_thread 需手动补
   conn.msg_len=n（读裸请求后设置），这是测试与服务端路径的行为对齐点。

5. **buf 层大端残留（用户已决策）**：rpc_conn_* 高层封装（conn->msgw/msgr）
   的 84 处 buf_put_u32/buf_get_u32 按 AC-6 设计保持大端自洽不改，收发对称，
   本机 download/upload_fileats 等测试覆盖该路径全过。协议层已全部切小端。
   用户决策：**纳入后续任务处理**，后续版本统一 buf 层字节序（见下一轮建议）。

6. **环境依赖失败的甄别**：readdir/mkdir/readlink/symlink/pwrite/download_fileat
   等测试失败均因 /opt/aio、/tmp 源文件缺失（HEAD 同环境同样失败），
   dir_tree 响应超时同为环境问题，均非本任务回归。对比基线的临时 worktree
   （headcheck/headtest/dirhead）已验证并全部移除。

## 失败原因（仅 rejected/partial）

N/A（用户 verdict 待定，当前所有 AC 判定通过）

## 适用边界

- 就地化覆盖 msg_* 系列消息体；file_stat/dir_tree 的 struct stat 打包
  仍跨缓冲（struct stat 无法就地，合理例外）。
- buf 层 rpc_conn_* 高层 API 仍为大端，仅协议层（rpc-protocol/rpc-msg）
  及帧头、STREAM INIT body 为小端。
- 协议版本 3 要求两端同步升级，新旧混跑会被 PROTO_VERSION 拒绝而非错乱。
- 本机为 x86 小端，ARM 互通字节序逻辑正确性由 letoh/htole 宏对称保证，
  未经真实 ARM 节点验证（无硬件条件）。

## 下一轮建议

1. **跟进任务（用户已确认）**：统一 buf 层（rpc_conn_* 高层）字节序，
   buf_put_u32/buf_get_u32 全套切换小端，需与 rdbcomm 共用方协调，
   影响面广（84 处调用 + rdbcomm），建议独立 T 编号排期。
2. ARM 节点实测跨机互通（无本地 ARM 硬件，需集成环境）。
3. T0216 遗留基准复核：bench_download/bench_concurrent 重新测量就地化+
   小端后的吞吐/并发（消除 memcpy 与 bswap 开销后的净收益量化）。
4. aio-speed 链接问题（do_is_dir/do_batch_list_dir_tree 声明无定义）
   为 T0212 遗留，建议独立跟进补齐实现。
