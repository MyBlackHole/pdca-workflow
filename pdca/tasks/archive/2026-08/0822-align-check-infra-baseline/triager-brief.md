# Triage Brief — align-check-infra-baseline

- **category**: bug
- **scenario_type**: bugfix
- **summary**: 修复 4 类测试基建与代码现实脱节的存量失败,恢复 make test / ctest 全绿基线
- **current behavior**: ctest 120 项中 3 项失败(p1_closure/tree_small_metadata_order/style_check 行数规则);Makefile test 目标引用 2 个不存在的脚本导致链路中断;style_check 因 4 处行数规则失配永远红
- **desired behavior**: 全部检查与测试通过,失败信号重新具备"指示真实回归"的可信度
- **key interfaces**: 风格检查脚本;源分解行数规则;p1 闭包回归脚本;集成测试清理逻辑;构建测试目标清单
- **acceptance criteria**:
  - 运行 bash tests/style_check.sh . 输出 PASS(exit 0)
  - 运行 bash tests/p1_closure_source_regression.sh . 输出 PASS
  - 运行 tree_small_metadata_order 集成测试输出 PASS 且无 rm 权限报错
  - 运行 make test 完整跑完不中断且 exit 0
- **out of scope**: 大文件拆分(另立 development 任务);新增测试覆盖;放松任何检查的治理意图
- **information gaps**: 无(根因已在 T0341 Check 阶段与本次核查中全部定位)
- **dedup results**: T0341 结论"下一轮建议"即本任务来源,无其他重复
- **recommended next steps**: 单轮 Grill 确认行数规则处置策略后合成 PRD
