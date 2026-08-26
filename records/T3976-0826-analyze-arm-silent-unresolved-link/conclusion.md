---
schema: pdca.asset/v1
id: T3976-0826-analyze-arm-silent-unresolved-link
phase: check
source_ids: [analysis-report]
---

## 上下文

用户指认 dmsbtex/xmake-arm.lua 为遗留多余文件，与 T3975 审查 CRITICAL#3 冲突。任务重定义为：分析死文件问题并更正审查结论。

## 假设与结果

- 假设：该文件不参与任何构建路径，T3975 相应发现为误报。
- 结果：成立。三重验证——零 includes 引用（grep 全仓库）、可达性扫描（40 lua 唯一死配置）、git 考古（B-1551 诞生起从未接入）。

## 分析

- **AC-1** ✅ analysis-report.md 存在且含历史时间线章节（B-1551 ×4 重复提交、0ec03d3d 机械同步证据）（analysis-report）
- **AC-2** ✅ 含对 T3975 的显式更正声明，Blocking 计数 CRITICAL 4→3（analysis-report）
- **AC-3** ✅ 同类风险面盘点完成：唯一死配置为该文件；packages/o/openssl4 两 lua 经 add_repositories 约定加载属活跃文件；附录脚本复跑实证一致（analysis-report）
- **AC-4** ✅ 处置建议含删除步骤、回归验证方式、防再积累机制三项要素（analysis-report）

关键结论均附可复核命令：git log --follow（2 提交）、grep xmake-arm（0 引用）、扫描脚本复跑（1/1 命中）。Check 独立复核与 Do 输出一致，无待验证假设。

## 适用边界

- 结论针对当前 HEAD 快照；若未来引入变量拼接式 includes 或通配符 includes，扫描脚本需升级（附录 A 已声明限制）。
- 更正仅覆盖 T3975 的 CRITICAL#3；其余 ~109 条发现不受影响。

## 下一轮建议

- 另行小任务执行 `git rm dmsbtex/xmake-arm.lua` + 回归验证（xmake -y / test 44 条）。
- 将可达性检查固化为 CI/pre-commit（白名单 packages/）。
