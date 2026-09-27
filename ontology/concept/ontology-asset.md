---
schema: pdca.asset/v2
id: ontology:concept/ontology-asset
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
status: active
authority: normative
revision: 4.0.0-rc.3
dcterms_modified: '2026-09-27'
summary: ONTOLOGY-01：定义可采用语义源与 project ontology revision 的 semantic construction contract
---

# ONTOLOGY-01：Project ontology semantic construction

ONTOLOGY-01 只回答两件事：

1. 一个 definition/reference 是否具备可采用的本体语义；
2. 一个 project/work ontology revision 是否具有足以被恢复、审查和投影的 semantic closure。

它不负责检索、采用授权、revision 演化、TREE/NODE 投影或 task 拆分。

## Model root

每个 project/work ontology revision 必须有一个**唯一 model root ref**。它不是新增 manifest schema，而是该 revision 的语义入口：从这个 ref 出发，在固定 payload/digest 内必须能够定位本 revision 的全部必要语义组成。

model root 至少固定或可解析到：

- project/work identity；
- ontology revision 与完整 payload digest；
- adopted definition refs；
- in-scope requirement refs 与 coverage；
- object definitions 与 current work instances；
- semantic relation definitions 与 relation instances；
- constraints / invariants；
- provenance/source refs；
- unknown / limitations。

模型可以是一个 Markdown、多个文件、数据库对象或外部固定模型；格式不重要。如果拆成多文件，model root 必须给出稳定、版本化的定位关系，而不是依赖目录遍历、“最新文件”或文件名猜测。

## Definition 与 Work Instance

必须区分：

- **Definition**：可跨 work 复用的 object/relation/constraint/type 语义；
- **Work Instance**：这些 definition 在当前 project/work/requirement 上的具体实例、适用范围与边界。

instance 必须能回指其 definition 或明确说明是当前 work 新定义的 candidate。reference entity、work instance、work node、task 不能因为名称相似而共用一个模糊身份。

```text
reusable definition
  -> adopted fixed definition
  -> current work instance
  -> TREE / DEPENDENCY projection
  -> qualified work node
  -> task seed
  -> task
```

## Object semantics

每个会影响当前 requirement、relation、constraint 或 node responsibility 的 object 至少需要：

- stable object identity；
- definition / instance distinction；
- semantic kind；
- relevant properties 及其 type/range/unit（需要时）；
- applicable requirement/source；
- unknown/limitation。

对象正文、代码符号、目录或图中的节点名称本身不构成稳定 ontology identity。

## Relation contract

每个会被当前 project ontology 使用的 semantic relation 必须能回答：

- stable relation identity/type；
- meaning；
- source endpoint 与 source role；
- target endpoint 与 target role；
- direction；
- endpoint kind/domain-range；
- cardinality/order 等约束（只有语义确实需要时）；
- provenance；
- 对 composition/dependency/constraint 是否有明确 implication。

relation instance 的两个端点必须在当前 revision 中可解析，或显式指向 adopted fixed external definition。

**generic `relates_to` 不产生 composition、dependency、ownership、data flow 或 task decomposition 语义。** TREE-01 / DEPENDENCY-01 只能消费本 revision 中有明确语义依据的 relation。

## Constraint / Invariant contract

重要 constraint/invariant 至少固定：

- stable constraint identity；
- subject；
- condition / predicate；
- applicability；
- expected invariant / forbidden condition；
- requirement/provenance；
- 可观察的 verification signal 或明确说明当前无法观察；
- unknown / limitation。

必须区分：

```text
semantic property       对象是什么
relation                对象之间是什么关系
constraint/invariant    什么必须成立
observation/test signal 如何观察是否成立
task acceptance         当前 task 是否接受产物
```

不能把 shell 命令、grep、测试步骤或 evidence 当作 ontology property 本身。

## Requirement coverage

每个 in-scope requirement 必须显式标明：

- covered：由哪些 object/relation/constraint/work-instance 承载；
- partial：已覆盖部分与缺口；
- uncovered：尚无模型承载；
- not_applicable：为什么不属于当前 work。

“正文提到过需求”不等于 coverage。Check 必须能从 requirement ref 导航到实际模型语义，也能从关键模型语义反查其 requirement/source。

## Provenance

source/provenance 必须尽量可复现：

- repository + fixed commit + path/symbol；
- stable external document/URL + version/date；
- PDCA record ref；
- environment-local source + explicit environment identity；
- unknown/missing source。

裸绝对路径只能作为 local historical clue；没有 environment identity 和固定内容依据时，不能把它升级成可移植 current evidence。

## Unknown / Limitation

重要 unknown 不能只写“待确认”，至少应说明：

- subject；
- unresolved claim/question；
- missing evidence/source；
- 对当前 relation/constraint/coverage/node qualification 的影响；
- resolution condition。

unknown 不阻止记录已知事实，但不能被摘要、confidence 或“看起来合理”覆盖。

## Semantic closure

一个 candidate project ontology revision 在 Modeling Check 中至少检查：

1. **identity closure**：model root 与所有关键 semantic refs 可定位；
2. **definition/instance consistency**：Definition、Work Instance、Node、Task 没有混用；
3. **relation endpoint closure**：relation type/meaning/endpoint/role 可解释；
4. **constraint observability**：constraint 与 observation/test signal 分离且可审查；
5. **requirement coverage**：in-scope requirement 有 covered/partial/uncovered 明确状态；
6. **provenance validity**：来源身份、版本与 local-only limitation 清楚；
7. **unknown completeness**：关键缺口没有被静默省略；
8. **composition/dependency separation**：generic relation 未被误投影；
9. **adoption scope**：只有 ADOPT-01 明确选择的 definition/claim/constraint 进入当前固定输入。

closure 是 AI semantic review，不要求项目专用 validator 或 rigid manifest。

## 与生命周期链的边界

- REUSE-01：找 definition/claim/constraint candidate；
- ADOPT-01：把选中的固定 semantic units 绑定为当前输入；
- EVOLVE-01：从固定模型产生候选新 revision；
- TREE-01 / DEPENDENCY-01：只消费本 revision 中明确的 relation semantics；
- NODE-01：从 work instance/responsibility 判断独立工作节点；
- DECOMP-01：只从 fixed qualified node 形成 task seed。

ONTOLOGY-01 不执行这些动作，也不把 reference 自动提升为 project ontology。

项目模型通常保存于 `PDCA_ROOT/ontology/projects/<project>/works/<work>/<revision>`，也可显式引用获准的外部固定模型。位置不改变语义要求；规则、reference、project model 与 task records 仍是不同写域。
