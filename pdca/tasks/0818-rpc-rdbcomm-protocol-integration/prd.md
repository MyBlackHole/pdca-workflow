# 完成 rpc/rdbcomm 协商时间全链路集成回归

## 问题陈述

共享协议和两个适配层需要证明跨模块 wire 一致、时序正确且不破坏既有业务。

## 解决方案

构造本地 TCP 双端测试矩阵，覆盖 TIME、默认明文 APP、mTLS APP、能力不匹配、服务端拒绝、未知帧、坏包、半包和超时，并运行既有 rpc/rdbcomm 回归。

## 验收标准

- [ ] AC-1: 运行双协议栈端到端测试得到三种第一阶段场景和明确错误场景全部符合协议。
- [ ] AC-2: 运行全量构建与既有测试得到无新增回归失败。

## 声明的测试接缝

- seam: rpc/tests/rpc_rdbcomm_negotiate_test.cpp -> rpc/rpc-io.cpp
- seam: rdbcomm/tests/rdbcomm_negotiate_test.c -> rdbcomm/client.c

## 验收标准
