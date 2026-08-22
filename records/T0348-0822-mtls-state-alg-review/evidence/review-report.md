# T0348 审查报告 — 四模块 mTLS 状态参数与算法参数

## 审查范围

| 模块 | 参数入口 | 握手实现 |
|------|---------|---------|
| rpc | `rpc/rpc-config.cpp:168-180` sec_resolve + CLI 覆盖 | `rpc-server.cpp:231-364` / `rpc-io.cpp:98-172` |
| rdbcomm 工具/服务 | `rdbcomm-main.c:601-612` / `rdbcommd-main.c:317-346` sec_resolve + CLI | `client.c:167-231` / `server.c:484-529` |
| dmsbtex | `network.c:96-133` getenv + sec_resolve_str | `main.c:235-248` / `network.c:160-288` |
| sbt(libobk) | `libobk/lib/sbt/libobk.c:67-95` getenv + sec_resolve_str | `oracleCmdTbl.c:859-879` / `libobk.c:141-236` |

共享底座：`libs/common.h:15-17`（算法名宏）、`libs/tls_cert.c`（slot 机制）。

---

## 标准轴

### HIGH

**H1 服务端接受任意客户端算法值，叠加 slot 空回落，协商字段可被完全绕过**
- `libobk/lib/logic/oracleCmdTbl.c:860-865`、`rdbcomm/server.c:490-519`、`dmsbtex/main.c:239-241`：客户端发来的 halg 为任意 u16，无合法值校验。
- `libs/tls_cert.c:366-368`：`tls_cert_find_slot()` 对 NULL/空 algorithm **回落 slots[0]**。
- 后果链：畸形 halg → `*_algorithm_name()` 返回 NULL → `tls_cert_get_ca_cn(ctx,NULL)` 命中 slot[0] 返回有效 ca_cn → 服务端回 `OK_MTLS` 并原样回传非法值 → `tls_cert_server_handshake(...,NULL)` 用 slot[0] 的证书上下文握手。多算法 profile 下实际算法由 slot 加载顺序决定，协商字段失效；客户端侧 alg_name 判空兜底（`rdbcomm/client.c:202-205`、`libobk.c:198`、`network.c:201`）使最终结果为连接失败而非降级，故定 HIGH 非 CRITICAL，但形成可诊断性黑洞与半握手 DoS 面。
- 修复方向：服务端校验 halg ∈ {SM4=1, AES=2}，非法即回错误码——`RDB_HS_ERR_ALGORITHM(0x8005)` 已定义却从未被使用。

**H2 atoi 解析 SBT_MTLS_ENABLE，fail-open 方向静默禁密**
- `dmsbtex/network.c:104`、`libobk/lib/sbt/libobk.c:74`：`atoi("abc")==0` → mTLS 静默禁用、备份数据明文传输；`"1x"` 又会被启用。
- 对比同项目 CLI 用 strtol 严格 0/1 校验（`rdbcommd-main.c:134-144`），同一布尔参数三种解析严格度。
- 修复方向：统一走 `sec_resolve_int` 或严格解析 + 非法值拒绝启动。

**H3 strstr 子串匹配算法名**
- 四份映射函数同病：`rdbcomm/msg.c:115-122`、`dmsbtex/protocol.c:69-76`、`rpc/rpc-protocol.cpp:208-221`、`libobk/lib/protocol.c:17-24`。
- `"sm2"` 命中 SM4_GCM_SM3 且被测试固化（`rpc/tests/rpc_own_handshake_test.cpp:56`）；匹配顺序依赖（SM4 先判）；配置笔误静默命中错误 profile，错误延迟到握手期暴露。
- 修复方向：strcmp 全串精确匹配，未知名显式报错。

**H4 协商语义三种并存，dm_hs_decide 决策树为死代码**
- rpc："优先采纳客户端算法，非法回落服务端配置"（`rpc-server.cpp:244-249`）；
- 其余三模块："无条件采纳客户端算法"；
- `dmsbtex/protocol.c:192-213` 的 `dm_hs_decide()`（flags+算法一致性决策树）在生产代码与测试中零调用；且其依赖的 `DM_HS_F_MTLS_REQUEST/REQUIRED` flags 在实际帧格式（CMD_HANDSHAKE body 仅 2 字节 algorithm）中无处承载——协议层与线上格式脱节。
- 同一部署不同通道安全属性不一致。修复方向：选定唯一语义（建议 dm_hs_decide 的强一致模型），接线或删除死代码。

### MEDIUM

**M1 枚举五处重复 + 映射函数四份**
- `rdbcomm/io.h:17-21`、`dmsbtex/protocol.h:93-97`、`rpc/rpc-protocol.h:87-89`、`libobk/include/protocol.h:73-76`；协议值 1=SM4 / 2=AES 靠人工对齐，漂移无编译期防护。收敛到 libs 单一头文件。

