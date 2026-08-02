# T0195 Triage Brief

## 分类

- 类型：feature
- 场景：development
- 父任务：T0194

## 本地源码核验

- `src/commands/fsck.rs`：bcachefs fsck CLI——`cmd_fsck` 解析参数
  （-n/--no-repair 只检查不修复、-f/--force、-y、-r），offline 路径
  （fsck.rs:419-447）`open_scan` 打开文件系统 → `bch2_fs_fsck_errcode`
  → 错误信息输出 → `process::exit(ret)`（ret=0 通过，非 0 失败）。
- `bch2_fs_fsck_errcode` 运行全部校验 pass（fsck=1 时内核 OR 入
  PASS_FSCK 全量 pass 集，fsck.rs:245-254 注释），失败返回 errcode。
- engine-local 对应：`verify_all`（engine.rs:739，T0194 聚合入口）已就绪；
  `open_persistent`（engine.rs:513）打开持久化引擎。

## 查重

T0194 conclusion 建议「verify_all 作为引擎公开 API 的健康检查入口，暴露
到 CLI/诊断层」；无同范围活动任务。subvol 目前是纯库（无 bin/examples），
CLI 为新增表面。

## 推荐

新增 `subvol-fsck` bin：打开持久化引擎 → 运行 verify_all → 打印校验
结果 → 退出码 0/非 0。仅实现 no-repair 模式（engine 无修复路径，
对应上游 -n 语义）。参数对齐上游：-n/--no-repair（唯一模式）、
-f/--force（即使标记干净也检查——engine 无 clean 标记，预留）、
路径参数。范围外：修复/repair、online fsck、多设备、自动挂载检查。
