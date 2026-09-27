# PDCA

PDCA 在一个 Git 工作副本中集中管理规则、本体、项目记录与资源预约。用户通过九个 Skill 入口定位项目、选择工作建议和逐阶段推进任务；同一任务始终由原 Agent 与用户交互。

[安装、更新与宿主发现](INSTALL.md) · [Skill 索引](skills/README.md) · [当前本体](ontology/README.md) · [AI 审查与现场验收](tests/README.md)

当前 release candidate：**protocol `4.0.0-rc.4` / Skill bundle `5.0.0-rc.3` / record schema `v4`**。本轮语义变更、兼容性与未验收范围见 [rc.4 release note](docs/releases/2026-09-27-protocol-4.0.0-rc.4.md)。

## 开始使用

按 [INSTALL](INSTALL.md) 安装后，在宿主中显式调用 `$pdca`，提供项目真实路径、`project_id` 与 `workspace_id`。它先只读定位已有绑定；新增或修改绑定时，会列出具体集中记录路径，核对用户的记录写入授权后才保存。缺失、多个匹配或根冲突时停止说明，不按目录名、Git remote 或最新任务猜测身份。

绑定完成后，显式调用 `$pdca-assist` 可读取当前绑定项目的必要记录、获准源码、文档与 Git 状态，从任务地图、项目上下文、证据审阅、协作交接四个视角提出少量建议。每个视角最多一个候选，标明依据、影响和所需授权。建议后等待用户选择，不创建记录、任务、Agent、阶段或资源预约，也不运行测试或写入业务项目。

选择建议后仍需核对具体动作与已有授权范围。创建任务、写记录、修改业务产物和执行某个阶段分别受对应的用户授权约束，选择本身不等于批准全部后续操作。

## 双根与归属

`PDCA_ROOT` 是集中 Git 工作副本，默认 `~/.agents/pdca`；`TARGET_ROOT` 是当前绑定业务项目的规范化真实路径。入口经符号链接解析后的根应与绑定一致；既有任务绑定优先于 cwd 或环境变量，冲突时停止。

[INDEX](ontology/INDEX.md) 只负责定位当前 authority，[LOAD-MAP](ontology/LOAD-MAP.md) 负责告诉 AI 在当前事件下最小读取什么。大量 domain/entity/pattern 等知识资产继续保留，但不会因为存在、被链接或标有 `authority` 就自动注入任务；只有按 REUSE/ADOPT 固定版本后的资料才进入当前任务输入。

```text
PDCA_ROOT/
  skills/                         # 九个共享同一中心的入口
  ontology/                       # 当前规则、记录格式与按需采用的知识
    projects/<project>/           # 按 work/revision 隔离的项目模型
  records/
    projects/<project>/workspaces/<workspace>/project-context.md
    works/<project>/<work>/        # 工作树、模型版本、投影映射
    tasks/<task>/                 # task、plan、control、events 与证据
    resources/<reservation>.md    # 全中心实际资源预约
TARGET_ROOT/
  <获准的业务源码、产品测试、文档或配置>
```

业务项目不自动生成 `.pdca/` 或独立流程记录，不接收安装器写入。公共知识、项目模型、任务记录和业务产物分别授权；集中存储与 Git 跟踪均不扩大跨项目读取或写入范围。外部已有模型可经明确采用后，以来源、版本、映射和证据集中登记。

## 本体驱动的任务与上下文

正式工作不是按文件数、LOC、工时、token 或“想并行”拆 Task。主链是：

```text
用户目标
  -> root modeling bootstrap
  -> candidate ontology / work instance
  -> candidate composition + node qualification
  -> Check
  -> Act 固定 ontology/tree/node revision
  -> DECOMP task seed candidate
  -> 用户创建
  -> fresh Agent
  -> CONTEXT minimum sufficient subgraph
  -> 独立 PDCA
```

首次 root modeling 是唯一允许在尚无 ontology node 时创建的 bootstrap task；它负责经 Check/Act 固定第一个 root node/revision。
**候选 ontology/tree/node 在固定前不能提前包装成正式 child seed。** 后续正式 child、implement、verify task 都必须绑定 fixed node/revision。

同一个 node 在三个场景中保持语义身份：Model 定义“应该是什么”，Implement 把模型投影到真实实体，
Verify 检查 requirement→model→implementation→behavior。正式拆分同时建立上下文边界：
child Agent 只取得当前 node、必要关系端点、依赖交付、共享不变量和 scene 输入，不继承父/兄弟完整活动历史。

Do-only Work Unit 只是正式 Task 内的局部执行切片，不产生新的 node/task，也不能替代这种正式上下文隔离。

## 阶段与场景

总入口 `$pdca` 负责绑定、定位和分流，`$pdca-assist` 负责只读建议。四个阶段入口 `$pdca-plan`、`$pdca-do`、`$pdca-check`、`$pdca-act` 操作已有任务；三个本体场景入口只负责显式选择、创建前置与路由，建模/投影/符合性验证的具体场景语义统一由 [SCENE-01](ontology/process/work-scenarios.md) 定义，入口名见 [Skill 索引](skills/README.md)。