**M2 rpc 独有明文降级路径，语义错位**
- `rpc-server.cpp:317-324`：客户端 want_mtls + 服务端无证书上下文 → 回 `HS_OK_PLAIN` 而非错误码；其余三模块一律拒绝。客户端 `rpc-io.cpp:130-137` 会检测降级并 abort，端到端安全但浪费一轮且违背"无降级"全局约定。应回 `HS_ERR_*` 明确拒绝。

**M3 配置层级不一致 + env 名碎片化**
- sbt/dmsbtex 算法只读 [security] 全局段（`libobk.c:69-72`、`network.c:98-101`）；rpc/rdbcomm 另支持 [tool] 段覆盖（`rpc-config.cpp:173-180`、`rdbcomm-main.c:604-612`）。
- mtls 开关 env 名分裂：`SBT_MTLS_ENABLE`（libobk+dmsbtex 共享同名，两套服务被一个变量同时影响）/ `RDBCOMM_MTLS_ENABLE` / `RDBCOMMD_MTLS_ENABLE` / aio-speedd 系列。运维误配面大，需统一键名或明确文档。

**M4 rdbcomm server_opts.tls_algorithm 死字段**
- `rdbcomm/server.h:16` 定义、`rdbcommd-main.c:330` 解析赋值，`server.c` 无任何消费点。删除，或接入 H1 的服务端算法白名单校验。

**M5 字节序约定不统一**
- libobk 握手 body 主机序 memcpy（`libobk.c:158,183-184`、`oracleCmdTbl.c:101-102,116-117,864-865`）；dmsbtex/rpc/rdbcomm 均网络序（htons / POKE_U16 大端）。当前 x86/ARM 小端互操作无害，但协议未规定字节序，大端平台必坏。libobk 应改网络序并写入协议文档。

### LOW

**L1 默认值双保险硬编码** — `rdbcomm/client.c:78-79` 在 tls_algorithm==0 时再兜底 SM4；uint16_t 无法区分"未设置"与 DEFAULT(0)，与 `RPC_TLS_ALGORITHM_DEFAULT`(libs/common.h:17) 语义重复。

**L2 服务端握手忽略本端 mtls_enabled** — `dmsbtex/network.c:234 (void)cfg;`；`rdbcommd-main.c:355` ctx 构建硬编码 mtls_enabled=1。注释表明"按需 mTLS"是有意设计，但 cfg 传而不用属接口噪音。

**L3 LSP 陈旧索引** — `libs/rpc-handshake.h`、`rdbcomm/handshake.h` 已不存在，clangd 缓存仍报 typedef 重定义；清理 `.cache/` 即可，非代码问题。

---

## 规范轴（PRD 十条线索逐条裁决）

| # | 线索 | 裁决 | 备注 |
|---|------|------|------|
| 1 | 枚举五处重复 | 确认 | 补充映射函数四份（M1） |
| 2 | strstr 子串匹配 | 确认 | "sm2"→SM4 有测试固化（H3） |
| 3 | 协商语义分裂 / dm_hs_decide 未接线 | 确认 | 细化为三种语义 + flags 无法装进帧格式（H4） |
| 4 | 服务端不校验算法合法性 | 确认并升级 | 叠加 find_slot NULL 回落 slots[0]，影响超预期（H1） |
| 5 | atoi fail-open | 确认 | H2 |
| 6 | 配置层级不一致 | 确认 | M3 |
| 7 | rpc OK_PLAIN 降级路径 | 确认 | 客户端有兜底 abort（M2） |
| 8 | 字节序不统一 | 确认 | 当前小端平台无害，协议缺陷（M5） |
| 9 | client.c 双保险默认 | 确认 | 降级 LOW（L1） |
| 10 | (void)cfg 忽略本端开关 | 确认 | 有意设计，降级 LOW（L2） |

新增发现：find_slot 空回落（N1→H1 核心）、server.tls_algorithm 死字段（N2→M4）、ERR_ALGORITHM 错误码从未使用（N3→H1）、rdbcomm 协议无显式 mtls_request flag、"发握手帧=要求加密"为隐含语义（N4→H4）、LSP 陈旧索引（N5→L3）。

---

## 风险评级

- HIGH ×4（H1-H4）：参数校验缺失与语义分裂，均已在代码层验证可达
- MEDIUM ×5（M1-M5）
- LOW ×3（L1-L3）

最严重问题：H1 —— 三模块服务端对客户端算法值零校验，叠加 `tls_cert_find_slot` 空回落，协商协议形同虚设。

## 建议（按优先级）

1. 服务端算法白名单校验（H1+M4+N3 一并解决，四模块对称修改）
2. SBT_MTLS_ENABLE 解析改 sec_resolve_int，非法值 fail-closed（H2）
3. 算法名 strcmp 精确匹配，修正固化 "sm2" 行为的测试（H3）
4. PDCA 立项统一协商语义与枚举单一来源（H4+M1，跨模块重构建议独立任务）
5. libobk 握手 body 改网络序（M5，需同步对端，属破坏性协议变更需评审）
