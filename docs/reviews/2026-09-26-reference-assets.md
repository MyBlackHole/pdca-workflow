# 首批参考资产治理：维护审查记录

日期：2026-09-26。审查基线：`f7bd52ada68df583d567f4fa59460ebd916e242e`（已合并 PR #14）。
这是同一 AI 对本包维护变更的审查记录，不是正式 PDCA Task、独立 Agent 评审或宿主验收。
按基线 [AGENTS](../../AGENTS.md) 与 [flow-check](../../ontology/process/flow-check.md) 阅读并核对，没有新增语义验证脚本。

## Scope Review

本批按内容核对两份操作型 reference、三份退役指针与一份短定义，属于定向审查，不是全库清洗。
配套读取 REUSE、ADOPT、EVOLVE、INDEX、来源说明及 TRANSITION/EVIDENCE 当前权威。
不改变 Task 拆分、fresh Agent、上下文隔离、阶段授权、Work Unit、安装器、CI、记录 schema 或活动记录。

| 对象（路径相对于仓库） | 基线 blob SHA | 处置与依据 |
|---|---|---|
| `ontology/domain/pdca/skill-advance-phase.md` | `8f51e30618067a4a484ff402e3cf2396d77d7587` | 原位 archived；“单阶段回执”不如 TRANSITION-01 的 phase_started / phase_completed / archived 事件精确，且重复当前方法 |
| `ontology/domain/pdca/skill-register-evidence.md` | `fedfa8c0b51459bfabf5c129dafbb1648be64840` | 原位 archived；仅重述证据登记步骤，没有独立案例或运行证据。保留正文，导航到 EVIDENCE-01 与当前格式 |
| `ontology/concept/auto-induce-flow-trigger.md` | `ccbb3008822450a73f47e140603508450ef02b04` | 保持 retired；移除指向缺失 legacy 原文的链接，保留旧路径和明确的来源缺口 |
| `ontology/contracts/lifecycle-records.md` | `f0abd7549ad6b5bae106d5314fad4035387badc1` | 保持 retired；同上，不恢复旧 schema 或自动转换 |
| `ontology/contracts/record-relations.md` | `ae7b70e808c67ff6be1a9668012e4a20baf6f7c4` | 保持 retired；同上，不以兼容指针代替原文 |
| `ontology/concept/agent-brief.md` | `bf64a6e016cc3c19ff353311d7d04eb9cca344b5` | 原字节保留；虽正文仅一句，但有 ID 和 specializes 关系，不能凭长度判断无价值。保留 active + reference + unverified，不宣称已验证 |

## Consistency Review

参考生命周期只在既有 [REUSE-01](../../ontology/concept/ontology-reuse.md) 定义；ADOPT 与说明页只引用它。
active-reference 是现有两个字段的组合称呼，不新增 status 同义值、authority ID、Skill、schema 或 manifest。
archived 与 retired 只描述参考资产处置，不能套用到 Task 的归档事件或正式模型状态。

两份 archived 资产保留 ID、路径、relations、provenance、validation 和完整历史正文，只更新状态、revision、日期及增加归档说明。
三份 retired 指针保持原 status/schema/path；README 与 INDEX 不再声称当前树拥有 legacy 字节副本。
被替代的权威与 evidence 格式不修改，不把归档当成内容被证伪，也不把维护审查当作运行证据。

## Adversarial Review

- **短文档是否仍有价值？** agent-brief 有稳定 ID 和关系，未找到足以删除/合并它的依据，因此不动。
- **未验证是否意味着过时？** 不意味着。两份归档保持 unverified；没有对领域研究做普遍降级。
- **能否挑旧 active 修订绕过归档？** REUSE 要求新采用同时核对当前处置说明和固定修订，不仅检查所选旧文件的 status。
- **新状态是否会强制迁移旧任务？** REUSE/ADOPT 明确保留旧固定采用；替代链接不自动改绑，确证错误只影响相关动作。
- **历史正文里的命令会不会仍被当成当前步骤？** 归档说明置于原正文之前；REUSE 排除其作为普通新任务执行依据，恢复须先审查并获准产生新修订。
- **legacy 缺失是否代表历史已永久丢失？** 不能这样推断。根目录读取证明基线没有该目录；对 auto-induce-flow-trigger 旧定位的路径历史查询返回空，但未遍历所有 Git refs 或用户本地副本。
- **改变状态是否破坏其他文档链接？** 本批不删除/移动文件或改 ID，保留旧正文标题；全库引用用途未逐条审查，因此不声称对所有既有采用做过兼容性验收。

## Evidence Review 与验证边界

事实取自 GitHub 连接器对上述固定提交的文件/根目录读取与路径历史查询。代码搜索未返回结果，未将搜索未命中作为“对象不存在”的证据。
本地网络无法克隆仓库；只将 11 份待修改原文件按 GitHub blob SHA 逐字节核对后建立临时差异工作树。
校验原字节、生成差异属于通用文件/Git 操作，没有编写或运行 PDCA 语义 validator。

本地差异执行 `git diff --check`；PR 的现有 CI 另给出 `sh -n install.sh` 与差异空白检查的真实结果。
机械通过不表示所有 PDCA 语义或宿主行为通过。同一 AI 已完成上述四遍审查，未执行独立第二视角。

尚未验证：全库 reference 主张的真实性、其余 legacy 定位的可恢复性、所有反向引用与真实宿主采用/恢复行为。
本批没有恢复任何缺失原文，也没有完成 600+ 资产的逐条语义复核；真实宿主验收仍未运行。
