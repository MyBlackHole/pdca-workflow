---
schema: pdca.asset/v1
id: T0360-0822-tls-config-dead-fields
phase: check
source_ids: [evidence-cleanup]
---

## 上下文

T0358 Check 阶段用户指出工具 TLS 配置参数多余，grep 审计证实后立项清理。development 场景纯删除重构：五个结构体 22 个死字段 + 2 个 unused 函数。

## 假设与结果

| 假设 | 结果 |
|---|---|
| 死字段填充后全仓库零读取 | 成立并完成删除（净 -168 行） |
| 删除不影响行为 | 成立：六套测试回归 PASS，端到端校验行为未回归 |
| cert_dir/mtls/algorithm 为活跃字段需保留 | 成立：消费点逐一入册（evidence-cleanup.md） |

## 分析

- **AC-1 通过**：22 字段及关联填充代码全部删除，全量构建 ok
- **AC-2 通过**：rpc_own_handshake_test、rdbcomm_handshake_session_test、dmsbtex_session_test、libobk_session_test、mixed_mtls_integration 全 PASS；rdbcomm/aio-speedd 非法算法拒绝 exit=1（T0358 行为未回归）
- **AC-3 通过**：保留字段消费点审计清单入 evidence-cleanup.md

Grill 自检：
1. 误删风险——每个字段删除前均经 `grep 结构体前缀.字段` 全仓核实零读取；唯一边界是 rdbcommd server_options.tls_algorithm（T0348 M4 已确认死字段，tool_alg 解析校验保留）
2. ABI 影响——libobk.h 公开头的 sbtctx 布局变更随 libobk_version 1.0.1.2 发布，项目自产自用无外部消费者
3. 替代解释——unused sbt_client_cert_paths 注释称"保留兼容"，但其存在依赖已删字段且当前强制 cert_dir 路径，兼容语义早已失效

## 适用边界

- 不涉及 libs/tls_cert.c 内部 slot 结构与协议帧格式
- rdbcommd CLI --tls-algorithm 参数与校验保留（配置合法性检查），白名单消费归 T0357

## 下一轮建议

- T0357/T0359 按序推进；若 T0357 需要服务端算法配置字段，基于 tool_alg 解析重新引入

## Verdict

- verdict_id: V-T0360-20260822-01
- outcome: confirmed
- reason: 三条 AC 全过（evidence-cleanup sha256 待验）；纯删除重构零行为变更；提交 0ef0f8d 含完整版本递增
- at: 2026-08-22T21:00:48+08:00
