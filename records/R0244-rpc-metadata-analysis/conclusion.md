---
schema: pdca.asset/v1
id: R0244-rpc-metadata-analysis
phase: check
source_ids: [metadata-analysis-report-v4]
---

## 上下文

本轮针对 `rpc/rpc-metadata.c` 的海量文件元数据管理进行源码调研，报告已登记为 `metadata-analysis-report`，并以 `convergence-map` 建立了收敛映射。

## 假设与结果

- 假设：元数据以 LMDB 目录项复合键和固定值保存。结果：成立，报告给出结构体、比较器和 LMDB 封装证据。
- 假设：路径查询按深度扩展，目录读取按目录条目数扩展。结果：成立，报告覆盖对应 API 和 cursor 行为。
- 假设：海量规模的主要问题是容量、长事务、超大目录扫描和边界安全，而非全量内存索引。结果：源码支持该判断；容量/性能数值明确标注为推断，未冒充实测。

## 分析

Check 复核结果：

- AC-1：通过。报告说明 key/value、inode 分配及持久化，并引用 `rpc/rpc-metadata.c`、`.h` 和 `lmdb_dict.c`。
- AC-2：通过。报告覆盖新增、查询、删除、路径解析、目录遍历和事务生命周期。
- AC-3：通过。报告分析 O(d)、O(log N)、O(log N+k)、空间组成、`map_size`、checkpoint 和 cursor；未实测项已显式说明。
- AC-4：通过。报告按 P0/P1/P2 列出悬空指针、名称越界、容量、事务、删除、路径和测试覆盖风险。
- AC-5：通过。报告结构符合 research-report 要求，证据已登记，收敛验证器返回 `valid: true`，`git diff --check` 通过。

## 适用边界

结论适用于当前工作区版本及其直接调用链；没有代表性数据集下的真实吞吐、空间放大率或恢复时长测量，因此不能据此作容量承诺或性能 SLA。

## 下一轮建议

优先修复 `meta_system_open` 失败路径和名称长度校验；之后补充根路径、异常事务、重启恢复、长名称和百万级记录的回归/基准验证，并以实测数据校准 LMDB map size 和 checkpoint。
