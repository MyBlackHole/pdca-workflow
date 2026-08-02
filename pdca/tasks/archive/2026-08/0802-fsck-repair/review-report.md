# T0198 双轴代码审查报告（review-report）

审查范围：subvol 提交 `5806e58`（FixErrors 模式 + repair_derived_indexes
双向修复 + bit_mod_sync 事务 + CLI -y + 6 库级测试 + 2 集成测试）。

## A 轴：上游语义对齐

| 检查点 | 上游锚点 | 本实现 | 结论 |
|---|---|---|---|
| fix_errors 门控 | opts.h:132 FSCK_FIX_no/yes；init/error.c:433-463 分支 | FixErrors::No/Yes 枚举（No=只报错不修，Yes=执行修复） | 对齐 |
| 修复动作双向 | check.c:175-188 `bch2_check_alloc_key`（need_discard 补键 175-179、freespace 补/删 185-188）；388-423 `bch2_check_discard_key` 删除；352-386 `delete_freespace_key` | repair_derived_indexes：stale 键删除 + 缺失键补齐（freespace 用 alloc_freespace_pos 位置，need_discard 用桶位置，与 allocate/reclaim 写入一致） | 对齐 |
| 每键单事务 | delete_freespace_key（check.c:366-371）bit_mod + trans_commit | bit_mod_sync（bit_mod + commit，-12 重试，engine.rs:2674-2690 模板）；失败 `?` 中止 | 对齐 |
| 修复落盘 | fs.exit() 关盘（fsck.rs:457-460） | 修复后 flush_journal 再 verify_all（实测缺落盘 reopen 脏键复活） | 对齐 |
| 守卫不修复 | open/not_rw 为 skip 语义（discard.c:344-347/349-357） | 修复范围仅 FreespaceSet/NeedDiscardSet；verify_all 守卫检查不变 | 对齐 |
| 无新增行为分支 | — | 修复动作均出自 check.c 三处；无上游不存在逻辑 | 符合约束 8/12 |

## B 轴：安全/健壮性

- 修复幂等：删除/补齐集合由 alloc 树派生（expected 集），重复运行
  无副作用（已测 No 不改镜像、Yes 后 reopen 复验通过）。
- 事务安全：每键独立事务；-12 ENOMEM realloc 重试；非索引错误中止
  传播（AC-5），无部分修复。
- 键位置正确性：freespace 键 = alloc_freespace_pos（gc_gen 高位），
  与 verify_bucket_indexes / allocate_bucket 写入一致（engine.rs:1045-
  1050）；need_discard 键 = 桶位置（engine.rs:1053）。补键不产生错误
  位置的键。
- 扫描两阶段：先收集 stale/missing 集合（读借用）再逐键事务（写），
  无迭代器与事务借用冲突。
- 测试资源：持久化引擎唯一命名 + drop + remove_file 清理；reopen
  复验覆盖恢复一致性；flush_journal 确保脏键持久化可复现。
- 无 panic 新增路径；锁序（lock_fs）与既有模式一致。

## 结论

两轴通过；0 blocking / 0 MEDIUM / 0 LOW。残留：lib 既有 never-used
警告（非本次引入）。
