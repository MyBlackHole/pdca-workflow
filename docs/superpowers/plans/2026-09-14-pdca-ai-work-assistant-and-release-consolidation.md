# PDCA AI Work Assistant and Release Consolidation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the user-controlled `$pdca-assist` workbench while consolidating current-release control into `release.json` and removing redundant root and bootstrap material without invalidating historical task snapshots.

**Architecture:** `release.json` replaces the two current-release documents as the sole machine-readable authority: it holds release bytes, active snapshot members, the Skill index, and protocol metadata, but excludes its own digest. New installations and project bindings pin that file; existing bindings retain their old paired snapshot references. `$pdca-assist` is a ninth, explicit and default-read-only Skill that analyzes only the bound project and corresponding central records, then presents user-selectable actions.

**Tech Stack:** Python 3.10 standard library, POSIX `flock`, Markdown Agent Skills, JSON, `unittest`.

**Spec:** `docs/superpowers/specs/2026-09-14-pdca-ai-work-assistant-design.md`

## Global Constraints

- Keep `PDCA_ROOT` as the sole write domain for records, ontology, resource reservations, decisions, evidence, and task state.
- `$pdca-assist` may only read the currently bound `TARGET_ROOT` (source, docs, and Git state) and must obey host permissions; it must not scan other projects or unrelated central history.
- AI proposes options; the user selects, supplements, and explicitly authorizes any write or phase transition.
- Existing eight Skill names, original-Agent continuity, and explicit user initiation of every phase remain unchanged.
- `setup` remains an installer/registry tool, not an Agent scheduler, background monitor, business lock, or project-file writer.
- New release control is `release.json`; it does not self-hash, and bindings pin its byte digest. Existing task/binding snapshots using `protocol-release.md` plus `release-manifest.md` remain readable without rewriting or re-signing them.
- Do not delete `records/`, `ontology/projects/`, historical snapshots, or user-owned files.
- Use `apply_patch` for edits. Run `python3 -m unittest discover -s tests -v` and `python3 scripts/check_release.py .` before the final task commit.

---

## File Structure

| Path | Responsibility after this plan |
|---|---|
| `release.json` | Sole current-release machine authority: schema, version, byte digests, active set, catalog path, and protocol metadata. |
| `scripts/common.py` | Validates `release.json`, derives the catalog entry set, and retains a read-only legacy snapshot reader. |
| `scripts/build_manifest.py` | Builds `release.json`; no Markdown-manifest generation. |
| `scripts/check_release.py` | Validates current release control, Skill invariants, and active relative links. |
| `scripts/install.py` | Installs, snapshots, updates, checks, uninstalls, and registers using `release.json`, while accepting legacy binding snapshots. |
| `skills/catalog.json` | The sole list of current exported Skills, including `pdca-assist`. |
| `skills/pdca-assist/SKILL.md` | Explicit read-only workbench that offers task, context, evidence, and collaboration options and waits for user choice. |
| `ontology/contracts/entry-recovery.md` | Normative shared recovery/routing method formerly in `bootstrap/entry-check.md`. |
| `ontology/contracts/agent-dispatch.md` | Normative dispatch contract including the guidance formerly in `bootstrap/dispatch-guide.md`. |
| `ontology/concept/capability-protocol.md` | Owns host-native capability notes formerly in `bootstrap/native-agent-notes.md`. |
| `README.md`, `INSTALL.md` | Sole human-facing overview, use, installation, optional host guidance, and source citations. |
| `tests/test_install.py` | Regression coverage for release control, legacy bindings, dynamic Skill count, ninth export, and safe deletion. |
| `tests/host-acceptance.md` | Host checks updated from eight to catalog-derived entry discovery and the assist read-only behavior. |

### Task 1: Define and validate the single release descriptor

**Files:**
- Create: `release.json`
- Modify: `scripts/common.py`
- Modify: `scripts/build_manifest.py`
- Modify: `tests/test_install.py`

**Interfaces:**
- Consumes: repository files excluding mutable/history roots and `release.json` itself.
- Produces: `RELEASE = "release.json"`; `read_release(root: Path) -> dict`; `verify_release(root: Path, active_only: bool = False) -> dict`; `read_catalog(root: Path) -> list[dict]` whose accepted names are derived from catalog entries.

- [ ] **Step 1: Write failing descriptor tests**

