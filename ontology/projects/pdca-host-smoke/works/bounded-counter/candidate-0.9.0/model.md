---
model_kind: project_ontology
model_root_id: project-ontology:pdca-host-smoke/bounded-counter@candidate-0.9.0
model_root_ref: ontology/projects/pdca-host-smoke/works/bounded-counter/candidate-0.9.0/model.md
project_id: pdca-host-smoke
work_id: bounded-counter
revision: candidate-0.9.0
status: candidate
protocol_revision: 4.0.0-rc.5
payload_scope: this_model_root_file
fixed_by_modeling_act: false
base_candidate_ref: ontology/projects/pdca-host-smoke/works/bounded-counter/candidate-0.8.0/model.md
base_candidate_blob: bdbd71525425afee5990ed0dfe0d2bdb71ddf7d3
payload_digest_ref: docs/reviews/2026-10-20-opencode-ai-usefulness.md#2026-10-21-candidate-zero-nine-payload-digest
---

# Bounded Counter Project Ontology — candidate 0.9.0

This file is the unique model root for the bounded-counter construction candidate.
It is a real project ontology artifact, but it has **not** been fixed by a host-executed Modeling Act and must not be treated as host acceptance evidence.

This revision keeps the seed phrase “无持久化的示例” unresolved and does not infer a persistence constraint or scope exclusion. It also covers the seed's separate counter-state and label-representation model-shape requirement. Unlike candidate-0.8.0, it does not infer operation return contracts from state effects, or treat a synthetic one-to-one `read()`/label policy as a user requirement. State observability, operation result channels, label/read mapping detail, and negative-boundary observability remain explicit unknowns. This is a maintenance candidate, not a formal Modeling Act or implementation/behavior evidence.

Layer boundary in this model root:

- **ontology core**: Definitions, Work Instances, Relation Definitions/Instances, Constraints/Invariants;
- **traceability**: Requirement Coverage, Provenance, Unknowns/Limitations;
- **derived work projection**: candidate TREE, DEPENDENCY and NODE qualifications.

Traceability and work projection are linked to the ontology but are not domain ontology facts themselves.

## 1. Requirement traceability

| Requirement | Statement | Coverage | Carried by |
|---|---|---|---|
| REQ-BC-001 | Counter initial value is 0. | covered | DEF-COUNTER, INST-COUNTER, C-INIT |
| REQ-BC-002 | Starting from initial value 0, successive increment results are 1, 2, 2; the upper bound is 2. | covered | DEF-COUNTER, C-INC |
| REQ-BC-003 | read does not change state. | covered | DEF-COUNTER, C-READ |
| REQ-BC-004 | reset restores value to 0. | covered | DEF-COUNTER, C-RESET |
| REQ-LABEL-001 | A legal counter reading N is represented as `count=N`. | covered | DEF-LABEL, C-LABEL |
| REQ-COMP-001 | Label formatting consumes only a legal counter reading. | covered | REL-CONSUMES-LEGAL-READING, C-LABEL-INPUT |
| REQ-MODEL-SHAPE-001 | Counter state and label representation are separately described by inputs, outputs, constraints, and rejectable conditions. | covered | DEF-COUNTER, DEF-LABEL, C-INIT, C-INC, C-READ, C-RESET, C-LABEL, C-LABEL-INPUT, AC-NODE-COUNTER-1..4, AC-NODE-LABEL-1..2 and their oracles |
| REQ-SCOPE-001 | Seed phrase “无持久化的示例”; its subject and behavioral meaning are unresolved. | uncovered | U-PERSISTENCE-SCOPE |

The source requirement statements above stay separate from candidate API and mapping decisions. The increment sequence is modeled only from the initialized state described by the seed. `REQ-BC-003` covers the state effect only; it does not specify the value or type returned by `read()`. `REQ-COMP-001` covers consumption of a legal reading, not the number or timing of `read()` calls. The six seeded counter, label, and composition requirements and `REQ-MODEL-SHAPE-001` are covered at that level. `REQ-SCOPE-001` is uncovered; no candidate decision is credited as source coverage, and no claim is made about untracked source clauses.

## 2. Ontology core

### 2.1 Definitions

#### DEF-SYSTEM — BoundedCounterSystem

