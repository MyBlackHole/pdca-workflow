# T0145 调研报告 Do 阶段审查

## 审查范围

- `research-report.md`
- `analysis-process-ledger.md`
- `prd.md` 的 AC-1 至 AC-10

## 自动检查

| 检查 | 结果 |
|---|---|
| 两份报告、原始会话、原始 A、T0144 两轮 crash 哈希复算 | PASS，与报告记录一致 |
| 绝对路径引用目标存在 | PASS；带 `:line` 的链接由渲染器解析为文件行号 |
| verdict 标签 | PASS；`supported` 21 次、`refuted` 15 次、`inconclusive` 6 次 |
| 任务产物认证信息扫描 | PASS；未出现密码、`sshpass` 命令或认证值 |
| 目标源码 clone-null 释放顺序 | PASS；`rq_completed()` 位于 `free_old_rq_tio()` 之前 |
| 报告 B/T0144 crash 首轮 hash 关系 | PASS；均为 `d5ff1d...050f0a` |

## 验收标准逐项审查

| AC | 结果 | 覆盖位置 |
|---|---|---|
| AC-1：至少 7 个关键分歧及逐项判定 | PASS | “发现二”矩阵共 12 个维度 |
| AC-2：报告 A 分析过程账本 | PASS | `analysis-process-ledger.md` |
| AC-3：fault 指令、RDI 对象和 +0x8 字段 | PASS | “发现三” |
| AC-4：两种 UAF 生命周期闭合性 | PASS | “发现四”“发现七” |
| AC-5：iSCSI 三层判定 | PASS | “发现六” |
| AC-6：至少 4 类方法论原因 | PASS | “为什么差异会扩大”共 7 类 |
| AC-7：错误源码影响与仍可信事实 | PASS | “发现一”“发现三”“发现四” |
| AC-8：三态 verdict 与置信度 | PASS | 分歧矩阵及两份报告总体 verdict |
| AC-9：最可信根因、边界和最小验证 | PASS | “结论与建议” |
| AC-10：引用可定位、哈希记录 | PASS | “输入与完整性”“参考资料” |

## 内容轴审查

- 报告没有把历史 verdict 当作技术证据，而是回链到 crash、DWARF、源码和发行商公开材料。
- 报告同时审查 B 的过度表述，避免“后报告必然全对”的版本偏见。
- 报告把 `PTE=0` 的直接事实与 `vfree(old table)` 的高置信生命周期推断分开。
- 报告把代码级根因与具体外部触发者分开。
- 报告没有断言未经源码或发行商确认的 RHEL 修复版本。

## 格式轴审查

- 结构符合 research 技能要求：目标、方法、发现、结论建议、参考资料齐全。
- 关键关系使用矩阵，长因果链使用紧凑代码块，没有不必要的图示。
- 本地引用使用可点击绝对路径；外部引用仅采用 Linux/Red Hat 一手入口。

## Do 阶段审查结论

`PASS`。AC-1 至 AC-10 全部具有明确、可定位的实质证据，可进入证据登记与
convergence 验证。