Add tests that build a temporary source release and assert these exact invariants:

```python
release = read_json(source / "release.json")
assert release["schema"] == "pdca.release/v2"
assert "release.json" not in release["files"]
assert release["protocol"]["records_root"] == "PDCA_ROOT/records"
assert release["skill_index"] == "skills/catalog.json"
assert len(read_catalog(source)) == len(release["skills"])
```

Also write negative tests for a self-hashed descriptor, an active member absent from `files`, a `skills` list that disagrees with the catalog names, and a missing required protocol key.

- [ ] **Step 2: Run the new tests to verify failure**

Run: `python3 -m unittest tests.test_install.DefinitionTests -v`

Expected: FAIL because `release.json`, `read_release`, and the new descriptor validation do not exist.

- [ ] **Step 3: Implement `release.json` and common validation**

Create `release.json` with this top-level shape:

```json
{
  "schema": "pdca.release/v2",
  "version": "4.0.0-rc.2",
  "files": {},
  "active": [],
  "skill_index": "skills/catalog.json",
  "skills": [],
  "protocol": {
    "advance_policy": "explicit_user_operation",
    "records_root": "PDCA_ROOT/records",
    "resource_scope": "central_cross_project",
    "legacy_policy": "never_load_as_current_execution",
    "rule_authorities": {}
  }
}
```

Replace `MANIFEST` with `RELEASE = "release.json"` in `scripts/common.py`. Make `read_release` reject missing/extra-invalid structure, `release.json` in `files`, invalid hashes, non-subset `active`, a catalog path other than `skills/catalog.json`, duplicate Skill names, catalog/release name disagreement, and mutable paths. Keep a narrowly scoped `read_legacy_snapshot(root)` that recognizes only an old paired `protocol-release.md`/`release-manifest.md` snapshot for later binding compatibility; do not treat it as current release control.

- [ ] **Step 4: Make the builder generate the descriptor**

Change `build(root)` to calculate `files` and `active` as today, excluding `release.json`, then populate `skills` from `read_catalog(root)` and protocol metadata from a Python constant in `scripts/build_manifest.py`. Write JSON with a trailing newline to `root / "release.json"`. Remove Markdown fence emission.

- [ ] **Step 5: Run descriptor tests to verify success**

Run: `python3 -m unittest tests.test_install.DefinitionTests -v`

Expected: PASS, including new malformed-descriptor tests.

- [ ] **Step 6: Commit**

```bash
git add release.json scripts/common.py scripts/build_manifest.py tests/test_install.py
git commit -m "feat: consolidate release descriptor"
```

### Task 2: Migrate installer, snapshots, and bindings with legacy readability

**Files:**
- Modify: `scripts/install.py`
- Modify: `tests/test_install.py`

**Interfaces:**
- Consumes: `read_release`, `RELEASE`, catalog entries, and an existing `.pdca-install.json` that may have been created by the old format.
- Produces: snapshot path derived from `digest(source / "release.json")`; new project-context fields `release_ref` and `release_digest`; legacy contexts continue to pass `bindings()` validation without mutation.

- [ ] **Step 1: Write failing migration tests**

Add these tests:

```python
context = read_owned_md(Path(tool.register(root, str(project), "p", "main", True)["context_ref"]))
assert Path(context["release_ref"]).name == "release.json"
assert context["release_digest"] == digest(Path(context["release_ref"]).read_bytes())
assert "protocol_baseline_ref" not in context

legacy = make_old_format_snapshot_and_context(root, project)
assert tool.bindings(root) == [legacy]
assert Path(legacy[1]["protocol_baseline_ref"]).exists()
```

Add install/check/update tests that assert `skill_entries == len(read_catalog(source))`, and that upgrading an old-format installation requires `--update`, preserves old snapshots byte-for-byte, and emits a new `release.json` snapshot.

- [ ] **Step 2: Run migration tests to verify failure**

Run: `python3 -m unittest tests.test_install.InstallationTests -v`

Expected: FAIL because installation state, snapshot paths, and binding metadata still refer to `MANIFEST` and `protocol-release.md`.

- [ ] **Step 3: Implement current-release install state and snapshot logic**

