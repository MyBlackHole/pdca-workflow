# 接入 rdbcomm 第一阶段握手与统一时间协议

## 问题陈述

rdbcomm 当前无统一第一阶段协商和获取时间能力。

## 解决方案

在 rdbcomm 客户端/服务端连接路径接入共享协议；默认明文进入既有 APP 帧；显式 mTLS 成功后切换 TLS 数据面；增加 TIME 请求接口，返回统一时间响应后关闭连接。

## 验收标准

- [ ] AC-1: 运行 rdbcomm 明文集成测试得到初始化和业务 APP 帧正常收发。
- [ ] AC-2: 运行 rdbcomm mTLS 集成测试得到升级后业务帧正常收发且不降级。
- [ ] AC-3: 运行 rdbcomm 时间测试得到与 RPC 相同格式、字节序和语义的响应并关闭连接。

## 声明的测试接缝

- seam: rdbcomm/tests/rdbcomm_negotiate_test.c -> rdbcomm/client.c
- seam: rdbcomm/tests/rdbcomm_time_test.c -> rdbcomm/client.c

## 验收标准
