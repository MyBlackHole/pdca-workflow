# 面向 AI 使用与维护的防退化改动

基线：`138451df49a9f01d0b7a65a92921210b4c41fa68`（MyBlackHole/pdca-workflow/main）。
当前入口包为 `5.0.0-rc.3`，协议为 `4.0.0-rc.5`；不能把会话中的旧 `4.0.0-rc.3` 附件当成当前主线。
本次是维护入口、验收导航和机械 CI 的补丁，不改变 runtime Skill、authority、record-shape、安装器或版本采用规则。

## 旧审查的八项问题如何对应当前源码

| 旧问题 | 当前基线中的事实 | 本次处置与剩余证据边界 |
|---|---|---|
| 生成正文副本、拒绝 Skill 软链接 | install.sh 已直接 clone 到集中根，并以 ln -s 逐项注册仓库 Skill | 保留当前实现；不恢复旧 Python 安装器。真实宿主发现仍按 H1 单独验收 |
| 忽略旧 binding-r1.md 后重复登记 | 旧 scripts/install.py 已删除；当前由 project-workspace 与 AI 定位 | 用 M7/H2 覆盖旧路径与相同真实目标；不声称本轮已认证历史绑定或跑通迁移 |
| 无关项目坏记录阻断全部定位 | 原 Python 全表扫描器已删除 | M7 要求验证局部故障与真实冲突两面；不重造扫描器，也不将未知冲突跳过 |
| YAML 模板与 JSON-only 读取器冲突 | 旧读取器和根 templates 已删除，当前使用 record-shape | 保留通用解析工具边界，记录消费与恢复仍须针对现用宿主验证 |
| 版本字段漂移 | 总则已区分入口包、协议、asset 三个域；CI 已核对包/catalog/Skill 元数据 | 不把合法的 asset revision 差异改成统一版本，不升级活动任务 |
| 用 rc 字符串选 authority | 旧 manifest/build selector 已删除，改为 INDEX/LOAD-MAP | 不重新引入 manifest 或 authority semantic validator |
| 多个生成出口不同步 | 当前发现入口链接维护源，而不是导出正文副本 | 保留软链接；AGENTS 明确本地修改立即可见，远端保护不隔离活动任务 |
| 可执行位丢失不被检查 | install.sh 的 Git mode 是 100755，但 CI 仅运行 sh -n | 本次增加 Git mode 与实际文件类型/执行位检查，有限反例已运行 |

这些是对当前源码的重新定位，不是“八项原业务场景全部复测通过”。旧实现不存在只能说明旧复现不再直接适用，
不能据此证明 AI 在新路径上不会出现相同错误。

## 四遍审查

**范围**：用户要求直接以 PR 落地面向 AI 的维护和防偏离机制。保留集中 Git 资源根、原任务 Agent、用户阶段启动、
按需本体输入、真实产物与证据。没有加入自动阶段推进、第二套规则、本体批量重写、独立运行器或 adapter。

**一致性**：AGENTS 只新增维护动作，验收表引用现有 authority；tests 的案例不是业务指令。
保留当前无项目专用 semantic validator 的约束，机械 CI 不作授权或语义判定。
没有修改 H1–H18 状态，没有把现有宿主 smoke 的局部结果推广为完整正式 PDCA 验收。

**反证**：在临时 Git 仓库复现了旧 sh -n 对缺少执行位仍成功，以及 HEAD^→HEAD 漏查同次 push 较早提交的空白错误。
新检查拒绝这两类情况；合法执行位、无错误的完整 push/PR 和首次 push 正向通过。
测试 checkout 不匹配、缺失/恶意 baseline 字符串，以及 mechanical 上游 skipped/cancelled/failure/空结果的拒绝路径。
M1–M8 是给后续实际 AI 执行的维护挑战，未将编写这些场景计为已运行。

**证据**：对修改前的 AGENTS、tests/README 和 ci.yml 核对 Git blob SHA，均与上述基线匹配。
27 项本地有限控制通过，原始简报见 [mechanical evidence](evidence/2026-10-07-ai-maintenance-mechanical.txt)。
它们执行候选 workflow 中的真实 shell/Python 命令，但输入是临时 Git/包装元数据夹具，
不是在用户机器部署，也不是完整仓库安装、模型行为或原生交互验收。真实 GitHub Actions 结果应在 PR 按最终 SHA 查看。

## 机械 CI 的变化

- checkout 固定本事件 head，关闭凭据留存，设置运行时限；现有包元数据核对保留。
- 安装入口要求是可执行普通文件，并在 Git 索引记录为 100755。
- PR 检查 head 相对 merge-base 的完整差异；push 检查 before→head，而非仅最后一次提交。
- 首次 push 使用空树；缺失 baseline 或 checkout 不匹配直接失败，不缩小检查范围。
- `Mechanical result gate` 只有上游实际 success 才通过，不将 skipped/cancelled/failure 提升为成功。

## 采用限制

没有运行新的只读 AI 比较、原生可交互 Agent、用户四阶段、本体三场景或资源后端验证。
这些结果仍为 NOT_RUN；本 PR 不能用机械绿色声称“语义防退化已经强制保证”。

未启用远端 required checks、修改分支权限或绕过设置；workflow 和 PR 模板本身不是分支保护。
验收判据或 CI 自身的修改需要在 PR 单列原因并对照获准基线，不能由候选版本自行降低标准。
若需要强制合并边界，维护者须配置实际 required checks 与审查权限，并核对最终 head、检查来源和绕过权。

回退只回退本 PR 的维护/CI 改动；不清理集中记录、不改 Git 历史、不移动活动任务，不向现有任务补造授权。
