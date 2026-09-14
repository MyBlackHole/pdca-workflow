---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.2
authority: reference
status: active
---

# 集中项目绑定契约 v4

PDCA_ROOT统一保存规则、本体、任务与资源；TARGET_ROOT仅是业务项目。记录根为PDCA_ROOT/records，项目绑定在records/projects/<project>/workspaces/<workspace>/project-context.md。不得为跨项目调用创建第二个资源中心或TARGET_ROOT/.pdca。

项目身份由用户选择并集中登记，工作区对应规范化真实路径；不能只据目录basename或Git remote推导唯一项目。多个分支/worktree可属于同一project而有不同workspace。目录移动、两个ID指向同一目标、路径别名或多个匹配必须核对，不静默改绑。

现有task固定绑定优先于环境变量、cwd和当前入口版本；规则快照集中保存，不能将安装升级变成任务协议升级。业务写域、任务记录写域、公共知识与共享发布分别授权；全中心统一判断实际资源冲突。

安装器项目登记只新增元数据，不创建任务、不批准阶段、不修改目标项目指令或ignore。旧3.x及rc.1本地记录不自动搬迁，迁移需保存原字节与原始授权并核对未决操作。
