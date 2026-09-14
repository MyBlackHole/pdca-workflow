# PDCA Git Installation and Assistant Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the copy/snapshot installer with a safe Git-clone plus Skills-directory symlink installer, add `$pdca-assist`, and remove superseded package layers.

**Architecture:** `~/.agents/pdca` is the Git-managed `PDCA_ROOT`; `install.sh` only checks both targets, clones once, and makes `~/.agents/skills` point at its `skills/` directory. `$pdca` owns user-approved central binding records and records Git state; `$pdca-assist` is an explicit, read-only suggestions surface. No release manifest, copied snapshot, installer state, or automatic Git action remains.

**Tech Stack:** POSIX shell, Git, Markdown Agent Skills, Python 3.10 `unittest`.

**Spec:** `docs/superpowers/specs/2026-09-14-pdca-ai-work-assistant-design.md`

## Global Constraints

- Do not overwrite, merge into, delete, or otherwise modify an existing `~/.agents/pdca` or `~/.agents/skills` during installation.
- Check both destination paths before `git clone`; a rejected installation leaves no newly created central root.
- No script writes a business project, creates a binding, runs a Git update, or executes `git add`, `git commit`, checkout, reset, stash, or pull.
- Record writes and Git commits require separate, explicit user authorization.
- Remove `records/` and `ontology/projects/` from `.gitignore`; keep only private evidence and local-secret exclusions so centralized records are reviewable Git data.
- Retain the existing eight Skill semantics, original-Agent continuity, and explicit user initiation of every phase.
- `$pdca-assist` reads only one bound project’s central records and permitted `TARGET_ROOT` source/docs/Git state; it makes no writes or phase transitions while advising.
- Delete only the exact obsolete files named in the spec after all active links and tests have moved; leave `legacy/` and reference-knowledge directories untouched.
- Use TDD. Run `python3 -m unittest discover -s tests -v` before each task commit and preserve `NOT_RUN` for unperformed host acceptance.

---

### Task 1: Add a safe one-command Git installer

**Files:**
- Create: `install.sh`
- Create: `tests/test_install_script.py`
- Modify: `INSTALL.md`

**Interfaces:**
- `install.sh` consumes `HOME`, `PATH`, and Git; it clones `https://github.com/MyBlackHole/pdca-workflow.git` into `$HOME/.agents/pdca` and creates `$HOME/.agents/skills -> $HOME/.agents/pdca/skills`.
- Exit status is nonzero before clone if Git is unavailable, `$HOME/.agents/pdca` exists, or `$HOME/.agents/skills` exists.

- [ ] **Step 1: Write failing shell-installer tests**

Create `tests/test_install_script.py` using `tempfile.TemporaryDirectory`. Build a fake executable `git` in a temporary `bin/` that records `clone` arguments and creates the requested destination. Invoke `install.sh` with a temporary `HOME` and that `PATH`. Assert:

```python
self.assertEqual(result.returncode, 0, result.stderr)
self.assertTrue((home / '.agents/pdca/.git').is_dir())
self.assertEqual((home / '.agents/skills').resolve(), home / '.agents/pdca/skills')
self.assertIn('clone https://github.com/MyBlackHole/pdca-workflow.git', git_log.read_text())
```

