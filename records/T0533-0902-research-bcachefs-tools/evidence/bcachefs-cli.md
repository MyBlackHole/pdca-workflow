---
schema: pdca.asset/v1
id: ontology:entity/bcachefs-cli
type: entity
layer: Knowledge
status: active
summary: bcachefs CLI 实体 — COMMAND_GROUPS 8 组 >35 leaf、CmdKind 三形态（typed/raw/group）与 dispatch/symlink 及 Cargo/Make/DKMS 三构建
relations:
  specializes:
    - ontology:concept/domain-entity
  relates_to:
    - ontology:pattern/research-diagram-methodology
    - ontology:pattern/production-ontology-scientific-gate
    - ontology:pattern/scientific-research-methodology
attributes:
  - name: command_groups_and_cmdkind
    desc: COMMAND_GROUPS 8 组 >35 leaf（CmdDef { name/about/kind } + CmdKind typed/raw/group + typed_cmd!/raw_cmd! 宏）与 Group 子命令分发可测
    constraint: 覆盖 src/commands/mod.rs:12 的 CmdDef/CmdKind + 52 typed_cmd! + 70 raw_cmd! + 234 COMMAND_GROUPS 8 组 + 133 dispatch_with_path 按 Group 递归分发 + 209 defers_shrinkers 对 mount/fusemount，经 C4 L3 与决策树可一图建模
    testable_signal: "运行 grep -q 'COMMAND_GROUPS' /home/black/Documents/bcachefs-tools/src/commands/mod.rs && grep -q 'CmdKind' /home/black/Documents/bcachefs-tools/src/commands/mod.rs && grep -q 'typed_cmd' /home/black/Documents/bcachefs-tools/src/commands/mod.rs 且 grep -q 'cli' records/T0533-0902-research-bcachefs-tools/research-report.md 命中"
  - name: dispatch_and_symlink_shunt
    desc: dispatch 总线（dispatch/matches/clap_command/build_cli）与 symlink 分流（mkfs/fsck/mount/fusemount → format/fsck/mount/fusemount）及 usage 分组打印可测
    constraint: 覆盖 src/bcachefs.rs:263 的 main() 中 symlink 判 mkfs/fsck/mount/fusemount + missing/--help 分支 + raid_init + defers_shrinkers + 未知命令→usage 分组打印，经时序与状态机可一图建模
    testable_signal: "运行 grep -q 'symlink' /home/black/Documents/bcachefs-tools/src/bcachefs.rs && grep -q 'dispatch' /home/black/Documents/bcachefs-tools/src/commands/mod.rs && grep -q 'bcachefs_usage' /home/black/Documents/bcachefs-tools/src/bcachefs.rs 且 grep -q 'cli' records/T0533-0902-research-bcachefs-tools/research-report.md 命中"
  - name: cargo_make_dkms_tri_build
    desc: Cargo workspace（resolver2 + members 6）与 Make（VERSION:= + DKMSDIR + SRCS→libbcachefs.a）及 DKMS（dkms.conf/Make + 6.16）三构建联动可测
    constraint: 覆盖 Cargo.toml:1 [workspace] resolver2 + members [.,fs,shim,bindgen,docgen] + Makefile:13 VERSION:=git describe --dirty + 22 DKMSDIR + 240 SRCS→AR + bch_bindgen/build.rs:404 x-macro + fs/build.rs:1 watch_dir + -rdynamic，经 C4 L3 与时序可一图建模
    testable_signal: "运行 grep -q 'workspace' /home/black/Documents/bcachefs-tools/Cargo.toml && grep -q 'VERSION:=' /home/black/Documents/bcachefs-tools/Makefile && grep -q 'bch_bindgen' /home/black/Documents/bcachefs-tools/Cargo.toml 且 grep -q 'cli' records/T0533-0902-research-bcachefs-tools/research-report.md 命中"
---

# Bcachefs CLI（命令行框架）

CLI 为 `bcachefs` 单一二进制的 `COMMAND_GROUPS`（`src/commands/mod.rs:234` 8 组 >35 leaf）分发总线：`CmdDef { name/about/aliases/kind }` 持 `CmdKind::{Typed(Raw)/Group}`，`typed_cmd!`（`52`）/ `raw_cmd!`（`70`）宏生成 `__cmd/__run`，`dispatch_with_path`（`133`）按 `Group` 递归，`bch_bindgen/build.rs:404` + `fs/build.rs:1` 支撑 `build.rs:1 -rdynamic` 链接 `libbcachefs.a`，`Cargo workspace + Make + DKMS` 三构建。定位：`src/bcachefs.rs:263 main() → commands/mod.rs:234 → bch_bindgen/build.rs + fs/build.rs → Makefile:240`。

## C4 L3 Component — CmdDef/CmdKind + COMMAND_GROUPS + dispatch + 三构建

