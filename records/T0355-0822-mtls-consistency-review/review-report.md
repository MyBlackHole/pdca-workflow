# Review Report — rdbcomm/sbt/dmsbtex mTLS 模式与 rpc 实现逻辑一致性审查

- 任务: T0355 / 记录 T0355-0822-mtls-consistency-review
- 基准: `rpc` 模块（aio-speed 工具链，rpc-server/rpc-client/rpc-io）
- 待审: `rdbcomm`、`dmsbtex`、`sbt`（libobk/lib/sbt + libobk/lib/logic 服务端）
- 日期: 2026-08-22

## 一、审查范围

以 rpc 为基准，按 7 个维度比对三模块 mTLS 模式实现逻辑：

1. 协议常量（flags 位、结果码数值）
2. 协商状态机/决策函数
3. 无降级策略
4. 配置优先级链
5. TLS 构建时机与启动行为
6. 失败路径与资源清理
7. 错误码语义与日志行为

## 二、比对矩阵

判定：✅ 一致 ／ ⚠️ 部分偏差 ／ ❌ 偏差（Blocking 级另列）

| 维度 | rdbcomm | dmsbtex | sbt (libobk) |
|------|---------|---------|--------------|
| D1 协议常量数值 | ✅ RDB_HS_OK_MTLS=3、0x8004/0x8006/0x8008 同构 | ✅ DM_HS_* 同构 | ✅ OBK_HS_* 同构 |
| D2 协商状态机 | ⚠️ 无 flags 校验；算法直接采纳 halg，无"非法回落服务端配置" | ⚠️ 手写 dm_server_handshake；dm_hs_decide 死代码且语义漂移 | ❌ 握手帧长度校验必败（见 C2） |
| D3 无降级策略 | ✅ 客户端非 OK_MTLS 即失败；强制模式拒明文业务帧 | ✅ 同左 | ✅ 同左（但成功路径不可达，见 C2） |
| D4 配置优先级链 | ✅ CLI > ini(tool/global) > env > default，同构基准 | ⚠️ mtls 开关仅 env 直读 getenv；其余参数 ini(global) > env | ⚠️ 同 dmsbtex |
| D5 TLS 构建时机/启动行为 | ⚠️ mtls=1 且 init 失败→退出；mtls=1 且 cert_dir 空→警告继续（自相矛盾） | ⚠️ 强制模式 init 失败→退出（fail-closed，与基准 fail-open 分歧） | ⚠️ 同 dmsbtex |
| D6 失败路径/资源清理 | ✅ cleanup 覆盖握手失败/INIT 失败/连接销毁 | ✅ cleanup + ctx cleanup 成对 | ✅ 成对（但 _recv 栈溢出，见 C1） |
| D7 错误码语义/日志 | ⚠️ 明文帧拒气回通用 FAILURE 状态码；客户端握手失败静默无日志 | ⚠️ ca_cn 不可用不回错误帧直接断开；客户端失败静默 | ⚠️ 同 dmsbtex；另有死分支 |

四模块一致项：协议常量数值同构、按需握手（明文零握手直通）、重复握手防护断开、会话 plain/tls/cleanup 三件套生命周期。

合理差异（不计偏差）：基准的 MT_GET_TIME 未握手白名单豁免源自时间同步需求（历史任务 rpc-handshake-time-adapter），rdbcomm/dmsbtex/sbt 无 TIME 操作，故无白名单属合理裁剪。

## 三、规范轴发现（对照基准实现逻辑）

### Blocking（CRITICAL）

**C1 — sbt 客户端握手响应读取栈缓冲区溢出**
- 位置：`sbt_session_client_init`（libobk/lib/sbt/libobk.c:162）
- `char resp[4+201]`（205 字节）被 `_recv(io, resp, sizeof(activeioHeader) + sizeof(resp), NULL)` 读入 30+205=235 字节（`_recv` 循环写满 expect，见 oracleCmdTbl.c `_recv` 实现），栈溢出 30 字节。
- 评级：CRITICAL（内存安全）。修复：resp 扩容为 `sizeof(activeioHeader) + 205`，再前移 body。

**C2 — sbt mTLS 握手成功路径必败 + 服务端越界读**
- 客户端校验 `ph->bytes != sizeof(resp) - sizeof(activeioHeader)` 即期望 body=175 字节（libobk.c:167）；服务端发送 `hs_send_frame(..., resp, 4 + 201)` 即 h.bytes=205（oracleCmdTbl.c:119）。175≠205 → 客户端必 goto error，mTLS 升级永不成功。
- 同时服务端 `char resp[4+200]`（204 字节）却发送 205 字节 → `_send` 越界读 1 字节。
- 存活原因：libobk/test/session_test.c 仅覆盖配置解析与会话 IO 原语，无客户端↔服务端完整握手往返测试。
- 评级：CRITICAL（功能不可用 + 越界读）。修复：统一 body 长度为 4+200 或 4+201 单一常量，两端共用同一宏；补齐真实往返集成测试。

### HIGH

**H1 — "服务端无 TLS ctx"错误码语义分歧**
- 基准：强制模式下无 sctx 回 `HS_ERR_MTLS_REQUIRED`(0x8004)（rpc-server.cpp 握手分支）；三待审模块一律回 `*_ERR_MTLS_UNAVAILABLE`(0x8008)。
- 影响：跨模块排障语义不统一——REQUIRED 表达"策略拒绝"，UNAVAILABLE 表达"能力缺失"，二者混用会误导运维定位。评级：HIGH。建议：明确 0x8008 仅用于"非强制但请求了 mTLS 且无能力"场景，强制模式统一回 REQUIRED。

