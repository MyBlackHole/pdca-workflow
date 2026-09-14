# 安装一次，多个项目调用同一个 PDCA

## 双根与归属

`PDCA_ROOT` 是集中规则、本体、过程资料和资源管理根，默认 `~/.agents/pdca`；`TARGET_ROOT` 是用户选择的真实业务项目。环境变量或当前目录只能提供候选，已有任务固定绑定优先；冲突时停止，不能猜另一个根。

```text
PDCA_ROOT/
  skills/                         # 8 个入口的维护源，不各建 records
  bootstrap/ ontology/ templates/ # 当前规则、方法与集中知识
  ontology/projects/<project>/    # 项目领域模型，按 work/revision 隔离
  records/
    projects/<project>/workspaces/<workspace>/project-context.md
    works/<project>/<work>/       # 工作树、种子、模型版本、投影映射
    tasks/<task>/                 # 私有 task、plan、control、events、证据
    resources/<reservation>.md    # 全中心实际资源预约；不是锁的替代品
    protocol/<version>-<digest>/  # 集中固定规则快照，活动任务不跟随更新
TARGET_ROOT/
  <获准的业务源码、产品测试、产品文档或配置>
```

业务项目默认不生成 `.pdca/`，不复制 PDCA 规则、不写入独立的流程状态。已有外部模型或业务产物可明确采用，其引用、版本、映射与证据集中登记。公共知识、项目模型、任务草稿分别授权；集中存储不等于跨项目任意读取或写入。

## 安装与项目登记

执行 [INSTALL](INSTALL.md) 的安装器注册八个全局入口。它只管理安装和集中项目登记，不是任务运行器，不创建 Agent、不批准阶段、不取得业务资源锁。默认预览，`--apply` 才写入。

用户首次明确采用 PDCA 时，集中登记 project_id、workspace_id、规范化 TARGET_ROOT 与规则版本。可执行 `./setup register --project <真实项目根> --project-id <名称> --workspace-id <名称> --apply`。同一目标已有登记时沿用它；移动项目、重命名工作区或切换规则另行迁移，不把旧确认重新签为当前授权。原项目指令、Git 设置和业务文件不修改。

`./setup locate --project <当前目录>` 只读取集中绑定并返回匹配；多个可用任务必须让用户指定，不能只选最新任务。子 Agent 直接获得自己的 context/task 引用，不扫描所有任务的内容。

## 八个入口，两种维度

总入口 `pdca` 定位和分流；阶段入口 `pdca-plan/do/check/act` 操作已绑定任务；场景入口 `pdca-ontology-modeling/projection/conformance-verification` 提出或选择场景任务，也提供该场景的方法。完整名称见 [技能索引](skills/README.md)。

每场景、每节点、每 attempt 各有独立可交互 Agent 完成四阶段。**切换 Skill 不换 Agent**。在父会话调用阶段入口时，仅将原始用户操作路由到原任务，不代执行；缺可继续原实例的能力就阻断。

仅发现或加载 Skill 不授权创建或启动。新建获准后，任务 Agent 先展示 Plan 目标并等待；每阶段完成后报告产物、限制和下一目标，再等待用户。三个场景不是 Plan/Do/Check 的别名，不能自动串联。

## 集中资源与独立执行

所有项目对同一个文件、目录、设备、数据库等的访问都进入同一资源冲突范围，按实际对象识别而非 task/branch 名称。每个任务仅写自己的记录与获准业务作用域。资源取得、撤销和结清必须有真实依据，详见 [RESOURCE](ontology/concept/resource-ownership.md)。集中账本不代表真实排他；不满足所需保证时阻断冲突任务，不改为父 Agent 监工。

## 恢复与升级

每次正式操作先定位集中 context、原 task/Agent、最后完整事件、当前 run、请求／响应和未决资源。已固定任务使用其 `protocol_baseline_ref` 所在快照，不能用入口最新版本替代。恢复不产生授权，也不自动重放操作。

宿主未提供持久入口或重载时，用显式 Skill 调用恢复；不能承诺永不遗忘。安装器不暗改全局规则或注册假想 hook。[全局短引导](bootstrap/global-entry.md)可由用户按宿主实际支持的位置明确安装。

已有 rc.1 项目本地 `.pdca/` 不自动删除或搬迁，按 [迁移说明](migration/v4.0.0-rc.2-MIGRATION.md)保留原字节、原批准与未决资源。安装一次不是迁移旧任务。
