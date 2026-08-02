# T0195 fsck 风格 CLI：verify_all 健康检查入口

## 问题陈述

subvol 是纯库，verify_all 聚合校验（T0194）仅内部测试可用；外部调用方
无法对持久化引擎文件运行一致性检查。上游 bcachefs 提供 fsck 命令
（src/commands/fsck.rs）作为文件系统一致性检查入口，engine-local 缺少
对应 CLI。

## 目标

新增 `subvol-fsck` 二进制：打开持久化引擎 → 运行 verify_all → 输出
校验结果 → 退出码反映结果（对齐 `bch2_fs_fsck_errcode` + exit(ret) 语义）。

## 验收标准

- [ ] AC-1: 修改前逐段记录上游 fsck CLI（参数/流程/退出码）与引擎持久化 API 锚点。
- [ ] AC-2: subvol-fsck 打开持久化引擎运行 verify_all，通过退出 0，失败退出非 0 并输出具体错误（DerivedState 变体）。
- [ ] AC-3: CLI 仅 no-repair 模式（对应上游 -n），参数表对齐上游 fsck（-n/--no-repair、-f/--force、路径）。
- [ ] AC-4: 集成测试：损坏引擎文件（索引不一致）fsck 失败非 0 且输出包含错误名；健康引擎退出 0。
- [ ] AC-5: 库 API 不变；verify_all 行为不变（CLI 仅是调用方）。
- [ ] AC-6: workspace 全量测试、fmt、diff gate 通过，单项不超过一分钟。

## 实现决策

- bin 放 `crates/subvol/src/bin/subvol-fsck.rs`（与库同 crate）。
- 参数解析不用 clap（保持零依赖，与库一致）；手写简单解析或 std。
- 退出码：0 = 通过；1 = 校验失败；2 = 打开/IO 错误（区分校验失败与
  不可打开）。
- 输出：校验失败打印 `ERROR: <DerivedState 变体名> <详情>`（对齐
  bch2_fs_fsck_errcode 的错误打印）；通过打印 `OK`。

## 范围外

修复/repair 路径、online fsck、多设备、自动挂载检查、-y/-r 参数。

## 备注

前置：T0194 已归档，verify_all 聚合入口已就绪。