- kind: definition
- semantic kind: aggregate
- meaning: a small system composed of a bounded mutable counter and a label formatter
- candidate modeling decision: composition of aggregate and component responsibilities; see SRC-CANDIDATE-MODEL-DECISIONS
- requirements: REQ-BC-001..004, REQ-LABEL-001, REQ-COMP-001, REQ-MODEL-SHAPE-001

#### DEF-COUNTER — BoundedCounter

- kind: definition
- semantic kind: stateful component
- responsibility: maintain an integer count constrained to the inclusive range [0, upper_bound]
- properties:
  - `value`: integer, range [0, upper_bound]
  - `upper_bound`: positive integer; parameterization is a candidate abstraction, and this work instance fixes it to 2 under SRC-CANDIDATE-MODEL-DECISIONS
- operations:
  - `increment()`: the source specifies the result sequence from initial state; its result channel/type remains unresolved under U-OPERATION-RETURN-CONTRACT
  - `read()`: the source specifies a non-mutating state effect; its result value/type remains unresolved under U-OPERATION-RETURN-CONTRACT
  - `reset()`: the source specifies restoration to zero; its result value/type remains unresolved under U-OPERATION-RETURN-CONTRACT
- inputs: `increment()`, `read()`, `reset()` operations
- outputs: seeded increment results; the concrete result channel and read/reset result contracts are unresolved under U-OPERATION-RETURN-CONTRACT
- constraints: C-INIT, C-INC, C-READ, C-RESET
- rejectable conditions: missing initialization, an incorrect seeded increment result sequence, incorrect reset-to-zero semantics, or a read that mutates state; state-preservation conformance remains subject to U-READ-OBSERVABILITY
- requirements: REQ-BC-001..004, REQ-MODEL-SHAPE-001

#### DEF-LABEL — CountLabelFormatter

- kind: definition
- semantic kind: stateless component
- responsibility: map a legal counter reading with semantic value N to the exact text `count=N`
- input: the candidate abstract semantic value `legal_count_value` representing a legal counter reading; its concrete operation/API mapping remains unresolved under U-LABEL-READ-MAPPING
- output: label text
- constraints: C-LABEL, C-LABEL-INPUT
- rejectable conditions: wrong exact text or an input that is not a legal reading; whether the current harness can expose/reject an out-of-range value remains unresolved under U-LABEL-REJECTION-OBSERVABILITY
- requirements: REQ-LABEL-001, REQ-COMP-001, REQ-MODEL-SHAPE-001

### 2.2 Work instances

#### INST-SYSTEM — bounded-counter-demo

- kind: work_instance
- instance_of: DEF-SYSTEM
- project/work: `pdca-host-smoke / bounded-counter`
- purpose: minimal project ontology used to exercise rc.5 construction and projection semantics

#### INST-COUNTER — demo-counter

- kind: work_instance
- instance_of: DEF-COUNTER
- upper_bound: 2
- initial_value: 0

#### INST-LABEL — demo-label

- kind: work_instance
- instance_of: DEF-LABEL

## 3. Relation definitions

### RELDEF-COMPOSED-OF

- meaning: aggregate semantic responsibility is partly realized by the target component responsibility
- source role: aggregate
- target role: component
- direction: source -> target
- source kind: aggregate work instance
- target kind: component work instance
- cardinality: one aggregate may compose one or more components
- composition implication: yes
- dependency implication: no
- provenance: composition requirement and explicit candidate-level interpretation in SRC-CANDIDATE-MODEL-DECISIONS; the endpoint responsibilities are proposed model semantics, not independent source clauses

### RELDEF-CONSUMES-LEGAL-READING

- meaning: target formatter consumes a legal counter reading whose semantic value is N
- source role: legal-reading provider
- target role: consumer
- direction: source -> target
- source kind: counter work instance / legal-reading semantics
- target kind: formatter work instance
- cardinality: many readings may be consumed over time
- composition implication: no
- dependency implication: yes, on the abstract interface `legal_count_value`; concrete operation and transport mapping remain unresolved under U-LABEL-READ-MAPPING
- dependency reading: semantic relation direction is producer -> consumer; any derived work dependency is interpreted from the consumer responsibility toward the required producer/interface. No work-node identity is part of this ontology relation.
- provenance: REQ-COMP-001 for abstract legal-reading consumption; exact operation mapping is a candidate choice motivated by SRC-READ-ORIGIN-TUI-REVIEW and remains unresolved under U-LABEL-READ-MAPPING

