# Triage Brief — 0824-checksum-mismatch-datafile

- **category**: enhancement
- **scenario_type**: research
- **summary**: 分析 XtraBackup 使用中 "Checksum mismatch in datafile" 报错的产生机制与全部可能根因，产出根因分析报告。
- **current behavior**: 报错出现时用户只知道某个数据文件校验失败，缺乏从错误文案到代码判定逻辑、再到物理根因的完整映射。
- **desired behavior**: 一份结论文档：精确定位报错在源码中的产生点，拆解页损坏判定的全部分支，给出按发生阶段组织的排查决策树与每类根因的可观测验证手段。
- **key interfaces**: 表空间文件首页校验入口（Datafile 校验逻辑）；页损坏判定内核（BlockReporter 判定逻辑）；备份阶段逐页读取游标（xb 文件游标读取循环）；页内校验和字段布局（页头 checksum 字段、页尾 old-checksum/LSN 尾字段）。
- **acceptance criteria**:
  - 运行 `grep -rn "Checksum mismatch"` 于本仓库 InnoDB 存储层目录，得到唯一拼接点文件，且报告引用该位置并解释两段文案如何拼合 → AC 通过。
  - 阅读报告中"判定分支"章节，能对任意一个真实损坏样本指出命中的分支（分支数 ≥5 且各有行号证据）→ AC 通过。
  - 运行报告中决策树章节给出的诊断命令（innochecksum / hexdump 关键偏移 / keyring 状态检查），命令均可直接复制执行且有预期输出说明 → AC 通过。
  - 对照报告根因清单（≥6 条），每条存在对应的排查手段描述，无"仅罗列无验证方法"条目 → AC 通过。
- **out of scope**: 修复任何被判定为缺陷的代码（如需修复另立 bugfix 任务）；非 InnoDB 数据文件（MyISAM、undo/redo 日志文件本身损坏的分析）；性能优化。
- **information gaps**: 错误实际发生的阶段（backup / prepare / copy-back / 恢复后 mysqld 启动）；是否使用加密或压缩表空间；是否有完整报错日志（含 Space ID、Flags、文件路径）。这些缺口不阻塞研究主体（代码机制分析），但影响排查决策树的定制深度，P2 Grill 向用户确认。
- **dedup results**: out-of-scope-manager check "checksum-mismatch-datafile" 未命中；活跃任务目录与归档目录 grep 无同名主题历史任务。
- **recommended next steps**: P2 向用户确认发生阶段与环境特征（加密/压缩/GoldenDB 定制改动），随后 Do 阶段产出根因分析报告 conclusion 文档。
