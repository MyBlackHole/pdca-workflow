# POC 测试启用国密前后传输性能（C demo）— 规格文档

## 问题陈述

- design.md「性能预期」章节当前引用**公开资料数据**（bench_sm4_gcm.c / bench_sm2.c 基于 KB 搜索与公开资料，截止 2026-07），缺少实际环境实测数据
- 需求验收 5.4（性能测试：加密对备份性能的影响基线）要求实测支撑
- 核心问题：启用国密加密后，端到端传输吞吐相对明文/常规 TLS 的开销占比是多少？是否满足备份场景（千兆/万兆链路）？

## 环境事实（P0 核查，已验证）

| 项 | 结果 |
|----|------|
| 系统 OpenSSL 3.6.3 | EVP 层 SM2/SM3/SM4 ✅；**TLS 套件层无国密套件** ❌（无 ECDHE-SM4-*） |
| xmake OpenSSL 1.1.1-w | 同上 ❌（libssl.a 无 ECDHE-SM4 字符串，未编译国密 TLS 套件） |
| GMSSL 3.1.1（xmake 包，静态链接） | TLCP 上下文/握手 ✅（test_gmssl 已跑通 10 组） |
| 证书资产 | demo-gmssl/openssl_certs（rsa+sm2）、tls_keygen_certs（Ed25519）已存在可复用 |

**结论**：端到端「OpenSSL 国密 TLS 套件」组在当前环境不可行（需重编 OpenSSL，非 POC 范围）。端到端国密组以 **GMSSL TLCP** 实测；OpenSSL 侧提供加密层（EVP SM4-GCM / SM2）实测数据。

## 目标

- 使用 C 编写 demo，本机回环实测传输性能：
  1. **端到端**：明文 TCP / OpenSSL 常规 TLS / GMSSL TLCP 三组 × 3 档（128MB/512MB/1GB）吞吐与耗时
  2. **加密层**：SM4-GCM 吞吐（OpenSSL EVP vs GMSSL）；SM2 操作耗时（签名/验签/密钥交换，OpenSSL vs GMSSL）
- 输出对比报告，回答国密加密对备份传输的性能影响

## 验收标准

- [ ] AC-1: C demo 完成端到端传输测试（明文 TCP / OpenSSL 常规 TLS / GMSSL TLCP × 128MB/512MB/1GB），输出吞吐 MB/s 与耗时
- [ ] AC-2: C demo 完成加密层测试（SM4-GCM 吞吐 OpenSSL vs GMSSL；SM2 签名/验签/密钥交换耗时两实现对比）
- [ ] AC-3: 环境事实核查记录入报告（OpenSSL 3.6.3/1.1.1-w 无国密 TLS 套件；GMSSL TLCP 可用）
- [ ] AC-4: research-report.md 含三组端到端对比表、加密层对比表、结论（国密相对明文/常规 TLS 开销占比、备份场景适用性判断）
- [ ] AC-5: 结论登记 evidence（evt-001 research-report）并沉淀 knowledge（如国密性能实测结论可复用）

## 任务拆解

| 子任务 | 范围 | 操作 |
|--------|------|------|
| T1 demo 骨架 + 证书准备 | 源码结构、证书复用 | 复用 openssl_certs（rsa/sm2）+ tls_keygen_certs（Ed25519）；搭建三组传输骨架 |
| T2 端到端传输测试 | 三组 × 3 档 | 明文 TCP（socket 直传）/ OpenSSL TLS（mTLS AES-GCM）/ GMSSL TLCP（SM2+SM4）流式收发 |
| T3 加密层测试 | SM4-GCM + SM2 | OpenSSL EVP vs GMSSL EVP 吞吐；SM2 签名/验签/密钥交换耗时 |
| T4 报告与结论 | 对比表 + 结论 | research-report.md + evidence 登记 |

## 产出

- C demo 源码（bench_transfer / bench_crypto，放 F/139 仓库 demo 目录）
- research-report.md（性能对比与结论）

## 范围外

- 真实跨机传输（本任务本机回环）
- OpenSSL 国密 TLS 套件端到端（环境不支持，重编 OpenSSL 非 POC 范围）
- TLCP 双证书 vs 单证书性能差异（GMSSL 单证书模式即可）
- 硬件加速（SM4-NI/ARMv8 CE）专项测量

## 备注

- 参考：knowledge/nbu/gmssl-tlcp-mtls.md（GMSSL API 速查）、demo-gmssl/test_gmssl.c（TLCP 骨架）
- 复用 T0162 单端口协商模型结论作为设计上下文（本 POC 不含协商头实现）
