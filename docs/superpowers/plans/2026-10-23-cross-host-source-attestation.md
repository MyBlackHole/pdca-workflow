# Cross-Host Source Attestation Implementation Plan

> Execution subskill: `superpowers:executing-plans` for inline execution. The user has approved the design; this plan fixes the implementation boundary and verification steps.

## Goal

Define and verify a fail-closed source-attestation protocol for a user response relayed from Codex to OpenCode Mini. Preserve CONFIRM-01 as the authority that interprets whether a response approves one fixed request. Preserve separate origin-user and relay/operator identities. Mark CAP-01 `communicate` usable only after both hosts provide native issuance/verification evidence and the negative cases pass.

## Architecture

Codex's native source event may issue a versioned attestation bound to one response, request, subject, and OpenCode target session. A trusted OpenCode recipient verifies the attestation and route before Mini receives the response. PDCA records immutable references to both host facts, then CONFIRM-01 independently matches the response to the pending request. Missing host support, uncertain provenance, mismatch, expiry, invalid signature, or replay remains `unknown`/`blocked` and cannot consume the request.

This repository is a Markdown ontology/skills package, not either host's implementation. It can define record contracts, authority rules, and conformance procedures. It cannot claim native support by adding a schema or prompt adapter. If either host has no native issuance or trusted verification extension point, record the capability as unavailable and keep host integration out of scope for this change.

## Tech Stack

- Markdown ontology contracts and manual host-acceptance procedures.
- Native Codex/OpenCode host receipts only if explicitly exposed by the hosts.
- `git diff --check` for whitespace and the four-pass AI review in `ontology/process/flow-check.md` for semantic review.
- No new runtime, prompt-only adapter, custom PDCA semantic validator, or test dependency.

## Spec path

`docs/superpowers/specs/2026-10-23-cross-host-source-attestation-design.md`

## Global Constraints

- Preserve CONFIRM-01, GATE-01, and current fail-closed behavior; an attestation proves source and routing facts, never authorization by itself.
- Keep origin user, relay/operator, and recipient verifier identities distinct.
- Bind each receipt to the exact response digest, request ID/digest, subject digest, scope/action/phase/run, target host/session, expiry, and one-time nonce.
- Do not accept Agent-supplied source labels, thread IDs, copied text, hashes, or a prompt secret as host proof.
- Do not use the existing RPC Plan request or mutate its records, state, or fixed subject for this work.
- Do not access `records/`, inspect unrelated user configuration, or infer host capability from a project name or model response.
- Do not write test fixtures, logs, caches, or build output under `/tmp`; do not run commands that cannot be kept inside the workspace.
- Do not create a project-specific semantic validator. Use the documented host acceptance and AI review process.
- A static schema, passing document review, or simulated receipt cannot upgrade CAP-01 to PASS.

## Exact File Map

| File | Planned change |
|---|---|
| `tests/opencode-interactive-provenance.md` | Add the verified/unsupported boundary for native source-attestation issuance and OpenCode recipient verification; preserve the existing TUI-human-origin limitation. |
| `tests/source-attestation-conformance.md` | Add a manual protocol and host conformance matrix for valid delivery and fail-closed negative cases. |
| `ontology/contracts/record-shapes/source-attestation.md` | Define `pdca.source-attestation/v1`, separating issuer statement, origin event, recipient verification, route, expiry, and replay facts. |
| `ontology/contracts/record-shapes/response.md` | Add `source_attestation_ref` while keeping the response record limited to raw response and source facts. |
| `ontology/concept/pdca-ai-friendly-confirmation.md` | Define how CONFIRM-01 consumes a verifier-backed source fact without changing response interpretation or authorization semantics. |
| `ontology/concept/capability-protocol.md` | Specify host-pair-scoped `communicate` evidence and the conditions required for PASS. |
| `ontology/contracts/record-shapes/capability-check.md` | Record source/recipient host pair, version/config scope, evidence references, and limitations without promoting `not_run` or `unknown`. |
| `tests/host-acceptance.md` | Add a separately reported cross-host source-attestation acceptance case and retain overall H1–H18 status unless the full existing suite is rerun. |
| `ontology/INDEX.md` | Add the new record shape to the authority locator if required by its current structure. |
| `ontology/LOAD-MAP.md` | Add the new record shape to the minimal read path for response-source verification if required by its current structure. |