## 4. Relation instances

### REL-COMP-SYSTEM-COUNTER

- type: RELDEF-COMPOSED-OF
- source: INST-SYSTEM
- target: INST-COUNTER
- shared interface: bounded-counter operations satisfy their seeded state/result requirements; concrete result channels and the legal-reading transport are unresolved under U-OPERATION-RETURN-CONTRACT and U-LABEL-READ-MAPPING
- shared invariant: counter-visible values satisfy C-INIT/C-INC/C-READ/C-RESET
- parent composition responsibility: INST-SYSTEM owns the aggregate guarantee that bounded counter behavior is present as a component responsibility
- composition semantics: aggregate responsibility includes this component responsibility
- provenance: SRC-CANDIDATE-MODEL-DECISIONS

### REL-COMP-SYSTEM-LABEL

- type: RELDEF-COMPOSED-OF
- source: INST-SYSTEM
- target: INST-LABEL
- shared interface: a legal counter reading is represented by semantic value N and the formatter produces `count=N`; no request protocol is inferred
- shared invariant: label behavior satisfies C-LABEL and C-LABEL-INPUT
- parent composition responsibility: INST-SYSTEM owns the aggregate guarantee that legal counter readings can be represented as labels
- composition semantics: aggregate responsibility includes this component responsibility
- provenance: SRC-CANDIDATE-MODEL-DECISIONS

### REL-CONSUMES-LEGAL-READING

- type: RELDEF-CONSUMES-LEGAL-READING
- source: INST-COUNTER
- target: INST-LABEL
- interface: `legal_count_value`
- interface contract: a legal counter reading with semantic value N, where 0 <= N <= 2, is represented by the abstract candidate interface `legal_count_value`; the formatter represents that same N as `count=N`. The operation that creates the reading, call count, freshness, reuse, and concrete transport are unresolved under U-OPERATION-RETURN-CONTRACT and U-LABEL-READ-MAPPING.
- dependency semantics: formatter responsibility requires the counter producer's `legal_count_value` interface

## 5. Constraints and invariants

### C-INIT

- subject: INST-COUNTER
- predicate: immediately after initialization, `value == 0`
- applicability: before any mutating operation
- expected invariant: initial value is exactly 0
- observation signal: initialize, then the first increment has the seeded result 1; the concrete result channel remains unresolved under U-OPERATION-RETURN-CONTRACT
- requirement: REQ-BC-001

### C-INC

- subject: INST-COUNTER
- predicate: from initial state 0, successive increment results are 1, 2, 2, and the counter does not exceed the work-instance upper bound 2
- applicability: the seeded sequence beginning from initial state
- expected invariant: the specified sequence is observed without exceeding the work-instance bound
- observation signal: from initial state, three increments produce results 1, 2, 2; the result channel is not inferred
- requirement: REQ-BC-002

### C-READ

- subject: INST-COUNTER
- predicate: `value_after == value_before`
- applicability: every `read()`
- expected invariant: read is observational and non-mutating
- observation signal:
  - reach counter values 0, 1, and 2 through initialization and `increment()` operations
  - at each value N, use an independent permitted observation surface to record state before and after a `read()` call and require the observed state after the call to remain N; the `read()` result, if any, cannot prove its own non-mutation
  - repeated reads may be used as a test sequence, but neither their count nor a returned value is a source requirement
  - after `reset()`, independently observe state 0, then check that a `read()` call leaves the independently observed state unchanged
- observation limitation: U-READ-OBSERVABILITY; if no independent permitted state surface exists, retain state-preservation conformance as unknown and do not require private-state access
- requirements: REQ-BC-003, REQ-MODEL-SHAPE-001

### C-RESET

- subject: INST-COUNTER
- predicate: after `reset()`, `value == 0`
- applicability: every reset
- expected invariant: reset restores the counter state to its initial value
- observation signal: reach 2, reset, then the next increment produces the seeded result 1; no reset return value is assumed
- requirement: REQ-BC-004

### C-LABEL

