# PDCA 维护仓库入口

维护本包不等于实际运行正式 PDCA，不补造 Agent 或用户批准。集中根是 Git 工作副本，当前规则与修改通过 Git 审阅和追溯。

核心不得回归：PDCA_ROOT 集中保存本体、records 和资源预约；TARGET_ROOT 只放获准的产品产物。九个 Skill 共用一中心；阶段切换不换原 Agent；每阶段用户启动，完成后等待；父 Agent 不监工、不代答。pdca-assist 仅显式调用、默认只读；记录写入与 Git 提交分别授权。

[ontology/INDEX.md](ontology/INDEX.md) 是当前 authority 的定位索引，[ontology/LOAD-MAP.md](ontology/LOAD-MAP.md) 定义 AI 按事件最小读取的方法。domain/entity/pattern 等参考知识不能因路径、链接或 authority 字段自动进入任务，必须按 REUSE/ADOPT 固定采用。

## 审查原则

维护 PDCA 本身时，不创建 Python/Shell 等项目专用 semantic validator 来重新编码 PDCA 规则。
AI 直接读取当前 Skill、authority、Plan、diff/产物和证据，按 [flow-check](ontology/process/flow-check.md) 做：

1. Scope Review；
2. Consistency Review；
3. Adversarial Review；
4. Evidence Review。

通用命令只采集事实，例如 `git diff`、`git status`、`git show`、`rg`、`sh -n install.sh`。
业务项目已有测试也只作为 evidence。不要维护“Skill 必须几个”“某 authority 应是什么”之类的脚本断言；
这些语义由 AI 从唯一权威直接判断。

高影响变更可使用一次性只读独立 AI 第二视角，但不创建新的 PDCA 生命周期、不轮询监工，其结论仍需当前 Check 验证证据与反证。

安装与更新参见 [INSTALL](INSTALL.md) 和 [install.sh](install.sh)，使用参见 [README](README.md)。不得把本文件覆盖到业务项目。已有任务保留原绑定、Git 来源与原授权，依据缺失或规则冲突时停止；参考资产不全量注入，历史指针不作为当前规则。

机械检查可以使用 `sh -n install.sh` 与 `git diff --check`；它们不解释 PDCA 语义，也不替代 AI Check。真实宿主验收见 [tests/host-acceptance.md](tests/host-acceptance.md)。
