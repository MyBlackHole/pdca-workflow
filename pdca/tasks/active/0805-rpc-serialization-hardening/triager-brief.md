# Triage Brief — rpc 序列化补强

## 分类

- category: `enhancement`（安全加固 + 协议演进 + 性能）
- scenario_type: `development`
- 任务 ID: T0217

## 验证结果（2026-08-05）

代码事实（非用户断言）：

1. **帧头层已有防护（T0211 完成）**：`rpc_frame_parse`（rpc-msg.c:14）按 magic →
   version → total_len 上限（8MB）顺序校验，先校验后分配。✅ 不属本次范围。

2. **消息体层无字段级校验（本次核心缺口）**：所有 `msg_*_ntoh`（rpc-protocol.cpp）
   变长字段长度直接取自对端并立即 `memcpy`：
   - `msg_cmd_ntoh` L184：`host->cmd_len = ntohl(net->cmd_len); memcpy(host->command, net->command, host->cmd_len);`
   - `msg_mkdir_ntoh` L245、`msg_unlink_ntoh` L219、`msg_key_verify_ntoh` L125、
     `msg_dir_tree_ntoh` L305、`msg_scp_download_ntoh` L286、`msg_nc_extend_ntoh` L724 等同样模式。
   - 服务端分发（rpc-server.cpp:170）读入 `net_buf[MSG_BUFF_LEN=512KB]` 后 L178 仅
     `msg_base_ntoh` 解析 uiMT/uiLEN，**未校验 uiLEN ≤ 实际读入 bytes**；随后各
     `msg_*_ntoh` 直接按对端长度 memcpy。恶意/损坏帧可构造超大 len 造成 host_buf 越界读写。
   - 部分调用点事后有补救（execute_cmd L697 `cmd_len = MIN(..., MSG_BUFF_LEN-1)`），
     但**14 个 ntoh 函数本体无边界参数**，防护不一致。

3. **字段版本协商缺失**：帧头全局 version=2（ADR-0012），无字段级演进能力；新增
   字段无法向后兼容。

4. **大块传输零拷贝现状**：`msg_download_block_t.data[512]` 固定数组 + `memcpy`
   （rpc-protocol.cpp L505/518）；流式块（STREAM 帧）经 `buf` + `readn` 整块读入，
   无缓冲链/游标零拷贝。对齐 nginx 思路存在空间。

## 查重结果

- 归档 `0803-rpc-protocol-transport-refactor`（T0211）：覆盖帧头协议/长度上限/
  传输部分读写，**不覆盖消息体字段级校验、版本协商、大块零拷贝**。
- knowledge `c-buffer-api-size_t-frame-validation.md`：记录"字段级再校验"原则但未落地到 ntoh。
- 无重叠活跃任务。✅ 无重复。

## 信息缺口 / 需 Grill

- 三个子项的**范围取舍**：是否全部纳入本任务，还是先做安全校验（核心）？
- 版本协商的形态：帧头 version 字段协商 vs 消息体扩展字段。
- 零拷贝是否只针对 STREAM 大块路径（不碰 512B 小块业务消息）。

## 推荐下一步

1. P1/P2 Grill：确认范围取舍与验收粒度。
2. 定稿 PRD（验收标准需 checkbox 格式）。
3. 终审后进入 Do。
