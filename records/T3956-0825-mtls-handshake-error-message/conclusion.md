---
schema: pdca.asset/v1
id: T3956-0825-mtls-handshake-error-message
phase: check
source_ids: [ac1-user-repro, e2e-matrix, hs-err-test, rdbcomm-session-test, dmsbtex-session-test, libobk-session-test, mixed-mtls-integration, rpc-own-handshake-test, grep-bare-result]
---

## 上下文

用户报告：服务端开启 mTLS 强制模式后，未启用 TLS 的客户端连接被拒，但报错只有 `result=0x8004` 十六进制码、退出码为无意义的 252，要求同时检查其他工具同类问题。Triage 验证确认四模块（rpc/libobk/rdbcomm/dmsbtex）客户端均存在报错不可读或静默失败，任务按 bugfix 路径执行（commit b531ec02）。

## 假设与结果

| 假设 | 结果 |
|------|------|
| 四模块拒绝路径接入统一 hs_err_str 后，客户端输出可读英文文案 | 成立：aio-speed 实测输出 "server requires mTLS but client TLS is disabled; enable tls and cert_dir in client config (mTLS required)" |
| rpc 退出码固定 -2（shell 254）可稳定复现 | 成立：原始场景 exit=254；e2e S4 断言通过 |
| 码表归一至 libs/common.h + 别名宏可保持运行时值不变且全量编译通过 | 成立：全量 xmake 通过，四模块 session/集成测试无回归 |

## 分析

- **AC-1** ✅ aio-speed 明文连强制 mTLS 服务端：stderr 含 "mTLS required" 可读指引、无裸 result=0x、exit=254（ac1-user-repro、e2e-matrix S4）
- **AC-2** ✅ hs_err_test 覆盖 0x8001~0x8008 全部码值（含关键短语断言）、OK_PLAIN/OK_MTLS 及未知码 "unknown" 提示，全部通过（hs-err-test）
- **AC-3** ✅ rdbcomm 由 e2e S17 直接断言拒绝日志含 "mTLS required" 且业务未执行；dmsbtex/libobk 拒绝分支已接入 dm_hs_err_str/obk_hs_err_str 并随 session test 行为验证通过——注意：dmsbtex/libobk 的日志内容为代码级+码表单测间接覆盖，未做端到端日志文本断言（rdbcomm-session-test、dmsbtex-session-test、libobk-session-test（静默设计 exit=0）、e2e-matrix）
- **AC-4** ✅ 正常象限无回归：e2e 17/17（S1/S2/S3/S7/S8/S16 等）、mixed_mtls_integration AC1-7、rpc_own_handshake_test ALL PASS（mixed-mtls-integration、rpc-own-handshake-test、e2e-matrix）
- **AC-5** ✅ grep 四模块客户端源码唯一残留为 hs_err_str 内部 unknown 分支（设计内：未知码需携带原始码诊断）（grep-bare-result）

Grill 追问结论可靠性：
1. dmsbtex/libobk 日志文本无端到端断言是否削弱 AC-3？→ 文案生成函数已由 AC-2 单测锁定，接入点位于拒绝分支内且构建/行为测试通过，风险低；已如实标注间接性。
2. rpc-io.cpp 分支合并（删除降级独立文案）是否改变行为？→ 唯一调用点 rpc-io.cpp:189 且函数入口 mtls_enabled=0 提前返回，被删分支不可达；rpc_own_handshake_test "client mtls rejected downgrade to plain" 用例覆盖该语义。
3. 退出码变更是否会破坏既有脚本？→ 原值 -32772→252 为随机截断无稳定语义，不存在合理依赖；新值 254 已文档化于 rpc-client.h 注释与 PRD。

## 适用边界

- 适用于四模块当前码集（0x8001~0x8008 与 OK_PLAIN/OK_MTLS）；新增握手错误码需同步扩展 libs/common.h 定义与 hs_err_str case，否则落入 unknown 提示（仍非裸码）。
- rpc 工具退出码约定 254 仅适用于 aio-speed 等 RPC CLI；libobk/rdbcomm/dmsbtex 库 API 返回值维持 -1 约定不变。
- 不覆盖服务端侧报错（服务端文案本就可读）与协议帧格式演进。

## 下一轮建议

- 可选跟进：dmsbtex/libobk 补充端到端日志文本断言（捕获 ErrorLog 输出）使 AC-3 三模块证据强度对齐。
- 可选跟进：libs/tests/rpc_handshake_test.c 为引用已删除头文件的死代码，可在清理类任务中移除。
- 0823 评审遗留的"四套错误码定义归一"已由本任务实质落地（common.h 单一定义+别名），后续新增模块直接引用 common.h 即可。

verdict: {"outcome": "confirmed", "reason": "用户确认五条 AC 判定与证据强度如实（含 AC-3 dmsbtex/libobk 间接验证标注），修复效果与回归结论成立", "verdict_id": "T3956-check-v1", "at": "2026-08-25T11:03:00+08:00"}