Replace every current-release `MANIFEST` lookup with `RELEASE`. `snapshot_path` must use `release["version"]` plus the first 16 hex characters of `release.json`'s SHA-256. Copy `[ *release["files"], RELEASE ]` into the installed root and `[ *release["active"], RELEASE ]` into a new snapshot. Store `release_name`, `release_digest`, and `snapshot` in new installation state; when loading an old state, read its stored `release-manifest.md` digest only to detect that an explicit update is needed.

Set preview/check result `skill_entries` to `len(catalog)`. Iterate catalog names rather than the removed fixed `SKILLS` tuple for install, check, and uninstall.

- [ ] **Step 4: Implement dual binding validation without silent conversion**

For a context with `release_ref`/`release_digest`, require that its `release_ref` is a `release.json` inside `records/protocol`, verify its digest and active release bytes, and obtain its version from `read_release`. For a context with the complete legacy field set, preserve the existing paired-reference checks unchanged. Reject mixed, partial, or unknown formats. `register()` must write only the new fields and must never rewrite an existing legacy context.

- [ ] **Step 5: Run migration tests to verify success**

Run: `python3 -m unittest tests.test_install.InstallationTests -v`

Expected: PASS; no test may report a fixed number of Skill entries.

- [ ] **Step 6: Commit**

```bash
git add scripts/install.py tests/test_install.py
git commit -m "feat: migrate installs to release json"
```

### Task 3: Make release checking catalog-driven and add `$pdca-assist`

**Files:**
- Create: `skills/pdca-assist/SKILL.md`
- Modify: `skills/catalog.json`
- Modify: `skills/README.md`
- Modify: `scripts/check_release.py`
- Modify: `tests/test_install.py`
- Modify: `tests/host-acceptance.md`

**Interfaces:**
- Consumes: a current project context, current `PDCA_ROOT`, the bound `TARGET_ROOT`, and the user’s current request.
- Produces: a read-only report with `现状`, `候选动作`, `影响`, `所需授权`, and `等待用户选择`; no record, task, Agent, phase, or target write is produced before explicit selection.

- [ ] **Step 1: Write failing assistant and dynamic-catalog tests**

Add static assertions that the catalog includes `pdca-assist` once and exports its complete body. Assert the Skill text contains all of the following literals:

```python
for required in (
    "只读", "当前已绑定的 TARGET_ROOT", "不扫描其他项目",
    "用户选择", "不创建任务", "不启动阶段", "不派发 Agent",
):
    self.assertIn(required, assist)
```

Update install and host-acceptance tests to compare entry sets/counts to `read_catalog(ROOT)`, not `8` or `SKILLS`.

- [ ] **Step 2: Run assistant tests to verify failure**

Run: `python3 -m unittest tests.test_install -v`

Expected: FAIL because `pdca-assist` is absent from catalog and export output.

- [ ] **Step 3: Create the explicit workbench Skill**

Write `skills/pdca-assist/SKILL.md` with frontmatter `name: pdca-assist` and `disable-model-invocation: true`. Its procedure must:

```text
1. Locate one bound project and its current release/task context; ambiguity blocks.
2. Read only that project’s central records and, when host permission allows, that TARGET_ROOT’s source, docs, and Git status.
3. Present at most one concise option per lens: task map, context, evidence, collaboration.
4. Mark each option as read-only, record-write, task-create, phase-route, or target-write.
5. Wait for the user’s selection; do not create records, tasks, Agents, reservations, or writes merely from analysis.
```

For selection, direct the user to the existing explicit PDCA entry or request the specific writing authorization; do not invoke a phase or task creation itself.

- [ ] **Step 4: Add the catalog entry and derive all checks from it**

Append a ninth entry whose `name` is `pdca-assist`, `kind` is `entry`, and path is `skills/pdca-assist/SKILL.md`. Remove exact-eight validation and the `SKILLS` constant. In `check_release.py`, verify each catalog source starts with its declared frontmatter name, prohibit automatic Agent declarations in every entry, and require the protocol’s central records-root value from `release["protocol"]`.

- [ ] **Step 5: Update Skill and host documentation**

Add `$pdca-assist` to `skills/README.md` as the explicit suggestion-only workbench. In `tests/host-acceptance.md`, replace “eight” with “catalog-listed”, add a row that observes `$pdca-assist` produces no write before user selection, and preserve `NOT_RUN` status.

- [ ] **Step 6: Run assistant tests to verify success**

Run: `python3 -m unittest tests.test_install -v`

Expected: PASS, and installed discovery directories contain exactly the set in `skills/catalog.json`.

