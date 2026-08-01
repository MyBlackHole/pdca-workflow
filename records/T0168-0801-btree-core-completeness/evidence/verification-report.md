# Verification Report — T0168 审计结论验证

- 验证日期：2026-08-01（Check 阶段）
- 验证对象：review-report.md 全部 8 项 AC 声明
- 方法：源码行号抽查（subvol + bcachefs 对照）+ 证据元数据校验（schema/digest 由 register-evidence 保证）+ 收敛验证

## 一、D1 缺陷三要点抽查（AC-5 核心声明）

| 声明 | 验证结果 |
|------|---------|
| subvol 空间检查独立判空、不累加同 leaf 占用（update.rs:1953-1975） | **通过**：对每个 update 独立 `bch2_btree_node_insert_fits(b, required_u64s)`，无跨 update 累加；含 whiteout 压缩与 split_leaf 单 key 路径 |
| bcachefs 有 `u64s += i->k->k.u64s` 累加（commit.c:1083-1097） | **通过**：`same_leaf_as_prev` 判断 + `u64s += i->k->k.u64s` + `btree_key_can_insert`，`*stopped_at = i` 中止点一致 |
| bcachefs EBUG_ON 剩余空间防御（commit.c:189-195）在 subvol 缺失 | **通过**：commit.c:194 `EBUG_ON(insert->k.u64s > bch2_btree_keys_u64s_remaining(b))` 存在；subvol bset_update.rs 无对应断言 |
| 越界写发生于 bset_update.rs:188 copy_nonoverlapping | **通过**：bset_update.rs:188-195 `copy_nonoverlapping`（key_u64s / val_u64s 两段），写前仅 assert 局部 u64s 值非负，无节点容量边界检查 |

## 二、AC-1/AC-2/AC-3 抽查（行号锚点）

| 模块 | 声明的关键行号 | 验证 |
|------|--------------|------|
| journal.rs flush/res_get（1005-1226/899） | 文件 2264+ 行，行号区间存在 | 通过（行号在文件长度内，符号名与 bcachefs journal.c 对应） |
| engine.rs recover（916-955） | 存在 | 通过 |
| cache.rs mem_alloc/data_free/evict（429/402/671） | 存在 | 通过 |
| bcachefs 12 对照文件存在 + 5 关键符号 | ls + grep 抽查 | 通过（见 review-report 第七节） |

## 三、证据与门禁状态

| 项 | 状态 |
|----|------|
| review-report（AC-1..AC-8） | 已登记，schema 校验通过，digest 已固化 |
| checkpoint-cow-heap-rootcause（AC-5） | 已登记 |
| convergence-map | 已登记，指向全部 8 AC |
| convergence-validation | **valid: true，0 issues** |
| Do→Check 门禁（PRD + 证据 + convergence） | 全部满足，已转换 |
| task.json meta.record | 已指向记录 |

## 四、结论

review-report 的全部关键声明经源码抽查验证一致，无虚报行号或结论漂移。8 项 AC 均有证据覆盖。Check 阶段验收**通过**，可推进 Check→Act。

遗留：D1 为真实 CRITICAL 缺陷（三要点双重确认），修复动作应在 Act 阶段决策（建议独立 bugfix 任务）。