`CmdDef`（`mod.rs:12`）含 `name/about/aliases/kind`，`CmdKind`（`19`）分 `Typed{ cmd:fn()->Command, run:fn(Vec<String>)->ExitCode } / Raw{ run } / Group{ children: &[&CmdDef] }`；`COMMAND_GROUPS`（`234`）8 组：`Superblock(6: format/super/...)/Images/Mount(3: mount/fusemount/wait_devices)/Repair(4: fsck/rewind/recovery)/Running fs(1 group fs→4)/Devices/Subvol(1)/Fs data(2)/Encryption(3)/Migrate(2)/File opts(3)/Debug(8: dump/list/kill...)/Misc(2: completions/version)`；`Cargo.toml:1` `resolver="2"` + `Makefile:13 VERSION:=` + `bch_bindgen/build.rs:404` 生成 `extern.c`。C4 L3 图以 `CmdDef/CmdKind → COMMAND_GROUPS(8) → dispatch(Group递归) → symlink分流 → 三构建` 五层呈现。

```mermaid
graph TD
    DEF["CmdDef/CmdKind<br/>mod.rs:12/19<br/>Typed/Raw/Group"]
    DEF --> MACRO["typed_cmd!<br/>52  raw_cmd! 70"]
    MACRO --> GROUPS["COMMAND_GROUPS 8<br/>mod.rs:234<br/>>35 leaf"]
    GROUPS --> DISP["dispatch_with_path<br/>133 Group递归"]
    DISP --> SYM["symlink 分流<br/>bcachefs.rs:288<br/>mkfs→format/fsck→fsck"]
    SYM --> USAGE["bcachefs_usage<br/>按 Group 分组打印"]
    GROUPS --> CARGO["Cargo workspace<br/>Cargo.toml:1 resolver2"]
    CARGO --> MAKE["Make<br/>Makefile:13 VERSION:="]
    MAKE --> BIND["bch_bindgen 404<br/>fs/build 1<br/>-rdynamic libbcachefs.a"]
    %% Source: /home/black/Documents/bcachefs-tools/src/commands/mod.rs:12 + src/commands/mod.rs:234 + src/bcachefs.rs:263 + Cargo.toml:1 + Makefile:13
```

Source: `/home/black/Documents/bcachefs-tools/src/commands/mod.rs:12`（`CmdDef`）+ `/home/black/Documents/bcachefs-tools/src/commands/mod.rs:19`（`CmdKind`）+ `/home/black/Documents/bcachefs-tools/src/commands/mod.rs:52`（`typed_cmd!`）+ `/home/black/Documents/bcachefs-tools/src/commands/mod.rs:234`（`COMMAND_GROUPS` 8 组）+ `/home/black/Documents/bcachefs-tools/src/bcachefs.rs:263`（`symlink + usage`）+ `/home/black/Documents/bcachefs-tools/Cargo.toml:1` + `/home/black/Documents/bcachefs-tools/Makefile:13`

## 时序 — main → symlink → dispatch → Group 递归 → run

1) `bcachefs` 或 `mkfs.bcachefs`（`symlink`）进 `main:263` 复 `SIGPIPE`、置 `setvbuf`、调 `raid_init`；2) `symlink` 判 `mkfs→format/fsck→fsck/mount→mount/fusemount`，`--help` 进 `bcachefs_usage` 按 `COMMAND_GROUPS` 分组打印；3) `commands::dispatch(name, argv)` 遍历 `COMMAND_GROUPS` 找 `matches`；4) `CmdDef::dispatch`→`dispatch_with_path` 若 `Group` 则按 `argv[1]` 匹配 `children` 递归；5) `Typed` 经 `clap::Parser::parse_from` 后 `run`，`Raw` 直调 `run`；6) `defers_shrinkers` 决定 `mount/fusemount` 延迟 `linux_shrinkers_init`。时序图以 `main → symlink → dispatch → Group递归 → Typed/Raw run` 全链呈现。

```mermaid
sequenceDiagram
    participant M as main:263
    participant S as symlink 判
    participant D as dispatch
    participant G as Group 递归
    participant R as Typed/Raw run
    M->>S: mkfs/fsck/mount?</br>→ format/fsck/mount
    S->>D: dispatch(name,argv)
    D->>D: 遍历 COMMAND_GROUPS matches
    D->>G: Group? 按 argv[1] 递归 children
    G->>R: Typed: clap parse_from→run<br/>Raw: 直调 run
    R-->>M: ExitCode
    %% Source: /home/black/Documents/bcachefs-tools/src/bcachefs.rs:263 + src/commands/mod.rs:133 + src/commands/mod.rs:188
```

Source: `/home/black/Documents/bcachefs-tools/src/bcachefs.rs:263`（`main + symlink + usage`）+ `/home/black/Documents/bcachefs-tools/src/commands/mod.rs:133`（`dispatch_with_path`）+ `/home/black/Documents/bcachefs-tools/src/commands/mod.rs:188`（`dispatch`）

## 状态机 — symlink 与 Group 分发

`symlink` 四态 `bcachefs → mkfs/fsck/mount/fusemount`：按 `args[0] contains` 映射 `format/fsck/mount/fusemount`。`help` 三态 `missing → usage → success`：`None` 打印 `missing command + usage` 返 1，`--help` 返 0。`dispatch` 四态 `match → Group → leaf → run`：`Group` 缺 `subcmd` 时打印 `Commands:` 并按 `help` 与否返 0/1。`build` 二态 `Cargo → Make`：`SRCS` 改动即 `cargo build --release -rdynamic` 重链。状态机图覆盖 `symlink→Group→run` 与 `help` 分支。

