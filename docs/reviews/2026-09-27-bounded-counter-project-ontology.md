# Bounded-counter project ontology candidate：维护审查

日期：2026-09-27
审查对象：`ontology/projects/pdca-host-smoke/works/bounded-counter/candidate-0.1.0/model.md`
审查 blob：`8086fdb3ac5ebc89a4240eb92b885290b496a422`
协议：`4.0.0-rc.5`

这是维护级 semantic-closure 审查，不是正式 Modeling Check、Act fixation、fresh-Agent recovery 或 H1–H18 host acceptance。

## Scope

本审查只判断这份 candidate 是否正确使用 rc.5 的 ontology construction contract，重点检查：

- ontology core / traceability / work projection 是否分层；
- Definition / Work Instance / Work Node / Task 是否混用；
- relation semantics 是否足够支持 TREE/DEPENDENCY projection；
- constraint/invariant 与 observation/AC 是否分开；
- requirement coverage 是否可追踪；
- provenance 是否可复现；
- unknown 是否明确；
- 是否存在“为了拆 task 而反向发明 ontology”的迹象。

## 1. Model root

candidate 有唯一 `model_root_id` 和 `model_root_ref`，并明确 `status: candidate`、`fixed_by_modeling_act: false`。

当前 payload 为单文件，因此从 model root 可以直接解析完整 candidate semantics。正式 `payload_digest` 尚未固定，这一点被显式保留给 Modeling Act，而不是伪造一个自引用 digest。

结论：model-root 设计正确；fixation 尚未完成。

## 2. Ontology core 与周边层次

文件明确区分：

```text
ontology core
  definitions
  work instances
  relation definitions/instances
  constraints/invariants

traceability
  requirement coverage
  provenance
  unknown/limitations

derived work projection
  TREE
  DEPENDENCY
  NODE qualification
```

这避免把 requirement、source、task tree 当成 domain ontology facts。

结论：使用方式正确。

## 3. Definition / Work Instance

存在三个 definitions：

- `DEF-SYSTEM`
- `DEF-COUNTER`
- `DEF-LABEL`

以及三个对应 work instances：

- `INST-SYSTEM`
- `INST-COUNTER`
- `INST-LABEL`

实例显式 `instance_of` definition，且 Work Node 使用 `ontology/work ref` 回指 instance，没有把 node/task 混入 ontology identity。

结论：Definition / Work Instance / Node 分层正确。

## 4. Relation semantics

candidate 没有使用 generic `relates_to` 推导工作结构。

两个 relation definitions 分别明确：

- `RELDEF-COMPOSED-OF`：只有 composition implication，没有 dependency implication；
- `RELDEF-CONSUMES-LEGAL-READING`：只有 dependency implication，没有 composition implication。

source/target roles、direction、endpoint kinds、cardinality/接口语义均可恢复。

另外已经显式区分：

```text
semantic relation direction
  producer -> consumer

derived dependency reading
  consumer depends on producer/interface
```

避免把 relation arrow 与 dependency graph direction 混为一谈。

结论：relation contract 使用正确。

## 5. Constraint / observation / AC

六个 constraints 都分别定义 subject、predicate、applicability、expected invariant、observation signal 和 requirement。

没有把 grep/shell/test recipe 写成 semantic property，也没有把 observation signal 当成 constraint 本体。

当前 model 不直接写 task AC；它只提供可供后续 Plan/CASE/TEST 使用的 semantic constraints 与 observation signals。

结论：分层正确。

## 6. Requirement coverage

六条 in-scope requirement 均有显式 coverage，并映射到 definition / work instance / relation / constraint。

没有仅通过“正文提及”宣称覆盖。

当前没有 partial/uncovered/not_applicable 条目，因此后续真实需求若增加，必须更新 coverage table，不能靠默认覆盖。

结论：当前 bounded-counter scope 内 coverage closure 成立。

## 7. Provenance

需求与 protocol provenance 都固定到仓库 `MyBlackHole/pdca-workflow` 和 commit：

`3d16861e95692fd2131ae40882cd5c7e6e8f9353`

同时明确说明 smoke requirement 不是 native host user-message receipt。

没有使用裸 `/home/...` 本机路径作为 current evidence。

结论：provenance 使用正确。

## 8. Unknown / Limitation

candidate 保留三类 material unknown：

- host Modeling Act fixation；
- fresh-Agent cross-context recovery；
- concrete implementation / behavior evidence。

每个 unknown 都说明 missing evidence、impact 和 resolution condition。

因此当前文件不会把“静态模型完整”升级成“宿主/实现已验证”。

结论：unknown handling 正确。

## 9. TREE / DEPENDENCY / NODE projection

TREE 只从两个 `RELDEF-COMPOSED-OF` relation instances 派生：

```text
bounded-counter-system
├─ counter-core
└─ label-format
```

`REL-CONSUMES-LEGAL-READING` 不生成 composition child，只生成 label 对 counter legal-count interface 的 dependency candidate。

三个 NODE candidates 都回指 ontology/work instance、responsibility、I/O、constraints、composition/dependency refs，并声明独立 reject boundary。

结论：当前 projection 是从 ontology semantics 派生，而不是从文件结构/任务便利性反向制造 ontology。

## 10. 仍未证明的事项

以下不能由本维护审查升级为 PASS：

1. 正式 Modeling Plan/Do/Check/Act 是否能自然产出等价模型；
2. Modeling Act 是否能固定 complete payload digest；
3. fresh Agent 是否能只从 fixed model root/refs 恢复相同 semantic graph；
4. CONTEXT-01 是否能基于 fixed graph 选择真正 minimum sufficient child subgraph；
5. pdca-implement / pdca-verify 是否能消费这些 semantics 而不重新解释模型。

这些仍对应 host-smoke / H11 / H18 的真实验收。

## Verdict

就**本体论使用方式**而言，这份 candidate 没有把 ontology 当成任务树、目录结构、流程 DSL 或证据容器使用；它保持了 ontology core、traceability 和 work projection 的边界。

因此可以把它作为 rc.5 的第一份 project ontology construction candidate 合入仓库，用来驱动后续真实 host-smoke。

但它仍是 `candidate`，不是 fixed ontology revision，也不改变 H1–H18 的 `NOT_RUN` 状态。
