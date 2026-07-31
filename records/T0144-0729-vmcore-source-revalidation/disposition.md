# T0144 Act 处置

## Verdict

`confirmed`

用户确认根因证明链、指定源码映射、iSCSI 触发边界和详细报告满足本任务验收要求。

## 知识处置

处置结果：`projected`

已生成可复用知识：

- `knowledge/kernel-debugging/device-mapper-blk-mq-uaf-vmcore-method.md`

知识条目仅保留跨任务成立的方法，包括故障指令与字段还原、页表状态、旧新 table 身份、
释放生命周期、suspend guard 位置、补丁同源性门槛和外部触发因素证明门槛。

本次主机、指针地址、`dm-19` 和具体 NVMe 设备身份仍保留在 record 中，不写成通用规则。

## 架构改进处置

目标内核的回移植、构建和 A/B 压测需要新的实施授权，未在本分析任务内直接修改源码。
候选改进已写入 `improvement-backlog.md`，包括回移植、运行验证和可选的 iSCSI 专项取证。

## 未扩大声明

- 未宣称上游补丁已经在 3.10.0-1160.83.1.el7 上完成运行验证。
- 未宣称 iSCSI 是本次直接触发者。
- 未把本次结论泛化为所有 dm、NVMe 或 iSCSI 故障。
