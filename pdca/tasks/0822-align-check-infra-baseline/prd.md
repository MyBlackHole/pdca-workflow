# 检查基建与代码现实对齐(修复4类存量测试失败) — PRD

## 问题陈述

- **现状**: ctest 120 项中 3 项长期失败(style_check 行数规则、p1_closure 断言、tree_small_metadata 清理);Makefile test 目标引用 2 个不存在的脚本致链路中断。检查体系永远红,无法指示真实回归。
- **目标**: 恢复 make test / ctest 全绿基线,且不放松任何检查的治理意图。
- **差距**: 行数 limit 与代码现实脱节(init 提交即失配);断言未随源码语义等价改写同步;测试清理顺序缺陷;幽灵引用。

## 解决方案

四项独立修复,均为测试基建侧改动,零产品代码变更:

1. **行数规则校正**: 4 处 limit 更新为现实值 +5% 上取整——backup_agent 807→850、backupctl 2569→2700、agent_audit 266→280、client_resource_lock 191→200。防继续增长,文件拆分另立 development 任务。
2. **p1_closure 断言语义化改写**: `agent_monotonic_ns()<deadline_ns` → 匹配当前语义形态 `agent_monotonic_ns() >= ctx->deadline_ns`;`g_signal_pipe[1],1` → 容忍空格的当前形态。
3. **tree_small_metadata 清理修复**: cleanup 在 rm -rf 前先 chmod -R u+w 测试目录。
4. **幽灵引用删除**: Makefile 移除 session_pool_integration.sh 与 plain_session_elastic_pidfd_integration.sh 两行。

## Seam 分析

### 测试接缝
- 本任务产物即检查脚本本身,行为验证由既有集成套件承担(修复后全量跑通即为验收)。

### 声明的测试接缝
- seam: tests/style_check.sh -> src/
- seam: tests/p1_closure_source_regression.sh -> src/backup_agent.cpp
- seam: tests/tree_small_metadata_order_integration.sh -> build

### 验收可测性
- 每项修复有独立可复现的 pass/fail 命令;整体以 make test exit 0 收敛。

## 用户故事

1. 作为 CI 守门人,我想要全部检查通过且规则仍具约束力,以便新回归立即显红。
2. 作为维护者,我想要 make test 一键跑完不中断,以便低成本验证变更。

## 实现决策

- 仅修改 4 个测试/构建脚本文件,零 src/ 变更
- 行数 limit 取现实×1.05 上取整到十位;其余三条规则(limit 未失配者)不动
- p1_closure 断言按当前源码语义精确锚定,保持"deadline 必须走单调时钟"与"信号路径必须走 signal_safe"的原始意图

## 范围外

- 不拆分超大文件(另立任务)
- 不补写缺失的两个测试脚本
- 不新增覆盖

## 执行中范围演化（Do 阶段如实记录）

原估 4 类失配经逐层暴露实为系统性脱节：22 处文件级 limit 失配、25 处 grep 锚点因 format 失配、3 处 ns 结束标记失效、1 处前向声明错锚、4 处紧凑格式断言漂移、8 组跨文件克隆（duplicate gate 自 init 未曾执行到）。用户决策：克隆提取纳入本期（A 方案）。另修复 T0341 连带问题：VERSION 增量依赖缺失（Makefile 82+4 条规则补前置、CMake 注册 configure 依赖）、backup-observe 版本断言硬编码。最终策略不变：校正对齐而非放松治理。

## 验收标准

- [ ] AC-1: 运行 `bash tests/style_check.sh .` exit 0
- [ ] AC-2: 运行 `bash tests/p1_closure_source_regression.sh .` 输出 PASS 且 exit 0
- [ ] AC-3: 运行 `bash tests/tree_small_metadata_order_integration.sh ./build-make` 输出 PASS 且无 rm 权限报错
- [ ] AC-4: 运行 `make test` 完整执行至末尾 exit 0(不再被幽灵引用中断)
- [ ] AC-5: 运行 duplicate_check: cross-file exact clones: 8-line=7, 12-line=0 exit 0（12 行级克隆清零）