Add separate tests that pre-create central root or discovery path and assert nonzero exit, no Git invocation, and no newly created sibling path.

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest tests.test_install_script -v`

Expected: FAIL because `install.sh` does not exist.

- [ ] **Step 3: Implement the minimal installer**

Write POSIX shell with `set -eu`. Define `pdca_root="$HOME/.agents/pdca"` and `skills_dir="$HOME/.agents/skills"`; use `command -v git`; test both paths with `[ -e "$path" ] || [ -L "$path" ]` before `mkdir -p "$HOME/.agents"`, `git clone`, and `ln -s`. Print the exact root, link, `$pdca` entry point, and manual `git -C "$pdca_root" pull` update command. Do not add an uninstall or update mode.

- [ ] **Step 4: Verify GREEN and document**

Run: `python3 -m unittest tests.test_install_script -v`

Expected: PASS. Update `INSTALL.md` to use the `curl -fsSL ... | bash` command, explain both refusal cases, Git-managed updates, and required host reload.

- [ ] **Step 5: Commit**

```bash
git add install.sh tests/test_install_script.py INSTALL.md
git commit -m "feat: add Git clone installer"
```

### Task 2: Move active rules out of bootstrap and record formats into contracts

**Files:**
- Create: `ontology/contracts/entry-recovery.md`
- Create: `ontology/contracts/record-shapes/project-task-context.md`
- Create: `ontology/contracts/record-shapes/agent-assignment.md`
- Create: `ontology/contracts/record-shapes/dispatch.md`
- Create: `ontology/contracts/record-shapes/capability-check.md`
- Create: `ontology/contracts/record-shapes/evidence.md`
- Create: `ontology/contracts/record-shapes/conclusion.md`
- Create: `ontology/contracts/record-shapes/resource-reservation.md`
- Create: `ontology/contracts/record-shapes/operation.md`
- Create: `ontology/contracts/record-shapes/ontology-revision.md`
- Modify: `ontology/contracts/agent-dispatch.md`
- Modify: `ontology/concept/capability-protocol.md`
- Modify: `ontology/contracts/record-shapes/*.md`
- Modify: all eight existing `skills/*/SKILL.md`
- Modify: `ontology/concept/pdca.md`
- Modify: `.gitignore`
- Test: `tests/test_skill_links.py`

**Interfaces:**
- Every current Skill links only to current `skills/`, `ontology/`, and `records/` guidance; no link targets `bootstrap/` or `templates/`.
- Record-shape contracts contain the canonical fields and a compact Markdown example formerly supplied by each active template.

- [ ] **Step 1: Write failing link/contract tests**

Create `tests/test_skill_links.py`. Walk `skills/**/SKILL.md` and only current ontology documents (`schema: pdca.contract/v4` or `authority: normative`), resolve relative Markdown links, and assert they exist. Assert no text contains `bootstrap/` or `templates/`. Use an explicit map from each former current template to its record-shape contract; create the nine absent shapes listed above. For every mapped contract, assert it contains `示例` and the old schema identifier.

Copy the existing non-installer safety assertions from `tests/test_install.py` into this file: all phase Skills retain original-Agent/no-spawn behavior; scene Skills do not recursively create tasks; resource ownership forbids timeout release and parent supervision; and every phase remains user-controlled. Add assertions that `.gitignore` does not ignore `records/` or `ontology/projects/`, while private evidence remains ignored.

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest tests.test_skill_links -v`

Expected: FAIL because current Skills reference bootstrap and current templates remain separate.

- [ ] **Step 3: Move rules and examples**

Move the full recovery method to `ontology/contracts/entry-recovery.md`; merge dispatch procedure into `ontology/contracts/agent-dispatch.md`; merge native capability table into `ontology/concept/capability-protocol.md`. Copy each of the 18 current template bodies into the corresponding record-shape contract under `## 示例`, retaining its current schema and required fields. Change all links to those owning files. Remove the two broad mutable-data exclusions from `.gitignore` but retain exclusions for `records/**/artifacts/private/`, `records/projects/**/private/`, local installation leftovers, bytecode, and secrets.

- [ ] **Step 4: Verify GREEN**

Run: `python3 -m unittest tests.test_skill_links -v`

Expected: PASS with no current bootstrap/template link.

- [ ] **Step 5: Commit**

```bash
git add ontology skills tests/test_skill_links.py
git commit -m "refactor: consolidate PDCA rules and record formats"
```

### Task 3: Add explicit Git-aware binding and assistance Skills

**Files:**
- Create: `skills/pdca-assist/SKILL.md`
- Modify: `skills/pdca/SKILL.md`
- Modify: `skills/catalog.json`
- Modify: `skills/README.md`
- Modify: `tests/host-acceptance.md`
- Modify: `tests/test_skill_links.py`

**Interfaces:**
- A project context written by `$pdca` includes `project_id`, `workspace_id`, `target_root`, `pdca_root`, `records_root`, `rules_git_head`, and `rules_git_status`.
- `$pdca-assist` produces four labelled suggestion lenses and waits for a user selection.

- [ ] **Step 1: Write failing static tests**