**H2 — dmsbtex/sbt ca_cn 不可用时不回错误帧**
- 基准与 rdbcomm 均回专门错误帧（HS_ERR_CA_CN / RDB_HS_ERR_CA_CN）；dmsbtex `dm_server_handshake` 与 libobk `sbt_session_server_handshake` 仅记日志后 return -1，客户端只见连接关闭，无法区分失败类别。评级：HIGH（可诊断性）。建议：对齐回 CA_CN 帧。

**H3 — 明文业务帧防护响应方式分歧**
- 基准：回 `HS_ERR_MTLS_REQUIRED` 帧（rpc-server.cpp 明文帧防护段）；rdbcomm：回通用 `RDBCOMM_MSG_FAILURE` 状态（server.c 明文帧防护段）；dmsbtex/libobk：直接断开无任何响应（main.c / oracleCmdTbl.c 各自防护段）。
- 影响：客户端无法程序化识别"因 mTLS 策略被拒"。评级：HIGH。建议：三模块统一回各自协议内定义的 ERR_MTLS_REQUIRED 载荷。

**H4 — 启动行为策略分歧且 rdbcomm 自相矛盾**
- 基准：证书 init 失败 → WarningLog 继续启动，明文服务 + 握手期自然拒绝（main.cpp cert 加载段注释明示该设计）。
- rdbcomm：mtls=1 且 init 失败 → 退出；但 mtls=1 且 cert_dir 为空 → 仅 Warning 继续（运行时全拒）。同一失败域两种策略。
- dmsbtex/libobk：强制模式 prepare 失败 → 进程退出。
- 评级：HIGH（部署行为可预期性）。建议：ADR 裁决"启动 fail-closed 还是握手期 fail-closed"，四模块统一。

### MEDIUM

**M1 — dm_hs_decide 死代码且语义漂移（dmsbtex）**
- `dm_hs_decide`（protocol.c）定义了纯决策逻辑（含 server_mtls&&!client_mtls→ERR_MTLS_REQUIRED），但生产路径 `dm_server_handshake` 手写等价逻辑未调用它，且手写版不检查客户端 flags（任何 HANDSHAKE 都尝试升级）。未来若有人"清理"为调用 decide 将产生行为变化。OBK 协议头同样复制了 `OBK_HS_F_MTLS_REQUIRED` 但全仓无消费方。评级：MEDIUM。建议：删除或真正接线，二选一。

**M2 — 三模块客户端握手失败静默返回 -1**
- dmsbtex `sbt_session_client_init`、libobk `sbt_session_client_init`、rdbcomm client 握手段均以 fail 标志聚集后直接 return，无 ErrorLog；违反知识库 structured-mtls-failure-diagnostics 规则（应记录 role/stage/algorithm/ca_cn）。基准 rpc 客户端含 cert_dir/ca_cn/algorithm/fd 详细诊断。评级：MEDIUM。建议：每个 goto error/fail 分支补充分类日志。

**M3 — mtls 开关配置链层级缺失（dmsbtex/sbt）**
- 两模块 mtls 开关仅 `getenv(SBT_MTLS_ENABLE)`；而同函数内算法/证书路径已走 `sec_resolve_str(ini>env)`。基准与 rdbcommd 为 CLI>ini>env 全链。ini 中开启 mTLS 对这两模块无效，易造成"配置了但不生效"。评级：MEDIUM。建议：改用 sec_resolve_int 对齐。

**M4 — libobk 死分支**
- `alg_name = result ? obk_hs_algorithm_name(halg) : ctx->tls_algorithm_name`（libobk.c:179）：此处 result 已恒等于 OK_MTLS，else 支不可达。评级：LOW-MEDIUM。顺手修复。

## 四、标准轴发现（编码质量基线）

- libobk C1/C2 同时是标准轴内存安全硬违规（缓冲区边界、长度常量单点化缺失）。
- dmsbtex/libobk 的握手客户端实现大量复制粘贴（sbt_client_cert_paths、config init 几乎逐行相同），Duplicated Code 坏味——本次 C1/C2 的长度不一致正是复制后单侧修改的典型后果。建议后续任务收敛共享握手层（历史已有 unified-first-stage-protocol 方向）。
- rdbcomm/dmsbtex/libobk 会话三件套（init_plain/init_tls/cleanup）结构良好，与基准分层一致。

## 五、架构备注

四模块当前为三套独立握手承载：rpc（MT_HANDSHAKE 业务帧）、rdbcomm（buf 消息层 RDBCOMM_MSG_HANDSHAKE）、dmsbtex（network_header_t CMD_HANDSHAKE）/libobk（activeioHeader active_handshake）。部署上 libobk↔libobk 自成体系、dmsbtex 独立服务，互不为对端；但"统一第一阶段协议"的知识资产（unified-first-stage-mtls-time）在 SBT 侧尚未落地，协议常量同构仅停留在枚举层面。

## 六、结论 verdict

- 核心安全语义（无静默降级、强制模式拒明文、按需握手、重复握手防护）四模块一致。
- 但存在 2 项 CRITICAL（C1/C2，均在 libobk 握手路径）、4 项 HIGH、4 项 MEDIUM 偏差。
- 门禁判定：**fail（Blocking = 2）** —— libobk mTLS 模式实际不可用且含内存安全缺陷；修复 C1/C2 并对齐 H1–H4 后需复审。
