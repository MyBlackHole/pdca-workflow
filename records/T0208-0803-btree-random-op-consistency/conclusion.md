# T0208 结论：btree 随机操作序列一致性属性测试

任务：T0208-0803-btree-random-op-consistency

## Verdict

**complete**（V-T0208-001）——4 项 AC 全部收敛，测试一次通过，
无修复需求，无遗留。

## AC 收敛状态

| AC | 内容 | 状态 | 证据 |
|----|------|------|------|
| AC-1 | 多 id 隔离与扫描一致性 | 完成 | check-evidence |
| AC-2 | 拓扑变更一致性（split/merge） | 完成 | check-evidence |
| AC-3 | 崩溃重开一致性（journal 重放） | 完成 | check-evidence |
| AC-4 | 全量测试 + fmt + diff gate | 完成 | check-evidence |

## 关键结论

1. 多 btree id 隔离成立：逐步全量比对证明每 btree 独立 root
   （bch2_btree_id_root）下，操作只影响目标 id，其余 id 扫描
   与 shadow 模型不变。
2. 拓扑变更（4 id 同时 768 键 split + 3/4 删除 merge）后
   verify_all 与全 id 扫描一致——merge 的 restart（-4）由
   commit 循环透明处理，物理布局对逻辑模型不可见。
3. 崩溃重开（drop 不 flush = 崩溃；open_persistent 重放已
   durable 记录）后已同步部分全部恢复，继续追加操作仍一致。
4. 门禁：247 测试全绿（10.61s）、fmt 干净、diff 仅测试代码
   （7889482）。

## 沉淀建议

- 属性测试模式（多 id shadow 模型 + 崩溃重开）可登记知识
  `knowledge/core/`（btree 随机序列一致性模式），供后续
  btree 相关任务复用。

## 后续

无遗留项。T0207 之后交付重点的缺口（多 id 随机序列一致性）
已补齐。
