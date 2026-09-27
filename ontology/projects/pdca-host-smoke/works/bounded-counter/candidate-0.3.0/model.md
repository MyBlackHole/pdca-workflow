---
model_kind: project_ontology
model_root_id: project-ontology:pdca-host-smoke/bounded-counter@candidate-0.3.0
model_root_ref: ontology/projects/pdca-host-smoke/works/bounded-counter/candidate-0.3.0/model.md
project_id: pdca-host-smoke
work_id: bounded-counter
revision: candidate-0.3.0
status: candidate
protocol_revision: 4.0.0-rc.5
payload_scope: this_model_root_file
fixed_by_modeling_act: false
base_candidate_ref: ontology/projects/pdca-host-smoke/works/bounded-counter/candidate-0.2.0/model.md
base_candidate_blob: c3919a2d085e393b95c41f5c4d677a953592c5bd
---

# Bounded Counter Project Ontology — candidate 0.3.0

This file is the unique model root for the bounded-counter construction candidate.
It is a real project ontology artifact, but it has **not** been fixed by a host-executed Modeling Act and must not be treated as host acceptance evidence.

Layer boundary in this model root:

- **ontology core**: Definitions, Work Instances, Relation Definitions/Instances, Constraints/Invariants;
- **traceability**: Requirement Coverage, Provenance, Unknowns/Limitations;
- **derived work projection**: candidate TREE, DEPENDENCY and NODE qualifications.

Traceability and work projection are linked to the ontology but are not domain ontology facts themselves.

## 1. Requirement traceability

| Requirement | Statement | Coverage | Carried by |
|---|---|---|---|
| REQ-BC-001 | Counter initial value is 0. | covered | DEF-COUNTER, INST-COUNTER, C-INIT |
| REQ-BC-002 | Starting from 0, successive increment results are 1, 2, 2; increment saturates at upper bound 2. | covered | DEF-COUNTER, C-INC |
| REQ-BC-003 | read returns current value and does not mutate state. | covered | DEF-COUNTER, C-READ |
| REQ-BC-004 | reset restores value to 0. | covered | DEF-COUNTER, C-RESET |
| REQ-LABEL-001 | A legal counter reading N is represented as `count=N`. | covered | DEF-LABEL, C-LABEL |
| REQ-COMP-001 | Label formatting consumes only a legal counter reading. | covered | REL-CONSUMES-LEGAL-READING, C-LABEL-INPUT |

No in-scope requirement is currently partial, uncovered or not_applicable.

## 2. Ontology core

### 2.1 Definitions

#### DEF-SYSTEM — BoundedCounterSystem

- kind: definition
- semantic kind: aggregate
- meaning: a small system composed of a bounded mutable counter and a label formatter
- requirements: REQ-BC-001..004, REQ-LABEL-001, REQ-COMP-001

#### DEF-COUNTER — BoundedCounter

- kind: definition
- semantic kind: stateful component
- responsibility: maintain an integer count constrained to the inclusive range [0, upper_bound]
- properties:
  - `value`: integer, range [0, upper_bound]
  - `upper_bound`: positive integer; current work instance fixes it to 2
- operations:
  - `increment() -> integer`
  - `read() -> integer`
  - `reset() -> integer`
- requirements: REQ-BC-001..004

#### DEF-LABEL — CountLabelFormatter

- kind: definition
- semantic kind: stateless component
- responsibility: map a legal count value N to the exact text `count=N`
- input: legal count value
- output: label text
- requirements: REQ-LABEL-001, REQ-COMP-001

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
- provenance: REQ-COMP-001 plus current modeling decision

### RELDEF-CONSUMES-LEGAL-READING

- meaning: target formatter input is a legal value produced by source counter read semantics
- source role: producer
- target role: consumer
- direction: source -> target
- source kind: counter work instance
- target kind: formatter work instance
- cardinality: many readings may be consumed over time
- composition implication: no
- dependency implication: yes, on interface `legal_count_value`
- dependency reading: semantic relation direction is producer -> consumer; any derived work dependency is interpreted from the consumer responsibility toward the required producer/interface. No work-node identity is part of this ontology relation.
- provenance: REQ-COMP-001

## 4. Relation instances

### REL-COMP-SYSTEM-COUNTER

- type: RELDEF-COMPOSED-OF
- source: INST-SYSTEM
- target: INST-COUNTER
- shared interface: system delegates `increment/read/reset` bounded-state responsibility and receives `legal_count_value`
- shared invariant: counter-visible values satisfy C-INIT/C-INC/C-READ/C-RESET
- parent composition responsibility: INST-SYSTEM owns the aggregate guarantee that bounded counter behavior is present as a component responsibility
- composition semantics: aggregate responsibility includes this component responsibility

