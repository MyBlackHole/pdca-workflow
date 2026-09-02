---
schema: pdca.asset/v1
id: ontology:entity/bcachefs-mount
type: entity
layer: Knowledge
status: active
summary: bcachefs Mount 实体 — bdev/handle/ioctl 三层 wrappers 与 degrade 路由及 fstab 集成
relations:
  specializes:
    - ontology:concept/domain-entity
  relates_to:
    - ontology:pattern/research-diagram-methodology
    - ontology:pattern/production-ontology-scientific-gate
    - ontology:pattern/scientific-research-methodology
attributes:
  - name: wrappers_three_layer
    desc: wrappers 三层（bdev 块设备打开/handle *mut bch_fs 封装/ioctl 类型安全派生）与 sysfs/super_io 可测
    constraint: 覆盖 src/wrappers/mod.rs 7 模块（bdev/handle/ioctl/super_io/sysfs/sb_display/online_iter）+ handle RAII + ioctl 由 fs/codegen.rs 的 ioctls_gen 派生 + super_io 的 bch2_read_super/write_super，经 C4 L3 与时序可一图建模
    testable_signal: "运行 grep -q 'wrappers' /home/black/Documents/bcachefs-tools/src/wrappers/mod.rs 且 grep -q 'handle' /home/black/Documents/bcachefs-tools/src/wrappers/handle.rs 且 grep -q 'ioctl' /home/black/Documents/bcachefs-tools/src/wrappers/ioctl.rs 且 grep -q 'mount' records/T0533-0902-research-bcachefs-tools/research-report.md 命中"
  - name: mount_degrade_and_fstab
    desc: mount 降级（degraded=very/no）与 fstab/mount.bcachefs.sh 集成可测
    constraint: 覆盖 mount.rs 的 degraded 选项映射 BCH_DEGRADED_* + bch2_fs_alloc 后 journal_read + recovery 26 passes + mount(2) 与 mount.bcachefs.sh 多设备拼装，经时序与决策树可一图建模
    testable_signal: "运行 grep -q 'degraded' /home/black/Documents/bcachefs-tools/src/commands/mount.rs 且 grep -q 'bch2_fs_alloc' /home/black/Documents/bcachefs-tools/fs/sb/io.c 且 grep -q 'mount.bcachefs' /home/black/Documents/bcachefs-tools/mount.bcachefs.sh 且 grep -q 'mount' records/T0533-0902-research-bcachefs-tools/research-report.md 命中"
  - name: fusemount_and_wait_devices
    desc: fusemount（FUSE 回退）与 wait_devices 等待可测
    constraint: 覆盖 fusemount.rs 的 fuser 直接对 /dev/fuse（无 libfuse3）+ defers_shrinkers 延迟 shrinker + wait_devices 轮询 /sys/fs/bcachefs，经状态机与正例可一图建模
    testable_signal: "运行 grep -q 'fusemount' /home/black/Documents/bcachefs-tools/src/commands/fusemount.rs 且 grep -q 'defers_shrinkers' /home/black/Documents/bcachefs-tools/src/commands/mod.rs 且 grep -q 'wait_devices' /home/black/Documents/bcachefs-tools/src/commands/wait_devices.rs 且 grep -q 'mount' records/T0533-0902-research-bcachefs-tools/research-report.md 命中"
---

# Bcachefs Mount（挂载）

`mount` 经 `wrappers` 三层（`bdev` 打开块设备 → `handle` 封装 `*mut bch_fs` → `ioctl` 类型安全派生自 `fs/codegen.rs`）触发 `bch2_fs_alloc + journal_read + recovery`，最终 `mount(2)` 或 `mount.bcachefs.sh` 多设备拼装；`fusemount` 直写 `/dev/fuse` 无 `libfuse3`。定位：`src/bcachefs.rs:263 → mount.rs/wait_devices.rs → wrappers/{bdev,handle,ioctl} → fs/sb/io.c + fs/journal/read.c`。

## C4 L3 Component — wrappers 三层与 mount 路径

