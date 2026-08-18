# 实现 rpc/rdbcomm 统一第一阶段握手与时间协议

## 问题陈述

rpc 与 rdbcomm 需要在 TLS 前识别 TIME、明文继续、mTLS 升级和错误。

## 解决方案

实现共用版本化固定头：magic、版本、operation、能力/算法、payload 长度、结果码，提供编解码、判定、半包/超时和错误处理。

## 验收标准

- [ ] AC-1: 运行协议单测得到 rpc/rdbcomm 对同一报文的解析结果完全一致。
- [ ] AC-2: 运行判定测试得到 TIME、明文继续、mTLS 升级和拒绝四类结果正确。
- [ ] AC-3: 运行坏包、未知 operation、半包和超时测试得到明确错误码。

## 声明的测试接缝

- seam: rpc/tests/rpc_rdbcomm_negotiate_test.cpp -> rpc/rpc-io.cpp

## 验收标准
