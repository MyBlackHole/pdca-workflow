# mTLS 参数链路审查发现 — 四模块横向一致性陷阱

> 来源：T0348-0822-mtls-state-alg-review（2026-08-22），适用 rdbcomm / libobk(sbt) / dmsbtex / rpc 及一切复用 `libs/tls_cert.c` 的新模块。

## 陷阱 1：tls_cert_find_slot 对空算法回落 slots[0]

`libs/tls_cert.c:366-368`：`algorithm == NULL || ""` 时静默回落第一个 profile。

后果：上层若把未经校验的协商值透传给 `tls_cert_get_ca_cn()` / `tls_cert_server_handshake()`，映射函数返回 NULL → find_slot 回落 slot[0] → ca_cn 查询成功、TLS 用默认 slot 算法完成——**协商字段完全失效**，多 profile 下实际算法由 slot 加载顺序决定。

规则：**服务端必须在入口处白名单校验客户端算法枚举值**（仅接受已知 ID），非法即回显式错误码；不得依赖下游 NULL 兜底。

## 陷阱 2：安全开关用 atoi 解析 = fail-open

`getenv("SBT_MTLS_ENABLE") + atoi(v)`（dmsbtex/network.c:104、libobk.c:74）：`"abc"`→0 静默禁用 mTLS，备份数据明文传输；`"1x"` 又被启用。

规则：安全布尔开关统一走 `sec_resolve_int` 或严格 strtol 校验，非法值 fail-closed（拒绝启动或显式告警）。

## 陷阱 3：strstr 匹配受控枚举名

四份 `*_hs_algorithm_from_name()` 均用子串匹配：`"sm2"` 命中 SM4_GCM_SM3 且被单测固化；配置笔误静默命中错误 profile，错误延迟到握手期。

规则：受控枚举名一律 strcmp 全串精确匹配；未知名显式报错而非返回 DEFAULT。

## 反模式：同一参数链路在各模块独立演化

同一 mtls_enabled/tls_algorithm 在四个模块出现：5 处枚举定义、4 份映射函数、3 种协商语义、2 种字节序约定。协议值靠人工对齐必然漂移。

规则：新增握手模块时，枚举与名称映射必须收敛到 libs 单一头文件；协商语义（决策树）选定唯一实现并接线，死代码删除。

## 已确认待修清单（T0348 报告）

| 级别 | 问题 | 关键位置 |
|------|------|---------|
| HIGH | 服务端零校验+slot 空回落 | oracleCmdTbl.c:860、server.c:490、network.c(dm):248 |
| HIGH | atoi fail-open | network.c:104、libobk.c:74 |
| HIGH | strstr 子串匹配 | msg.c:115、protocol.c:69、rpc-protocol.cpp:208、libobk protocol.c:17 |
| HIGH | 协商语义分裂+dm_hs_decide 死代码 | dmsbtex protocol.c:192 |
| MED | rpc OK_PLAIN 降级语义错位 | rpc-server.cpp:317 |
| MED | libobk 握手 body 主机序 | libobk.c:158,183 |

错误码 `*_HS_ERR_ALGORITHM(0x8005)` 各处已定义但从未使用——修复 H1 时直接可用。

## 补充（T0358 修复后遗留）

- **`sec_resolve_int` env 层仍是 atoi**（libs/rdb-config.c:203）：`RDBCOMM_MTLS_ENABLE=abc` 等经该底座解析的安全开关依旧 fail-open。该函数为通用 int 解析器无错误通道，修复需 API 变更——已决定并入 T0357。
- **TLS 配置结构体死字段模式**：tls-cert 重构收敛 cert_dir 唯一路径后，`ca_cn/ca_cert/server_cert/server_key` 在 rpc/dmsbtex/rdbcomm 三处结构体填充后零消费。清理任务 T0360。
- **修复范式（T0358 已落地）**：布尔安全开关 = strtol 全串校验仅收 "0"/"1"，非法返回 -1 拒绝初始化；算法名 = strcmp 规范名全串匹配 + 配置加载时白名单校验，未知名启动即失败。

## 补充 2（T0361 后定稿）

- **mtls 布尔开关统一 API**：`sec_resolve_bool(tool,tool_key,global,global_key,env,default)`——env/[tool]/[security] 三层严格 "0"/"1"，非法返回 **-1 错误哨兵**，调用方必须拒绝启动。六入口（rdbcomm/rdbcommd/aio-speed/aio-speedd/dmsbtex/libobk 客户端+服务端）已全部接入；通用 `sec_resolve_int` 保持 atoi 语义勿混用。
- **CLI 意图字段模式**：删除 set/enabled 双布尔；载体直接用消费字段（配置打底 → getopt 覆盖 → `<0` 校验）。
- **构建验证铁律**：删结构体成员/改头文件后，回归必须跑 `xmake test` 全量重建——增量构建对"测试文件未同步修改"静默放过旧二进制（T0360/T0361 连续两次中招）；审计 getenv 类解析点须按函数入口全量扫 `getenv`+`atoi` 组合，不能只 grep 结构体前缀。
