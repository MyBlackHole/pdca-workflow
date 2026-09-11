# cross-project.1 增量功能

基于 3.4.4 增加显式跨项目双目录接入。协议/schema版本不批量升级；新增附件有独立 extension_revision。原固定历史和正式示例不改写，新跨项目工作固定更新后的发布清单及本附件摘要，旧任务继续使用原固定快照。

新增 USE-PDCA 入口、双目录契约、workspace/context/index 三个模板、使用示例及维护测试清单。records/<task-id> 和 records/works/<work-id> 不变，项目索引只关联这些对象；源码和产品测试在目标，设计/记录/报告/证据在 PDCA。

更新导航和私有证据 ignore 路径。默认不创建目标入口、不移动 .trellis、不执行 Git 写操作、不添加适配器。旧维护程序继续检查原普通/生命周期profile；跨项目单独提供范围有限的本地文件验证，不声称生产资格。