```mermaid
stateDiagram-v2
    [*] --> Main: bcachefs / mkfs.bcachefs
    Main --> Symlink: args[0] contains mkfs/fsck/mount
    Symlink --> Format: mkfs→format
    Symlink --> Fsck: fsck→fsck
    Symlink --> Mount: mount→mount/fusemount
    Main --> Help: --help/missing
    Help --> Usage: bcachefs_usage 按 Group 打印
    Usage --> [*]
    Main --> Dispatch: dispatch(name,argv)
    Dispatch --> Group: Group + argv[1] 匹配 children
    Group --> Leaf: Typed/Raw
    Leaf --> Run: clap parse 或直调
    Run --> [*]
    %% Source: /home/black/Documents/bcachefs-tools/src/bcachefs.rs:263 + src/commands/mod.rs:133
```

Source: `/home/black/Documents/bcachefs-tools/src/bcachefs.rs:263` + `/home/black/Documents/bcachefs-tools/src/commands/mod.rs:133` + `/home/black/Documents/bcachefs-tools/src/commands/mod.rs:188`

## 决策树

```mermaid
flowchart TD
    START(["bch2_install_fatal_handlers<br/>+ SIGPIPE 复位"]) --> Q1{"args[0] 含 mkfs/fsck/mount?"}
    Q1 -- 是 --> SYM["symlink 映射<br/>mkfs→format"]
    Q1 -- 否 --> Q2{"args[1] 为 --help/missing?"}
    Q2 -- 是 --> U["bcachefs_usage<br/>COMMAND_GROUPS 分组"]
    Q2 -- 否 --> DISP["dispatch 遍历 matches"]
    SYM --> DISP
    U --> END1(["Exit 0/1"])
    DISP --> Q3{"命中 Group?"}
    Q3 -- 是 --> G["按 argv[1] 递归 children"]
    Q3 -- 否 --> Q4{"Typed 还是 Raw?"}
    G --> Q4
    Q4 -- Typed --> CLAP["clap parse_from → run"]
    Q4 -- Raw --> RAW["直调 run(argv)"]
    CLAP & RAW --> END2(["ExitCode"])
    %% Source: /home/black/Documents/bcachefs-tools/src/bcachefs.rs:263 + src/commands/mod.rs:133
```

Source: `/home/black/Documents/bcachefs-tools/src/bcachefs.rs:263` + `/home/black/Documents/bcachefs-tools/src/commands/mod.rs:133` + `/home/black/Documents/bcachefs-tools/build.rs:1`

## 正例

```c
// 正例：多组分发 + symlink
mkfs.bcachefs /dev/sda           // symlink → format (per-device)
bcachefs fs usage /mnt            // Group fs → fs_usage::CMD
bcachefs device add /mnt /dev/sdc // Group device → add
bcachefs dump --help              // Typed: clap 派生 help 按 COMMAND_GROUPS 分组
// 验证：symlink 与 Group 递归配对，Typed/Raw 分工正确
```

命中：`symlink` 与 `format/fsck` 配对，`Group` 与 `children` 配对，`Typed/Raw` 与 `clap` 配对。

## 反例

```c
// 反例1：Group 缺 subcmd 仍返 0
// 错：bcachefs fs (无子命令) 静默成功
// 正确：Group 无匹配时打印 Commands: 并按 --help 与否返 0/1（mod.rs:154）

// 反例2：per-device 误用 clap 全局
// 错：format 用 clap 导致 --label 全局生效
// 正确：format 手工解析按裸 path 边界累积 DevOpts（format.rs:1 注释）
```

## 门禁

- **多图门禁**：`grep -c '```mermaid' ontology/entity/bcachefs-cli.md` ≥3
- **溯源门禁**：`grep -c 'Source:' ontology/entity/bcachefs-cli.md` ≥3 且每图含 `Source: /home/black/Documents/bcachefs-tools/... file:line`
- **正文门禁**：`wc -l ontology/entity/bcachefs-cli.md` ≥80 且含 `决策树` `正例` `反例` `门禁`
- **属性门禁**：`attributes` ≥3 且每条 `testable_signal` 含 `grep -q` 且双源可回归
- **本体校验**：`python3 scripts/ontology-validate.py` 0 issues 且 `islands:0`
- **脚手架门禁**：`python3 scripts/ontology_test_scaffold.py --node ontology:entity/bcachefs-cli --out /tmp/x.py` 可产
- **Gate 门禁**：`python3 scripts/production-ontology-gate.py --node ontology:entity/bcachefs-cli` GATE OK

Source: `/home/black/Documents/bcachefs-tools/src/commands/mod.rs:12` + `/home/black/Documents/bcachefs-tools/src/bcachefs.rs:263` + `/home/black/Documents/bcachefs-tools/Cargo.toml:1`
