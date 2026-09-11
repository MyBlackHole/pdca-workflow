---
schema: pdca.asset/v2
id: ontology:process/work-scenarios
type: process
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.2
summary: 三场景整树交接与逐节点覆盖
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/process
  relates_to:
  - ontology:concept/work-ontology-tree
  - ontology:concept/work-node-contract
  - ontology:concept/work-tree-scheduling
  - ontology:process/independent-work-review
  - ontology:concept/task-rework
  - ontology:concept/ontology-reuse
  - ontology:concept/ontology-evolution
  - ontology:concept/ontology-adoption
  - ontology:concept/task-decomposition
scene_ids:
- ontology_modeling
- ontology_projection
- ontology_conformance_verification
---

# 三场景整树交接与逐节点覆盖

## SCENE-01：一个工作、三种场景、每节点完整循环

默认顺序是目标生成 → 执行工作 → 独立审查。场景工作清单位于 `records/works/<work-id>/`，每一行绑定 node_id/scene/attempt/task_id/产物及状态。它是宿主根据固定交付物维护的清单，不是父 Agent 对子任务活动上下文的汇总。

N 节点首次完整工作，三场景基准覆盖为 3N 个节点任务；实际失败、修复、重建产生新 attempt，不能用“必须恰好3N”删除失败历史。每个节点/场景的首次任务不可因节点简单、属于组合节点或复用了定义而省略。

## 场景一：工作目标生成（根→叶）

输入是用户目标与原有知识，不是已完成的整树。宿主派发根建模任务；其 Plan 依据通用建模契约，Do 定义根和直接子目标种子，Check 核对局部覆盖与建模正反例，Act 交付。父任务在此只承诺子目标边界，不虚假声称孩子已实现。

孩子只能在父 seed 固定且被采纳后建立；每个孩子的新 Agent 重复同一完整循环，可在独立分支并行。节点不直接 spawn 自己的后代并逐步控制；把 seed 交付给宿主调度。

孩子发现父边界冲突时产生带证据的设计问题，不自行改父定义。需要改变已确认父义务则触发父节点建模新 attempt，按 TREE-01 处理受影响 seed；不会让未结束父任务反向依赖孩子才能完成，避免生成死锁。

完成条件：TREE-01整树检查，以及宿主工作级tree_confirmation路径取得的真实冻结确认（不复用根seed的任务确认）；NODE-01 内容与 TEST-01 套件均覆盖所有节点。结构检查可归并局部声明；语义未确定的项保持未冻结，不自动继承“大家都完成”。

## 场景二：执行工作（叶→根）

只对已冻结树派发。每节点一个完整执行任务；叶就绪可并行，组合节点必须等全部必需孩子交付可用并固定。父本体任务此时才开始自己的 Plan，不作为提前常驻的父 Agent。

Do 实现本实体，运行其正反例单元测试。内部节点执行真实组合、接口/错误/状态传播测试。Check 是本任务自检，不以父 Agent 回执为准；Act 交付固定实现包。任务结束、局部产物可用和最终审查通过分别记录。

失败/partial 子任务可以合法归档，但不自动解除父节点依赖。本协议不支持降级交付例外；不得临时把失败孩子设为可选。需要新的运行模式先变更目标契约并重新确认。全部节点执行任务有闭合记录且根产物可用后形成固定 release 清单；工作失败也可交付明确缺项的失败包进入审查，不伪称成功。

## 场景三：审查工作（定义↔实现）

对同一冻结树每节点创建新的审查 Agent；输入为节点定义、对应实现 release、suite 与必要证据。叶局部审查可并行；父审查在直接孩子审查包可用后核对真实组合，不机械传递 PASS。细则见 REVIEW-01。

审查任务的业务成果是有证据的正确审查报告。它可以成功完成，但报告 `subject_conformance=fail`；这不能变成被审查实现成功。整树通过仅当所有必需节点 subject_conformance=pass，组合/根目标通过且没有未解决的阻断缺陷、未知项或过期证据。

## 场景间返工

审查发现实现错误：绑定原 node_id/scene=ontology_projection 的新 attempt、新 Agent；导入最小复现和固定输入。对修复后节点、受影响依赖者和祖先逐节点重做必要执行/组合与独立审查，不能就地改旧报告。

审查发现目标/测试 oracle 错误：回到建模场景的新任务，生成新树版本并重新确认，再按新版本覆盖三个场景。具体测试与停止预算见 REWORK-01。

## 失败与退出

缺能力保持未执行；用户取消/宿主强制终止按CONTROL-01先停止/撤权/结清，再保留原phase和interrupted，不伪造四阶段。尚未终止的可恢复blocked尝试可以原Agent按原基线继续；已终止尝试不复活、不作为正常完成覆盖，新工作用新Agent/new attempt。


## 交接不能反向阻塞本地任务

建模任务先局部通过并正常交付，TREE-01工作级冻结事件在全树建模结束后执行；它没有新的phase，也不复活根Agent。执行返工的节点先局部交付，再由祖先逐节点组合；工作issue和release的关闭/发布在最后。所有实质生成、实现、审查工作仍属于具名节点的完整PDCA。

## 建模复用优先与场景交接

每个建模节点Plan必须按REUSE-01先检索、逐要求比对并固定主要决定；Do才实例化既有定义/生成local delta/修订候选/创建定义，Check验证适用性和正反例，Act交付当前节点并可confirm_existing/no_new_knowledge/candidate_only。共享发布按EVOLVE-01与独立发布审查；节点不为等待全库迁移而阻断自己的正常结束。

实现和审查不重新决定或替换冻结definition_refs，只核对字节/适用性/公告；旧案例规范可作固定输入，当前任务必须产生自己的真实run。树更新后逐节点场景覆盖不减少，复用不是合并任务或沿用Agent。

## 完整实体与递归建模交接

modeling任务的当前动作是设计，但NODE描述整项工作实体跨场景的职责，不把projection/verification从实体定义永久排除。审查项目时：modeling建立审查目标；projection实际执行审查并产出报告/证据；verification独立复核审查报告与目标的对应，不能把整个工作偷换成创建草稿。

每个孩子都按DECOMP-01判断是否再拆自己的孩子。父只固定接口/义务和允许的组成槽；普通槽展开不反向等待后代。展开后以最终N计逐场景任务覆盖，不以首次五节点/固定深度阻止合法分解。知识库定义/组合模式可多树共享，工作实例与Agent不可合并。

modeling场景完成指全体本地建模任务与TREE-01固定树确认；共享发布若列为工作必需义务，则工作知识目标仍未完成直到按REUSE/EVOLVE履行。两者分别记录，不能把父seed完成、全树冻结、ontology入库、其他树升级合成一个completed。

## 固定交接记录

整树确认前按TREE-01生成技术readiness；执行产物汇总使用VERDICT-01的工作release清单，审查与批准回执在外层关联。三场景任务与新Agent边界不变。每场景scope与实际对象固定，不把本次运行记录的格式审查代替原项目符合性审查。


<a id="scene-required-set"></a>
## SCENE-01 · 必需集合的固定来源

frontmatter `scene_ids` 是本条既有三场景名称的可定位投影。节点首次覆盖和整树冻结均从此集合与经过核验的节点集合组合；候选 manifest 的 required_scenes 只是被核对项，不是缩减场景的授权。没有真实执行的场景标 not_run，不与“测试契约不存在”混淆。