每个场景、节点和 attempt 都由绑定的可交互 Agent 完成四阶段。切换 Skill 不换 Agent；父会话调用阶段入口时，只无损路由用户原始操作到原实例，不监工、不代答、不接管。不能继续原实例时阻断。

仅发现或加载 Skill 不授权创建或启动。任务获准创建后，原任务 Agent 先确认 Plan 目标并等待；Plan/Do/Check 都由用户明确启动，完成后报告产物、限制和下一候选并等待。Act 也是显式启动，但它是当前 attempt 的终态处置：完成后同一授权下 terminalize/archive，不再等待“第五阶段”。三个场景各有完整 PDCA，读取场景方法不再次创建任务，也不自动串联场景。

## Check 后的下一步不是自动流程

Check 结束后只产生候选方向：

- 同一 Plan/baseline/AC/identity 与写域不变时，可按 REWORK-01 判断是否继续同 attempt 的新 Do；此时**不先进入 Act**；
- 接受、限制性使用、失败归档或发布当前结果时，才进入 Act；
- 需要改变目标/oracle/model identity/Agent 或当前 attempt 已终态时，只形成新 attempt/task 候选；
- 已存在 fixed task seed 且 dependency ready 时，SCHED-01 只负责提示可创建候选，不自动派发。

Act 一旦完成并 archived，当前 attempt 不再回到 Do。经验沉淀也不是默认收尾动作；只有 Act 明确授权 learning/persist/publish 时才使用 LEARN-01，共享发布后的知识也只是 REUSE candidate，其他 task 仍需显式 REUSE→ADOPT。

## AI 审查

PDCA 语义不通过项目专用验证脚本重复实现。Check 直接读取固定 Plan、当前 authority、真实 diff/产物和证据，按 Scope、Consistency、Adversarial、Evidence 四遍进行 AI 审查。

需要可执行 case 时，CASE-01 先固定 oracle，TEST-01 只保存实际 observation；EVIDENCE-01 把 claim 绑定到 observation/反证，VERDICT-01 再聚合当前 subject 的必需 AC。Git、编译器、业务项目测试和独立 reviewer 都只是事实/claim 来源，不会因为“退出 0”或“另一个 Agent 同意”直接产生 PASS。正式 pdca-verify 是独立 scene/task，不等于 Check 内的一次性第二视角。

## Git 来源与记录授权

`records/` 与 `ontology/projects/` 可由 Git 跟踪；私有证据路径和本地秘密继续忽略。每次获准写入绑定、任务或事件前，在集中根只读采集 `GIT_OPTIONAL_LOCKS=0 git rev-parse HEAD` 与 `GIT_OPTIONAL_LOCKS=0 git status --porcelain`，记录为 `rules_git_head`、`rules_git_status`。查询失败或无有效 HEAD 时停止。

HEAD 与工作树状态只用于追溯，不是不可变规则副本。记录写入授权和 Git 提交授权分开；只有用户另行明确要求提交具体范围后才可执行相应 `git add`/`git commit`。AI 不自动提交、拉取、切换分支、暂存、还原或覆盖集中工作树。发现脏工作树时报告事实与审阅、提交、暂存或继续的选项；更新由用户自行使用 Git 完成。

## 恢复、资源与已有资料

每次正式操作先核对集中 context、原 task/Agent、最后完整事件、当前 run、请求／原始响应和未决资源，详见 [共同恢复入口](ontology/contracts/entry-recovery.md)。更新集中根不自动改绑、重写或升级活动任务；原依据缺失或当前规则影响既有授权时停止说明，不自动 checkout 历史提交，也不重放操作。恢复本身不产生授权。

全中心按实际文件、目录、设备、数据库等对象识别资源冲突，不按 task 或分支名隔离。每个任务仅写自己的记录与获准作用域；取得、撤销和结清必须有真实依据，结果未知仍保留占用。集中账本不能代替真实锁或沙箱，详见 [资源归属](ontology/concept/resource-ownership.md)。

已有项目本地 `.pdca/`、旧任务记录和原引用保持原字节，不由安装或绑定自动搬迁。迁移须逐项核对原 Agent、请求、写权、未决资源与在途操作，保留旧新路径及来源；文件移动不证明原会话已迁移。不能保持原授权语义时，停止并由用户选择后续处置，不将旧确认转换为新阶段启动。

未采用的参考知识保留在 Git 仓库中，按需查阅；历史指针不成为当前规则，不全量注入任务。当前树不包含 `legacy/`，旧定位不能当作已保存的原文；核对方式见[来源说明](ontology/provenance/README.md)。正式派发依赖真实可交互、可恢复的宿主能力；静态检查不能认证这些能力，[现场验收](tests/host-acceptance.md)仍为 `NOT_RUN`。