### REL-COMP-SYSTEM-LABEL

- type: RELDEF-COMPOSED-OF
- source: INST-SYSTEM
- target: INST-LABEL
- shared interface: system supplies a legal count value and receives exact label text
- shared invariant: label behavior satisfies C-LABEL and C-LABEL-INPUT
- parent composition responsibility: INST-SYSTEM owns the aggregate guarantee that legal counter readings can be represented as labels
- composition semantics: aggregate responsibility includes this component responsibility

### REL-CONSUMES-LEGAL-READING

- type: RELDEF-CONSUMES-LEGAL-READING
- source: INST-COUNTER
- target: INST-LABEL
- interface: `legal_count_value`
- interface contract: integer N where 0 <= N <= 2
- dependency semantics: formatter responsibility requires the counter producer's `legal_count_value` interface

## 5. Constraints and invariants

### C-INIT

- subject: INST-COUNTER
- predicate: immediately after initialization, `value == 0`
- applicability: before any mutating operation
- expected invariant: initial value is exactly 0
- observation signal: initialize then `read()` returns 0
- requirement: REQ-BC-001

### C-INC

- subject: INST-COUNTER
- predicate: `value_after = min(value_before + 1, 2)`
- applicability: every `increment()`
- expected invariant: value stays in [0,2] and saturates at 2
- observation signal: from initial state, three increments return 1, 2, 2
- requirement: REQ-BC-002

### C-READ

- subject: INST-COUNTER
- predicate: `read()` returns current value and `value_after == value_before`
- applicability: every `read()`
- expected invariant: read is observational and non-mutating
- observation signal: read twice without mutation; both values are equal
- requirement: REQ-BC-003

### C-RESET

- subject: INST-COUNTER
- predicate: after `reset()`, `value == 0`
- applicability: every reset
- expected invariant: reset returns the counter to initial state
- observation signal: increment to 2, reset, then read 0
- requirement: REQ-BC-004

### C-LABEL

- subject: INST-LABEL
- predicate: for legal input N, output is exactly the UTF-8 text `count=N`
- applicability: N in [0,2]
- expected invariant: deterministic exact representation
- observation signal: inputs 0,1,2 produce `count=0`, `count=1`, `count=2`
- requirement: REQ-LABEL-001

### C-LABEL-INPUT

- subject: REL-CONSUMES-LEGAL-READING
- predicate: formatter input N satisfies 0 <= N <= 2 and originates from the counter legal-reading interface
- applicability: every label formatting operation in this work instance
- expected invariant: formatter does not consume out-of-domain counter values
- observation signal: dependency interface value satisfies the range before formatting
- requirement: REQ-COMP-001

## 6. Provenance

### SRC-USER-SEED

- kind: user_requirement
- source: `tests/host-smoke.md` bounded-counter seed in protocol rc.5 repository
- repository: `MyBlackHole/pdca-workflow`
- commit: `3d16861e95692fd2131ae40882cd5c7e6e8f9353`
- source limitation: this maintenance construction uses the checked-in smoke requirement text; it is not a native host user-message receipt

### SRC-PROTOCOL

- kind: normative_protocol
- source: ONTOLOGY-01 / SCENE-01 at protocol 4.0.0-rc.5
- repository: `MyBlackHole/pdca-workflow`
- commit: `3d16861e95692fd2131ae40882cd5c7e6e8f9353`
- source limitation: protocol semantics are current repository rules; this artifact itself is not evidence that a host obeys them

### SRC-REFINEMENT

- kind: maintenance_review
- source: fresh-session recovery hardening after public-model runtime testing
- repository: `MyBlackHole/pdca-workflow`
- commit: `cb40eda41e3a29a7a1d46bb77d8f50ee7beff851`
- change intent: remove derived NODE/TREE/DEPENDENCY identity leakage from ontology core while preserving relation semantics

## 7. Unknowns and limitations

### U-HOST-FIXATION

- subject: this ontology revision
- unresolved question: can a real host-executed Modeling task reproduce and fix equivalent semantics through Act?
- missing evidence: native fresh-Agent task, phase receipts and Modeling Act fixation
- impact: this revision remains candidate and cannot satisfy H11/H18
- resolution condition: execute host-smoke and compare the fixed host-produced model root against this semantic contract

### U-CROSS-AGENT-RECOVERY

- subject: model-root recoverability
- unresolved question: can another fresh Agent recover the same definitions, instances, relations, constraints and requirement coverage using only fixed refs?
- missing evidence: native fresh-Agent initialization/load trace
- impact: semantic recoverability is not yet proven
- resolution condition: H18-style fresh-Agent recovery check

### U-IMPLEMENTATION

