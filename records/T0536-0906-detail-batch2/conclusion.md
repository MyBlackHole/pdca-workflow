---
schema: pdca.asset/v1
id: T0536-0906-detail-batch2
phase: check
source_ids: [report-snapshot, report-crypto, report-btreesearch, report-writepath, report-recovery, guide-diff, validate-output, ac34-verify, convergence-map]
---

## 上下文
用户指定第二批为内核态 5 篇。并行子代理扩充，主会话抽查验收。

## 假设与结果
- 假设 1：子代理扩充真实。结果：成立，抽查函数名行号命中；恢复篇纠正 3 处行号漂移并指出 2 隐患。
- 假设 2：门禁链条可走通。结果：成立，AC 从 1 编号、--file 唯一、证据支撑对齐一次通过（T0535 教训已落实）。

## 分析
- **AC-1** ✅ 5篇扩充到代码级精讲（213KB），逐函数签名参数返回调用链（5 report 证据）
- **AC-2** ✅ 抽查源码断言命中；恢复篇行号漂移已纠正（5 report 证据）
- **AC-3** ✅ 报告文件已更新；对话交付本回复摘要，全文位置明确（ac34-verify）
- **AC-4** ✅ 5 指南节点增补指向扩充版，三查全绿，validate 全绿（guide-diff）

关键结论：5 篇代码级精讲落盘；恢复篇纠正行号漂移。
复核途径：按各报告末节复核命令定位源码。

## 本体沉淀

决策：`ontology:ontology:domain/core-snapshot-study-guide` 等 5 指南节点（更新增补行）。

理由：指南节点增补指向扩充版报告行，属本体更新，满足强制本体化。来源 record `T0536-0906-detail-batch2`。

## 适用边界
- 扩充内容抽查置信，未逐行全审。
- 剩余 10 篇分后续批次。

## 下一轮建议
- 第三批：GC/编排/超块/搬迁/配额。

verdict: {"outcome": "confirmed", "reason": "4 AC 全绿，5篇精讲落盘+指南增补", "verdict_id": "vt0536-confirmed", "at": "2026-09-06T00:00:00+08:00"}