Extend `tests/test_skill_links.py` to assert catalog includes exactly one `pdca-assist` path and that its text includes `当前已绑定的 TARGET_ROOT`, `不扫描其他项目`, `用户选择`, `不创建任务`, `不启动阶段`, and `不派发 Agent`. Assert `$pdca` includes separate wording for record-write authorization and Git-commit authorization, `git rev-parse HEAD`, and `git status --porcelain`.

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest tests.test_skill_links -v`

Expected: FAIL because the ninth Skill and Git-aware binding instructions are absent.

- [ ] **Step 3: Implement Skill guidance**

Add `pdca-assist` to the catalog and index. Write its explicit-only Skill procedure: identify one binding, report Git state, read only bound records and permitted target files, show at most one candidate for each of task/context/evidence/collaboration with impact and required authorization, then stop. Update `$pdca` to create/locate central bindings only after explicit record-write consent, capture Git HEAD/status in the context, and request a separate confirmation before any Git commit. It must never invoke Git mutation automatically.

- [ ] **Step 4: Update host acceptance**

Replace static “eight entries” text with catalog-listed entries; add `pdca-assist` verification that no record, Agent, phase, reservation, or target write happens before user selection. Keep every status `NOT_RUN`.

- [ ] **Step 5: Verify GREEN and commit**

Run: `python3 -m unittest tests.test_skill_links -v`

Expected: PASS.

```bash
git add skills tests/test_skill_links.py tests/host-acceptance.md
git commit -m "feat: add Git-aware PDCA assistant"
```

### Task 4: Delete the superseded package layers and verify final tree

**Files:**
- Modify: `README.md`
- Modify: `INSTALL.md`
- Modify: `tests/README.md`
- Delete: `setup`, `scripts/install.py`, `scripts/common.py`, `scripts/build_manifest.py`, `scripts/check_release.py`, `tests/test_install.py`
- Delete: `release-manifest.md`, `protocol-release.md`, `SKILL.md`, `USE-PDCA.md`, `migration/v4.0.0-rc.2-MIGRATION.md`
- Delete: `bootstrap/`
- Delete: `templates/`
- Test: `tests/test_skill_links.py`, `tests/test_install_script.py`

**Interfaces:**
- README is the sole overview/use guide; INSTALL is the sole install/update/discovery guide.
- No current Markdown link names any deleted path.

- [ ] **Step 1: Write failing absence tests**

Add assertions for each deleted root path and both deleted directories:

```python
for rel in ('setup', 'scripts/install.py', 'release-manifest.md', 'protocol-release.md',
            'SKILL.md', 'USE-PDCA.md', 'bootstrap', 'templates'):
    self.assertFalse((ROOT / rel).exists())
```

In the same test, walk active Markdown and fail on relative links resolving to a deleted path.

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest tests.test_skill_links -v`

Expected: FAIL because the legacy layers still exist.

- [ ] **Step 3: Consolidate docs then delete**

Move dual-root use, project binding, phase routing, Git write/commit authorization, and host guidance from obsolete guides into README/INSTALL. Remove every stale install/snapshot/template reference. Delete exactly the listed obsolete files and directories; do not touch `legacy/`, `ontology/domain/`, `ontology/entity/`, `ontology/fact/`, `ontology/pattern/`, `ontology/pitfall/`, or `ontology/decision/`.

- [ ] **Step 4: Verify the final package**

Run:

```bash
python3 -m unittest discover -s tests -v
rg -n 'bootstrap/|templates/|release-manifest\.md|protocol-release\.md|USE-PDCA\.md' README.md INSTALL.md skills ontology tests || true
git diff --check
```

Expected: all tests pass, the search has no current-reference hits, and no whitespace errors exist.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor: simplify PDCA Git distribution"
```

## Plan Self-Review

- Spec coverage: Task 1 implements clone/link installation and refusal behavior; Task 2 removes bootstrap/template duplication; Task 3 delivers Git-aware binding and read-only assistance; Task 4 deletes only approved layers and runs the mandatory suite.
- Placeholder scan: every task declares concrete files, red/green commands, expected outcomes, and a commit.
- Interface consistency: Tasks 2 and 3 remove links before Task 4 deletes their targets; Task 1 is independent of deleted installer code; no task mutates Git automatically.
