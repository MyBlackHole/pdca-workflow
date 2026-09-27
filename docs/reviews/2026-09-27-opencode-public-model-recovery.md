# OpenCode public free-model ontology recovery review

日期：2026-09-27

这是维护级真实模型执行证据，不是正式 PDCA Task、Modeling Act fixation 或 H11/H18 host acceptance。

## Environment

- OpenCode: `v1.18.32`
- GitHub Actions run: `36317798199`
- job: `108615697335`
- repository protocol: `4.0.0-rc.5`
- provider credential: none
- selected model: `opencode/mimo-v2.6-flash-free`

OpenCode v1.18.32 provider implementation supports a public fallback when no `OPENCODE_API_KEY` is present and disables paid models. This run exercised that public free-model path.

## Input isolation

The workflow derives a temporary input from:

`ontology/projects/pdca-host-smoke/works/bounded-counter/candidate-0.2.0/model.md`

and removes everything from:

`## 8. Derived work projection candidates`

onward before model execution.

Therefore the model receives only:

- requirement traceability;
- definitions;
- work instances;
- relation definitions/instances;
- constraints/invariants;
- provenance;
- unknown/limitations.

It does **not** receive the declared TREE / DEPENDENCY / NODE projection answer.

## Skill use

The prompt explicitly requires OpenCode to load the `pdca` Skill through the native Skill tool.

The JSON event stream was checked after execution and contained a completed `skill` tool call. The test fails if no Skill tool call is present.

This is stronger than static `opencode debug skill` discovery: the model-driven OpenCode run actually used the runtime Skill mechanism.

## Reconstructed result

The selected public model returned:

```json
{
  "tree": {
    "root": "INST-SYSTEM",
    "edges": [
      {"parent":"INST-SYSTEM","child":"INST-COUNTER","rel":"REL-COMP-SYSTEM-COUNTER"},
      {"parent":"INST-SYSTEM","child":"INST-LABEL","rel":"REL-COMP-SYSTEM-LABEL"}
    ]
  },
  "dependency": {
    "rel":"REL-CONSUMES-LEGAL-READING",
    "semantic_direction":"INST-COUNTER -> INST-LABEL",
    "projected_edge":"NODE-LABEL -> NODE-COUNTER",
    "interface":"legal_count_value",
    "status":"candidate"
  },
  "nodes": [
    {"node":"INST-SYSTEM","instance_of":"DEF-SYSTEM"},
    {"node":"INST-COUNTER","instance_of":"DEF-COUNTER"},
    {"node":"INST-LABEL","instance_of":"DEF-LABEL"}
  ],
  "ready": false
}
```

The complete model answer also preserved the important limitations:

- ontology candidate not fixed by host Modeling Act;
- no fixed-ref fresh-Agent recovery trace;
- no implementation/behavior evidence;
- checked-in smoke requirement is not a native host user-message receipt;
- dependency/node projection remains derived work structure rather than ontology-core facts.

## Semantic comparison

The runtime answer agrees with the prior core-only maintenance reconstruction on all decisive dimensions:

| Dimension | Expected from rc.5 model core | OpenCode public-model result |
|---|---|---|
| TREE root | INST-SYSTEM | INST-SYSTEM |
| composition child 1 | INST-COUNTER | INST-COUNTER |
| composition child 2 | INST-LABEL | INST-LABEL |
| dependency semantic direction | counter producer -> label consumer | same |
| dependency work direction | label depends on counter/interface | same |
| interface | legal_count_value | legal_count_value |
| readiness | false / candidate | false / candidate |
| counter responsibility | bounded mutable counter | recovered |
| label responsibility | exact count=N formatter | recovered |
| aggregate responsibility | compose both component semantics | recovered |

## What this proves

For this synthetic bounded-counter case on the tested OpenCode version/environment:

```text
install.sh
  -> OpenCode Skill discovery
  -> real model session
  -> native skill(pdca) use
  -> ontology-core-only input
  -> semantic TREE / dependency / node reconstruction
```

completed successfully without a user-provided provider secret.

This is direct runtime evidence that the rc.5 ontology core is usable by an external coding-agent host/model and is sufficient for this work-projection reconstruction.

## What this does not prove

This run still does not satisfy formal H11/H18 because it does not include:

- a user-authorized formal root Modeling task;
- Plan/Do/Check/Act receipts;
- Modeling Act fixation of `payload_digest`, tree and node identities;
- a second formal fresh Agent created from fixed task/assignment refs;
- CONTEXT-01 minimum-subgraph initialization evidence;
- original-Agent continuation/recovery semantics;
- implementation + verify scenes.

The model was a fresh `opencode run` inference, but that is not equivalent to the protocol's formal fresh-Agent task lifecycle.

Therefore H1–H18 remain `NOT_RUN`.

## CI policy

The public free-model probe remains non-blocking because free endpoints can be rate-limited or temporarily withdrawn.

The stable hard OpenCode compatibility gate remains CLI Skill discovery/parse; successful public-model reasoning is retained as stronger supplemental evidence.
