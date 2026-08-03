# ADR-0012: SCP 流式化帧协议版本 1 → 2 破坏性替换

- 日期: 2026-08-03
- 状态: 已确认

## 背景

T0211 交付 STREAM 流帧原语与 16B 帧头协议（version=1），但 SCP 生产路径
（do_scp_upload / do_scp_download）仍使用旧消息格式：`msg_scp_upload_t`
512KB 块逐条发送、`msg_scp_download_resp_t` 循环 push。旧路径无 timeout_ms
语义、错误无结构（仅 uiResult 数字）、不遵守流式拆分。

## 决策

- 帧头 `version` 从 1 → 2，客户端与服务端同版本整体替换，**无兼容期**
- 上传（客户端 push）：`STREAM INIT`（元数据 mode/atim/mtim/ctim/total_size +
  timeout_ms + block_size + block_count + name）→ `STREAM DATA` 序列 → `STREAM END`
- 下载（服务端 push，语义与现状一致）：客户端发 `msg_scp_download_t` 请求 →
  服务端回 `STREAM INIT` → `STREAM DATA` 序列 → `STREAM END`
- INIT 帧 v2 = [subtype][block_count][block_size][timeout_ms][meta_len][meta][name_len][name]
- 删除 `msg_scp_upload_t` / `msg_scp_upload_resp_t` / `msg_scp_download_resp_t`
- `is_link` 软链上传路径保留
- 压缩/加密/校验和三开关在 DATA 块上行为不变

## 权衡

- 备选：双协议兼容期（按 version 分发）—— 放弃（同仓库同版本整体升级，
  无历史客户端；兼容期使回归面翻倍且删除滞后）
- 备选：保留拉模式下载 —— 放弃（服务端现状即为 push，载体替换语义不变）

## 影响

- rpc/rpc-command.cpp：do_scp_upload / do_scp_download 重写
- rpc/rpc-server.cpp：rpc_scp_download 改为 STREAM push（rpc-server.cpp:932）
- rpc/rpc-msg.h：INIT 元数据扩展 + 旧类型删除
- 新增测试 rpc/tests/scp_stream.cpp（socketpair 端到端）
- 断点续传：现状无此机制，不引入（范围外）
