# Triage Brief — 0824-xtrabackup-bin-retry-evidence

- **category**: enhancement
- **scenario_type**: research
- **summary**: 取证分析 GoldenDB 部署的 xtrabackup 二进制是否定制处理了首页校验(validate_first_page)问题或实现重试逻辑。
- **current behavior**: T0389 从源码证明上游零重试；但实际部署二进制可能含定制改动，源码结论不能直接外推。
- **desired behavior**: 二进制级证据报告：各关键函数的重试/恢复结构有无、backup 可达性、与上游差异清单。
- **key interfaces**: 表空间首页校验入口；备份拷贝游标读取；系统表空间启动校验路径（retry+doublewrite 恢复）；文件扫描注册循环。
- **acceptance criteria**:
  - 运行报告中给出的 nm/objdump 命令，能得到与报告一致的调用计数与函数边界 → AC 通过。
  - 对照报告"重试判定"章节，能独立判断每个函数有无重试结构 → AC 通过。
- **out of scope**: 反编译完整伪代码；非相关模块性能分析；修改任何二进制。
- **information gaps**: 无阻塞缺口（对象文件已在手，全部事实可自查）。
- **dedup results**: out-of-scope check 未命中；归档任务无同类主题。
- **recommended next steps**: 直接进入终审后产出取证报告。
