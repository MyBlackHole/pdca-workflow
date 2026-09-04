---
schema: pdca.asset/v1
id: ontology:domain/skill-retrospective
name: retrospective
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/skill-retrospective/1.0.0
summary: 编码会话完成后的七分类回顾技能，按严重度呈现可落地的改进候选
description: 在编码会话或 Act 阶段触发，读取一次资料后按七类扫描并依影响排序呈现候选，供用户抉择是否进入改进任务
invocation: manual
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/retrospective
    - ontology:concept/self-optimization-loop
attributes:
  - name: trigger_condition
    desc: skill 的触发条件集合，限定何时应启动回顾而非在编码过程中打断
    constraint: 仅在会话完成、用户显式请求或 Act 阶段入口时触发；编码进行中不主动插入回顾
    testable_signal: 检查回顾记录是否标注触发来源（会话完成/显式调用/Act 入口）及会话范围；非触发期的介入视为违规
  - name: primary_sources
    desc: 回顾所需的一次资料范围，决定候选是否有据可查
    constraint: 必须读取会话的核心产出与轨迹（任务产物、执行轨迹、校验结果等），缺资料时标记跳过而非推断
    testable_signal: 检查回顾输出是否可追溯到具体的一次资料片段或文件；无来源的候选视为不可信
  - name: seven_category_scan
    desc: 七分类扫描清单，复用 retrospective 定义的维度作为结构化检查表
    constraint: 逐类扫描且不照搬提示词原文，以本体重述的分类边界为准；未覆盖维度需显式标记为无候选
    testable_signal: 检查输出中七类是否均有扫描结论（有候选或明确无候选）；缺类或仅罗列英文名无释义视为不完整
  - name: severity_ordered_presentation
    desc: 候选的呈现排序规则，确保用户优先看到影响最大的改进点
    constraint: 按可观测影响或频次排序呈现，先高后低；同级内保持确定性排序
    testable_signal: 检查呈现列表是否按严重度排序且每条附带影响说明；无序或无依据的排序视为无效
  - name: candidate_disposition
    desc: 候选的处置边界，明确回顾不直接改写流程而进入受控实施
    constraint: 候选仅作呈现与建议，是否落盘需用户确认并经由新的 PDCA 任务承载
    testable_signal: 检查是否有候选绕过确认直接修改权威流程或省略新任务创建；此类即视为越权
---

# Skill: retrospective

编码会话或任务进入 Act 前的结构化回顾技能。依托 `ontology:concept/retrospective` 的七类定义，将一次资料扫描为可排序、可抉择的改进候选，并衔接 `ontology:concept/self-optimization-loop` 的受控实施分支。

## 触发条件

满足其一即触发：

- **用户显式调用**：用户请求对指定会话做回顾
- **会话完成**：一个编码会话或子任务产出已落地，需在下一阶段前做横向扫描
- **Act 阶段入口**：任务进入 Act，按本 skill 完成回顾后再决定知识处置与 `disposition`

编码进行中不主动触发；无可回溯材料时应跳过而非虚构候选。触发时需记录会话范围与一次资料清单，作为后续候选的可追溯依据。

## 输入与前置

- 会话的一次资料：任务产物、执行轨迹、自动化校验或日志结果等
- 写作风格遵循信息层级与渐进披露原则，呈现时精简准确，不堆砌冗余指标
- 已有的 `self-optimization-loop` 纵向模型作为候选处置的下游路径

## 七分类扫描清单

按 `ontology:concept/retrospective` 重述的七类逐项扫描，每类给出“有候选/无候选”的明确结论：

1. **Navigation（导航寻址）**：是否存在可补充的导航指针或入口映射以降低下次寻址阻力
2. **Automated checks（自动化校验）**：是否存在可拦截同类失误的检查缺口（lint、类型、测试、文件系统等）
3. **Coding standards（编码规范）**：是否存在可供审查视角强制执行的新规则
4. **Global AGENTS.md（全局指令分层）**：是否存在更适于下沉到规范或检查的全局条目
5. **Tool economy（工具经济性）**：是否存在可合并、缓存或轻量替代的高成本调用序列
6. **No-ops（空操作）**：是否存在无行为差异的无效转向条目
7. **Information access（信息可达性）**：是否存在在只读边界内可扩展的信息源（日志分流、只读观测等）

每条候选需关联到具体资料片段或观测，避免主观断言。审查与实施的上下文压力差异决定了规范类候选应以审查方可执行为判据。

## 候选呈现流程

1. **读取一次资料**：定位并读取会话指定的核心产出与轨迹，未找到材料时直接报告跳过
2. **七类扫描**：按上述清单逐类评估，产出候选或标记该类无候选
3. **严重度排序**：按可观测影响或出现频次对候选排序，突出最值得优先处理的若干项
4. **结构化呈现**：以列表形式呈现候选，每条包含类别、现象、影响与可选处置方向
5. **用户抉择**：由用户决定哪些候选晋级为改进任务；被选中的候选按 `self-optimization-loop` 进入“确认的 PDCA 任务→跨周期验证”路径，不在本 skill 内直接改写流程

呈现时不照搬远端提示词措辞，以本体的中文释义为准；英文类名仅作对照锚点。

## 与关联概念的衔接

- `retrospective`：提供七类的权威定义与适用边界
- `self-optimization-loop`：承接本 skill 产出的候选，完成受控实施与效果判定

## 已知坑

- 在编码高峰期插入回顾会干扰主线；本 skill 仅在会话完成后触发
- 无轨迹支撑的经济性与空操作判定易成为主观精简；此类候选必须附带对比依据
- 候选不得绕过用户确认直接落盘为流程变更；确认后的改进仍需新建 PDCA 任务承载
