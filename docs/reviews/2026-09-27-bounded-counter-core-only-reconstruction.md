# Bounded-counter core-only work projection reconstruction

日期：2026-09-27
对象：`ontology/projects/pdca-host-smoke/works/bounded-counter/candidate-0.2.0/model.md`
candidate blob：`c3919a2d085e393b95c41f5c4d677a953592c5bd`
协议：`4.0.0-rc.5`

这是同一维护 AI 的 **core-only reconstruction exercise**，不是独立 Agent、正式 Modeling Check、Act fixation 或 H18。

## Input discipline

重建输入只允许：

- model root Section 1–7：Requirement Traceability、Ontology Core、Relations、Constraints、Provenance、Unknowns；
- current TREE-01；
- current DEPENDENCY-01；
- current NODE-01。

在形成下面的重建结果前，不把 Section 8 `Derived work projection candidates` 当作推理依据。Section 8 只用于最后对照。

## Reconstructed TREE

从 ontology core 可见两个 relation instances 使用 `RELDEF-COMPOSED-OF`：

```text
REL-COMP-SYSTEM-COUNTER
  INST-SYSTEM -> INST-COUNTER

REL-COMP-SYSTEM-LABEL
  INST-SYSTEM -> INST-LABEL
```

`RELDEF-COMPOSED-OF` 明确 `composition implication: yes`，并且两个实例分别固定 shared interface、shared invariant 和 parent composition responsibility。

因此 TREE-01 只能得到：

```text
INST-SYSTEM
├─ INST-COUNTER
└─ INST-LABEL
```

没有第三条 composition relation；`REL-CONSUMES-LEGAL-READING` 明确 `composition implication: no`，不能成为 child edge。

结论：唯一 composition topology 可恢复，root 唯一且无环。

## Reconstructed dependency candidate

`REL-CONSUMES-LEGAL-READING` 定义：

- semantic direction：counter producer -> label consumer；
- interface：`legal_count_value`；
- dependency implication：yes；
- composition implication：no。

因此从 consumer 视角恢复：

```text
label responsibility
  depends on
counter legal_count_value interface
```

即语义上的 consumer→producer dependency：

```text
NODE-LABEL -> NODE-COUNTER / legal_count_value
```

但当前 ontology revision 仍是 candidate，没有 fixed producer deliverable version/digest，也没有 ready evidence。

所以 DEPENDENCY-01 只能得到 **dependency candidate**：

```text
ready = false
fixed deliverable version/digest = not_fixed
```

不能得到 ready dependency edge。

## Reconstructed work-node semantics

### System node

来源：`INST-SYSTEM instance_of DEF-SYSTEM` 加两条 composition relations。

可恢复 responsibility：组合 bounded-counter 与 label-formatting 两项责任。

可恢复边界：

- inputs：counter operations + label request；
- outputs：bounded legal count + exact label text；
- constraints：C-INIT / C-INC / C-READ / C-RESET / C-LABEL / C-LABEL-INPUT；
- composition：counter + label；
- internal dependency：label consumes counter legal-count interface。

可恢复 node-level acceptance/oracle：如果任一 component responsibility 缺失、label 不经 legal_count_value、或 required semantic constraint 缺失/矛盾，则 aggregate node 可被独立拒收。

### Counter node

来源：`INST-COUNTER instance_of DEF-COUNTER`。

可恢复 responsibility：维护 `[0,2]` bounded mutable counter。

可恢复 I/O：

- inputs：increment / read / reset；
- output：由 relation contract 暴露的 `legal_count_value`。

可恢复 constraints：C-INIT / C-INC / C-READ / C-RESET。

可恢复 oracle：

```text
initial read = 0
increment sequence = 1, 2, 2
repeated read without mutation is stable
reset then read = 0
```

### Label node

来源：`INST-LABEL instance_of DEF-LABEL` 与 `REL-CONSUMES-LEGAL-READING`。

可恢复 responsibility：把合法 counter reading 表示成 exact `count=N`。

可恢复 I/O：

- input：legal_count_value；
- output：exact label text。

可恢复 constraints：C-LABEL + interface constraint C-LABEL-INPUT。

可恢复 oracle：0/1/2 分别映射为 `count=0/1/2`，且当前 composition/dependency 不允许 out-of-domain value 进入 formatter。

## Node ID boundary

从 ontology core 可以稳定恢复的是**node semantics**，不是某个字符串命名。

例如另一个建模者可能在未固定前称 counter node 为 `NODE-COUNTER` 或 `counter-responsibility`；仅凭 ontology core 不应要求不同 Agent 独立发明完全相同的 node_id。

正确生命周期是：

```text
ontology semantics
  -> Modeling projection selects stable node_id
  -> Check
  -> Act fixes node_id + ontology/tree refs
  -> later Agent reads the fixed node_id
```

因此 H18 的 cross-Agent recovery 应验证“读取 fixed node identity 后恢复相同语义”，而不是要求 fresh Agent 重新命名出相同字符串。

## Comparison with declared Section 8

在完成上述重建后再读取 Section 8，对照如下：

| Dimension | Core-only reconstruction | Declared projection | Result |
|---|---|---|---|
| TREE root | system aggregate | NODE-SYSTEM / INST-SYSTEM | semantic match |
| TREE children | counter, label | NODE-COUNTER, NODE-LABEL | semantic match |
| Composition edges | 2 | 2 | exact semantic match |
| Dependency | label consumes counter `legal_count_value` | same | exact semantic match |
| Dependency readiness | not fixed / not ready | `not_fixed`, `ready: false` | exact match |
| Node semantic responsibilities | system/counter/label | system/counter/label | match |
| Counter constraints/oracle | C-INIT/C-INC/C-READ/C-RESET + 0/1,2,2/read/reset oracle | same | match |
| Label constraints/oracle | C-LABEL + C-LABEL-INPUT | same | match |
| System composition acceptance | both responsibilities + legal-value dependency + required constraints | same | match |

## What candidate-0.1.0 exposed

这个 reconstruction exercise 同时发现 0.1.0 有三个真实 contract gap：

1. composition relation instances 缺 shared interface / invariant / parent composition responsibility；
2. NODE candidates 缺 NODE-01 要求的 acceptance criteria / oracle；
3. dependency candidate 没有显式说明缺 fixed version/digest + ready evidence，因此容易被误读成 ready edge。

`candidate-0.2.0` 修正以上三点，并保留 0.1.0 历史字节而不是原地覆盖。

## Result

在 bounded-counter 这个小模型上，**ontology core + traceability 已足以决定 work projection 的语义结构**：

```text
ontology core
  -> unique composition topology
  -> one dependency candidate
  -> three independently rejectable node semantics
```

这支持“Ontology → TREE/DEPENDENCY/NODE 是 projection，而不是为了拆 Task 反向制造 ontology”的设计。

但本结果仍不能证明：

- native fresh Agent 只读 fixed model root 时一定恢复相同语义；
- Modeling Act 能正确固定 payload digest/tree/node；
- CONTEXT-01 的最小子图在真实宿主中不会泄漏额外历史；
- implementation/verify 能无重新建模地消费这些 semantics。

因此 H11/H18 仍保持 NOT_RUN。
