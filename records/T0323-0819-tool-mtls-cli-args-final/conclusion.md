---
schema: pdca.asset/v1
id: T0323-0819-tool-mtls-cli-args-final
phase: check
source_ids: [full-build, full-test, implementation-review, convergence-map]
---

## 上下文

本任务审查并补齐 `rdbcomm`、`rdbcommd`、`aio-speed`、`aio-speedd` 的 mTLS 开关与 TLS 算法命令行参数支持。

## 假设与结果

- AC-1：通过。四个工具 help 均说明 `--mtls-enable=0|1`、`--tls-algorithm=...`、合法值、默认值、配置优先级和使用案例。
- AC-2：通过。CLI 覆盖状态在工具启动时注入共享配置解析层，并优先于环境变量、配置段和默认值。
- AC-3：通过。非法 mTLS 值和算法值均由具体工具明确报错并返回失败状态。
- AC-4：通过。RPC 与 rdbcomm 真实工具集成测试覆盖明文、AES mTLS、SM4 mTLS 以及证书异常场景。
- AC-5：通过。全量构建成功，`xmake test -v` 结果为 36/36，通过且未修改协议帧和业务帧逻辑。

## 分析

共享宏和配置 setter 将参数解析与 TLS 初始化解耦，四个工具保持独立工具配置项，同时使用统一的算法枚举和值校验。测试证明新增参数不会破坏既有时间获取、明文握手和 mTLS 握手路径。

## 适用边界

CLI 覆盖是进程级启动配置，适用于工具单次启动的客户端或服务端进程；证书路径、`ca_cn` 和协议握手流程仍由既有配置及握手实现负责。

## 下一轮建议

将这组 CLI 参数及优先级规则纳入后续工具模板和新工具接入检查清单，避免新增工具遗漏 help、宏和非法值测试。

## Verdict

- outcome: confirmed
- verdict_id: V0323-0819-tool-mtls-cli-args-final-check
- reason: 用户已确认 Check 结论；全部验收标准均有构建、测试或审查证据支持。
- at: 2026-08-19T09:57:47+08:00
