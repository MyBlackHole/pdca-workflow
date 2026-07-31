---
schema: pdca.asset/v1
id: T0146-0730-rpc-ipv6-support
phase: check
source_ids:
  - evidence/manifest.jsonl
---

## 上下文
为 RPC 项目添加 IPv6 支持。原始代码硬编码 `AF_INET`、`struct sockaddr_in`、`inet_ntoa()`，无法在纯 IPv6 环境中运行。

## 假设与结果
- **假设**: 服务端使用 `AF_INET6` + `IPV6_V6ONLY=0` 单 socket 双栈，客户端使用 `inet_pton` 自动识别地址族，即可无缝支持 IPv4/IPv6。
- **结果**: 验证通过。所有 AC 满足，编译零错误。

## 分析
- AC-1 服务端双栈: `rpc-server.cpp` — `AF_INET6`、`in6addr_any`、`IPV6_V6ONLY=0`、`accept4` 适配
- AC-2 客户端 IPv6 连接: `rpc-io.cpp` — `inet_pton` 检测地址族，直接填充 `sockaddr_in`/`sockaddr_in6`
- AC-3 IPv4 回归: `inet_pton(AF_INET, ...)` 对 IPv4 地址正常工作
- AC-4 `--bind-ip` IPv6: `rpc-server.h` `sockaddr_storage` 足够容纳 IPv6
- AC-5 日志显示正确: `addr_to_str()`/`addr_port()` 基于 `ss_family` 动态分发
- 新增验收: 客户端精确使用用户指定的地址族（IPv4→AF_INET，IPv6→AF_INET6）

## 失败原因
无

## 适用边界
- DNS 主机名解析不在当前范围内（仅接受 IP 字符串）
- IPv6 ACL/防火墙规则管理不在当前范围内

## 下一轮建议
- 如需支持主机名解析，可将来扩展 `inet_pton` → hostname fallback 逻辑
- 运行态测试建议在纯 IPv6 环境中验证连接