# PDCA 维护仓库入口

维护本包不等于实际运行正式 PDCA，不补造 Agent 或用户批准。当前版本 4.0.0-rc.2；[发布清单](release-manifest.md)固定当前文件。

核心不得回归：PDCA_ROOT 集中保存本体、records 和资源预约；TARGET_ROOT 只放获准的产品产物。八个 Skill 共用一中心；阶段切换不换原 Agent；每阶段用户启动，完成后等待；父 Agent 不监工、不代答。

安装参见 [INSTALL](INSTALL.md)，使用参见 [USE-PDCA](USE-PDCA.md)。不得把本文件覆盖到业务项目。已有任务采用原快照；参考资产不全量注入，历史指针不作为当前规则。

修改当前文件后更新 release-manifest.md，并运行 `python3 -m unittest discover -s tests -v` 与 `python3 scripts/check_release.py .`。它们不是现场宿主验收；现场清单在 tests/host-acceptance.md。
