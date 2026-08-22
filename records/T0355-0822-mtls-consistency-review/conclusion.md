---
schema: pdca.asset/v1
id: T0355-0822-mtls-consistency-review
phase: check
source_ids: [review-report]
---

## 上下文

以 rpc 模块（aio-speed 工具链）为基准，按 7 维度（协议常量/协商状态机/无降级策略/配置优先级链/TLS 构建时机/失败路径与资源清理/错误码语义与日志）审查 rdbcomm、sbt（libobk）、dmsbtex 三模块 mTLS 模式实现逻辑一致性。产出 `review-report.md`（evidence: review-report，digest sha256:37bfc2…3172）。

## 假设与结果

- 假设 H1：三待审模块 mTLS 实现与基准存在偏差 → **成立**。发现 2 CRITICAL + 4 HIGH + 4 MEDIUM。
- 假设 H2：核心安全语义（无静默降级/强制拒明文/按需握手/重复握手防护）一致 → **成立**，四模块同构。
- 假设 H3（triage 摸底）：rdbcomm 存在调用未声明函数缺陷 → **不成立**。LSP 报的 `rpc_hs_session_cleanup` 在当前源码无命中（grep exit=1），为过期诊断；实际符号均为 `rdb_hs_session_cleanup`。

## 分析

关键确凿发现（数值经编译验证 sizeof(activeioHeader)=30）：

1. **C1（CRITICAL）**：libobk 客户端 `sbt_session_client_init` 中 resp[205] 被 `_recv(expect=235)` 写满 → 栈溢出 30 字节。
2. **C2（CRITICAL）**：客户端校验 body 长度 175 vs 服务端发送 h.bytes=205 → libobk mTLS 握手成功路径必败；且服务端从 buf[204] 发送 205 字节越界读 1 字节。测试缺口：session_test 仅覆盖配置解析与 IO 原语，无完整握手往返。
3. **H1–H4**：无 ctx 错误码分歧（UNAVAILABLE vs REQUIRED）；dmsbtex/sbt ca_cn 失败不回错误帧；明文帧拒绝响应方式三样；启动 fail-open/fail-closed 策略分歧且 rdbcommd 自相矛盾。
4. **M1–M4**：dm_hs_decide 死代码且与手写逻辑语义漂移；三模块客户端握手失败静默无诊断日志（违反 structured-mtls-failure-diagnostics 规则）；mtls 开关缺 ini 层级；死分支。
5. 合理差异（不计偏差）：MT_GET_TIME 未握手白名单仅基准需要（时间同步），其余三模块无此需求属合理裁剪。

逐条 AC 判定：

| AC | 判定 | 证据 |
|----|------|------|
| AC-1 | pass | review-report 含 rdbcomm×12、dmsbtex×17、sbt 多处命中；conclusion 同构覆盖 |
| AC-2 | pass | 比对矩阵 D1–D7 × 3 模块全覆盖，含 ✅/⚠️/❌ 判定 |
| AC-3 | pass | C1/C2/H*/M* 均引用源码符号（sbt_session_client_init/hs_send_frame/dm_hs_decide/send_handshake_resp 等），已 grep 复核命中 |
| AC-4 | pass | 每项偏差带 高/中/低 或 CRITICAL/HIGH/MEDIUM 评级 + 修复建议；verdict=fail |

## 适用边界

- 结论适用于当前 commit 的代码状态；C1/C2 数值依赖 pack(1) 下 activeioHeader=30 字节，结构体变更需重算。
- dmsbtex 客户端 sbt_session_client_init 仅测试可达（生产为服务端程序），其客户端侧偏差影响面小于服务端侧。
- 审查限于 mTLS 模式实现逻辑，未覆盖证书生成管理与非 mTLS 加密通道（范围外）。

## 下一轮建议

1. 立即修复 C1/C2（body 长度常量单点化 + 缓冲区扩容），并补 libobk 客户端↔服务端真实 TLS 往返集成测试。
2. ADR 裁决 H4 启动策略后四模块统一；统一 H1 错误码语义与 H2/H3 错误帧响应。
3. 后续任务收敛四模块重复的握手客户端实现（Duplicated Code 已实际引发 C1/C2 类缺陷）。

## verdict

- verdict_id: V-T0355-check-01
- outcome: confirmed
- reason: 审查结论经数值复核与 grep 符号回溯验证成立；核心判定"三模块与基准存在多处偏差，其中 libobk mTLS 握手路径不可用且含内存安全缺陷"证据充分。outcome=confirmed 表示审查结论本身可信成立（结论内容为 fail 判定，指向被审代码需修复）。
