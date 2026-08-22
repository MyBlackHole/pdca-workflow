# rpc mTLS 降级与证书初始化缺陷修复（F1/F2/F3）— 规格文档

## 问题陈述

- **现状**: T0348 审查发现三处缺陷：F1) `rpc/rpc-io.cpp:130` client `mtls=1` 收到 server 回 `HS_OK_PLAIN` 时静默降级明文，违背"客户端要求密文即必须密文"；F2) `rpc/rpc-server.cpp:270/311` `tls_cert_get_ca_cn` 返回 NULL 时回落可能为空的 `g_rpc_config->ca_cn` 并下发空 ca_cn，错误被推到 client 侧才暴露；F3) `rpc/main.cpp:409` `cert_dir` 有值但证书损坏时 init 失败直接 exit，导致纯明文服务也不可用。**用户澄清：F3 无需阻止服务启动，只需阻止客户端发起 mTLS 通信**——即证书坏时服务端照常启动（明文），因无 sctx 客户端 mTLS 握手自然不可用。
- **目标**: F1 client 要求密文被拒即失败不降级；F2 空 ca_cn 时 server 直接回 `HS_ERR_CA_CN` 留在可诊断位置；F3 cert init 失败不再 exit，降级 `sctx=NULL` 明文继续，日志明确输出模式。
- **差距**: 三处分支逻辑缺失/错误；对应回归测试缺口。

## 解决方案

F1：client 收 `HS_OK_PLAIN` 且自身 `mtls_enabled=1` → ErrorLog "server downgraded to plain but mTLS requested" + 失败退出。F2：server 侧 cn 为空时回 `HS_ERR_CA_CN` + ErrorLog cert_dir 与算法。F3：cert init 失败一律不再 exit，统一 WarningLog "cert load failed, serving plain only" 且 `server_tls_ctx=NULL`——服务端明文继续，客户端 mTLS 因无 sctx 自然被拒（HS_ERR_MTLS_REQUIRED / HS_OK_PLAIN 路径）。

## Seam 分析

### 声明的测试接缝

- seam: rpc/tests/mixed_mtls.cpp -> ../rpc-io.h

### 验收可测性

- F1/F3 用真实 aio-speedd/aio-speed 进程断言退出码与日志；F2 构造空 ca_cn 场景断言 HS_ERR_CA_CN。
- 边界：坏证书目录、ca_cn 目录缺失均可独立构造。

## 用户故事

1. 作为客户端使用者，当我要求 mTLS 但服务端只能明文时，我希望命令明确失败而非静默明文发送敏感数据。
2. 作为运维，证书目录损坏时我希望服务端仍能提供明文服务并日志告警，而不是拒绝启动。
3. 作为运维，证书缺 ca_cn 时我希望在服务端日志看到具体 cert_dir 与算法，而不是 client 侧模糊报错。

## 实现决策

- **模块**：
  - `rpc/rpc-io.cpp:130`：F1 分支
    ```c
    if (resp_host.result != HS_OK_MTLS) {
        if (g_rpc_config->mtls_enabled) {
            ErrorLog("handshake: server downgraded to plain but mTLS requested");
            return -1;
        }
        return 0;
    }
    ```
  - `rpc/rpc-server.cpp:267/308`：F2 分支
    ```c
    const char *cn = tls_cert_get_ca_cn(sctx, negotiated_name);
    if (!cn || !cn[0]) {
        ErrorLog("handshake: ca_cn unavailable: cert_dir=%s algorithm=%s",
                 g_rpc_config->cert_dir, negotiated_name);
        /* 回 HS_ERR_CA_CN */
    }
    ```
  - `rpc/main.cpp:409`：F3 分支
    ```c
    if (tls_cert_init_server(...) != 0) {
        if (tool_mtls_enabled) { ErrorLog(...); exit(-ret); }
        WarningLog("cert load failed, serving plain only");
        server_tls_ctx = NULL;
    }
    ```
- **技术澄清**: 不改协议帧与握手状态机；F2 新增使用既有 `HS_ERR_CA_CN(0x8006)`。

## 测试决策

- 扩展 `mixed_mtls_integration`：新增 AC-6（client1+server0无sctx→exit!=0）、AC-7（坏证书目录+mtls=0→server 启动成功且 plain 可用）、AC-8（缺 ca_cn 目录→server 日志含 ca_cn unavailable）。

## 验收标准

- [ ] AC-1: client mtls=1 + server 无 sctx 回 PLAIN → client exit != 0，ErrorLog 含 "downgraded to plain"。
- [ ] AC-2: sctx 缺 ca_cn 时 server 回 `HS_ERR_CA_CN`，且 ErrorLog 含 cert_dir 与算法名。
- [ ] AC-3: mtls=0 + cert_dir 指向不存在目录 → 服务端启动成功、明文业务可用、WarningLog 含 "serving plain only"。
- [ ] AC-4: cert init 失败 → 服务端不退出，继续以明文服务；客户端发起 mTLS 时被 `!sctx` 分支拒绝。
- [ ] AC-5: 既有象限（plain 通 / mixed MTLS 通 / forced MTLS 通 / 缺 cert_dir 拒绝）全部无回归。

## 范围外

- 不改协议帧格式；不做自动重试；不改 libs 握手行为。

## 备注

- 来源：T0348 review-report.md F1/F2/F3；F4 断言随本任务 AC 测试顺手补；F5 仅文档。
