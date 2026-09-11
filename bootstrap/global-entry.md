# 通用 PDCA 全局入口 · cross-project.2-hotfix.3

将以下正文放入宿主实际会加载的个人/全局指令一次。更新仓库不会更新过去复制的全局正文，需一并替换。不在每个目标内安装文件，也不自动修改用户配置。

---

对每个新开发工作，先在本会话实际工具环境观察真实 cwd 和唯一的环境变量 PDCA_ROOT；不要先 cd 到规则库。不得通过环境转储收集其他变量。

**启用条件**：用户明确要求 PDCA、用户已选择 PDCA 默认工作流，或本会话观察到非空 PDCA_ROOT，任一成立即使用 PDCA。非空 PDCA_ROOT 在本条已加载时就是工作流选择，不再要求用户重复说“使用 PDCA”。用户明确要求本次不用 PDCA 则不启用，遵守更高优先级指令。未启用且变量为空，不对普通项目强行查找或初始化 PDCA。

父派发/恢复不是新工作：必须沿用并核验固定 project-context；缺失时报告上下文缺失，不按子 Agent 默认 cwd 新建绑定。新工作 TARGET_ROOT=初始真实 cwd；PDCA_ROOT=非空配置相对该 cwd 解析的真实目录，未设置/空值则等于 TARGET_ROOT。不能自动上提到 Git 根或在错误配置时回退。

保持工具开发 cwd 为 TARGET_ROOT，用绝对路径读取 PDCA_ROOT/USE-PDCA.md，随后**必须继续读取 PDCA_ROOT/bootstrap/entry-check.md，按其显式读集加载 PDCA_ROOT/ontology/README.md、权威与阶段入口**。不能读完使用说明就直接修改源码，也不能期待另一仓库的 AGENTS.md 自动加载。读取一次即可，已读入口互相链接不形成递归加载。

所有流程规则/模板路径锚定 PDCA_ROOT；正文中的 records/... 布局锚定 PDCA_ROOT；产品源码路径锚定 TARGET_ROOT；Markdown 相对链接以该文件位置解析，旧固定记录引用遵守原 ref_base。禁止将它们统一相对工具 cwd 解析。目标自己的原生指导仍按宿主规则读取，冲突不能靠覆盖解决。

先回报实际 TARGET_ROOT、PDCA_ROOT、资料根、已读取的协议版本及当前阻断层级，再按原 TASK/CAP/RESOURCE/CONFIRM 推进。只读到规则不等于有写权、新 Agent 或阶段批准；能力不足要列具体缺项，不能笼统称路径错误或自己模拟。流程资料只进入 PDCA_ROOT/records 获权区，开发留在固定 TARGET_ROOT 获权区；不得创建目标 .pdca/records 兜底。

---

本文件是加载指令，不是自动安装程序。没有实际加载本条的宿主不会因磁盘上存在此文件而自动运行。它也不证明真实全局加载、独立 Agent、权限或完整 PDCA 已运行。
