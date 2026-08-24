# 【F】e2e 场景矩阵二期 — 规格文档

## 问题陈述

- **现状**: 一期矩阵（S1-S10）覆盖基本双算法/开关/fail-closed/keygen；结论建议扩充 CRL、并发、大输出、交替协商等进阶场景。
- **目标**: 扩展 test/e2e_tool_scenarios.sh 至 S11-S16，覆盖安全与稳定性进阶路径，保持一期场景零劣化。

## 解决方案（新增场景）

| 场景 | 内容 |
|------|------|
| S11 CRL 吊销拒绝 | 脚本内 openssl 构造迷你 CA 与吊销列表，独立 cert_dir 服务端实例启用 crl.pem 后，持被吊销证书的客户端握手必须失败（fail-closed） |
| S12 全无效证书目录 | RPC_TLS_CERT_DIR=/nonexistent 的 mtls 服务端 → plain only；mTLS 客户端必须被拒（T0390 兜底语义 e2e 锚） |
| S13 并发客户端 | 6 个 aio-speed mTLS 请求并发执行，全部成功（ctx 缓存并发安全锚） |
| S14 大输出命令 | 5000 行输出经 mTLS 通道传输后行数完整 |
| S15 双算法交替 | 同一服务端 SM4/AES 各 3 轮交替请求全部成功（缓存键控不串) |
| S16 rdbcomm AES | rdbcomm --tls-algorithm=TLS_AES_256_GCM_SHA384 mTLS 执行成功 |

## Seam 分析

### 声明的测试接缝
- seam: test/e2e_tool_scenarios.sh -> libs/tls_cert.c
- seam: test/e2e_tool_scenarios.sh -> rpc/rpc-io.cpp
- seam: test/e2e_tool_scenarios.sh -> rdbcomm/server.c

### 验收可测性
- 每场景 PASS/FAIL 独立断言；脚本汇总退出码。

## 用户故事

1. 作为 `维护者`，我想要吊销与并发等安全语义有自动化回归，以便演进时不悄悄破坏 fail-closed 保证。

## 实现决策

- S11 使用独立临时 cert_dir 实例（RPC_TLS_CERT_DIR 注入），不污染现网规范目录；openssl ca 迷你库脚本化生成吊销环境。
- 并发采用 bash 后台作业 + wait 收集退出码。

## 测试决策

- 二期场景追加至现有脚本尾部；一期场景原样保留作回归对照。

## 验收标准

- [ ] AC-1: 脚本扩展至 S16 且可重复执行（连跑两次结果一致）
- [ ] AC-2: 一期 S1-S10 保持全绿（零劣化）
- [ ] AC-3: 新增 S11-S16 全部 PASS（其中 S11 断言"被吊销→拒绝"、S13 断言"6/6 成功"、S14 断言"5000 行完整"）
- [ ] AC-4: 报告落盘任务 records 目录

## 范围外

- 产品代码修改（新缺陷另行立项）
- 性能压测指标

## 备注

- 前置：T0391 证书基线、T0394 rdbcomm 修复均已就位。