- [ ] **Step 7: Commit**

```bash
git add skills scripts/check_release.py tests/test_install.py tests/host-acceptance.md
git commit -m "feat: add PDCA assist workbench"
```

### Task 4: Move bootstrap rules into their owning contracts

**Files:**
- Create: `ontology/contracts/entry-recovery.md`
- Modify: `ontology/contracts/agent-dispatch.md`
- Modify: `ontology/concept/capability-protocol.md`
- Modify: `skills/pdca/SKILL.md`
- Modify: `skills/pdca-plan/SKILL.md`
- Modify: `skills/pdca-do/SKILL.md`
- Modify: `skills/pdca-check/SKILL.md`
- Modify: `skills/pdca-act/SKILL.md`
- Modify: `skills/pdca-model/SKILL.md`
- Modify: `skills/pdca-implement/SKILL.md`
- Modify: `skills/pdca-verify/SKILL.md`
- Test: `tests/test_install.py`

**Interfaces:**
- Consumes: the existing recovery/dispatch/capability wording in `bootstrap/`.
- Produces: active Skill links only to `ontology/contracts/entry-recovery.md`, `ontology/contracts/agent-dispatch.md`, and `ontology/concept/capability-protocol.md`.

- [ ] **Step 1: Write failing link and semantic-regression tests**

Add tests that scan every catalog Skill and assert no `bootstrap/` link remains, while all phase Skills retain these recovery rules:

```python
assert "原任务" in text
assert "不可路由就阻断" in text
assert "不创建项目本地 .pdca" in text
assert "不自动切换" in text
```

Add direct-link assertions for the three destination documents.

- [ ] **Step 2: Run migration-link tests to verify failure**

Run: `python3 -m unittest tests.test_install.DefinitionTests -v`

Expected: FAIL because current Skills link into `bootstrap/`.

- [ ] **Step 3: Create the recovery contract and consolidate dispatch**

Move the complete five-step recovery/routing protocol from `bootstrap/entry-check.md` into `ontology/contracts/entry-recovery.md` with `schema: pdca.contract/v4`. Merge the operational dispatch paths from `bootstrap/dispatch-guide.md` into `ontology/contracts/agent-dispatch.md`, replacing its reference to bootstrap. Preserve all stop conditions: no parent monitoring, no substitute Agent on recovery failure, no automatic phase action, and retained ownership on unknown creation.

- [ ] **Step 4: Move native capability guidance and update all links**

Append the host capability verification table and its “do not guess tool names” constraint to `ontology/concept/capability-protocol.md`. Change all phase/scene Skill recovery links to `../../ontology/contracts/entry-recovery.md`; change all dispatch links to `../../ontology/contracts/agent-dispatch.md`; change any native-note link to `ontology/concept/capability-protocol.md`. Do not leave duplicated normative text in Skills.

- [ ] **Step 5: Run migration-link tests to verify success**

Run: `python3 -m unittest tests.test_install.DefinitionTests -v`

Expected: PASS with no active `bootstrap/` reference.

- [ ] **Step 6: Commit**

```bash
git add ontology skills tests/test_install.py
git commit -m "refactor: move bootstrap rules into contracts"
```

### Task 5: Consolidate human documentation and remove obsolete files

**Files:**
- Modify: `README.md`
- Modify: `INSTALL.md`
- Modify: `migration/v4.0.0-rc.2-MIGRATION.md`
- Modify: `tests/test_install.py`
- Delete: `SKILL.md`
- Delete: `USE-PDCA.md`
- Delete: `protocol-release.md`
- Delete: `release-manifest.md`
- Delete: `bootstrap/dispatch-guide.md`
- Delete: `bootstrap/entry-check.md`
- Delete: `bootstrap/global-entry.md`
- Delete: `bootstrap/install-sources.md`
- Delete: `bootstrap/native-agent-notes.md`
- Delete: `bootstrap/work-methods.md`

**Interfaces:**
- Consumes: the migration destination documents completed in Tasks 1–4.
- Produces: no current link/reference to any deleted path; README is the overview/use guide and INSTALL is install/update/uninstall/optional-host guidance.

- [ ] **Step 1: Write failing absence and content-preservation tests**

Add a test with these exact assertions:

