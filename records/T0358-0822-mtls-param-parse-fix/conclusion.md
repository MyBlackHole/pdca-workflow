---
schema: pdca.asset/v1
id: T0358-0822-mtls-param-parse-fix
phase: check
source_ids: [evidence-test]
---

## 上下文

T0348 审查发现的 H2（atoi fail-open）/H3（strstr 宽松匹配）修复。用户终审批准双 fail-closed 策略：mtls 开关非法值拒绝启动、算法名未知名加载时拒绝。bugfix 场景 TDD 红→绿执行。

## 假设与结果

| 假设 | 结果 |
|---|---|
| atoi 是静默明文根因，严格解析可消除 | 成立：dmsbtex/libobk 初始化对非法值返回 -1，调用方退出 |
| strstr/别名是错误 profile 静默命中根因 | 成立：rpc 版实为 strcmp+显式别名（sm2/ed25519），其余三份为 strstr；全部收敛为规范名精确匹配 |
| 未知名可在配置加载时拦截（早于协商） | 成立：dmsbtex/libobk init 内校验；rdbcomm/rpc 四个工具入口 env/ini 路径校验后 exit=1 |

## 分析

- **AC-1 通过**：`SBT_MTLS_ENABLE=abc` 等 5 组非法值 → `sbt_client_tls_config_init`/`sbt_tls_config_init` 返回非 0 并输出期望格式告警；调用方 libobk.c:458 / dmsbtex main.c:125 均已检查并终止。
- **AC-2 通过**：四份映射函数（msg.c、protocol.c×2、rpc-protocol.cpp）统一 strcmp 规范名全串匹配；测试覆盖子串污染名（TLS_SM4_GCM_SM3X）、别名（sm2/SM2/ed25519）、空串、NULL。
- **AC-3 通过**：全量构建 ok；六套测试 PASS（四套会话/握手 + mixed_mtls_integration 含 no-downgrade/plains-only 场景）；工具端到端 RDBCOMM_TLS_ALGORITHM=sm2 与 AIO_SPEEDD_TLS_ALGORITHM=x 均 exit=1。

Grill 自检：
1. 关键路径覆盖——客户端与服务端、env/ini/CLI 三入口均已覆盖；CLI 路径原 getopt 已严格校验无需改动。
2. 行为变更风险——依赖 "sm2"/"ed25519" 别名的部署会从静默映射变为启动失败；这是 fail-closed 设计意图，发布说明需标注。
3. **新发现（范围外）**：共享底座 `libs/rdb-config.c:203` `sec_resolve_int` env 层同为 atoi——rdbcomm/rpc 工具的 `RDBCOMM_MTLS_ENABLE=abc` 仍宽松解析为 0（fail-open）。该函数为通用 int 解析器无错误通道，修改影响所有调用方，超出本任务已批准范围。建议并入 T0357 或单独小任务处理。

## 适用边界

- 仅覆盖 dmsbtex/libobk 的 mtls env 解析与四模块算法名映射；sec_resolve_int 底座缺陷未修（见新发现）
- 协商协议帧格式与白名单校验属 T0357/T0359 范围

## 下一轮建议

1. sec_resolve_int env 层 atoi 缺陷并入 T0357 处理（或新增专用 bugfix 任务）
2. 发布说明标注：算法别名（sm2/SM2/ed25519）不再被协商层接受；SBT_MTLS_ENABLE 仅接受 "0"/"1"

## Verdict

- verdict_id: V-T0358-20260822-01
- outcome: confirmed
- reason: 三条 AC 全部通过且有测试证据（evidence-test sha256:361cbec9）；TDD 红→绿纪律完整；一处范围外新发现已登记并给出跟进建议
- at: 2026-08-22T20:43:13+08:00
