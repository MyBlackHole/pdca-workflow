# PDCA 维护仓库入口

维护本包不等于实际运行正式 PDCA，不补造 Agent 或用户批准。集中根是 Git 工作副本，当前规则与修改通过 Git 审阅和追溯。

核心不得回归：PDCA_ROOT 集中保存本体、records 和资源预约；TARGET_ROOT 只放获准的产品产物。九个 Skill 共用一中心；阶段切换不换原 Agent；每阶段用户启动，完成后等待；父 Agent 不监工、不代答。pdca-assist 仅显式调用、默认只读；记录写入与 Git 提交分别授权。

安装与更新参见 [INSTALL](INSTALL.md) 和 [install.sh](install.sh)，使用参见 [README](README.md)。不得把本文件覆盖到业务项目。已有任务保留原绑定、Git 来源与原授权，依据缺失或规则冲突时停止；参考资产不全量注入，历史指针不作为当前规则。

修改当前文件后运行 `python3 -m unittest discover -s tests -v` 与 `git diff --check`。它们不是现场宿主验收；现场清单在 [tests/host-acceptance.md](tests/host-acceptance.md)。
