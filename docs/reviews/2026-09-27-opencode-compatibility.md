# OpenCode v1.18.32 compatibility review

日期：2026-09-27

这是维护级宿主兼容性审查，不是 H1/H11/H18 正式现场验收。

## Tested version and artifact

- OpenCode: `v1.18.32`
- Linux x64 archive: `opencode-linux-x64.tar.gz`
- verified SHA-256: `3046e0404fdc60fb80307e7a47824ba07477364178a4d09baa8548496dd6d43b`
- GitHub Actions workflow run: `36317199256`
- job: `108614035021`

## Installation path under test

The workflow uses an isolated HOME and executes this repository's real `install.sh`.

Expected runtime layout:

```text
~/.agents/pdca/
  skills/<name>/SKILL.md

~/.agents/skills/
  pdca -> ~/.agents/pdca/skills/pdca
  pdca-assist -> ~/.agents/pdca/skills/pdca-assist
  ...
  pdca-verify -> ~/.agents/pdca/skills/pdca-verify
```

The installer step completed successfully and all nine symlinks resolved to readable nonempty `SKILL.md` files.

## Source-level compatibility check

OpenCode `v1.18.32` source was checked before interpreting the runtime result:

- `packages/opencode/src/skill/index.ts` scans global `~/.agents/skills/**/SKILL.md` when external skills are enabled;
- the scan uses `symlink: true` / glob `follow: true`;
- `packages/opencode/src/cli/cmd/debug/skill.ts` directly calls `Skill.all()` and prints the loaded Skill objects;
- official docs for the same tag list `~/.agents/skills/<name>/SKILL.md` as a supported global discovery location.

Therefore the repository's centralized checkout + runtime Skill links are aligned with OpenCode's documented and implemented CLI discovery model.

## CLI result — PASS for discovery/parse scope

The compatibility gate runs:

`opencode debug skill`

and checks the returned Skill objects, not only filesystem paths.

All nine expected PDCA runtime Skills were discovered:

- `pdca`
- `pdca-assist`
- `pdca-plan`
- `pdca-do`
- `pdca-check`
- `pdca-act`
- `pdca-model`
- `pdca-implement`
- `pdca-verify`

For every Skill the smoke verifies:

- nonempty `description`;
- OpenCode-reported location under `~/.agents/skills/<name>/SKILL.md`;
- the `pdca` object contains the actual body marker `PDCA：定位、绑定与运行入口分流`.

This proves, for OpenCode v1.18.32 on the tested Linux Actions environment:

```text
PDCA install.sh
  -> ~/.agents/skills runtime links
  -> OpenCode CLI discovery
  -> SKILL.md parse
  -> actual Skill content loaded
```

## Headless server diagnostic — not a compatibility gate

`opencode serve` starts successfully and `/api/health` reports healthy.

However, in the same Actions environment, instance-scoped `/api/skill` only exposed OpenCode's built-in `customize-opencode` Skill and did not expose the external PDCA Skills, even when:

- external-skill disable flags were explicitly false;
- `x-opencode-directory` was supplied;
- real directories were tested instead of symlink directories;
- explicit `skills.paths` was tested.

Because the direct CLI `Skill.all()` path succeeds while this headless API path does not, the review does **not** reinterpret the API behavior as an installer failure.

The server endpoint is retained as a non-gating diagnostic until its instance/config behavior is separately understood.

## Provider boundary

The workflow explicitly checks only credential presence by environment-variable name and does not consume repository secrets.

Current run reported:

`No provider credential is present in this job.`

Therefore the following were not executed:

- model inference;
- native interactive Agent reasoning;
- fresh-Agent semantic recovery;
- real Plan/Do/Check/Act interaction;
- H11;
- H18.

## Acceptance interpretation

This review supports a narrow compatibility statement:

> OpenCode v1.18.32 CLI can discover and parse all nine PDCA runtime Skills installed by this repository's current `install.sh` layout.

It does **not** support:

- H1 PASS, because H1 requires a real OpenCode/Codex new-session discovery interaction, not `debug skill` alone;
- H11/H18 PASS;
- headless server/session compatibility;
- provider/model compatibility;
- original-Agent continuation semantics.

Accordingly H1–H18 remain unchanged (`NOT_RUN`) unless separately supported by actual host evidence.
