---
schema: pdca.asset/v1
id: ontology:concept/retrospective
type: concept
layer: Knowledge
status: active
summary: Act 阶段结构化回顾的七类改进候选模型，覆盖导航、校验、规范、指令分层、工具效率、空操作与信息可达性
relations:
  specializes:
    - ontology:concept/pdca-continuous-improvement
  relates_to:
    - ontology:concept/self-optimization-loop
attributes:
  - name: applicability
    desc: 适用于编码会话结束或 Act 阶段的横向回顾，需具备可回溯的会话原始材料
    constraint: 仅在存在任务产出、执行轨迹或校验结果等一次资料时触发；不替代 Plan 阶段 grilling 或 Check 结论判定
    testable_signal: 检查回顾记录是否标注触发范围与输入材料清单；无材料时应标记跳过而非虚构候选
  - name: navigation
    desc: Navigation 维度——评估 Agent 定位目标文件、模块或上下文指针的阻力
    constraint: 仅当寻址存在可复现阻力或缺少入口映射时才形成候选
    testable_signal: 检查候选是否指向具体文件路径、指针缺失点或寻址耗时轨迹；无依据的导航建议视为无效
  - name: automated_checks
    desc: Automated checks 维度——评估是否可通过自动化校验捕获会话中出现的人工失误
    constraint: 候选须对应可落地的检查形态（lint、类型、测试、文件系统校验等）且能复现错误
    testable_signal: 检查候选是否说明拟新增的检查类型、触发样例与预期拦截效果；无法复现的检查不予采纳
  - name: coding_standards
    desc: Coding standards 维度——评估是否需为审查视角新增可强制执行的编码规范
    constraint: 规范候选须区分实施视角与审查视角，且可在审查阶段被客观判定
    testable_signal: 检查候选是否为审查方可执行的判定规则；仅描述倾向而无法判定的规则视为不完整
  - name: global_agents
    desc: Global AGENTS.md 维度——评估全局指令中是否存在应下沉到编码规范或自动化检查的条目
    constraint: 仅当全局指令可被更低层约束替代且下沉后可被自动或审查捕获时才迁移
    testable_signal: 检查候选是否指明原全局条目、拟迁移目标层级及迁移后可被捕获的验证路径
  - name: tool_economy
    desc: Tool economy 维度——评估会话中是否存在可合并、缓存或替代的高成本工具调用
    constraint: 候选须关联到具体调用频次或成本观测，不做无数据猜测
    testable_signal: 检查候选是否引用轨迹中的调用序列或成本对比；无轨迹依据的经济性建议视为无效
  - name: no_ops
    desc: No-ops 维度——评估转向文件中不改变 Agent 行为的无效指令
    constraint: 仅当指令在实际执行中无可观测行为差异时才判定为无操作
    testable_signal: 检查候选是否以对比实验或轨迹说明该指令有无行为差异；无对比依据的判定不采纳
  - name: information_access
    desc: Information access 维度——评估提升 Agent 信息可达性的机会
    constraint: 候选须在不扩大越权的前提下增加只读或可观测信息源
    testable_signal: 检查候选是否说明拟开放的信息源、只读边界与预期可观测增益；涉及越权的访问不予采纳
---

# Retrospective（七分类回顾）

Act 阶段或编码会话完成后的结构化横向扫描模型，将自由形式的回顾收敛为七类可复核的改进候选。纵向闭环仍由 `ontology:concept/self-optimization-loop` 的“记录→分析→决策→受控实施→效果验证”五步承载，本概念提供 Act 回顾时的横向检查清单。

## 七类定义

以下七类是对齐远端 `mattpocock/skills` retro 语义的本体重述，不照搬其提示词措辞，仅保留分类边界：

1. **Navigation（导航寻址）**：审视 Agent 在会话中定位正确文件、模块或入口指针的难易度。候选关注“是否缺少导航指针、索引或上下文映射导致寻址阻力”，产出为补充可检索的指针或入口收敛。
2. **Automated checks（自动化校验）**：审视会话中出现的人工失误是否可被自动化检查拦截。候选关注“是否需要新增或强化 lint、类型检查、测试、文件系统校验等”，以在下次同类错误发生时自动失败。
3. **Coding standards（编码规范）**：审视是否应为审查视角增补一条可强制的编码规则。与 implementation 视角的上下文压力不同，review 视角具备更稳定的判定条件，候选需落在可被审查方客观执行的规则形态。
4. **Global AGENTS.md（全局指令分层）**：审视全局转向文件中是否存在更适于下沉的条目——即本应在编码规范或自动化检查层执行的约束被误置于全局指令层。候选关注“上移抽象或下沉具体”的分层合理性。
5. **Tool economy（工具经济性）**：审视会话中是否存在可合并、缓存、批量或以更轻量方式替代的高成本工具调用。候选关注调用序列的经济性，而非工具功能正确性。
6. **No-ops（空操作指令）**：审视转向文件中对实际行为无可观测影响的条目。判定需以行为对比为依据，而非主观精简倾向。
7. **Information access（信息可达性）**：审视提升 Agent 信息获取能力的机会，例如将开发服务日志分流为可读产物、开放第三方只读观测等。候选须遵守只读与最小授权边界，不扩大写入或越权能力。

## 适用边界

- **触发前提**：需具备可回溯的一次资料（任务产出、执行轨迹、校验或日志结果）。无资料时不凭空生成候选。
- **不适用**：替代 Plan 阶段的 Grill 决策树展开、替代 Check 阶段对证据与结论的判定、或作为绕过 `final_confirmation`/`check_confirmation` 的自动化变更授权。
- **与 self-optimization-loop 的关系**：本七类是 Act 回顾的横向扫描维度，其产出的候选仍需进入 `self-optimization-loop` 的受控实施与效果验证分支（候选→确认的 PDCA 任务→跨周期验证），不直接修改权威流程。
- **与审查压力分层的关系**：Coding standards 的增补以审查视角可执行为判据；Global AGENTS.md 的迁移以“可被规范或检查替代”为判据；二者共同体现实施与审查在上下文压力上的差异。
- **信息访问的边界**：Information access 仅扩展只读可观测性，不隐含写入、提权或绕过既有访问控制。

## 来源

- `mattpocock/skills` `skills/in-progress/retro/SKILL.md`（HEAD 6654f6b，七分类语义来源，仅对齐分类边界，未照搬措辞）
- `ontology:concept/self-optimization-loop`（纵向五步反馈模型）
- `ontology:concept/pdca-continuous-improvement`（Act→Plan 的循环语义）

## 已知坑

- 以提示词原文复述七类会造成措辞漂移与翻译失真；应以本概念的中文释义为准，英文名仅作对照锚点。
- 无轨迹或无校验依据的经济性、空操作判定易成为主观断言；此类候选必须以可复现对比为支撑。
