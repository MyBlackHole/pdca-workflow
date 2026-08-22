# 审查 rdbcomm/sbt/dmsbtex mtls 模式与 rpc 实现逻辑一致性

## 问题陈述

仓库内四个模块各自实现了 mTLS 握手/协商逻辑。用户要求以 rpc 模块（aio-speed 工具链）为基准（即任务中的 "rp"），审查 rdbcomm、sbt（libobk/lib/sbt）、dmsbtex 三模块的 mTLS 模式实现逻辑是否与其一致。

| 模块 | 角色 | 握手结果码前缀 |
|------|------|--------------|
| rpc（aio-speed 工具链） | 基准 | HS_OK_MTLS / HS_ERR_* |
| rdbcomm | 待比对 | RDB_HS_OK_MTLS / RDB_HS_ERR_* |
| dmsbtex | 待比对 | DM_HS_OK_MTLS / DM_HS_ERR_* |
| sbt（libobk/lib/sbt） | 待比对 | OBK_HS_OK_MTLS / OBK_HS_ERR_* |

## 方案

产出一致性审查报告 `conclusion.md`：

1. **比对矩阵**：三待审模块 × 审查维度，逐格标注 一致/偏差/不适用。
2. **证据引用**：每项结论引用具体源码符号与行为描述。
3. **风险评级**：每项偏差给出 高/中/低 评级与影响分析。
4. **修复建议**：每项偏差附建议方向（不改代码）。

## 用户故事

- 作为维护者，我能通过比对矩阵快速定位四模块 mTLS 实现的行为差异。
- 作为维护者，我能依据风险评级决定哪些偏差需要立即收敛。

## 实现/测试决策

- review 场景，无代码产物、无测试产物；验证方式为报告内证据可回溯到源码符号。
- 历史审查框架复用：首阶段三场景一致性、transport I/O 绑定、SSL cleanup 覆盖面（见 implement.jsonl 注入知识）。

## 审查维度（全维度 + 错误码细节）

1. 协议常量：握手 flags 位定义、OK_MTLS/ERR_MTLS_REQUIRED/ERR_MTLS_UNAVAILABLE 数值。
2. 协商状态机/决策函数：纯决策逻辑的分支语义（强制/请求/算法匹配组合）。
3. 无降级策略：强制模式下失败路径，是否存在静默降级为明文。
4. 配置优先级链：CLI → ini → 环境变量的解析顺序与覆盖语义。
5. TLS 构建时机：按需握手升级 vs 启动时构建；构建失败的启动行为。
6. 失败路径与资源清理：SSL cleanup 覆盖握手失败/业务初始化失败/正常关闭。
7. 错误码语义与日志行为：role/stage/算法/凭据路径诊断信息完备性。

## 范围外

- 不修改任何代码。
- 不审查 TLS 证书生成/管理本身（独立任务线）。
- 不审查非 mTLS 的传输加密（如 sbt-transfer-encryption）。

## 备注

- triage 摸底已发现的疑似缺陷（rdbcomm 客户端调用未声明的 `rpc_hs_session_cleanup`）纳入审查范围核实。
- 相关历史任务：0818-rdbcomm-rpc-mtls-followup、0819-sbt-mtls-simplify、0819-dmsbtex-libobk-mtls、0819-tool-mtls-config。

## 验收标准

- [ ] AC-1: 运行 `grep -c "rdbcomm\|sbt\|dmsbtex" conclusion.md` 得到三模块均出现在比对矩阵中（≥3 行命中）。
- [ ] AC-2: conclusion.md 覆盖全部 7 个审查维度，每维度对每个模块有一致/偏差判定。
- [ ] AC-3: 报告中每项"偏差"结论均含源码符号级证据引用，可通过 grep 在对应源文件命中该符号。
- [ ] AC-4: 每项偏差附风险评级（高/中/低）与修复建议；conclusion.md 含 verdict 段给出总体判定。