Do not edit the design spec or the already committed source-gap observation. Read each listed authority only when its task begins; do not expand this file map during execution without first recording the newly required path and reason in the plan review.

## Implementation Tasks

### Task 1 — Define conformance cases before changing normative contracts

Create `tests/source-attestation-conformance.md` first. Specify inputs, fixed object identity, expected records, and expected state for:

- valid signature, matching response/request/subject/phase/run/target session, fresh nonce;
- forged issuer and invalid signature;
- modified response text or response digest;
- mismatched request, subject, scope, phase, run, host, or session;
- expired receipt;
- replayed nonce/event and duplicate delivery (idempotent result, no second decision/run);
- missing issuer or trusted verifier;
- valid source receipt with an ambiguous or non-approving response (source may verify, but CONFIRM-01 does not authorize).

For every rejection case, require no request consumption, no decision that asserts positive authorization, and no phase/run start. Distinguish rejected evidence from `unknown` where the host fact cannot be observed. Include an initially `unknown` row for each host; Task 2 fills it from native evidence.

**Verification:** an independent reader can map every design invariant in sections 2–6 to at least one case, and every case names its required native evidence. Document-only cases must not be described as executed tests.

### Task 2 — Run a read-only native-host feasibility gate

Inspect only the approved provenance/acceptance documents and host metadata explicitly exposed in the current sessions. Determine separately whether:

1. Codex exposes an issuer event that binds the actual user's response to the fixed approval object and can produce a host-verifiable receipt; and
2. OpenCode exposes a trusted receiving hook that verifies issuer, signature, response digest, request/subject, target session, expiry, and nonce before delivering the response to Mini.

Treat prompt text, Agent assertions, generic message-role fields, and routing IDs as insufficient. Do not install extensions, alter host configuration, create credentials, or perform a real approval in this read-only gate.

**Expected result:** fill the host rows in the conformance document with each side marked `available`, `unavailable`, or `unknown`, the exact host/version evidence reference, and the limit. If either side is not demonstrably available, keep CAP-01 `communicate` unavailable and do not implement or simulate a host adapter. Protocol documentation may proceed, but real-host acceptance remains `NOT_RUN`.

**Verification:** compare each claim with the exact cited host evidence and the already approved design. No host evidence means `unknown`; do not browse, inspect unrelated host files, or infer support.

### Task 3 — Add the source-attestation record shape

Create `ontology/contracts/record-shapes/source-attestation.md` using the repository's current record-shape conventions. Define issuer assertion and recipient-verifier receipt as separate facts. Include the minimum bindings from the approved design: issuer/key reference, receipt/version, issue/expiry time, one-time nonce, source host/user/message/transcript/conversation/turn references, response digest, request ID/digest, subject digest, scope/action/phase/run, target host/session, native delivery reference, verifier result/reference, replay/consumption status, and limitations.

Store references and public verification facts only; never store private signing keys or credentials. Do not choose a cryptographic algorithm or claim a trusted key source until Task 1 identifies real host support. If a required value cannot be produced natively, represent the fact as missing/unknown and fail closed; do not make the field syntactically mandatory in a way that fabricates evidence.

**Verification:** use Task 2 cases to check that the record can represent valid, rejected, expired, replayed, mismatched, and unknown states without collapsing origin and relay actors or confusing verification with authorization.

### Task 4 — Connect the response contract and CONFIRM-01

Extend `pdca.response/v4` with `source_attestation_ref` in `ontology/contracts/record-shapes/response.md`. Clarify that:

