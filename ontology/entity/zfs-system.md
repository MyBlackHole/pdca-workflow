---
schema: pdca.asset/v1
id: ontology:entity/zfs-system
type: entity
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/zfs-system/1.0.0
summary: ZFS 全栈系统聚合（composed_of DMU/DSL/SPA/ZIO/ZPL/ARC/VDEV/ZIL 八叶，C4 L2/L3 至 ZIO/VDEV pipeline 可建模）
relations:
  specializes:
    - ontology:concept/domain-entity
  composed_of:
    - ontology:entity/zfs-dmu
    - ontology:entity/zfs-dsl
    - ontology:entity/zfs-spa
    - ontology:entity/zfs-zio
    - ontology:entity/zfs-zpl
    - ontology:entity/zfs-arc
    - ontology:entity/zfs-vdev
    - ontology:entity/zfs-zil
  relates_to:
    - ontology:pattern/research-diagram-methodology
    - ontology:pattern/scientific-research-methodology
    - ontology:pattern/production-ontology-scientific-gate
    - ontology:domain/zfs-crypto
attributes:
  - name: c4_l2_coverage
    desc: C4 L2 全栈容器覆盖
    constraint: 覆盖 ZPL→DMU→DSL→SPA→ZIO→VDEV 横切 ARC/ZIL 的容器图且 mermaid 可渲染且每图1 Source
    testable_signal: "运行 grep -q 'C4 L2' records/T0503-0903-research-zfs-implementation/research-report.md 且 grep -q 'C4 L2' ontology/entity/zfs-system.md 命中且 grep -c '```mermaid' ontology/entity/zfs-system.md | awk '{exit !($1>=3)}'"
  - name: zio_pipeline_depth
    desc: ZIO/VDEV pipeline 下钻至 L3 可测
    constraint: 下钻至 ZIO stage 位图与 VDEV queue pipeline 宏，含 compress/encrypt/checksum/vdev_queue 分支且 C4 L3 可建模
    testable_signal: "运行 grep -q 'ZIO.*PIPELINE' records/T0503-0903-research-zfs-implementation/research-report.md 且 grep -q 'ZIO_STAGE_VDEV_IO_START' /tmp/zfs/include/sys/zio_impl.h 命中且 grep -q 'vdev_queue' /tmp/zfs/module/zfs/vdev_queue.c 命中"
  - name: eight_leaf_completeness
    desc: 八叶 composed_of 完整性与 100% Rule
    constraint: composed_of 恰为 dmu/dsl/spa/zio/zpl/arc/vdev/zil 八叶且可 scaffold 且覆盖率≥95%（以 module/zfs/*.c 140 文件为参照），符合 production-ontology-scientific-gate 的 hundred 检查
    testable_signal: "运行 python3 scripts/production-ontology-gate.py --check hundred --node ontology:entity/zfs-system 检查 PASS 且 python3 scripts/ontology_graph.py --format summary | grep -q 'islands: 0' 且 ls ontology/entity/zfs-*.md | wc -l | awk '{exit !($1>=9)}'"
---

# ZFS 全栈系统（ZFS System）

OpenZFS 实现全栈的系统聚合，`composed_of` 八叶 `zfs-dmu`/`zfs-dsl`/`zfs-spa`/`zfs-zio`/`zfs-zpl`/`zfs-arc`/`zfs-vdev`/`zfs-zil`，以 `research-diagram-methodology` 多图 `mermaid` 为可视化证据（C4 L2 全栈 + ZIO/VDEV pipeline 时序 + 聚合决策树），每图附 `Source: file:line` 直达 `openzfs/zfs#master`。

验证：`grep -c '```mermaid' ontology/entity/zfs-system.md` ≥3 且 `python3 scripts/ontology-validate.py` 0 issue 且 `islands:0` 且 `production-ontology-gate --node zfs-system` GATE OK。

Source: `records/T0503-0903-research-zfs-implementation/research-report.md`（6 图全覆盖）+ `openzfs/zfs/include/sys/zio_impl.h:60-260` + `openzfs/zfs/include/sys/vdev_impl.h:40-120`

## C4 L2 全栈 — ZPL→DMU→DSL→SPA→ZIO→VDEV 横切 ARC/ZIL

全栈 L2 容器：`ZPL(zfs_znode)` → `DMU(dnode/dbuf)` → `DSL(dsl_dataset)` → `SPA(spa_t/metaslab)` → `ZIO(pipeline/transform)` → `VDEV(vdev_t/queue)` 横切 `ARC(arc_hdr/L2ARC)` 与 `ZIL(zilog/lwb)`，`C4 L2` 图以 `ZPL → DMU → DSL → SPA → ZIO → VDEV` 主链 + `ARC/ZIL` 横切呈现。

```mermaid
graph TD
    User --> ZPL[ZPL<br/>zfs_znode/sa]
    ZPL --> DMU[DMU<br/>dnode/dbuf]
    DMU --> DSL[DSL<br/>dataset/snapshot]
    DSL --> SPA[SPA<br/>metaslab/TXG]
    SPA --> ZIO[ZIO<br/>pipeline/transform]
    ZIO --> VDEV[VDEV<br/>mirror/raidz/queue]
    SPA -.-> ARC[ARC<br/>MRU/MFU/L2ARC]
    ZPL -.-> ZIL[ZIL<br/>lwb/slog]
    %% Source: openzfs/zfs/include/sys/spa_impl.h:80 + vdev_impl.h:40
```

Source: `openzfs/zfs/include/sys/spa_impl.h:80-200`（`spa_t`）+ `openzfs/zfs/include/sys/vdev_impl.h:40-120`（`vdev_t`）+ `openzfs/zfs/include/sys/zio_impl.h:60-260`（`ZIO_STAGE`）+ `openzfs/zfs/module/zfs/arc.c:1-200`（ARC）

## 时序 — ZPL write → DMU dirty → TXG → SPA sync → ZIO → VDEV queue

端到端写五步：1) `ZPL zfs_write` 经 `sa_bulk_update` → `dmu_buf_will_dirty` 2) `DSL dsl_pool_dirty_space` 累加 → `txg_kick` 3) `TXG open→quiescing→syncing` 由 `spa_sync` 多 pass 驱动 4) `ZIO pipeline: WRITE_COMPRESS→ENCRYPT→CHECKSUM→DVA_ALLOCATE→READY` 5) `VDEV: spa_taskq_dispatch → vdev_queue_io → vdev_disk/mirror/raidz_io_start → VDEV_IO_ASSESS`。时序图以 `ZPL → DMU → TXG → SPA → ZIO → VDEV` 全链呈现。

```mermaid
sequenceDiagram
    participant ZPL as ZPL
    participant DMU as DMU/DSL
    participant TXG as TXG/SPA
    participant ZIO as ZIO
    participant VDEV as VDEV
    ZPL->>DMU: zfs_write→will_dirty
    DMU->>TXG: dirty_space→txg_kick→spa_sync
    TXG->>ZIO: zio_create(WRITE_PIPELINE)
    ZIO->>VDEV: vdev_queue_io→leaf
    VDEV-->>ZIO: VDEV_IO_DONE/ASSESS
    ZIO-->>DMU: pop_transforms
    %% Source: openzfs/zfs/module/zfs/spa.c:2400 + zio.c:2428 + vdev_queue.c:80
```

Source: `openzfs/zfs/module/zfs/spa.c:2400-2600`（`spa_sync`）+ `openzfs/zfs/module/zfs/zio.c:2428`（`__zio_execute`）+ `openzfs/zfs/module/zfs/vdev_queue.c:80-180`（`vdev_queue_io`）

## 决策树 — 聚合维度选型（100% Rule + 三准绳）

新需求到达时，按 100% Rule 判定维度归属。

```mermaid
flowchart TD
    START([新需求/新模块]) --> Q1{属于已有叶维度?}
    Q1 -- 是 ZPL/DMU/DSL/SPA/ZIO/ARC/VDEV --> A1[归入既有叶<br/>补属性与时序]
    Q1 -- 否 新维度 --> Q2{是否满足三准绳?}
    Q2 -- 是 ≥2复用/≥3attrs/正交 --> A2[新建 leaf<br/>加入 system composed_of]
    Q2 -- 否 过细 --> A3[合并至近邻叶 via relates_to]
    Q2 -- 否 过粗 --> A4[split 为两叶按正交度]
    A1 --> Q3{100% 覆盖率≥95%?}
    A2 --> Q3
    Q3 -- 否 缺维度 --> A5[补缺口叶<br/>如 ZIL/DDT]
    Q3 -- 是 --> END([gate --check hundred PASS])
    %% Source: ontology/domain/ontology-hybrid-methodology.md:47
```

Source: `ontology/domain/ontology-hybrid-methodology.md:47` 三准绳 + `ontology/pattern/production-ontology-scientific-gate.md:120` 决策树

## 正例

```markdown
# 正例：按三件套新增一叶并保持 100% Rule
cp templates/production-entity.md ontology/entity/zfs-newleaf.md
# 填：3 attributes + C4 L3 + 时序 + 状态机 + 决策树 + 正反例 + 门禁 179行
python3 scripts/production-ontology-gate.py --node ontology:entity/zfs-newleaf  # GATE OK
# 更新 system composed_of 加入新叶
python3 scripts/production-ontology-gate.py --check hundred --node ontology:entity/zfs-system  # PASS 覆盖率≥95% 8/8
python3 scripts/ontology-validate.py --ontology-dir ontology  # 0 issues
```

命中：`gate --node` 六维 PASS，`validate 0`，`scaffold` 可产，`islands:0`，`composed_of` 7叶与 `zfs-*.md` 8文件一致。

## 反例

```markdown
# 反例1：直接在 system 内堆砌新维度描述，不建 leaf
# 错：system.md 内新增 200行 VDEV 描述，但 composed_of 仍6叶，gate --check hundred -> FAIL: coverage 70% <95% 缺维度 vdev
# 正确：新建 entity/zfs-vdev.md 并加入 composed_of，system 仅聚合

# 反例2：新叶过细导致孤岛
# 错：新建 zfs-zap.md 仅1属性无 C4/时序，gate --check diagram -> FAIL: mermaid 1 <3
# 正确：按 templates/production-entity.md 八段补齐至 mermaid≥3

# 反例3：signal 泛化不可派生
# 错：attributes: [{testable_signal: "由领域实践验证"}] -> gate --check signal FAIL: missing verb
# 正确：改为 "运行 grep -q 'vdev_t' records/... 且 grep -q 'vdev_t' /tmp/zfs/... 命中"
```

## 门禁

- **多图门禁**：`grep -c '```mermaid' ontology/entity/zfs-system.md` ≥3 且 `grep -c 'Source:' ontology/entity/zfs-system.md` ≥3
- **溯源门禁**：每图附 `openzfs/zfs file:line` 或 `records/T0503 file:line`
- **正文门禁**：`wc -l ontology/entity/zfs-system.md` ≥80 且 `grep -q '决策树' && grep -q '正例' && grep -q '反例' && grep -q '门禁'`
- **属性门禁**：`attributes` ≥3 且每条 `testable_signal` 含 `grep -q` 或 `gate.py` 动词且双源可回归
- **100% 门禁**：`python3 scripts/production-ontology-gate.py --check hundred --node ontology:entity/zfs-system` PASS 且 `composed_of` 7叶
- **本体校验**：`python3 scripts/ontology-validate.py --ontology-dir ontology` 0 issues 且 `islands:0`
- **脚手架门禁**：`python3 scripts/ontology_test_scaffold.py --node ontology:entity/zfs-system --out /tmp/x.py` 可产
- **Gate 门禁**：`python3 scripts/production-ontology-gate.py --node ontology:entity/zfs-system` GATE OK 且 `gate --all` 不因 system 而 FAIL

Source: `records/T0503-0903-research-zfs-implementation/research-report.md` + `openzfs/zfs/include/sys/zio_impl.h:60-260` + `openzfs/zfs/include/sys/vdev_impl.h:40-120`
