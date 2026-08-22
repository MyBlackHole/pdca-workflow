---
schema: pdca.asset/v1
id: T0344-0822-rpc-mixed-mtls
phase: check
source_ids: ["unit-quad", "tool-integration", "build-v2"]
---

## 上下文

T0344 目标：rpc 混合/强制 mTLS。`server mtls=0` 按 `want_mtls` 双通（明文直通 + 按需密文），`server mtls=1` 强制密文不回退。握手契约：客户端上报 algorithm，服务端协商后返回 `ca_cn` 定位证书。

## 假设与结果

- **AC-1** server0 x want0：`PASS` — 工具级实测 aio-speed 明文业务 exit 0（unit-quad + tool-integration）
- **AC-2** server0(有sctx) x want1：`PASS` — HS_OK_MTLS 且返回 ca_cn=ED25519 Test CA，客户端按其定位证书完成 mTLS 业务
- **AC-3** server1 x want1：`PASS` — 强制 MTLS 业务命令 exit 0
- **AC-4** 缺 cert_dir：`PASS` — client exit 255 不回退明文
- **AC-5** server1 x want0：`PASS` — server 拒绝明文业务帧并 ErrorLog 'mTLS required' 后断开

## 分析

- 双层证据：mixed_mtls_test（分流逻辑单测）+ mixed_mtls_integration（真实 aio-speedd/aio-speed 进程级）
- 发现并修复：client 明文业务帧被 server 拒时静默断开无日志 → 补 ErrorLog 'reject plain business frame ... mTLS required'
- 握手协商缺陷修复：服务端原固定回自身算法，现采纳客户端算法并按其取 ca_cn（commit 5203d4e）

## 适用边界

- 仅 rpc 目录；libs 零改动
- server 0 无 cert_dir 时固定 PLAIN；MT_GET_TIME 帧有意放行明文

## 下一轮建议

- client 收 HS_ERR_MTLS_REQUIRED 帧误当业务响应解析的退出码语义可优化（当前依赖 server 日志判定）
