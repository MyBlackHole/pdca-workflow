# T0175 Triage Brief

## 分类
- category: bug / scenario_type: bugfix
- 来源：T0174 Do 阶段 split_stress_preserves_model 阶段 1 预写 2000 键稳定复现 Transaction(-12)

## 查重结果
- 无既有任务记录该缺陷（T0168 矩阵 A1 将 interior split 列为「部分」对齐，
  未拆出此具体错误路径；T0169 为 commit 空间检查问题，不同根因）
- 结论：不重复

## Claim 验证
- 复现：split_stress_preserves_model 阶段 1 预写（engine.put，update.rs:383 行失败点）
  → Transaction(-12)（proptest 最小失败输入已产出）
- 根因：update.rs:110-114 __bch2_trans_kmalloc 在 mem_bytes != 0 时设置
  realloc_bytes_required 返回 null → subbuf reserve（update.rs:219）返回 -12 →
  engine.rs commit 循环仅对 -4 restart（engine.rs:871），-12 硬失败
- bcachefs 对照：commit.c:1319-1320 bch2_err_matches(ret, ENOMEM) 与
  transaction_restart 同级均重试；__bch2_trans_kmalloc 失败返回
  -BCH_ERR_ENOMEM_trans_kmalloc（iter.c:3791）；__bch2_trans_subbuf_alloc
  失败返回 ERR_PTR 错误码（update.c:609-634）——ENOMEM 全部可重试

## 修复方向（待确认细节）
- engine.rs commit 循环错误分支：ret == -4 → ret == -4 || ret == -12
- 需确认 bch2_trans_begin 重置 realloc_bytes_required/mem 使 restart 后扩容成功
- 需评估所有 -12 返回点（update.rs 15+ 处）是否均为 ENOMEM 语义（应是，
  但需逐个确认无其他含义）

## 推荐下一步
- 直接进入 Plan：确认 bch2_trans_begin 语义 → PRD → 终审 → Do

## 日期
2026-08-01
