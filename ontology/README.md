# AI 工作入口

跨项目先完成[入口交接](../bootstrap/entry-check.md)的固定双根和读取事实。下面的 Markdown 链接相对本文件；协议文件/模板及新 records 布局锚定 PDCA_ROOT，源码命令锚定 TARGET_ROOT。只读过 USE-PDCA 不代表已运行本文要求。

先读[唯一权威与设计目标](concept/pdca.md)并固定[协议发布清单](../protocol-release.md)。保留用户原目标；ontology_modeling是场景选择，不把审查项目改成建设系统。维护文件编辑不是已运行的正式PDCA。

派发前按[TASK](concept/pdca-task.md)/[CAP](concept/capability-protocol.md)核实真实新Agent、独立交互路由、确认消费、写权、控制和摘要能力。缺失保持blocked_unexecuted，不用父Agent模拟或自己确认；未知派发先查询。[恢复](concept/pdca-recovery.md)不倒填旧记录。

正式任务按[阶段入口](process/pdca-flow-model.md)运行；[按需定位表](LOAD-MAP.md)只导航，不替代权威。当前建模Plan采用[通用入口suite](../tests/modeling-entry/suite.md)的本地固定绑定和真实确认；Do产生定义/实例/直接seed及当前节点三场景suite。未来运行可not_run，必需规范不可not_defined；父本地完成不等后代。

[REUSE](concept/ontology-reuse.md)/[NODE](concept/work-node-contract.md)/[DECOMP](concept/task-decomposition.md)规定复用、双产物与递归；[TEST](concept/task-unit-test.md)/[CASE](concept/task-test-case.md)要求真实正负样本、独立oracle与保留观测；[REWORK](concept/task-rework.md)保留失败、阻断影响、完整回归和累计预算。

[TREE](concept/work-ontology-tree.md)在整树确认前核验技术readiness、完整闭包和终态；[VERDICT](concept/pdca-verdict.md)分开本地交付、工作issue和精确版本发布。历史异常只追加完整性记录；新版不能自动使旧run有效。

按需定位[审查定义](concept/audit/project-review.md)、[模板](../templates/README.md)、[原材料回归](../tests/records-regression/README.md)和[全索引](INDEX.md)。fixture/source/模板不是授权；不全库加载，不安装adapter。

## 跨项目入口（显式采用）

目标不在本仓库时，先读[USE-PDCA](../USE-PDCA.md)和[双目录应用投影](contracts/project-workspace.md)，分别固定协议资料根与开发根。保留用户原目标，不因读取PDCA规则而把开发目标改成PDCA项目；固定的project-context随新Agent派发输入传递。