```python
for removed in (
    "SKILL.md", "USE-PDCA.md", "protocol-release.md", "release-manifest.md", "bootstrap",
):
    self.assertFalse((ROOT / removed).exists())

readme = (ROOT / "README.md").read_text()
install = (ROOT / "INSTALL.md").read_text()
self.assertIn("PDCA_ROOT", readme)
self.assertIn("TARGET_ROOT", readme)
self.assertIn("release.json", install)
```

Add an `rg`-backed release test that rejects every deleted-path string in active files, except a clearly labeled legacy-compatibility branch in installer code and the migration document’s historical-description section.

- [ ] **Step 2: Run documentation-removal tests to verify failure**

Run: `python3 -m unittest tests.test_install.DefinitionTests -v`

Expected: FAIL because the obsolete files still exist and current links still target them.

- [ ] **Step 3: Merge user-facing content before deletion**

Move the dual-root model, registration, locating, phase/scene distinction, recovery, resource boundaries, and no-project-write rules from `USE-PDCA.md` into focused sections in `README.md` and `INSTALL.md`. Move optional global-host guidance and installation source citations into `INSTALL.md`. Update every README link to the new locations and replace static entry-count prose with “catalog-listed entries.”

- [ ] **Step 4: Delete only migrated or dead material**

Delete the listed files only after Step 3 and Task 4 links are complete. Remove root-Skill compatibility references from the migration note; preserve only the factual statement that prior releases may contain old snapshot filenames. Do not delete any old files inside installed `records/protocol` snapshots.

- [ ] **Step 5: Rebuild release control and run absence checks**

Run:

```bash
python3 scripts/build_manifest.py .
rg -n 'bootstrap/|USE-PDCA\.md|protocol-release\.md|release-manifest\.md|^SKILL\.md$' \
  README.md INSTALL.md skills ontology scripts tests migration || true
python3 -m unittest tests.test_install.DefinitionTests -v
```

Expected: the search output contains only documented legacy parser/migration text; the test suite passes.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "refactor: consolidate PDCA release structure"
```

### Task 6: Run the full verification and record real limits

**Files:**
- Modify: `release.json`
- Modify: `README.md`
- Modify: `INSTALL.md`
- Modify: `tests/host-acceptance.md`

**Interfaces:**
- Consumes: completed Tasks 1–5.
- Produces: a regenerated descriptor whose hashes match source bytes and documentation that distinguishes static verification from host acceptance.

- [ ] **Step 1: Rebuild the release descriptor**

Run: `python3 scripts/build_manifest.py .`

Expected: `release.json` is regenerated; it lists every releasable source file except itself and includes `pdca-assist` through the catalog-derived `skills` field.

- [ ] **Step 2: Run the complete unit suite**

Run: `python3 -m unittest discover -s tests -v`

Expected: PASS. A failure involving a removed filename is fixed by migrating the active reference or legacy test fixture, never by restoring the obsolete current-release file.

- [ ] **Step 3: Run current-release consistency verification**

Run: `python3 scripts/check_release.py .`

Expected: JSON with `"passed": true`, a catalog-derived `skill_entries` count, and `"host_acceptance": "NOT_RUN"`.

- [ ] **Step 4: Review the release diff and removed-path proof**

Run:

```bash
git diff --check HEAD~1
git status --short
rg -n 'bootstrap/|USE-PDCA\.md|protocol-release\.md|release-manifest\.md' \
  README.md INSTALL.md skills ontology scripts tests migration || true
```

Expected: no whitespace errors, no unaccounted working-tree files, and only expressly documented legacy compatibility references.

- [ ] **Step 5: Commit verification and descriptor bytes**

```bash
git add release.json README.md INSTALL.md tests/host-acceptance.md
git commit -m "test: verify consolidated PDCA release"
```

## Plan Self-Review

- Spec coverage: Tasks 1–2 implement the one-descriptor model and historical binding compatibility; Task 3 implements the explicit read-only AI workbench and catalog-driven discovery; Tasks 4–5 remove bootstrap and redundant root documentation only after content migration; Task 6 verifies static behavior and preserves the `NOT_RUN` host-acceptance boundary.
- Placeholder scan: no deferred implementation markers are present; every task defines paths, interfaces, executable test commands, expected failure/pass state, and a commit.
- Type consistency: all current-release code uses `RELEASE`, `read_release`, `release_ref`, and `release_digest`; legacy handling is intentionally limited to old paired snapshot references.
