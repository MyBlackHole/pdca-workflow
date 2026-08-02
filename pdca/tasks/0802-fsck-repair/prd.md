# T0198 fsck 修复路径：索引不一致 repair 模式

## 问题陈述

T0195 明确将 repair 列为范围外：`fsck_image`（engine.rs:2424）仅
no-repair（打开 + verify_all，对齐上游 `-n` → fix_errors=no）。引擎
只能报告索引不一致（FreespaceSet / NeedDiscardSet），无法自愈；上游
fsck 在 fix_errors=yes/ask 下会执行修复（`__bch2_check_freespace_key`
删除错误 freespace 键、`bch2_check_discard_key` 删除错误 need_discard
键、`bch2_check_alloc_key` 删除无效 alloc 键）。

## 目标

新增修复模式：库侧 fsck_image 支持 fix_errors 模式（对齐上游单入口
`bch2_fs_fsck_errcode` + fix_errors 选项），修复动作 = 删除与 alloc
树不一致的派生索引键（freespace / need_discard），修复后镜像
reopen 必过 verify_all；CLI 新增 `-y/--yes` 自动修复模式（对齐
fsck.rs:34 auto_repair + fix_errors=yes），`-n` 保持默认只检查。

## 验收标准

- [ ] AC-1: 修改前逐段记录上游锚点：fix_errors 门控（init/error.c:433-463
      FSCK_FIX_no/yes/ask/exist 分支）、check_allocations 修复动作
      （alloc/check.c:144-190/388-423/399-473 三处删除）、CLI 参数
      （fsck.rs:34-38 auto_repair/no_repair、266-269 no_repair→nochanges+
      fix_errors=no），与 engine-local fsck_image / verify_bucket_indexes
      / set_need_discard_index（engine.rs:2674 bit_mod 写路径）对应。
- [ ] AC-2: 库 API 修复模式：修复动作与上游一致（删除与 alloc 树不一致
      的派生索引键：freespace 对齐 delete_freespace_key、need_discard 对齐
      bch2_btree_bit_mod_buffered(false)）；每键一个事务（对齐
      delete_freespace_key trans_commit，engine.rs:2674-2690 模板）；
      修复后 verify_all 必须通过。
- [ ] AC-3: 修复范围边界：仅 alloc↔派生索引（freespace/need_discard）
      一致性（FreespaceSet / NeedDiscardSet）；OpenBucketFree /
      NotRwBucketFree 等守卫错误名不在修复范围（上游为 discard skip
      语义，非 fsck 修复动作）。
- [ ] AC-4: CLI -y/--yes 修复模式：损坏镜像（索引不一致）默认退出 1、
      -y 后修复成功退出 0 且输出修复信息；打开失败仍退出 2；
      -n/--no-repair 保持只检查（退出 1 不改镜像）。
- [ ] AC-5: 修复原子性：每键独立事务；修复遇非索引错误（Io/事务）中止
      并上报（对齐上游 ret 传播），不部分修复后假装成功。
- [ ] AC-6: workspace 全量测试、fmt、diff gate 通过，单项不超过一分钟。

## 实现决策

- 库：`fsck_image(path)` 扩展为带 fix_errors 模式参数（枚举
  FixErrors::No / FixErrors::Yes，对齐 FSCK_FIX_no/yes），单入口
  （上游 bch2_fs_fsck_errcode 为单函数 + fix_errors 选项）；既有调用点
  显式传 No（行为不变，AC 覆盖）。
- 修复动作：扫描 freespace / need_discard 树，删除不在 alloc 派生集
  （verify_bucket_indexes 的 expected 集）中的键；每键一个事务
  （bit_mod set=false + trans_commit，engine.rs:2674-2690 模板）。
- CLI：`-n/--no-repair`（默认，T0195 语义）、`-y/--yes`（自动修复，
  对齐 fsck.rs:34 auto_repair）；`-f/--force` 保持 T0195 预留语义。
  退出码沿用 0/1/2 分层；-y 路径打印 `FIXED: <btree> <pos>` 修复消息
  （对齐 fsck 修复输出）。
- 测试：库级测试构造索引不一致镜像（set_need_discard_index /
  freespace 注入脏键）→ 修复模式 → verify_all 通过 + 键已删除断言 +
  reopen 后再次 verify_all；-n 路径镜像不变断言；CLI 集成测试 -y/-n
  退出码与输出。

## 范围外

open bucket / not_rw 守卫错误名的自动修复（skip 语义）、alloc 键修复
（engine 单设备）、interactive ask 模式、-f force 语义实现、多设备。

## 备注

前置：T0195（fsck_image 无修复入口）、T0197（模型裁决注入）已归档；
verify_bucket_indexes 已给出 alloc↔派生索引的精确集合比对
（engine.rs:618-668）。
