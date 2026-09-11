# 优化 T2154 aio-tools 知识地图调用链细节

## 背景
T2154 已产出 `rdb-tools-design` skill 与版本化 references，用于 aio-tools/rdb-tools 代码知识地图导航。当前用户要求“进一步优化调用链细节”，目标不是重做知识地图，而是让调用者在进入 skill 后更稳定地完成：入口判断、版本选择、分册跳转、代码证据定位、跨模块调用链追踪和异常回退。

## 目标
在 T2154 产物基础上补强调用链使用说明，使 skill 从“知识地图目录”提升为“可执行的调用链导航协议”。优化应尽量落在既有 `rdb-tools-design` 目录中，保持 6.2.0.0 版本化结构和 T2154 证据链可追溯。

## 范围
1. 梳理现有 `SKILL.md`、`references/00-index.md`、01-05 分册中的调用链相关内容，识别入口、跳转、跨分册、证据定位、失败回退的缺口。
2. 在 `SKILL.md` 增补调用链执行步骤：触发条件、版本选择、请求分类、分册选择、代码证据读取顺序、输出格式、回退策略。
3. 在 `references/00-index.md` 或对应分册补充调用链路由矩阵/锚点，使常见问题能从入口定位到具体分册与代码路径。
4. 保持 T2154 版本化格式：不破坏 6.2.0.0 目录组织，不将旧证据改写成不可追溯状态。

## 非目标
- 不重新审计 aio-tools 全仓源码。
- 不改变 T2154 已归档 verdict。
- 不新增与 aio-tools 无关的通用 PDCA 流程规则。

## 验收标准
- [ ] AC-1 `rdb-tools-design/SKILL.md` 明确给出调用链执行协议，覆盖入口判断、版本选择、分册跳转、证据读取、输出约束和失败回退。
- [ ] AC-2 `references/00-index.md` 或分册中存在可操作的调用链路由矩阵，至少覆盖 fs-backup、rpc/rdbcomm、libs、s3/xbsa、build/release 五类入口。
- [ ] AC-3 修改保持 T2154 版本化结构可追溯：相关文件仍能引用 6.2.0.0 基线，且通过文本检查确认没有断开的本地引用。

## 关联输入
- T2154 record：`/home/black/Documents/pdca-workflow-pro/records/T2154-0910-aio-tools-knowledge-map/`
- 目标 skill：`/home/black/Public/aio/rdb-skills/skills/rdb-tools-design/`
