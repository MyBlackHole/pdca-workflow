# OpenCode fresh-session ontology semantic recovery

日期：2026-09-27

这是 bounded-counter `candidate-0.3.0` 的维护级 fresh-session runtime evidence，不是正式 PDCA Task、Modeling Act fixation 或 H18 PASS。

## Runtime evidence

- OpenCode: `v1.18.32`
- Actions run: `36318354583`
- job: `108617248254`
- model run 1: `opencode/mimo-v2.6-flash-free`
- model run 2: `opencode/mimo-v2.6-flash-free`
- session 1: `ses_f1d358061ffecywgkdDqJI8OF4`
- session 2: `ses_f1d34cd5effeNeFjSga8hVsbsZ`

The two session IDs are distinct and neither run used `--continue` or `--session`.

## Why candidate-0.3.0 exists

`candidate-0.2.0` still contained one derived-work identity leak inside Sections 1–7:

`NODE-LABEL -> NODE-COUNTER`

appeared in a relation projection note.

That did not change the semantic relation itself, but it weakened a true ontology-core-only recovery test because the model could see derived node names before reconstructing work projection.

`candidate-0.3.0` preserves 0.2 history and removes derived `NODE-*` identity from ontology core.

The CI hard-checks the stripped Sections 1–7 with:

`NODE-* leak count = 0`

before any model call.

## Input boundary

Each fresh OpenCode run receives only candidate-0.3 Sections 1–7:

- requirement traceability;
- definitions;
- work instances;
- relation definitions/instances;
- constraints/invariants;
- provenance;
- unknown/limitations.

Section 8 TREE / DEPENDENCY / NODE projection is removed.

The prompt also explicitly says not to invent or assume precomputed work-node identities.

## Native Skill use

Each run must call OpenCode's native `skill` tool and the serialized tool event must reference `pdca`.

The comparison step fails if either fresh run omits the Skill call.

Both runs passed.

## Normalized semantic contract

Each model answer is parsed as JSON and validated against ontology identities rather than natural-language wording.

Required semantic facts:

```text
tree root       = INST-SYSTEM
tree children   = {INST-COUNTER, INST-LABEL}

dependency producer  = INST-COUNTER
dependency consumer  = INST-LABEL
dependency interface = legal_count_value
dependency ready     = false

responsibility instances = {INST-SYSTEM, INST-COUNTER, INST-LABEL}
```

Responsibility prose is required to be nonempty but is not byte-compared.

## Result

Both independent sessions produced exactly the same normalized structure:

```json
{
  "tree": {
    "root": "INST-SYSTEM",
    "children": ["INST-COUNTER", "INST-LABEL"]
  },
  "dependency": {
    "producer": "INST-COUNTER",
    "consumer": "INST-LABEL",
    "interface": "legal_count_value",
    "ready": false
  },
  "responsibility_instances": [
    "INST-COUNTER",
    "INST-LABEL",
    "INST-SYSTEM"
  ]
}
```

The workflow emitted:

`same_semantics: true`

and:

`different_sessions: true`

followed by:

`two fresh OpenCode sessions recovered equivalent bounded-counter semantics`

## What this proves

For this synthetic bounded-counter model, the rc.5 ontology core is sufficiently explicit for two independent OpenCode model sessions to recover equivalent work-projection semantics without access to the declared Section 8 projection.

This is stronger evidence than:

- static maintenance reconstruction;
- one model inference;
- Skill discovery alone.

It directly supports the architectural claim:

```text
ontology core
  -> semantic work projection
```

rather than:

```text
task/node design
  -> back-filled ontology
```

## Node identity interpretation

The test deliberately compares work-instance semantics rather than requiring the two sessions to independently invent identical future node IDs.

Correct protocol behavior remains:

```text
ontology semantics
  -> Modeling projection chooses stable node_id
  -> Check
  -> Act fixes node_id + model/tree refs
  -> later task/Agent reads the fixed identity
```

Fresh semantic reconstruction and fixed identity recovery are related but distinct requirements.

## Why H18 remains NOT_RUN

This test still lacks the formal lifecycle required by H18:

- no user-authorized root Modeling task;
- no Plan/Do/Check/Act phase receipts;
- no Modeling Act fixing complete payload digest/tree/node identities;
- no formal DECOMP seed;
- no TASK/CONTEXT/CAP/CONFIRM/dispatch-created child task;
- no assignment record proving minimum sufficient context;
- no parent/child activity-history isolation evidence.

Therefore it is best classified as **pre-H18 fresh-session semantic recovery evidence**, not H18 acceptance.

H1–H18 remain `NOT_RUN`.

## CI policy

The double public-model probe remains non-blocking because free external endpoints are volatile.

The deterministic hard OpenCode compatibility gate remains CLI Skill discovery/parse.
