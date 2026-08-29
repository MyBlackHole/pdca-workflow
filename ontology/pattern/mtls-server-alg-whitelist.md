---
schema: pdca.asset/v1
id: ontology:pattern/mtls-server-alg-whitelist
type: pattern
layer: Knowledge
status: active
summary: 服务端握手算法白名单校验四模块落地范式
source_task: T0357
relations:
  specializes: [ontology:pattern]
  guides: [ontology:entity/mtls-handshake, ontology:entity/tls-configuration]
attributes:
  - name: applicability
    desc: 服务端入口处白名单校验客户端算法枚举值
    constraint: ""
    testable_signal: 非法算法回显式错误码（0x8005）fail-closed，不依赖下游 NULL 回落
---

# 服务端握手算法白名单校验 — 四模块落地范式（T0357）
# 服务端握手算法白名单校验 — 四模块落地范式（T0357）

> 规则层见 `tls/mtls-param-review-findings.md` 陷阱 1：服务端必须在入口处白名单校验
> 客户端算法枚举值，非法即回显式错误码；不得依赖下游 `find_slot(NULL)` 空回落。
> 本文是可复用的**落地代码范式**与四模块精确入口。

## 四模块入口定位（grep 锚点）

| 模块 | 入口函数 | 关键行 | 错误码常量 |
|------|----------|--------|-----------|
| rdbcomm | `server.c` `on_connect` HANDSHAKE 分支 | ~507 | `RDB_HS_ERR_ALGORITHM`(0x8005) |
| libobk | `oracleCmdTbl.c` `sbt_session_server_handshake` | ~104 | `OBK_HS_ERR_ALGORITHM`(0x8005) |
| dmsbtex | `network.c` `dm_server_handshake` | ~223 | `DM_HS_ERR_ALGORITHM`(0x8005) |
| rpc | `rpc-server.cpp` `RpcService::StartRPCServiceWoker` | ~244 | `HS_ERR_ALGORITHM`(0x8005，**需补定义**) |

错误码值统一为 `0x8005`（与 `RDB_HS_ERR_*` 系列对齐）；rpc 原先缺失，在
`rpc-protocol.h` 的 Handshake result codes 区补 `#define HS_ERR_ALGORITHM 0x8005`。

## C 模块修复范式（rdbcomm/libobk/dmsbtex 同构）

```c
const char *algo_name = <mod>_hs_algorithm_name(halg);
if (!algo_name) {
    /* 畸形/未知算法值：白名单语义，禁止回落，显式拒绝（fail-closed） */
    result = <MOD>_HS_ERR_ALGORITHM;
    <halg_field> = halg;
    memcpy(resp, &result, 2);
    memcpy(resp + 2, &<halg_field>, 2);
    send_handshake_resp(...);   /* 发 4 字节 body 错误帧 */
    return -1;                  /* 断开 */
}
const char *cn = tls_cert_get_ca_cn(sctx, algo_name);   /* 不再传 NULL */
/* ca_cn 不可用时保持既有拒绝分支 */
```

要点：
- 先取算法名再查 `ca_cn`；**绝不**把未校验的 `halg` 直接透传给
  `tls_cert_get_ca_cn`（`NULL` 名会触发 `find_slot(NULL)` 静默回落 `slots[0]`）。
- `tls_cert_server_handshake` 也改用 `algo_name`，避免重复调用与二次 NULL 风险。
- 合法 SM4(1)/AES(2) 路径行为不变。

## rpc 修复范式（删除配置回落，抽 fail-closed 协商函数）

```c
/* rpc-protocol.cpp */
uint16_t hs_negotiate_algorithm(uint16_t client_alg, uint16_t *negotiated)
{
    if (client_alg != HS_ALG_SM4_GCM_SM3 &&
        client_alg != HS_ALG_AES_256_GCM_SHA384)
        return HS_ERR_ALGORITHM;     /* 不再回落 g_rpc_config->tls_algorithm */
    *negotiated = client_alg;
    return 0;
}
```
服务端：`hs_negotiate_algorithm(hs_host.algorithm, &negotiated)` 非 0 即发
`HS_ERR_ALGORITHM` 响应并 `goto return__` 断开。测试 mock 服务端同步接入该函数，
确保端到端语义一致。

## 测试接缝（回归用例）

每模块测试构造畸形 `halg`（0 与 0xFFFF 两类）握手帧，断言：
- 服务端回 `<MOD>_HS_ERR_ALGORITHM` 帧；
- **未**回落升级（如 libobk 断言 `io.tssl == NULL`、dmsbtex 断言握手返回非 0）。

注意（踩坑）：流式 socket 读取响应帧必须用循环读满固定长度，**裸 `recv` 一次性读
不可靠**（全量测试环境下可能只读回部分字节导致断言 `n==sizeof(resp)` 失败）。

## 关键教训（可跨任务复用）

**全量回归测试 PASS ≠ 验收标准 AC-1 满足**。本任务早期 `xmake test` 全量 40 用例
PASS，但 libobk/dmsbtex/rpc 的畸形算法值回落 bug 仍静默存在——因为既有测试从未
构造畸形算法值帧去触发 `find_slot(NULL)` 回落路径。必须显式构造畸形协商帧覆盖
拒绝分支，才能证明白名单校验生效。

## 范围外

- `libs/tls_cert.c` `find_slot` 空回落**不修改**：入口白名单后 NULL 不可达，回落
  保留为防御层（评估结论见 findings 陷阱 1）。
- 跨模块协商语义统一（flags 表达/强一致决策树）归 T0359。
