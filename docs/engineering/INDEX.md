# 工程技能入口迁移

本仓库本轮涉及的工程技能统一为 [systems-programming](../../skills/systems-programming/SKILL.md)，版本 3.0.0。其 SKILL.md 按实际任务选择内部参考资料；本页只记录旧入口的迁移位置，不另建规则来源。

| 原工程入口 | 统一入口内的资料 |
| --- | --- |
| secure-coding | [安全边界](../../skills/systems-programming/references/security-boundaries.md) |
| systematic-debugging | [根因调查](../../skills/systems-programming/references/debugging.md) |
| testing-strategy | [测试策略](../../skills/systems-programming/references/testing-strategy.md) |
| tdd-workflow | [测试先行与回归循环](../../skills/systems-programming/references/tdd.md) |
| code-review-checklist | [代码审查](../../skills/systems-programming/references/code-review.md) |
| build-config | [构建与依赖](../../skills/systems-programming/references/build-and-dependencies.md) |
| code-comments | [编码与文档](../../skills/systems-programming/references/coding-and-documentation.md)，专门补注另见项目约定 |
| chinese-environment | [可选项目约定](../../skills/systems-programming/references/project-conventions.md) |
| feature-commit-format、bug-commit-format | [提交与变更说明](../../skills/systems-programming/references/git-commit.md) |

中间整理过程中创建的 git-commit 独立入口同样归入上述参考，不作为最终技能保留。旧工程 SKILL.md 不保留别名副本；使用时统一调用 `$systems-programming`。

[PDCA 运行入口名录](../../skills/catalog.json) 仍只管理阶段、场景及定位流程，不因工程规范合并而改变。工程技能内部的方法不能自动启动正式 PDCA 生命周期。

本次范围是仓库内已知工程资产。当前宿主插件的启停、缓存和自身指令由宿主管理；本次未对其作修改或声称全局停用。统一工程技能自含所需方法，不依赖额外工程技能或插件。

迁移与验证证据见 [维护记录](../reviews/2026-10-29-engineering-skills-consolidation.md)。历史报告中的旧名保留为当时的来源标识，不作为当前入口。