- subject: implementation behavior
- unresolved question: does any concrete implementation satisfy these constraints?
- missing evidence: pdca-implement artifact and behavior tests
- impact: no subject_conformance or delivery_usable claim may be made
- resolution condition: implement and verify scenes produce actual evidence

## 8. Derived work projection candidates

This section is a projection from ontology semantics, not additional ontology facts.

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
interface: legal_count_value@candidate-0.3.0
source relation: REL-CONSUMES-LEGAL-READING
fixed deliverable version/digest: not_fixed
ready evidence: none
ready: false
```

This is only a dependency **candidate** derived from ontology semantics. It cannot become a DEPENDENCY-01 ready edge until a fixed producer deliverable/interface version+digest and actual ready evidence exist.

### Candidate NODE qualifications

#### NODE-SYSTEM — bounded-counter-system

- ontology/work ref: INST-SYSTEM
- responsibility: compose bounded counter semantics with legal-value labeling semantics
- inputs: user operations increment/read/reset and label request
- outputs: bounded counter value and label text
- constraints: C-INIT, C-INC, C-READ, C-RESET, C-LABEL, C-LABEL-INPUT
- composition refs: REL-COMP-SYSTEM-COUNTER, REL-COMP-SYSTEM-LABEL
- dependency refs: REL-CONSUMES-LEGAL-READING
- acceptance criteria:
  - AC-NODE-SYSTEM-1: both composition responsibilities REL-COMP-SYSTEM-COUNTER and REL-COMP-SYSTEM-LABEL are present and traceable
  - AC-NODE-SYSTEM-2: the label responsibility consumes only the legal_count_value interface governed by C-LABEL-INPUT
  - AC-NODE-SYSTEM-3: all required counter and label semantic constraints are represented without unresolved blocking unknown
- oracle: reject the node if either component responsibility is missing, if label input is not linked to legal_count_value, or if a required constraint is absent/contradictory
- independently rejectable: yes, if composition semantics or any required interface invariant is absent

#### NODE-COUNTER — counter-core

- ontology/work ref: INST-COUNTER
- responsibility: maintain and expose bounded counter state semantics
- inputs: increment/read/reset
- outputs: legal_count_value
- constraints: C-INIT, C-INC, C-READ, C-RESET
- parent composition: REL-COMP-SYSTEM-COUNTER
- acceptance criteria:
  - AC-NODE-COUNTER-1: initialization semantics satisfy C-INIT
  - AC-NODE-COUNTER-2: increment semantics satisfy C-INC including saturation at 2
  - AC-NODE-COUNTER-3: read semantics satisfy C-READ
  - AC-NODE-COUNTER-4: reset semantics satisfy C-RESET
- oracle: from initial state read=0; increment sequence yields 1,2,2; repeated read without mutation is stable; after reset read=0
- independently rejectable: yes, by counter constraint violations

#### NODE-LABEL — label-format

- ontology/work ref: INST-LABEL
- responsibility: format a legal count reading
- inputs: legal_count_value
- outputs: exact label text
- constraints: C-LABEL, C-LABEL-INPUT
- parent composition: REL-COMP-SYSTEM-LABEL
- dependency: REL-CONSUMES-LEGAL-READING
- acceptance criteria:
  - AC-NODE-LABEL-1: legal inputs 0,1,2 map exactly to `count=0`, `count=1`, `count=2`
  - AC-NODE-LABEL-2: the consumed input is constrained by C-LABEL-INPUT and originates from the legal_count_value interface
- oracle: reject if a legal input is formatted differently or if the current composition/dependency permits an out-of-domain value to reach the formatter
- independently rejectable: yes, by format or input-domain violations

## 9. Candidate semantic-closure self-review

- identity closure: complete within this single model root
- definition/instance consistency: explicit
- relation endpoint/role closure: explicit, including shared interface/invariant and parent composition responsibility on composition edges
- constraint observability: explicit
- requirement coverage: all in-scope requirements covered
- provenance validity: source identities present; host-receipt limitation explicit
- unknown completeness: host fixation, cross-Agent recovery and implementation evidence remain explicit
- composition/dependency separation: explicit; Sections 1–7 contain no `NODE-*` identity and express only semantic implications/roles; dependency remains candidate/ready=false until fixed deliverable version/digest + ready evidence exist
- adoption scope: no external reference semantic unit is adopted in this candidate
- node qualification contract: candidate nodes include explicit acceptance criteria/oracles derived from ontology constraints and relations
- payload fixation: current candidate bytes are identifiable by Git path/blob during review, but a formal complete payload digest is intentionally deferred until Modeling Act fixation

This self-review is maintenance evidence only. It is not a formal Modeling Check and does not fix the candidate revision.