`wrappers/mod.rs:1` 声明 `accounting/bdev/handle/ioctl/online_iter/sb_display/super_io/sysfs` 7 模块：`bdev.rs` 封装 `openat`/`BLKGETSIZE64`，`handle.rs` 以 `*mut c::bch_fs` RAII 管理 `bch2_fs_open`/`close` 并 `SbLockGuard`，`ioctl.rs` 由 `fs/codegen.rs` 生成 `Ioctl` 派生类型安全号，`super_io.rs` 封装 `bch2_read_super`/`bch2_write_super`，`sysfs.rs` 读写 `/sys/fs/bcachefs/*/`. `mount.rs` 聚合 `degraded`→`BCH_DEGRADED_yes/very/no` 映射。C4 L3 图以 `mount cmd → bdev → handle → ioctl → fs_alloc/journal_read → mount(2)` 五层呈现。

```mermaid
graph TD
    M["mount.rs<br/>degraded/very"]
    M --> BDEV["bdev<br/>wrappers/bdev.rs<br/>BLKGETSIZE64"]
    BDEV --> HDL["handle<br/>wrappers/handle.rs<br/>*mut bch_fs RAII"]
    HDL --> IOCTL["ioctl<br/>wrappers/ioctl.rs<br/>codegen 派生"]
    IOCTL --> FS["bch2_fs_alloc<br/>fs/sb/io.c + journal/read.c"]
    FS --> REC["recovery 26 passes<br/>init/passes_format.h:24"]
    REC --> MNT["mount(2)<br/>mount.bcachefs.sh"]
    MNT --> SYS["/sys/fs/bcachefs<br/>sysfs.rs"]
    %% Source: /home/black/Documents/bcachefs-tools/src/wrappers/mod.rs:1 + src/wrappers/handle.rs:1 + src/wrappers/ioctl.rs:1 + fs/sb/io.c:1
```

Source: `/home/black/Documents/bcachefs-tools/src/wrappers/mod.rs:1`（7 模块）+ `/home/black/Documents/bcachefs-tools/src/wrappers/handle.rs:1`（`*mut bch_fs` RAII）+ `/home/black/Documents/bcachefs-tools/src/wrappers/ioctl.rs:1`（`Ioctl` 派生）+ `/home/black/Documents/bcachefs-tools/fs/sb/io.c:1` + `/home/black/Documents/bcachefs-tools/mount.bcachefs.sh:1`

## 时序 — mount 全链

1) `mount.bcachefs /dev/sda:/dev/sdb /mnt -o degraded` 解析为 `mount` cmd；2) `bdev::open` 逐设备 `openat`，`handle::open` 调 `bch2_fs_alloc` 分配 `bch_fs`；3) `ioctl` 触发 `bch2_journal_read`（`journal/read.c`）→ `journal_start_info` 取 `last_seq/replay_end/cur_seq`；4) `bch2_fs_recovery` 跑 26 passes（含 `journal_replay`）；5) `mount(2)` 或 `fusemount` 直写 `/dev/fuse`（`fuser` 无 `libfuse3`），`defers_shrinkers` 延迟初始化；6) `wait_devices` 轮询 `sysfs` 直至设备全部 `online`。时序图以 `bdev → handle → ioctl → fs_alloc → recovery → mount` 全链呈现。

```mermaid
sequenceDiagram
    participant U as mount -o degraded
    participant B as bdev
    participant H as handle
    participant J as journal_read
    participant R as recovery
    U->>B: bdev open 多设备
    B->>H: handle *mut bch_fs
    H->>J: bch2_journal_read
    J-->>R: last_seq→replay_end→cur_seq
    R->>R: 26 passes + journal_replay
    R-->>U: mount(2) / fusemount /dev/fuse
    %% Source: /home/black/Documents/bcachefs-tools/src/commands/mount.rs:1 + src/wrappers/handle.rs:1 + fs/journal/read.c:1 + fs/init/passes_format.h:24
```

Source: `/home/black/Documents/bcachefs-tools/src/commands/mount.rs:1` + `/home/black/Documents/bcachefs-tools/src/wrappers/handle.rs:1` + `/home/black/Documents/bcachefs-tools/fs/journal/read.c:1` + `/home/black/Documents/bcachefs-tools/fs/init/passes_format.h:24`

## 状态机 — mount degraded 与 wait

`degraded` 三态 `no → yes → very`：`no` 缺盘即拒，`yes` 允许单盘缺，`very` 允许多盘缺且 `errors continue`。`mount` 五态 `init → bdev_open → fs_alloc → recovery → mounted`：`recovery` 失败则 `ro`。`wait_devices` 二态 `waiting → online`：轮询 `sysfs` 直至 `online` 或超时。`fusemount` 二态 `fuse_init → fuse_serve`：直写 `/dev/fuse`。状态机图覆盖 `degraded` 与 `wait` 分支。

