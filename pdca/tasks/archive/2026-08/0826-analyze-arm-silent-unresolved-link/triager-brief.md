# Triage Brief — analyze-arm-silent-unresolved-link

- **category**: enhancement
- **scenario_type**: research
- **summary**: 分析 dmsbtex/xmake-arm.lua 遗留死文件问题（用户指认），更正 T3975 审查中的误报 CRITICAL，沉淀死构建文件风险知识
- **current behavior**: xmake-arm.lua 全仓库零 includes 引用（grep 双重验证）；真正 ARM 构建走根 xmake.lua 的 os.arch() 分支复用同一份 dmsbtex/xmake.lua（deps 齐全：logger/tools/tls_cert）；T3975 将死文件误判为活跃 ARM 入口产生误报 CRITICAL
- **desired behavior**: 厘清文件历史与被取代过程、量化死构建文件的误导机制、给出处置建议（删除）、向 T3975 报告留痕更正
- **key interfaces**: xmake includes 解析范围、os.arch() 运行时分支、审查证据链的可信度维护
- **acceptance criteria**:
  - 运行 `ls records/<record>/analysis-report.md` 得到报告存在
  - 运行 `grep -c '误报\|更正' analysis-report.md` 得到 ≥1 处对 T3975 CRITICAL#3 的显式更正声明
  - 运行 `git log --follow -- dmsbtex/xmake-arm.lua` 的结论写入报告（文件诞生/最后一次实质修改时间线）
  - 处置建议含删除步骤与回归验证方式
- **out of scope**: 不执行实际删除（另行任务）；不重审 T3975 其余发现
- **information gaps**: 无——零引用已经 grep 全仓库验证
- **dedup results**: 无同类任务
- **recommended next steps**: Plan 终审后执行分析
