---
schema: pdca.asset/v1
id: T3970-0826-oss-https-opt-in
phase: check
source_ids: [runtime-ac1-ac4, unit-test-result, build-regression, convergence-map]
---

## 上下文

aio-oss 此前为强制 HTTPS（T0368），证书缺失即服务不可启动，无证书环境完全不可用。T3970 将 HTTPS 改造为可选开关：默认明文 HTTP，显式配置（CLI/env/rdb.conf 四层）后才启用 HTTPS 且保持 fail-closed。提交 a72580d9。

## 假设与结果

- 假设 1：在既有 chooseStr 4 层模型上增加开关解析链即可满足"默认 HTTP + 参数开启"，无需改动证书构建逻辑 → 成立。`buildServingTLS` 零改动，仅在 `serverMain` 前置分发。
- 假设 2：urfave/cli v3 的 BoolWithInverseFlag 可表达三态开关 → 成立。`--tls/--no-tls` + IsSet 区分未设置/显式开/显式关，vendor 内 API 已确认可用。
- 假设 3：HTTP 模式可完全跳过 TLS 链路而不破坏 fail-closed 语义 → 成立。fail-closed 仅作用于显式开启路径（AC-3 运行时复验 exit=1）。

## 分析

- **AC-1** ✅ 默认启动（无任何开关配置）为明文 HTTP：GET=200 且日志含 `listening HTTP on ":18101"`（runtime-ac1-ac4）
- **AC-2** ✅ `--tls` + 证书齐备：TLS 握手 GET=200、同端口明文请求被拒(400)，日志 `listening HTTPS`（runtime-ac1-ac4）
- **AC-3** ✅ 显式开 HTTPS 但证书缺失：进程 exit=1，错误含"加载证书/私钥失败"，fail-closed 保持（runtime-ac1-ac4）
- **AC-4** ✅ 四层优先级：env 开启生效、`--no-tls` 压过 env、rdb.conf 全局段/工具段生效且工具段优先；另验证可疑假值(ture)告警不误报合法 false（runtime-ac1-ac4）
- **AC-5** ✅ `go test ./cmd` 全绿(11 PASS，含新增 TestParseEnableStr/TestResolveTLSEnabled/TestServeHTTPPlain)、`xmake build aio-oss` 成功、build_oss.sh 回归 ALL PASS（unit-test-result / build-regression）

备注：PRD AC-5 文本写 `xmake build oss` 为笔误——仓库目标名已由工作区既有改动改为 `aio-oss`（本提交一并纳入并同步修复 build_oss.sh 的旧目标名调用，经用户批准）。等价性无争议：同一 target 的构建回归。

## 适用边界

- 结论仅适用于 oss/cmd 服务端启动链路；客户端 TLS、sm2 国密、双端口并存、mTLS 不在范围内
- "默认 HTTP"的破坏性变更以内部 emulator、部署方可控为前提；对外产品化场景需重新评估默认值
- Go 标准库不支持 sm2 证书的前提沿用 T0368，若引入国密 TLS 库需重新设计

## 下一轮建议

- T3972（已创建）：aio-oss Go 单测接入 xmake test 架构，使本任务新增用例进入 CI 测试链
- 存量加密部署迁移文档：在部署手册标注 --tls 参数与 rdb.conf 开关键的对应关系
- 历史遗留清理：T0259(0814-oss-https-support) 状态 Pending 但功能已被 T0368 覆盖，建议关闭归档

## verdict

{"outcome": "confirmed", "reason": "单元/构建/运行时验证全部通过，AC-1~AC-5 逐条证据支撑，收敛校验 valid=True，审查 Warning 已修复复验", "verdict_id": "T3970-0826-oss-https-opt-in-check", "at": "2026-08-26T11:14:30+08:00"}