```mermaid
stateDiagram-v2
    [*] --> BdevOpen: mount -o degraded
    BdevOpen --> FsAlloc: bdev 全部打开
    BdevOpen --> Degraded: 缺盘但 degraded=very
    Degraded --> FsAlloc: 仍 alloc
    FsAlloc --> Recovery: bch2_fs_alloc
    Recovery --> Mounted: 26 passes ok → mount(2)
    Recovery --> RO: recovery fail → ro
    Mounted --> Waiting: wait_devices
    Waiting --> Online: sysfs online
    Online --> [*]
    %% Source: /home/black/Documents/bcachefs-tools/src/commands/mount.rs:1 + src/commands/wait_devices.rs:1
```

Source: `/home/black/Documents/bcachefs-tools/src/commands/mount.rs:1` + `/home/black/Documents/bcachefs-tools/src/commands/wait_devices.rs:1` + `/home/black/Documents/bcachefs-tools/fs/init/passes_format.h:24`

## 决策树

```mermaid
flowchart TD
    START(["mount 入口"]) --> Q1{"degraded 模式?"}
    Q1 -- no --> A1["缺盘即 EIO"]
    Q1 -- yes/very --> A2["缺盘仍 alloc"]
    A1 & A2 --> Q2{"journal_read 成功?"}
    Q2 -- 否 --> E1["退 degraded/ro"]
    Q2 -- 是 --> Q3{"recovery 失败?"}
    Q3 -- 是 --> E1
    Q3 -- 否 --> Q4{"FUSE 回退?"}
    Q4 -- 是 --> F["fusemount /dev/fuse<br/>fuser 无 libfuse3"]
    Q4 -- 否 --> M["mount(2)"]
    F & M --> Q5{"需等待设备?"}
    Q5 -- 是 --> W["wait_devices 轮询 sysfs"]
    Q5 -- 否 --> END(["mounted"])
    W --> END
    %% Source: /home/black/Documents/bcachefs-tools/src/commands/mount.rs:1 + src/wrappers/mod.rs:1
```

Source: `/home/black/Documents/bcachefs-tools/src/commands/mount.rs:1` + `/home/black/Documents/bcachefs-tools/src/wrappers/mod.rs:1` + `/home/black/Documents/bcachefs-tools/mount.bcachefs.sh:1`

## 正例

```c
// 正例：多设备 mount + degraded
mount.bcachefs /dev/sda:/dev/sdb /mnt -o degraded
// → bdev 逐开 → handle RAII → bch2_journal_read → recovery 26 passes → mount(2)
// 验证：handle Drop 自动 close，mount 后 /sys/fs/bcachefs/*/online 为 1
```

命中：`bdev→handle→ioctl` 配对，`degraded` 与 `recovery` 配对。

## 反例

```c
// 反例1：跳过 handle 直接 ioctl
// 错：无 bch_fs 即 ioctl，空指针
// 正确：先 handle::open 再 ioctl

// 反例2：FUSE 误用 libfuse3
// 错：依赖 libfuse3，与 Cargo fuse feature (fuser) 冲突
// 正确：fusemount 直写 /dev/fuse，经 fuser crate
```

## 门禁

- **多图门禁**：`grep -c '```mermaid' ontology/entity/bcachefs-mount.md` ≥3
- **溯源门禁**：`grep -c 'Source:' ontology/entity/bcachefs-mount.md` ≥3 且每图含 `Source: /home/black/Documents/bcachefs-tools/... file:line`
- **正文门禁**：`wc -l ontology/entity/bcachefs-mount.md` ≥80 且含 `决策树` `正例` `反例` `门禁`
- **属性门禁**：`attributes` ≥3 且每条 `testable_signal` 含 `grep -q` 且双源可回归
- **本体校验**：`python3 scripts/ontology-validate.py` 0 issues 且 `islands:0`
- **脚手架门禁**：`python3 scripts/ontology_test_scaffold.py --node ontology:entity/bcachefs-mount --out /tmp/x.py` 可产
- **Gate 门禁**：`python3 scripts/production-ontology-gate.py --node ontology:entity/bcachefs-mount` GATE OK

Source: `/home/black/Documents/bcachefs-tools/src/wrappers/mod.rs:1` + `/home/black/Documents/bcachefs-tools/src/wrappers/handle.rs:1` + `/home/black/Documents/bcachefs-tools/mount.bcachefs.sh:1`
