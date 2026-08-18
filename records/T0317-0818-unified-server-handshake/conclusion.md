---
schema: pdca.asset/v1
id: T0317-0818-unified-server-handshake
phase: check
source_ids: [full-test, build, scan, implementation, param-test, param-build, param-scan, param-implementation]
verdict_id: T0317-check-20260818
outcome: confirmed
at: 2026-08-18T16:34:35+08:00
---

## 上下文

统一 RPC/rdbcomm 服务端首阶段握手编排，支持 TIME、明文、mTLS 协商与 TLS session 升级；补齐客户端和服务端显式握手配置参数。

## 假设与结果

- AC-1：通过。握手单元测试覆盖 TIME、明文、mTLS、算法不匹配和明确错误。
- AC-2：通过。强制 mTLS 缺少有效算法证书链时初始化失败，未请求或算法不匹配不会降级明文。
- AC-3：通过。非强制模式无证书仍可明文，有证书可主动 mTLS，证书不可用时明确失败。
- AC-4：通过。真实 RPC/rdbcomm 工具集成测试通过，mTLS 第二阶段使用 TLS session 读写。
- AC-5：通过。`xmake build` 与完整 `xmake test -v` 通过，36/36 测试成功，服务端首阶段编排已统一。
- AC-6：通过。客户端 `rpc_hs_client_config_t` 与服务端 `rpc_hs_server_config_t` 显式传递 mTLS 开关和算法；工具保留既有配置入口，不新增 CLI 参数、不改变协议字段和 `ca_cn` 选择逻辑。
- AC-7：通过。`git diff --check`、引用扫描和参数接入验证通过，客户端/服务端参数语义一致。

## 分析

公共握手模块负责协议编排和 session 绑定，TLS 证书模块负责证书链与 OpenSSL 细节。服务端 mTLS 强制策略与证书可用性分离校验；非强制模式允许明文但不会把 mTLS 请求静默降级。客户端显式配置结构消除了高层连接逻辑对全局配置的直接依赖。TIME 仍是终止操作。

## 适用边界

算法取值仍由现有配置转换为 CLASSIC 或 SM；证书按既有 `ca_cn` 目录逻辑选择。当前不扩展 CLI 参数、不兼容旧协议、不改变第二阶段业务帧格式。

## 下一轮建议

后续新增协议算法时，应同步扩展客户端/服务端配置结构、证书可用性校验和真实工具集成测试，避免恢复重复握手编排。
