# Triage Brief — 0828-fix-squash-commit-msg-version

- **category**: bug
- **scenario_type**: bugfix
- **summary**: 修正 squash 合并提交的信息，并修正 libobk_version 误降版
- **current behavior**: 合并提交 24879258 提交信息为罗列式、版本表述混乱；根 xmake.lua 中 libobk_version 为 1.0.1.7（相对父 1.0.1.8 降版）
- **desired behavior**: 合并提交信息准确概括 F-139 TLS 安全链路整合与版本变化；libobk_version 恢复为 1.0.1.8（单调递增）
- **key interfaces**: 仓库根 xmake.lua 顶层版本变量；git 提交历史（amend）
- **acceptance criteria**: 运行 verify_version.sh 得到 PASS（libobk_version=1.0.1.8）；git log -1 首行概括 F-139 整合；提交信息含 libobk 版本 +1 说明
- **out of scope**: 不重排其他提交；不改其他组件版本号；不推送 origin
- **information gaps**: 无（已通过 Grill 确认修正范围选 A）
- **dedup results**: 无重复（新任务 T3993）
- **recommended next steps**: Do 阶段执行 amend（改 xmake.lua + 重写信息），Check 阶段运行 verify_version.sh 与 git log 校验
