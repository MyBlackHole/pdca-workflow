# 服务端 tls-algorithm 锁定语义 + cli_algorithm 字段去重

## 问题

1. T3960 审查确认：四模块服务端协商层忽略 tls-algorithm 配置，无法实现单算法锁定。
2. rpc-config.h 同时存在 `char cli_algorithm[128]` 与 `char tls_algorithm[128]`，前者仅为中转字段（main.cpp:373-376 合并后弃用），冗余。
3. **服务端 tls_algorithm 当前存在隐式默认值（SM4）**——语义上不应有默认值：未配置就是未设置。

## 语义定稿（用户拍板）

- **服务端 tls_algorithm 没有默认值**：env/ini/CLI 全部未命中时为"未设置"（algorithm=0/名称空串）。
- **设置了即锁定**：任一层显式命中 → 服务端仅接受该算法，其余合法算法回 `HS_ERR_ALGORITHM(0x8005)`。
- 未设置 → 无算法约束（保持现状白名单协商，向后兼容）。
- 显式配置的算法名仍需白名单校验（非法名启动失败 fail-closed，沿用 T0358 H3）。

## 方案

### 1. 配置层：去默认值 + 显式即锁

sec_resolve_str default 改传 NULL（NULL = env/ini 均未命中），四模块统一：

```c
alg_name = sec_resolve_str(..., NULL);
if (cli_algorithm) { alg_name = cli_algorithm; }   /* CLI 最优先 */
/* alg_name == NULL => 未设置：cfg->algorithm=0, name 空串, 不锁 */
if (alg_name) {
    白名单校验(失败即启动失败);
    cfg->algorithm = from_name(alg_name);  /* 非 0 即锁 */
}
```

结构体不加新字段——**`algorithm != 0` 即锁定信号**：
- rpc：rpc-config.h `g_rpc_config`（删 `cli_algorithm`；`tls_algorithm` 允许空串）
- rdbcomm：server_options（补算法字段，若无可设字段则新增）
- dmsbtex：dmsbtex_tls_config_t
- libobk：libobk_tls_config_t

### 2. 协商层过滤（四模块握手函数）

白名单校验通过后追加：

```c
if (cfg->algorithm != 0 && negotiated != cfg->algorithm)
    回 HS_ERR_ALGORITHM（携带客户端 halg）
```

- rpc-server.cpp 协商分支
- rdbcomm/server.c 协商处
- dmsbtex/network.c dm_server_handshake（启用 cfg 参数）
- libobk/oracleCmdTbl.c sbt_session_server_handshake（同上）

### 3. rpc cli_algorithm 去重

删 `cli_algorithm` 字段与 main.cpp 合并块；args_process case 1031 白名单校验后直写 `tls_algorithm`。

### 4. mixed_mtls_integration server_serve 复刻同步

测试内决策树当前保留旧"回落服务端配置"逻辑（L77-80），更新为真实语义：hs_negotiate_algorithm + 锁定过滤（cfg.algorithm 取自 server_env 新增的显式算法设置）。

### 5. e2e

新增 S18/S19：aio-speedd `--mtls-enable=1 --tls-algorithm=TLS_SM4_GCM_SM3`（显式锁定）→ AES 客户端被拒（输出含 "algorithm"）、SM4 客户端通行。现有场景不破坏（均未显式配算法 → 不锁）。

## 用户故事

1. 作为运维，我显式设置服务端 tls-algorithm 后其他算法客户端被明确拒绝；不设置时行为与现状一致且无隐式默认。

## Seam 分析

### 声明的测试接缝

- seam: rpc/tests/mixed_mtls_integration.cpp -> ../rpc-server.cpp
- seam: libobk/test/session_test.c -> ../lib/logic/oracleCmdTbl.c
- seam: dmsbtex/test/session_test.c -> ../network.c

## 测试决策

- mixed_mtls_integration 新增 AC-8/AC-9（锁定拒错配/放行匹配）；server_env 增加 lock 算法字段。
- libobk/dmsbtex session_test 各增锁定用例。
- e2e S18/S19；全量回归验证未设置路径兼容。

## 验收标准

- [ ] AC-1: mixed_mtls_integration 新增用例通过：lock=SM4 时 client AES 被拒（帧 result==HS_ERR_ALGORITHM）、client SM4 通行。
- [ ] AC-2: libobk/dmsbtex session_test 锁定用例通过（错配拒、匹配通）。
- [ ] AC-3: e2e S18/S19 通过：显式锁定服务端拒绝 AES 客户端（stderr 含 "algorithm" 文案）、放行 SM4。
- [ ] AC-4: 现有 e2e 17 场景全过；服务端未配置算法时四模块协商行为与现状一致（无隐式默认）。
- [ ] AC-5: grep 确认 rpc 无 cli_algorithm 残留；四模块握手函数均含 `algorithm != 0` 过滤分支；sec_resolve_str 调用点 default 为 NULL（不再回退 DEFAULT）。

## 范围外

- 独立拒绝码（复用 HS_ERR_ALGORITHM）；客户端侧语义变更；rdbcomm/dmsbtex/libobk CLI 参数扩展。
