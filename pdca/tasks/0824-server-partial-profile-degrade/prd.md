# 【B】服务端单算法证书加载失败不应禁用国密 — 规格文档

## 问题陈述

- **现状**: 服务端启动日志 `TLS setup failed: role=server stage=certificate algorithm=TLS_AES_256_GCM_SHA384` 后 `cert load failed (ret=-3), serving plain only`，mTLS 完全不可用，国密客户端 `connect to server failed`。
- **目标**: 单算法 profile 加载失败时保留其余可用算法（国密 SM4 照常服务），仅当全部算法失败才降级明文。
- **差距**: `tls_cert_init_server` 对多 profile 采取"全有或全无"语义——AES/ED25519 链数据无效（现网根目录缺 ed25519_host.* 且 host.* 由无关 CA 签发）连坐了本可用的 SM4。

## 根因（已取证）

1. `tls_cert_init_server` 循环 slot_create 任一失败即整体 goto error（libs/tls_cert.c），无部分成功路径；
2. 现网 cert_dir 根缺 ed25519_host.{crt,key}，且 ed25519_ca.crt 实为 MySM2RootCA 内容、host.crt 由 UUID CA 签发——ED25519 链数据无效属环境事实；
3. T0388 整套语义后 ED25519 不再借 host.* 兜底，该无效链由"静默可用"转为显式失败，暴露了全有或全无缺陷。

## 解决方案

1. `tls_cert_init_server`：profile 循环改为"尽力收集"——成功的 slot 计入 ctx，失败的记警告跳过；至少一个成功 → 返回 OK（ctx 仅含可用算法）；全部失败 → 返回首个错误码（保持 plain only 兜底）;
2. `tls_cert_get_ssl_ctx(ctx, algorithm)` 对未加载算法返回 NULL 的既有行为不变，握手协商自然拒绝不可用算法;
3. main.cpp 无需改动（init 返回 OK 即不再 plain only，WarningLog 改由库内输出各 profile 结果）。

## Seam 分析

### 测试接缝
- libs/tests/tls_cert_test.c 新增用例：构造"SM4 有效 + ED25519 文件缺失"目录，断言 init_server 返回 OK、get_ssl_ctx(SM4) 非 NULL、get_ssl_ctx(AES) 为 NULL；再构造全缺失目录断言 init 失败。

### 声明的测试接缝
- seam: libs/tests/tls_cert_test.c -> libs/tls_cert.c

### 验收可测性
- init 返回码 + get_ssl_ctx 判定 + 实机启动日志与国密握手，均可独立 pass/fail。

## 用户故事

1. 作为 `运维人员`，我想要某一算法证书配错时国密照常服务，以便局部配置问题不升级为全局 mTLS 中断。

## 实现决策

- 降级粒度为算法 profile；失败 profile 通过 ErrorLog 输出算法名与错误码（复用 tls_cert_log_setup_error）。
- ctx->slot_count==0 视为完全失败，回传最后一个失败码。

## 测试决策

- 先写失败用例（当前实现下 SM4+坏 AES 目录 init 整体失败）再改语义（TDD）。
- 回归：tls_cert_test 全量 + rdbcomm 握手会话。

## 验收标准

- [ ] AC-1: 新增单测证明 SM4 有效+ED25519 缺失时 init_server 返回 OK 且 get_ssl_ctx(SM4)!=NULL、get_ssl_ctx(AES)==NULL
- [ ] AC-2: 新增单测证明双算法全缺失时 init_server 返回非 OK（plain only 语义保留）
- [ ] AC-3: 实机重启 aio-speedd 后日志不再出现 serving plain only，且默认算法 aio-speed mTLS 握手成功执行命令
- [ ] AC-4: libs/tests 与 rdbcomm 既有回归全部保持通过

## 范围外

- 现网 ED25519 证书数据的修复/重签（运维事项）
- 协商层对不可用算法的偏好回避策略

## 备注

- 用户质询原文："默认不是使用国密的吗"——确认默认 TLS_SM4_GCM_SM3 不应被 AES 连坐。
- 关联：T0388 整套语义使无效 ED25519 链显式失败，暴露本缺陷。