- subject: INST-LABEL
- predicate: for legal input N, output is exactly the text `count=N`
- applicability: N in [0,2]
- expected invariant: the legal reading's numeric value is represented exactly
- observation signal: inputs 0,1,2 produce `count=0`, `count=1`, `count=2`
- requirement: REQ-LABEL-001

### C-LABEL-INPUT

- subject: REL-CONSUMES-LEGAL-READING
- predicate: every formatter input represents a legal counter reading N in [0,2], and the output represents the same N as `count=N`; the concrete read operation, origin transport, call count, reuse, and reread policy are not fixed
- applicability: every label formatting operation in this work instance
- expected invariant: each label represents only a legal reading value and preserves its semantic number in the formatted text
- observation signal:
  - a runtime contract observation pairs a legal reading value N with formatter output `count=N`; it does not assert a particular operation call, call count, freshness, or reuse policy
  - once a permitted harness can expose the input boundary, attempt a value outside [0,2] and observe whether it can reach formatting; if the interface or harness cannot expose this case, the result remains unknown under U-LABEL-REJECTION-OBSERVABILITY
- requirement: REQ-COMP-001

## 6. Provenance

### SRC-USER-SEED

- kind: user_requirement
- source: `tests/host-smoke.md` bounded-counter seed in protocol rc.5 repository
- source location: `tests/host-smoke.md:58-62` is the draft domain seed; line 63 is a task-scope boundary governed by host-smoke, not a domain ontology requirement
- repository: `MyBlackHole/pdca-workflow`
- commit: `138451df49a9f01d0b7a65a92921210b4c41fa68` (verified seed text and line locations)
- source limitation: the checked-in smoke text identifies itself as a draft for user confirmation; this maintenance construction is not a frozen user requirement or native host user-message receipt

### SRC-PROTOCOL

- kind: normative_protocol
- source: `ontology/concept/ontology-asset.md#ONTOLOGY-01` (`ontology:concept/ontology-asset`, revision `4.0.0-rc.3`) and `ontology/process/work-scenarios.md#SCENE-01` (`ontology:process/work-scenarios`, revision `4.0.0-rc.5`) at protocol `4.0.0-rc.5`
- repository: `MyBlackHole/pdca-workflow`
- commit: `138451df49a9f01d0b7a65a92921210b4c41fa68` (verified repository rules baseline for both source paths and revisions)
- source limitation: protocol semantics are current repository rules; this artifact itself is not evidence that a host obeys them

### SRC-REFINEMENT

- kind: maintenance_review
- source: fresh-session recovery hardening after public-model runtime testing
- repository: `MyBlackHole/pdca-workflow`
- commit: `cb40eda41e3a29a7a1d46bb77d8f50ee7beff851`
- change intent: remove derived NODE/TREE/DEPENDENCY identity leakage from ontology core while preserving relation semantics

### SRC-OBSERVABILITY-REVIEW

- kind: maintenance_review
- source: `candidate-0.3.0/model.md#C-LABEL-INPUT` compared with ONTOLOGY-01's constraint-observation contract
- repository: `MyBlackHole/pdca-workflow`
- commit: `138451df49a9f01d0b7a65a92921210b4c41fa68`
- source limitation: identifies that the prior signal observed value range but not interface origin; this review does not establish any concrete implementation behavior

### SRC-READ-ORIGIN-TUI-REVIEW

- kind: maintenance_review
- source: `docs/reviews/2026-10-20-opencode-ai-usefulness.md#2026-10-20-tmux-synthetic-trial`
- repository: `MyBlackHole/pdca-workflow`
- commit: `138451df49a9f01d0b7a65a92921210b4c41fa68` (rules baseline; not a commit containing the local review summary)
- change intent: a synthetic OpenCode implementation bypassed `read()` while constructing `legal_count_value`; an independent read-only review and a focused test exposed the mismatch, motivating an explicit value-preserving interface mapping
- source limitation: raw TUI transcript was not exported; the review summary is an uncommitted local artifact, and the scratch implementation is agent-generated. This is candidate motivation only, not a native user receipt, formal Model Check/Act, or host implementation evidence

### SRC-READ-OBSERVABILITY-REVIEW