- `source_ref`/`actor_ref`/`conversation_ref` identify the original source facts according to their existing meanings;
- `host_received_event_ref` identifies the recipient's native delivery event;
- the relay/operator remains the actual recipient-side actor;
- the attestation reference points to separately recorded issuer and verifier facts;
- CONFIRM-01 still evaluates response meaning against the exact pending request and does not treat signature validity as approval.

**Verification:** for each Task 2 case, determine whether it may produce a response record, whether it may be matched by CONFIRM-01, and whether it can consume the request. Only a complete, matching, unexpired, unconsumed verified source fact plus an unambiguous approving response may reach the existing confirmation decision path.

### Task 5 — Define CAP-01 evidence and pair scope

Update `ontology/concept/capability-protocol.md` and `ontology/contracts/record-shapes/capability-check.md` so `communicate` evidence names the source/recipient host pair, applicable host versions/configuration, issuer and verifier evidence, auditable delivery/verification receipts, negative-case results, and limitations. Require all four conditions from the approved design for PASS. Missing host-native capability or evidence remains `NOT_RUN`/`unknown`/`unavailable` as appropriate; do not generalize one pair's result to other versions, configurations, or routes.

**Verification:** review each Task 2 case against the capability result rules. A schema-only result, simulated proof, or successful positive case without rejection coverage cannot produce PASS.

### Task 6 — Integrate discovery and host acceptance guidance

Update `tests/opencode-interactive-provenance.md`, `tests/host-acceptance.md`, and the relevant entries in `ontology/INDEX.md` and `ontology/LOAD-MAP.md`. Keep the existing finding that OpenCode user-role/admission events do not alone prove human origin. The live procedure must use a new isolated fixed request and an explicitly authorized test action; it must not reuse the current RPC Plan request. Separate protocol conformance from actual host acceptance and report `NOT_RUN` until each host emits native evidence.

**Verification:** follow the documented read path from response-source verification to the new contract; confirm the index/load map does not cause unrelated ontology branches to be loaded. Ensure H1–H18 are not reported complete merely because this new case passes.

### Task 7 — Four-pass review and evidence check

Review the exact diff using `ontology/process/flow-check.md`:

1. Scope: only files in the file map changed; no existing RPC task or records touched.
2. Consistency: new contract, response shape, CONFIRM-01, CAP-01, index/load map, and tests agree.
3. Adversarial: forged/tampered/replayed/expired/misrouted evidence, ambiguous response, and missing native hooks all fail closed; duplicate delivery is idempotent.
4. Evidence: distinguish local document review from host behavior; keep real host acceptance `NOT_RUN` absent native issuer/verifier receipts.

Run `git diff --check -- <tracked changed paths>`; it must exit 0 with no whitespace diagnostics. For each new untracked document, run `git diff --no-index --check -- /dev/null <new path>`; it must print no whitespace diagnostic (exit 1 is expected because the file differs from `/dev/null`). Inspect `git status --short -- <exact file-map paths>` and `git diff -- <tracked file-map paths>`; the listed changes must stay within the file map, and no existing RPC task or records may appear. Then obtain a read-only independent review of the scoped diff if the high-impact review gate is still applicable; do not create a PDCA lifecycle task for maintenance. Fix blocking findings before claiming the documentation work is complete.

**Expected result:** whitespace check succeeds, the AI review has no unresolved blocking consistency/scope finding, and every capability claim is backed by its named evidence or remains explicitly unknown/not-run.

## Stop Conditions

Stop native-integration work immediately if either host cannot expose the required native event, trusted verification point, or auditable receipt. Do not replace the missing facility with a local signing secret, parent-Agent relay, prompt adapter, or manual `actor=user` label. Report the missing evidence and retain `communicate=unavailable`.

Stop before writing any out-of-map path. Stop if implementation would require a `/tmp` artifact, repository-wide search, access to `records/`, a new custom semantic validator, or mutation of the current RPC request. Re-scope in a reviewed plan before continuing.
