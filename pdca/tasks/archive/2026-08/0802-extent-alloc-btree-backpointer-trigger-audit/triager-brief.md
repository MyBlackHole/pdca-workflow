# T0180 分诊简报

## 分类

- 类别：review
- 场景：review
- 优先级：P1（空间分配与内部 btree 一致性的前置审计）

## 已核验事实

1. bcachefs `fs/btree/types.h:1260-1267` 将 extents、alloc、stripes、reflink、
   subvolumes 和内部 `BKEY_TYPE_btree` 纳入 transactional trigger 集合。
2. `fs/data/extents.h:419-446` 将 btree pointer 与 extent key 的 trigger 绑定为
   `bch2_trigger_extent()`；`fs/alloc/buckets.c:894-924` 仅在 transactional/GC
   阶段执行派生更新与 reconcile。
3. 在 extent pointer 的 transactional 路径，bcachefs 同一 transaction 更新 alloc
   并调用 `bch2_bucket_backpointer_mod()`（`buckets.c:681-684`）。
4. subvol 已有 extents iterator 自动分派（`btree/iter.rs:83-87`）、范围 update
   分派（`btree/update.rs:1510-1513`）和 `KEY_TYPE_btree_ptr_v2` 内部记录
   （`btree/interior.rs:695-704`），但尚无 extent/alloc/backpointer trigger 或
   transactional runner。
5. subvol 仅保留 `KEY_TYPE_backpointer` 格式常量，未实现它的派生生产、维护和
   verifier；当前 `bch_fs` 也没有 bcachefs GC visited 模型。

## 去重

- T0179 只覆盖 cookie/deleted/snapshot，已按 partial 处置；本任务是其显式跟进，
  不重复。
- 未发现其它 active/archive task 覆盖完整的 extent→alloc→backpointer 依赖图。

## 推荐

先绘制并验证完整派生依赖图，逐条判定“当前可达、缺失、实现前置条件、范围外”。
不要先写通用 runner：必须先确定独立引擎中要支持的最小 extent/alloc 模型及其
持久化/恢复边界，再拆分最小 bugfix 或 development 子任务。
