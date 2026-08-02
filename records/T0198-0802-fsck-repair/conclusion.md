# T0198 结论

## 概述

fsck 修复路径：`fsck_image` 扩展 FixErrors::No/Yes 模式（对齐
FSCK_FIX_no/yes，opts.h:132），Yes 模式双向修复 alloc<->派生索引
不一致（删除错误 freespace/need_discard 键 + 补齐缺失键，对齐
bch2_check_alloc_key alloc/check.c:175-188 等三处），每键单事务
（对齐 delete_freespace_key check.c:352-386），修复后 flush_journal
落盘（对齐 fs.exit() fsck.rs:457-460）再 verify_all；CLI 新增
`-y/--yes` 自动修复（对齐 fsck.rs:34 auto_repair），`-n` 保持默认
只检查，`-n`/`-y` 互斥退出 2。

## 验证

- 关键事实：rebuild_derived_state 只清 4/5/8 树（engine.rs:2014-2019），
  need_discard 树脏键跨 reopen 存活 → 修复模式有真实持久化场景
  （实验确认）。
- 库级 4 新测试：stale 删除 + reopen 复验 + 树中无脏键；缺失补键 +
  reopen 复验 + 树中有键；No 模式镜像不变（两次报告同错，Yes 仍可
  修复）；No 模式报告 NeedDiscardSet 错误名。
- CLI：-y 健康退出 0 + `OK (repaired)`；-n/-y 互斥退出 2 + 错误信息；
  打开失败退出 2（-y 同路径）；损坏（索引不一致）镜像 CLI 级构造
  不可达（脏键注入需内部 API），修复语义由库级测试承担（实现期
  round 3 口径）。
- workspace 全绿：220 lib + 10 btree_proptest + 5 fsck_cli = 235，
  单项 ≤1min（btree_proptest 44.04s）；fmt 通过；提交 5806e58
  （4 files，+341/-19）；fsck_image 签名变更 3 调用点同步。
- 双轴审查：0 blocking / 0 MEDIUM / 0 LOW。

## 边界与发现

- 修复动作仅覆盖 verify_bucket_indexes 报出的两类错误名
  （FreespaceSet / NeedDiscardSet）；OpenBucketFree / NotRwBucketFree
  为纯运行期内存不变量（open_buckets / rw_devs 不持久化），fsck 流程
  天然不遇到，上游对应 skip 语义（discard.c:344-347/349-357）——
  修复函数不触碰，verify_all 守卫检查不变。
- 修复必须落盘：缺 flush_journal 时 reopen 后脏键复活（journal replay
  只重放已落盘事务）——实测定位。
- freespace 树持久化脏键会被 open_persistent 重建清除，其修复动作
  （删/补）为防御性实现（对齐 check.c 语义），实际持久化触发路径以
  need_discard 树为主。

## 建议链（下一轮）

1. loom 风格并发交错：worker/discard/reclaim 在并发下的事务级验证
   （现有并发测试为端到端级）。
2. 模型状态机扩展：op 域扩大（含 fsck 修复操作？修复与运行期操作的
   交错序列）、case 数提升，纳入 CI 定时全量。
3. fsck 修复的故障注入：修复事务中途 -12/-ENOMEM 注入与恢复路径验证
   （对齐 recovery-fault-matrix 既有模式）。
