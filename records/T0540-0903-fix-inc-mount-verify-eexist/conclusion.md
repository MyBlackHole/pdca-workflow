# Conclusion — T0540 修复增量备份 mount_verify 临时目录 EEXIST 失败

## 判定
confirmed

## 证据对照

### AC-1 增量备份遇到 mount_verify 临时目录消失不再中断整体备份
- **证据**: `ev-fix-diff` (`fix-diff.md`), `ev-transfer-fix` (`transfer_file.cpp:372-384,464-483`), `ev-rpc-fix` (`rpc.cpp:1986-1991,2024-2029`)
- **验证**: 
  - `transfer_file.cpp` 新增 `is_ephemeral_dir()` 识别 `mount_verify*`/`DISK_CHECK*` 前缀，`backup_new_directory` 在 `ENOENT/ENOTDIR/IO_EOF(-3)` 时对临时目录返回 0（Warning 跳过）而非 -1 中断
  - `rpc.cpp` 修复 stale errno 打印，`ret==-3` 时显式打印 `IO_EOF` 而非 `strerror(errno)` 的陈旧 `EEXIST`
  - 逻辑上：临时目录消失属于可容忍的竞态，非临时目录仍保持失败中断，保证不掩盖真实备份缺失
- **结果**: PASS — 覆盖 AC-1，`convergence-map` index 1 已映射

### AC-2 回归测试覆盖临时/非临时路径差异行为
- **证据**: `ev-test-report` (`test-report.md`)
- **验证**:
  - 9 场景测试：mount_verify/DISK_CHECK + ENOENT/ENOTDIR/IO_EOF 均判为 skip；非临时路径 + ENOENT 判为 not skip；EACCES 不 skip
  - 覆盖边界：空路径、NULL、嵌套路径、前缀精确匹配
  - 结果 9/9 PASS
- **结果**: PASS — 覆盖 AC-2，`convergence-map` index 2 已映射

### AC-3 存量单测与构建无回归
- **证据**: `ev-test-report` (`test-report.md`)
- **验证**:
  - `xmake build` 100% ok (9.527s) 无新增告警
  - `xmake test` 32/32 passed (0.291s)，含 `fs_meta_comprehensive_test`、`readdir_tree`、`mkdir_path_test` 等核心用例
- **结果**: PASS — 覆盖 AC-3，`convergence-map` index 3 已映射

## 本体沉淀
- 本任务消费 `ontology:domain/backup`（增量备份容错）与 `ontology:concept/failure-mode`（失效模式 #3 代码跑不起来）
- 沉淀建议：后续可将临时目录前缀抽为 `fs-backup` 可配置 exclude 列表（当前为硬编码，PRD 开放问题已记录），并在 `ontology:domain/backup` 下新增 `backup-ephemeral-dir-tolerance` 模式节点

## 风险与遗留
- 风險已控制：仅 `mount_verify*`/`DISK_CHECK*` + `ENOENT/ENOTDIR/IO_EOF` 放行，其余仍失败；Warning 日志带路径/ret/errno 可审计
- 遗留：配置化待评估，不影响当前 verdict

## Verdict
confirmed — 三项 AC 均有直接证据支撑，构建与测试零回归，符合 PRD 目标
