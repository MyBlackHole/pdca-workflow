---
schema: pdca.asset/v1
id: T0348-0822-mtls-state-alg-review
phase: check
source_ids: [review-report]
---

## 上下文

用户要求审查 rdbcomm / sbt(libobk) / dmsbtex / rpc 四模块 mTLS 状态参数（mtls_enabled）与算法参数（tls_algorithm）的设置与使用问题。原始路径 `rdbcomm\sbt\dmsbt\rpc` 不存在，经用户确认为四模块横向审查。review 场景，无代码变更。

## 假设与结果

| 假设（triage 线索） | 结果 |
|---|---|
| 算法枚举多处重复 | 成立：枚举 5 处 + 映射函数 4 份 |
| strstr 宽松匹配算法名 | 成立："sm2"→SM4 且被测试固化 |
| 协商语义分裂、决策树未接线 | 成立：三种语义并存；`dm_hs_decide` 生产/测试零调用 |
| 服务端不校验客户端算法 | 成立并升级：叠加 `tls_cert_find_slot` 空回落 slots[0]，协商字段可被完全绕过 |
| atoi 解析 mtls_enabled fail-open | 成立："SBT_MTLS_ENABLE=abc" 静默禁密 |
| 配置层级不一致 | 成立：sbt/dmsbtex 只读全局段；env 名碎片化 |
| rpc 独有明文降级路径 | 成立：want_mtls+无证书回 OK_PLAIN（客户端兜底 abort） |
| 字节序不统一 | 成立：libobk 主机序，其余网络序；当前小端平台无害 |
| client.c 双保险默认值 | 成立，降级 LOW |
| `(void)cfg` 忽略本端开关 | 成立，属有意设计，降级 LOW |

## 分析

- **AC-1 通过**：报告覆盖四模块全部 mtls_enabled/tls_algorithm 设置入口（CLI/env/ini）、传递路径（结构体字段/ctx）、消费点（握手帧构造/校验/升级），12 条发现均附 file:line。
- **AC-2 通过**：HIGH×4 / MEDIUM×5 / LOW×3 分级，每条含修复方向；最严重为服务端算法零校验 + slot 空回落（H1）。
- **AC-3 通过**：10 条线索逐条裁决（规范轴表格），另产出 6 项新增发现（find_slot 回落、server.tls_algorithm 死字段、ERR_ALGORITHM 从未使用等）。

Grill 自检（review 场景追问）：
1. 关键路径覆盖——四模块 client/server 双端、共享底座 `libs/tls_cert.c` slot 机制均已核验；一处未入报告的微小点：dmsbtex main.c:191 向 worker 传栈上 tls_cfg 地址（accept loop 常驻故安全，纯风格问题）。
2. 风险评级复核——H1 中"半握手 DoS 面"表述略强于实测影响（畸形帧处理成本与正常失败相当），但 HIGH 定级由"协商失效 + 多 profile 下算法由 slot 顺序决定"独立支撑，定级不变。
3. 替代解释排除——`dm_hs_decide` 注释表明系共享握手库迁移残留，非预留设计，死代码定性成立。

## 适用边界

- 结论基于当前工作区代码静态审查，未运行时验证多 profile 下 slot 顺序行为（建议修复时补集成测试）
- 不涉及 payload 层 data_encrypt 对称加密体系与证书文件有效性
- M5 字节序修复属破坏性协议变更，需对端同步评审

## 下一轮建议

1. H1+M4+N3 合并立项：服务端算法白名单校验（四模块对称修改，错误码已备好）
2. H2/H3 小改动可合并一个 bugfix 任务（atoi→sec_resolve_int、strstr→strcmp、修正固化 "sm2" 的测试）
3. H4+M1 跨模块重构建议独立任务：统一协商语义 + 枚举单一来源
4. 清理 clangd `.cache` 消除陈旧索引误报（L3）

## Verdict

- verdict_id: V-T0348-20260822-01
- outcome: confirmed
- reason: 三条 AC 全部满足且证据充分（review-report.md，sha256:e05737f9）；10 条线索全部裁决，4 条 HIGH 发现均有可达性论证与修复方向
- at: 2026-08-22T19:37:03+08:00