- kind: maintenance_review
- source: `docs/reviews/2026-10-20-opencode-ai-usefulness.md#2026-10-20-c-read-observation-gap`
- repository: `MyBlackHole/pdca-workflow`
- commit: `138451df49a9f01d0b7a65a92921210b4c41fa68` (rules baseline; not a commit containing the local review summary)
- change intent: the candidate-0.5.0 C-READ observation and counter projection oracle did not require reads to match known nonzero counter states; an agent-generated constant-zero read mutant satisfied those stated observations
- source limitation: the one-off counterexample and strengthened sequence are synthetic maintenance probes, not a formal Verify result, host receipt, or proof about an adopted implementation

### SRC-PERSISTENCE-SCOPE-REVIEW

- kind: maintenance_review
- source: `docs/reviews/2026-10-20-opencode-ai-usefulness.md#2026-10-20-persistence-scope-coverage-gap`
- repository: `MyBlackHole/pdca-workflow`
- commit: `138451df49a9f01d0b7a65a92921210b4c41fa68` (rules baseline only)
- change intent: record that candidate-0.6.0 omitted this source phrase while claiming coverage
- source limitation: this review does not resolve its semantics or establish host/user evidence

### SRC-CANDIDATE-MODEL-DECISIONS

- kind: maintenance_review
- source: `docs/reviews/2026-10-20-opencode-ai-usefulness.md#2026-10-21-candidate-zero-eight-operation-contract-audit`
- repository: `MyBlackHole/pdca-workflow`
- commit: `138451df49a9f01d0b7a65a92921210b4c41fa68` (repository baseline only; the review summary is a local uncommitted artifact)
- decision status: proposed candidate semantics, not user-confirmed requirements
- decisions: parameterize the upper bound with this work instance fixed at 2; represent the system as an aggregate of counter and label responsibilities; route the abstract `legal_count_value` semantic interface from the counter responsibility to the label formatter
- source limitation: these are explicit modeling choices for a reviewable candidate. They do not establish a request protocol, concrete operation mapping, invocation count, freshness/reuse policy, or operation result contract; those remain unknown under U-OPERATION-RETURN-CONTRACT and U-LABEL-READ-MAPPING

### SRC-LABEL-REJECTION-PROBE

- kind: maintenance_review
- source: `docs/reviews/2026-10-20-opencode-ai-usefulness.md#2026-10-21-candidate-zero-eight-operation-contract-audit`
- repository: `MyBlackHole/pdca-workflow`
- commit: `138451df49a9f01d0b7a65a92921210b4c41fa68` (repository baseline only; the review summary is a local uncommitted artifact)
- decision status: proposed verification probe, not a source requirement
- probe: attempt an out-of-range label input only if a permitted implementation/test interface can expose it; otherwise retain rejection observability as unknown
- source limitation: the draft seed does not specify an invalid-input API or a rejection signal

## 7. Unknowns and limitations

### U-HOST-FIXATION

- subject: this ontology revision
- unresolved question: can a real host-executed Modeling task reproduce and fix equivalent semantics through Act?
- missing evidence: native fresh-Agent task, phase receipts and Modeling Act fixation
- impact: this revision remains candidate and cannot satisfy `tests/host-acceptance.md#H11` or `tests/host-acceptance.md#H18`
- resolution condition: execute host-smoke and compare the fixed host-produced model root against this semantic contract

### U-CROSS-AGENT-RECOVERY

- subject: model-root recoverability
- unresolved question: can another fresh Agent recover the same definitions, instances, relations, constraints and requirement coverage using only fixed refs?
- missing evidence: native fresh-Agent initialization/load trace
- impact: semantic recoverability is not yet proven
- resolution condition: `tests/host-acceptance.md#H18` fresh-Agent recovery check

### U-IMPLEMENTATION

- subject: implementation behavior
- unresolved question: does any concrete implementation satisfy these constraints?
- missing evidence: pdca-implement artifact and behavior tests
- impact: no subject_conformance or delivery_usable claim may be made
- resolution condition: implement and verify scenes produce actual evidence

### U-READ-OBSERVABILITY

- subject: C-READ before/after counter-state observation at values 0, 1, and 2
- unresolved question: which permitted, independent observation surface can reveal the state before and after each `read()` without relying on the `read()` return as its own proof or requiring private-state access?
- missing evidence: a fixed implementation/mapping with an independently observable state signal and a permitted host test surface for the before/after comparison
- impact: C-READ's state-preservation signal and NODE-COUNTER acceptance oracle cannot establish conformance if no such surface is available; operation result values alone are insufficient, and their semantics remain separately unresolved under U-OPERATION-RETURN-CONTRACT
- resolution condition: identify and validate an independent permitted observation surface tied to the fixed implementation, or retain C-READ conformance as unknown and record the observation limitation

