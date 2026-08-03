# SCP 业务流式化 — 规格文档（T0212）

## 问题陈述

- **现状**: T0211 已交付 STREAM 流帧原语（INIT/DATA/END + timeout_ms）与帧协议基础设施，
  但 SCP 生产路径未接入：`do_scp_upload` 仍按 `msg_scp_upload_t` 512KB 块逐条发送
  （rpc-command.cpp:525），`do_scp_download` 仍循环收 `msg_scp_download_resp_t`
  （rpc-command.cpp:34，服务端 rpc-server.cpp:932 push）。帧头 16B 协议仅用于
  request/response 包装，未发挥流式语义；AC-15 服务端超时执行路径无载体。
- **目标**: SCP 上传/下载改为 STREAM 帧序列传输，服务端超时执行生效，
  压缩/加密/校验和开关行为不变。
- **差距**: 旧消息路径无 timeout_ms 语义；块传输不遵守帧协议最大帧 8MB 上限的
  流式拆分；错误仅凭 uiResult 数字无错误码/详情结构。

## 解决方案

- 上传（客户端 push）：`STREAM INIT`（携带 mode/atim/mtim/ctim/total_size/name/
  timeout_ms/block_size/block_count）→ `STREAM DATA` 序列 → `STREAM END`；
  服务端边收边写，END 后回成功响应。
- 下载（服务端 push，语义与现状一致）：客户端发 `msg_scp_download_t` 请求 →
  服务端回 `STREAM INIT` → `STREAM DATA` 序列 → `STREAM END`；客户端解帧落盘。
- `is_link` 软链上传路径保留原消息。
- 删除 `msg_scp_upload_t` / `msg_scp_upload_resp_t` / `msg_scp_download_resp_t`
  旧块消息类型（帧头 version 同步升级）。

## Seam 分析

### 测试接缝
- 协议层：复用 T0211 的 rpc-msg.h 帧收发原语，socketpair 测试（与
  rpc/tests/stream_blocks.cpp 同构）
- 业务层：`do_scp_upload` / `do_scp_download` 为独立函数（rpc-command.cpp），
  可直接以真实文件 + socketpair 断言；不依赖服务器进程
- 服务端侧：`rpc_scp_download`（rpc-server.cpp:932）独立函数，以
  rpc_conn 接口注入

### 验收可测性
- 全部 AC 可在 socketpair + 临时目录上构造，无需真实网络
- 半写清理、超时路径可独立触发（timeout_ms 设小值）

## 用户故事

1. 作为客户端，我想要上传 1GB 文件走 STREAM 帧序列，以便获得块级内存峰值与
   超时执行语义
2. 作为管理员，我想要服务端在流超时时返回 RPC_ERR_TIMEOUT + 详情，以便诊断
3. 作为兼容依赖方，我想要压缩/加密/校验和开关在流式路径行为不变

## 实现决策

- 修改模块：rpc/rpc-command.cpp（do_scp_upload/do_scp_download）、
  rpc/rpc-server.cpp（rpc_scp_download 改为 STREAM push）、
  rpc/rpc-msg.h（STREAM INIT 元数据扩展 + 删除旧消息类型）
- 接口：STREAM INIT 增加文件元数据区（mode/times/size，复用 rpc_timespec_t）；
  INIT 帧格式 v2 = [subtype][block_count][block_size][timeout_ms][meta_len][meta][name_len][name]
- 技术澄清：下载保持"客户端单请求 → 服务端 push 流"语义不变，仅载体换为 STREAM 帧
- 架构决策：帧头 version 从 1 → 2（破坏性替换，无兼容期，记录 ADR）
- 数据模型：无
- API 合约：`rpc_send_stream_init/dat a/end` 系列服务端辅助函数

## 测试决策

- 新增 rpc/tests/scp_stream.cpp：上传/下载端到端（socketpair + 真实文件 +
  sha256 比对）、元数据往返、三开关组合、超时执行、半写清理
- 被测模块：do_scp_upload、do_scp_download、rpc_scp_download
- 先例参考：rpc/tests/stream_blocks.cpp、conn_limit.cpp

## 验收标准

- [ ] AC-1: 上传流式化——64MB 文件经 STREAM 帧序列上传，服务端落盘 sha256 与源一致
- [ ] AC-2: 下载流式化——服务端以 STREAM 帧 push，客户端解帧落盘，内容一致
- [ ] AC-3: 元数据往返——mode/atim/mtim/ctim/total_size 上传后一致
- [ ] AC-4: 三开关——压缩/加密/校验和各自开启时上传-下载往返内容一致
- [ ] AC-5: is_link 软链上传路径保留可用
- [ ] AC-6: 服务端超时执行——timeout_ms 到达流未完成，返回 RPC_ERR_TIMEOUT + 详情
- [ ] AC-7: 半写清理——DATA 序列缺 END 中断，服务端移除半写文件并报错
- [ ] AC-8: 全量回归——xmake test 全部通过（含 T0211 的 8 个新 target）
- [ ] AC-9: 吞吐——socketpair 上传 ≥ 400 MB/s（协议原语层 514 MB/s 的 80%）
- [ ] AC-10: 旧类型清除——msg_scp_upload_t/msg_scp_upload_resp_t/msg_scp_download_resp_t
      无残留引用

## 范围外

- 断点续传（现状无此机制，ftruncate 清零全量传输，不引入）
- rpc-server thread-per-conn → rpc-epoll 迁移（T0213）
- 非 SCP 命令（stat/rm/mkdir 等单帧命令）保持现状
- 帧头协议本体（16B 头、8MB 上限，T0211 已冻结）

## 备注

- 术语见 `pdca/CONTEXT.md`；ADR 记录 version 1→2 破坏性替换
- 依赖 T0211 交付：rpc/rpc-msg.h/c、rpc/tests/stream_blocks.cpp 模式
- 知识：debugging/c-buffer-api-size_t-frame-validation.md（size_t 输出参数
  与先校验后分配规则必须遵守）
