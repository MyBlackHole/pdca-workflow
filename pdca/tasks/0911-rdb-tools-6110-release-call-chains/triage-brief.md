---
schema: pdca.asset/v1
id: T2182-triage-brief
task_id: T2182
ontology_role: ontology_projection
---

# T2182 Triage Brief

## 分类

- 类型：enhancement。
- 专业职责：`ontology_projection`。
- 优先级：P1。

## 查重

- 未发现现有 6110 release 独立调用链任务。

## 已验证事实

- 唯一源码树：`/home/black/Public/aio/aio-tools/6110/release`。
- 分支与提交：`6.1.1.0-release@5ec42fd4`。
- 顶层 Xmake/Makefile 和入口初步独立发现 23 个候选业务工具。
- 产物为现有 `rdb-tools-design` 的五份 `6.1.1.0.md` 版本地图及共享路由更新，不修改产品源码。

## 用户决策

- “只需要发布分支”。
- “完全独立不依赖 6200”。
- 对新建独立 skill、全业务操作覆盖、静态验证边界答复“按推荐来”。
- 最终给出 `rdb-feature-design/references/` 树作为结构参照：总索引 + 业务域目录 + 每版本一文件；明确不要 `-6110` 后缀目录。

## 执行交接

Do 只能把 T2182 PRD、任务元数据和 6110 release 作为业务事实输入；可读取 `rdb-feature-design` 与现有 `rdb-tools-design` 的共享入口/索引以落实结构，但不得把 6200 源码或 `6.2.0.0.md` 当作 6110 事实。实现须更新 `SKILL.md`、`00-index.md`，并在五个现有知识域目录各新增 `6.1.1.0.md`；跨端必须双向闭合或明确标记未闭合。

## 下一步

等待用户对完整 PRD 作 final confirmation；确认后通过官方阶段门禁进入 Do，并派发与 T2182 一对一绑定的新执行上下文。
