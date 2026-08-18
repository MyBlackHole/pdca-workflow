# 接入 RPC 第一阶段握手与统一时间协议

## 问题陈述

RPC 连接建立和既有获取时间调用需要迁移到统一第一阶段协议。

## 解决方案

在 RPC 客户端/服务端连接路径接入共享协议；默认明文进入既有 APP 帧；显式 mTLS 成功后透明切换 TLS 数据面；`rpc_get_time` 映射到 TIME 操作并保持 API 兼容。

## 验收标准

- [ ] AC-1: 运行 RPC 明文集成测试得到 APP 帧正常收发。
- [ ] AC-2: 运行 RPC mTLS 集成测试得到升级后 APP 帧正常收发且不降级。
- [ ] AC-3: 运行 RPC 时间回归测试得到 `rpc_get_time` 原调用成功/失败语义保持不变。

## 声明的测试接缝

- seam: rpc/tests/rpc_rdbcomm_negotiate_test.cpp -> rpc/rpc-io.cpp

## 验收标准
