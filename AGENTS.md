# 项目入口

标准技能发现入口见[SKILL](SKILL.md)，只负责同一流程交接；不重复启动。使用 PDCA 时，先读[USE-PDCA](USE-PDCA.md)固定本次双根，再按[入口交接](bootstrap/entry-check.md)明确读取[ontology/README](ontology/README.md)及当前适用规则，不停在使用说明。

目标是新工作初始真实 cwd，不因读到了本仓库规则而切换为本仓库；父派发/恢复沿用固定 project-context。流程/模板与新 records 布局锚定 PDCA_ROOT；Markdown 链接锚定所属文件；源码和开发 cwd 锚定 TARGET_ROOT。

外部项目通过实际加载的[全局入口](bootstrap/global-entry.md)或用户明确读取指令进入。本文件不会因为配置环境变量而跨目录自动加载，不安装 adapter，不复制核心规则，不把维护操作声明为已运行的 PDCA 任务。

加载后继续[真实派发入口](bootstrap/dispatch-guide.md)：宿主派发根/就绪节点的完整PDCA，并先提交容量内的独立任务再等待；已有真实任务绑定的子Agent核验后执行自己的Plan，不再派发自己。缺能力不得转成“草稿归档”。