### U-OPERATION-RETURN-CONTRACT

- subject: result channels and result meanings of `increment()`, `read()`, and `reset()`
- unresolved question: whether the seeded increment results denote function return values or another result channel/type; whether `read()` returns a value and what that value means; and whether `reset()` has any result
- missing evidence: authoritative API/result-channel specification or user clarification for each operation
- impact: the seeded increment sequence remains a required result, but no return type/channel may be fixed; `read()` return-value conformance and every reset return-value claim are unknown. C-READ can only establish its state effect through an independent permitted observation surface
- resolution condition: obtain authoritative operation signatures/result-channel semantics; then update a successor's definitions, constraints, implementation interface and acceptance oracles without retroactively changing this candidate

### U-LABEL-READ-MAPPING

- subject: mapping a legal counter reading to the abstract formatter input `legal_count_value`
- unresolved question: which concrete operation/interface supplies a reading, whether one read call corresponds to one label, and whether readings may be reused or reread
- missing evidence: authoritative interface decision and a fixed producer-to-consumer mapping suitable for the implementation
- impact: `REQ-COMP-001` requires only consumption of a legal reading. The candidate does not require `read()` to supply it, one call per label, one-to-one correlation, freshness, unchanged wrapper metadata, or a no-reread policy; projected label-node mapping conformance remains unknown until the interface is fixed
- resolution condition: obtain an explicit interface/mapping decision, fix producer and consumer versions, then define only the needed mapping observations in a successor

### U-LABEL-REJECTION-OBSERVABILITY

- subject: observation of rejection for a label input outside [0,2]
- unresolved question: can a permitted implementation or host harness expose an out-of-range value at the formatter boundary and distinguish rejection from non-delivery?
- missing evidence: fixed interface and permitted test surface with an observable negative-case signal
- impact: an unobservable negative case cannot be reported as passed or failed; label rejection conformance remains unknown if the boundary cannot be exposed
- resolution condition: identify an allowed boundary and rejection signal, or keep this conformance point unknown in a successor

### U-PERSISTENCE-SCOPE

- subject: source phrase “无持久化的示例” recorded as REQ-SCOPE-001 from SRC-USER-SEED
- unresolved question: what is the phrase's subject and behavioral meaning, if any, including whether it concerns persistence or only describes the sample?
- missing evidence: authoritative source/user clarification identifying the subject and meaning, plus persistence boundary and observable signal if behavioral
- impact: REQ-SCOPE-001 remains uncovered; no `C-NO-PERSIST` may be inferred; full source-coverage/root semantic closure cannot be claimed; child-node impact remains unknown
- resolution condition: obtain authoritative clarification, then either define persisted subject/lifecycle/observation before adding a constraint or record an explicit scope exclusion and rationale in a successor

## 8. Derived work projection candidates

This section is a projection from ontology semantics, not additional ontology facts. Its node qualifications cover the seeded semantics and explicit candidate decisions. U-PERSISTENCE-SCOPE leaves the impact of the unresolved source phrase on child nodes unknown; U-OPERATION-RETURN-CONTRACT, U-LABEL-READ-MAPPING and U-LABEL-REJECTION-OBSERVABILITY leave their respective conformance points unresolved.

### Candidate TREE

```text
NODE-SYSTEM bounded-counter-system
├─ NODE-COUNTER counter-core
└─ NODE-LABEL label-format
```

Derivation:

- NODE-SYSTEM -> NODE-COUNTER comes only from REL-COMP-SYSTEM-COUNTER / RELDEF-COMPOSED-OF.
- NODE-SYSTEM -> NODE-LABEL comes only from REL-COMP-SYSTEM-LABEL / RELDEF-COMPOSED-OF.
- REL-CONSUMES-LEGAL-READING does not create a composition child; it creates a dependency candidate only.

### Candidate DEPENDENCY

```text
consumer: NODE-LABEL
producer: NODE-COUNTER
interface: legal_count_value@candidate-0.9.0
source relation: REL-CONSUMES-LEGAL-READING
fixed deliverable version/digest: not_fixed
ready evidence: none
ready: false
```

