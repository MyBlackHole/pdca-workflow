---
schema: pdca.asset/v1
id: T0212-0803-rpc-scp-stream-migration
phase: check
source_ids: [scp-stream-full-suite, scp-download-roundtrip, scp-meta-preserved, scp-switch-combos, scp-link-upload, scp-stream-timeout, scp-halfwrite-cleanup, full-regression, scp-throughput, ac10-old-types-grep]
---

## 上下文

SCP 业务流式化（T0212，承接 T0211 帧协议+流式块传输）：do_scp_upload/do_scp_download
迁移到 STREAM INIT/DATA/END 帧序列，删除旧 msg_scp_upload_t 系列消息类型，
协议版本号 1→2（ADR-0012 破坏性替换，无兼容期）。

## 假设与结果

| 假设 | 结果 |
|------|------|
| 上传流式化：64MB 经 STREAM 帧序列落盘 sha 一致 | 成立：64MB 往返内容+大小一致 |
| 下载流式化：服务端 push STREAM，客户端解帧落盘一致 | 成立：64MB 往返一致 |
| 元数据往返（mode/atim/mtim/ctim/total_size）| 成立：mode/size/mtime preserved |
| 三开关（压缩/加密/校验和）各自往返一致 | 成立：3 组合上传-下载内容一致 |
| is_link 软链上传路径 | 成立：symlink 创建+target 正确 |
| 服务端超时执行：timeout_ms 到达流未完成 → RPC_ERR_TIMEOUT+清理 | 成立：错误帧 code=-5 + 半写文件清理 |
| 半写清理：DATA 缺 END 中断 → 移除半写文件并报错 | 成立：broken stream 检测+文件清理 |
| 全量回归 | 成立：xmake test RPC 11 target 全过；dir_utils_dir_copy_test 为基线环境问题（T0211 已记录，与本次改动无关）|
| 吞吐 ≥ 400 MB/s | 成立：256MB socketpair 上传 564.9 MB/s |
| 旧类型清除（AC-10）| 成立：msg_scp_upload_t/upload_resp/download_resp 源码零残留，protocol_roundtrip 迁移到 file_stream_meta_t 往返 |

## 分析

1. **交付**：上传/下载双向 STREAM 化完成，10 个 AC 全部有非 map 证据；
   convergence-map-v2 验证 valid: True（0 issues）。
2. **调试中定位的协议陷阱**（均已在实现中闭环）：
   - DATA 帧 payload 无长度前缀，`buf_get_string_direct`（u32 前缀语义）误用会
     使 dlen 错位——统一改为 buf_ptr/buf_len 直读；
   - 文件大小恰为块整数倍（64MB=16×4MB）时最后一块无 END 标志，服务端无限
     等待——客户端 EOF 判定补 END + 服务端 total_size 兜底双保险；
   - 下载 REQUEST 必须保持 msg_scp_download_t 原始序列化（服务端 rpc_recv
     读原始字节入口），帧化 REQUEST 与旧解析不兼容；
   - 下载 INIT 解析须对齐 4 字段（bc/bs/ms/meta_len）。
3. **测试基建修复**：scp_stream 服务端线程下载侧须先 rpc_recv 填 net_buf
   模拟真实分发；rpc_recv_frame 复用 buffer 前必须 buf_clear。
4. **残留风险**：下载客户端侧半写清理未直接测试（旧逻辑保留）；下载 push
   方向无 timeout_ms 语义（沿用旧协议，PRD AC-6 仅覆盖上传方向）。

## 失败原因

无（不适用）。

## 适用边界

- 协议 version 2 与旧版本不兼容，双端需同步升级（ADR-0012 已冻结）。
- 超时执行仅覆盖上传流方向。
- 吞吐基线为本机 socketpair 测试环境。

## 下一轮建议

T0213（rpc-server 迁往 rpc-epoll 调度层）可启动；SCP 下载 push 方向如需
超时语义可后续单独评估。
