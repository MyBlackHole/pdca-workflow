---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.2
authority: reference
status: active
---

# 集中项目绑定契约 v4

PDCA_ROOT统一保存规则、本体、任务与资源；TARGET_ROOT仅是业务项目。记录根为PDCA_ROOT/records，项目绑定在records/projects/<project>/workspaces/<workspace>/project-context.md。不得为跨项目调用创建第二个资源中心或TARGET_ROOT/.pdca。

项目身份由用户选择并集中登记，工作区对应规范化真实路径；不能只据目录basename或Git remote推导唯一项目。多个分支/worktree可属于同一project而有不同workspace。目录移动、两个ID指向同一目标、路径别名或多个匹配必须核对，不静默改绑。

现有 task 固定绑定优先于环境变量、cwd 和当前入口版本；入口真实路径所在 Git 根必须与绑定的 PDCA_ROOT 一致，冲突即停止。更新集中 Git 工作副本不自动改绑或升级活动任务。业务写域、任务记录写域、公共知识与共享发布分别授权；全中心统一判断实际资源冲突。

`pdca` 只读定位已有绑定；新增或修改绑定前列明具体文件并核对用户的记录写入授权。明确批准后按[上下文格式](record-shapes/project-task-context.md)保存 `project_id`、`workspace_id`、`target_root`、`pdca_root`、`records_root`、`rules_git_head` 与 `rules_git_status`。记录根必须是 PDCA_ROOT/records；真实路径不能经符号链接写入其他根。登记只新增获准元数据，不创建任务、不批准阶段、不修改目标项目指令或 ignore。

每次获准写入绑定、任务或事件前，在 PDCA_ROOT 执行只读 `GIT_OPTIONAL_LOCKS=0 git rev-parse HEAD` 与 `GIT_OPTIONAL_LOCKS=0 git status --porcelain`，禁用可选索引写入，保存当时的 HEAD 和原样工作树状态（干净为空字符串）。Git 命令失败、无有效 HEAD 或权限不足时停止，不用未知值继续写入。Git 跟踪不扩大读写授权；这些字段仅供追溯，不是不可变快照，不复制规则或自动 checkout 历史提交。

Git 提交授权与记录写入授权分开；用户另行明确要求提交具体范围才执行相应 git add/commit，不自动提交、拉取、切换分支、暂存、还原或覆盖集中工作树。已有旧记录不自动搬迁或重写，原规则依据缺失或冲突时停止并说明；历史指针不成为当前规则。
