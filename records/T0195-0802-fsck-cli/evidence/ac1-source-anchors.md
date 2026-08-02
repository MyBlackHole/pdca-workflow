# T0195 AC-1 源码锚点

修改前对照记录。CLI 语义以本地 bcachefs-tools fsck 命令为唯一依据。

## 1. fsck CLI 流程 ← src/commands/fsck.rs

- `fsck.rs:419-447`（userspace offline fsck）：`device_scan::open_scan`
  打开设备集 → `bch2_fs_fsck_errcode(fs.raw, buf)` 运行全部校验 pass →
  非 0 时 `eprint!("{}", buf)` 打印错误 → `fs.exit()` 关闭 → 
  `process::exit(ret)`（0=通过，非 0=失败，ret2 失败时 `exit(ret|8)`）。
- `fsck.rs:56-64`：`-n/--no_repair`（Don't repair, only check for errors）
  与 `-p/--auto_repair`、`-y/--yes`、`-f/--force`（Force checking even if
  filesystem is marked clean）。
- `fsck.rs:245-254` 注释：fsck=1 时内核 OR 入完整 PASS_FSCK 默认 pass 集
  （check_allocations、check_alloc_info 等），即 fsck 命令 = 运行全部
  一致性 pass。
- engine-local 映射：verify_all（T0194）即"全部 pass"；CLI 流程
  打开引擎 → verify_all → 输出 → 退出码。

## 2. 只检查不修复 ← -n/--no_repair 语义

- `fsck.rs:60-61`：`-n` = "Don't repair, only check for errors"。
- engine-local：verify_all 只读校验（T0194 全执行首个错误），无修复
  路径——CLI 天然只有 no-repair 模式，与上游 -n 对齐；-p/-y 无对应
  （无修复能力）。

## 3. 错误输出与退出码 ← bch2_fs_fsck_errcode + exit(ret)

- `fsck.rs:431-436`：非 0 时 `eprint!("{}", buf)`（Printbuf 错误详情
  打印到 stderr）；`fsck.rs:443-447`：`process::exit(ret)`——
  errcode 直接作为进程退出码（0=通过）。
- engine-local 映射：退出码 0=通过 / 1=校验失败（verify_all Err 且
  DerivedState 变体名打印）/ 2=打开/IO 错误（进程级分层，扩展
  errcode 通道以区分失败类别，脚本可诊断）。

## 4. 引擎持久化 API（被调用方，行为不变）

- engine.rs:505 `create_persistent`：创建持久化引擎（测试/CLI 准备）。
- engine.rs:513 `open_persistent`：打开持久化引擎（CLI 主调用）。
- engine.rs:739 `verify_all`：聚合校验（T0194，CLI 调用对象）。
- engine.rs:240-248 `DerivedStateMismatch`：错误变体名（CLI 输出源）。
- 集成测试：crates/subvol/tests/btree_proptest.rs（现有集成测试样式参照）。

## 对应 subvol 现状

- crates/subvol/src/bin/：不存在（纯库，新增 subvol-fsck）。
- Cargo.toml：零依赖（urcu 仅），CLI 保持手写参数解析。
