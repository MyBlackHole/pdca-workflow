# T0348 — rdbcomm/sbt/dmsbt/rpc 四模块 mTLS 状态参数与算法参数审查

## 问题陈述

- **现状**: mTLS 开关（mtls_enabled）与算法参数（tls_algorithm）在四个模块中各自解析、各自定义协议枚举，设置链路与协商语义已出现分裂；部分模块存在宽松解析与未校验透传。
- **目标**: 产出一份带 file:line 证据的审查报告，按严重度分级列出问题并给出修复方向。
- **差距**: 此前任务分散修复各模块握手（0819-dmsbtex-libobk-mtls、0808-sbt-mtls-simplify 等），从未横向比对四模块参数链路的一致性。

## 审查范围

| 模块 | 路径 | 参数入口 |
|------|------|---------|
| rpc | `rpc/rpc-config.cpp` `rpc-server.cpp` `rpc-io.cpp` | sec_resolve_int/str + CLI |
| rdbcomm | `rdbcomm/rdbcomm-main.c` `rdbcommd-main.c` `client.c` `server.c` `msg.c` `io.h` | sec_resolve_* + CLI |
| dmsbtex | `dmsbtex/network.c` `protocol.c/h` `main.c` | getenv + sec_resolve_str |
| sbt(libobk) | `libobk/lib/sbt/libobk.c` `lib/logic/oracleCmdTbl.c` `include/protocol.h` | getenv + sec_resolve_str |

## 已验证的问题线索（triage 阶段代码证据）

1. **枚举五处重复**：`RDB_HS_ALG_*`(rdbcomm/io.h:17) `DM_HS_ALG_*`(dmsbtex/protocol.h:93) `HS_ALG_*`(rpc/rpc-protocol.h:87) `OBK_HS_ALG_*`(libobk/include/protocol.h:73) + 名称映射函数四份，协议值 1=SM4_GCM_SM3 / 2=AES_256_GCM_SHA384 靠人工对齐。
2. **strstr 子串匹配算法名**（四份映射函数同病）：`"sm2"` 命中 SM4（rpc/tests 固化该行为）；匹配顺序依赖；配置笔误静默命中。
3. **协商语义三种并存**：rpc 服务端"优先客户端算法+非法回落"；其余三模块"无条件采纳客户端算法"；dmsbtex 的 `dm_hs_decide()` 决策树已实现但 network.c 未接线。
4. **服务端不校验客户端算法合法性**：libobk oracleCmdTbl.c:860 与 rdbcomm server.c:490 收到任意 u16 直接使用；仅 rpc-server.cpp:246 校验+回落。
5. **atoi 解析 mtls_enabled**（fail-open）：dmsbtex/network.c:104、libobk.c:74 —— `"SBT_MTLS_ENABLE=abc"` 静默禁用 mTLS。
6. **配置层级不一致**：sbt/dmsbtex 算法只读 [security] 全局段；rpc/rdbcomm 另支持 [tool] 段覆盖。
7. **rpc 独有明文降级路径**：rpc-server.cpp:317 want_mtls+无证书上下文回 HS_OK_PLAIN（其余三模块无降级）。
8. **字节序不统一**：libobk 握手 body 主机序 memcpy（libobk.c:158,183）；其余三模块网络序（POKE_U16 大端 / htons）。
9. **默认值双保险硬编码**：rdbcomm client.c:78 在 options->tls_algorithm==0 时再兜底 SM4。
10. **dm_server_handshake 忽略 cfg**（dmsbtex/network.c:234 `(void)cfg;`）：服务端握手不看本端 mtls_enabled。

## 解决方案

review 场景：Do 阶段逐项核验上述 10 条线索（含 LSP 新暴露的 `libs/rpc-handshake.h`、`rdbcomm/handshake.h` typedef 重定义），补充遗漏点，产出结论报告。

### 声明的测试接缝

review 场景无测试产物，跳过。

## 验收标准

- [ ] AC-1: 报告覆盖四模块全部 mtls_enabled/tls_algorithm 设置、传递、消费点，每条发现附 file:line 证据
- [ ] AC-2: 发现按严重度分级（高危/中危/低危），每条给出修复方向
- [ ] AC-3: 对 10 条 triage 线索逐条给出"确认/证伪/修正"结论

## 范围外

- 不修改任何代码
- 不审查证书内容本身（cert/key 文件有效性）
- 不审查 payload 层 data_encrypt 对称加密（另有 crypt 体系）

## 备注

- 用户澄清记录：原始路径 `rdbcomm\sbt\dmsbt\rpc` 不存在，经确认范围为上表四模块
- 结论确认不设独立 AC：由 Check 阶段 Ch5 verdict + `check_confirmation` 门禁原生承载（Do 阶段无该交付物）