This is only a dependency **candidate** derived from ontology semantics. It cannot become a DEPENDENCY-01 ready edge until a fixed producer deliverable/interface version+digest and actual ready evidence exist.
NODE-LABEL -> NODE-COUNTER is the only dependency candidate: NODE-LABEL requires the counter's proposed `legal_count_value` interface; no fixed deliverable version or digest is available yet. NODE-SYSTEM's relation reference describes the composed subtree and does not create a separate direct edge without a distinct fixed interface deliverable.

### Candidate NODE qualifications

#### NODE-SYSTEM — bounded-counter-system

- ontology/work ref: INST-SYSTEM
- source refs: SRC-USER-SEED, SRC-PROTOCOL
- unknown refs: U-PERSISTENCE-SCOPE, U-READ-OBSERVABILITY, U-OPERATION-RETURN-CONTRACT, U-LABEL-READ-MAPPING, U-LABEL-REJECTION-OBSERVABILITY, U-HOST-FIXATION, U-CROSS-AGENT-RECOVERY, U-IMPLEMENTATION
- responsibility: compose bounded counter semantics with legal-value labeling semantics
- inputs: candidate counter operations increment/read/reset and a legal reading supplied to the label formatter; a separate label request protocol is not specified by the seed
- outputs: seeded increment results and label text; read/reset result channels remain unknown
- constraints: C-INIT, C-INC, C-READ, C-RESET, C-LABEL, C-LABEL-INPUT
- composition refs: REL-COMP-SYSTEM-COUNTER, REL-COMP-SYSTEM-LABEL
- dependency refs: REL-CONSUMES-LEGAL-READING
- acceptance criteria:
  - AC-NODE-SYSTEM-1: both composition responsibilities REL-COMP-SYSTEM-COUNTER and REL-COMP-SYSTEM-LABEL are present and traceable
  - AC-NODE-SYSTEM-2: the candidate relation identifies a legal-reading producer endpoint, consumer formatter endpoint, and semantic value range [0,2]; concrete operation mapping and call policy remain unknown under U-LABEL-READ-MAPPING
  - AC-NODE-SYSTEM-3: the currently defined counter and label semantic constraints are represented; U-PERSISTENCE-SCOPE prevents a full source-coverage or root semantic-closure claim, and its child-node impact is unknown
- oracle: reject the node if either component responsibility is missing, the proposed relation omits its endpoints or legal-reading range, or a seeded constraint is absent/contradictory. Do not reject on a specific read operation, call count, one-to-one correlation, freshness/reuse, wrapper, bypass, or reread policy while U-LABEL-READ-MAPPING is unresolved
- independently rejectable: yes, if composition semantics or any required interface invariant is absent

#### NODE-COUNTER — counter-core

- ontology/work ref: INST-COUNTER
- source refs: SRC-USER-SEED, SRC-PROTOCOL
- unknown refs: U-PERSISTENCE-SCOPE (child impact unknown), U-READ-OBSERVABILITY, U-OPERATION-RETURN-CONTRACT, U-LABEL-READ-MAPPING, U-HOST-FIXATION, U-CROSS-AGENT-RECOVERY, U-IMPLEMENTATION
- responsibility: maintain bounded counter state semantics
- inputs: increment/read/reset
- outputs: seeded increment results and the candidate abstract `legal_count_value` semantic reading; which operation supplies that reading remains unknown under U-LABEL-READ-MAPPING, and any `read()` result channel remains unknown under U-OPERATION-RETURN-CONTRACT
- constraints: C-INIT, C-INC, C-READ, C-RESET
- parent composition: REL-COMP-SYSTEM-COUNTER
- acceptance criteria:
  - AC-NODE-COUNTER-1: initialization semantics satisfy C-INIT
  - AC-NODE-COUNTER-2: from initial state 0, successive increment results are 1, 2, 2; no general result formula or return type/channel is inferred
  - AC-NODE-COUNTER-3: `read()` leaves independently observed state unchanged when a permitted independent observation surface is available; its return value, if any, is not specified
  - AC-NODE-COUNTER-4: reset semantics satisfy C-RESET
