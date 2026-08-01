---
schema: pdca.asset/v1
id: T0185-0802-derived-state-validator-fault-closure
phase: check
source_ids: [source-audit, verification, ac3-gap, convergence-map]
---

## 上下文

T0185 对 T0182 已有的派生写入与 recovery rebuild 增加独立 primary/derived 校验，并在两条
recovery 入口接入校验 gate。

## 假设与结果

- AC-1：通过。已记录本地 recovery、backpointer、alloc 检查分支。
- AC-2：通过。validator 比较 alloc/backpointer 集合及关键字段，并报告 mismatch。
- AC-3：部分通过。正常路径由既有测试覆盖，但尚无故意破坏派生记录的独立回归测试。
- AC-4：通过现有 journal/recovery 测试与 rebuild 后 gate 验证。
- AC-5：通过。workspace 184 个单测与 10 个属性测试、fmt gate 均通过。

## 分析

实现保持主记录为 authority，派生树仅作校验对象；rebuild 完成前不会返回可观察的恢复成功状态。
校验器不执行隐式修复，也未扩大到 allocator、GC、LRU、stripe 或 VFS。

## 失败原因（partial）

AC-3 仍缺少对持久化 alloc/backpointer 记录进行删除、复制或字段篡改后，验证器稳定返回
mismatch 的独立测试。

## 适用边界

当前只覆盖单一格式和本项目已有 physical pointer 布局；不代表完整 bcachefs fsck 或完整
allocator 一致性检查。

## 下一轮建议

补充一个可控的 derived-record corruption seam，覆盖 missing、duplicate、generation 和
owner mismatch，然后重新执行 Check；在此之前不归档为 confirmed。