- oracle: verify the seeded increment results 1, 2, 2 from initial state 0. Independently establish initial state 0 and reset-to-zero through a permitted surface if one is available; after reset, the next increment must produce the seeded result 1. For read nonmutation, compare independently observed state before and after a read where a permitted surface exists; if unavailable, retain C-READ conformance as unknown under U-READ-OBSERVABILITY. Do not infer read/reset return-value requirements under U-OPERATION-RETURN-CONTRACT
- independently rejectable: yes, by counter constraint violations

#### NODE-LABEL — label-format

- ontology/work ref: INST-LABEL
- source refs: SRC-USER-SEED, SRC-PROTOCOL
- unknown refs: U-PERSISTENCE-SCOPE (child impact unknown), U-OPERATION-RETURN-CONTRACT, U-LABEL-READ-MAPPING, U-LABEL-REJECTION-OBSERVABILITY, U-HOST-FIXATION, U-CROSS-AGENT-RECOVERY, U-IMPLEMENTATION
- responsibility: format a legal count reading
- inputs: legal_count_value
- outputs: exact label text
- constraints: C-LABEL, C-LABEL-INPUT
- parent composition: REL-COMP-SYSTEM-LABEL
- dependency: REL-CONSUMES-LEGAL-READING
- acceptance criteria:
  - AC-NODE-LABEL-1: legal inputs 0,1,2 map exactly to `count=0`, `count=1`, `count=2`
  - AC-NODE-LABEL-2: a legal reading with semantic value N in [0,2] is represented as the same N through the proposed `legal_count_value` interface; concrete operation mapping and rejection observability remain unknown
- oracle: reject if a legal reading N is formatted differently from `count=N`. The proposed interface must identify its semantic value range and relation endpoints. Do not require a concrete operation, call count, one-to-one correlation, unchanged wrapper metadata, freshness/reuse, bypass, or reread policy under U-LABEL-READ-MAPPING. An out-of-range negative case is assessable only if the permitted boundary is observable; otherwise retain it as unknown under U-LABEL-REJECTION-OBSERVABILITY
- independently rejectable: yes, by format or input-domain violations

## 9. Candidate semantic-closure self-review

- identity closure: this candidate has a unique model root and a review-side reference to its complete one-file SHA-256 payload digest; source-coverage/root semantic closure remains open on REQ-SCOPE-001
- definition/instance consistency: explicit
- relation endpoint/role closure: explicit, including shared interface/invariant and parent composition responsibility on composition edges
- constraint observability: C-READ requires an independent permitted before/after state surface to establish preservation; U-READ-OBSERVABILITY records the unresolved surface and leaves conformance unknown if unavailable. C-LABEL-INPUT checks semantic legal-reading/value preservation; operation mapping remains unknown under U-LABEL-READ-MAPPING, and negative rejection remains unknown if the boundary cannot be exposed under U-LABEL-REJECTION-OBSERVABILITY
- requirement coverage: the six counter, label and composition requirements and REQ-MODEL-SHAPE-001 are covered; REQ-SCOPE-001 is the remaining uncovered domain requirement in the identified draft seed, pending authoritative clarification; this does not resolve untracked source clauses
- provenance validity: source identities and the maintenance reviews motivating candidate decisions are recorded; neither review nor this model root establishes host/user clarification or a native host receipt
- unknown completeness: host fixation, cross-Agent recovery, implementation evidence, independent read-state observability, operation result contracts, legal-reading operation mapping, negative-boundary observability and the seed phrase's subject/meaning remain explicit; child-node impact of that phrase is unknown
- composition/dependency separation: explicit; ontology definitions and requirement traceability cross-reference candidate-node acceptance oracles to make rejectability and shape checks reviewable, while NODE identities remain derived projection candidates rather than ontology facts; dependency remains candidate/ready=false until fixed deliverable version/digest + ready evidence exist
- adoption scope: no external reference semantic unit is adopted in this candidate
- node qualification contract: candidate nodes include source/unknown refs and explicit acceptance criteria/oracles derived from ontology constraints and relations
- payload identity: `payload_digest_ref` resolves to the review heading that records the SHA-256 of this complete single-file candidate payload. This digest makes a proposed TREE input identifiable; Modeling Act fixation is still absent

This self-review is maintenance evidence only. It is not a formal Modeling Check and does not fix the candidate revision.
