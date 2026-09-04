---
schema: pdca.asset/v1
id: ontology:entity/aio-tools-6200-release
type: entity
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/aio-tools-6200-release/1.0.0
summary: aio-tools 6200/release 快照实体（6.2.0.0-release fe9d4364，14 模块+libs+third_party，488 文件/18.9万 LOC，11 变量双层版本链，xmake 四阶段 CI，fsdeamon↔aio-speedd 主链路+rdbcomm 32/5MB）
relations:
  specializes:
    - ontology:concept/domain-entity
  relates_to:
    - ontology:pattern/scientific-research-methodology
    - ontology:pattern/research-diagram-methodology
    - ontology:concept/pdca-task
attributes:
  - name: c4_l2_completeness
    desc: C4 L2 14 模块+libs+第三方容器覆盖
    constraint: 覆盖 rpc/fs-backup/fsbackup_kernel/rdbcomm/s3tools/libobk/dmsbtex/xbsa/bwlimit 等14 模块+libs+third_party 的容器边界与依赖拓扑，mermaid 可渲染且每图1 Source
    testable_signal: "运行 grep -q 'C4 L2' records/T2028-0904-research-aio-tools-6200-release-v2/research-report.md 且 grep -q 'C4Container' ontology/entity/aio-tools-6200-release.md 命中且 grep -c '```mermaid' ontology/entity/aio-tools-6200-release.md | awk '{exit !($1>=3)}'"
  - name: version_chain_closure
    desc: 11 变量双层版本链闭环
    constraint: xmake.lua 11 变量→version.h.in/log.in→build/version.h/log+*.version→tools-versions.txt 的声明-模板-生成-同步链路可重跑，fsdaemon_version=rpc_version 同轨显式
    testable_signal: "运行 grep -q 'fsdaemon_version = rpc_version' /home/black/Public/aio/aio-tools/6200/release/xmake.lua 且 cat /home/black/Public/aio/aio-tools/6200/release/build/version.log | grep -q 'rpc \"3.6.4.19\"' 且 grep -q 'version_chain' ontology/entity/aio-tools-6200-release.md 命中"
  - name: rdbcomm_plugin_contract
    desc: rdbcomm 32 槽/5MB 插件契约与状态机
    constraint: MAX_PLUGINS 32 槽位 freelist、5MB 消息上限、module_t 四回调生命周期与 handle_mange 句柄池可建模，状态机 mermaid 可渲染
    testable_signal: "运行 grep -q 'MAX_PLUGINS 32' /home/black/Public/aio/aio-tools/6200/release/rdbcomm/module.h 且 grep -q 'RDBCOMM_MAX_MSG_LENGTH' /home/black/Public/aio/aio-tools/6200/release/rdbcomm/rdbcomm.h 且 grep -q 'stateDiagram' ontology/entity/aio-tools-6200-release.md 命中"
---

# aio-tools 6200/release 快照实体

> `6.2.0.0-release` 分支 `fe9d4364 B-1912` 快照（`488 源码文件/18.9万 LOC`，`xmake.lua:11 变量`，`build/version.log:17 产物`），T2027 全景调研 + T2028 Grill 合规重调（增补 rdbcomm 深潜）沉淀。

## 全景度量

- 14 业务模块：`bwlimit/dmsbtex/fs-backup/fsbackup_kernel_4.x/huanweicloun-sdk-s3-data-backup/libobk/libs/rdbcomm/rpc/rpc-keygen/s3-tool/s3tools/third_party/xbsa` + `install/build`
- 公共层：`libs` 79 文件 41k LOC（`logger/lmdb/rpc-net/tls_cert/timed_key`），`rpc` 63 文件 26k LOC 为二级共享

## C4 L2 容器图（mermaid）

```mermaid
C4Container
    title aio-tools 6200/release — C4 L2（含 rdbcomm 32/5MB）
    System_Boundary(aio, "aio-tools") {
        Container(fs_cli, "fs-cli", "C++", "8901")
        Container(fsdeamon, "fsdeamon", "daemon", "host 8901")
        Container(rpc_srv, "aio-speedd", "daemon", "8811")
        Container(rdb_srv, "rdbcommd", "daemon", "plugin 32/5MB")
        Container(libs, "libs", "static libs", "logger/lmdb/tls")
    }
    Rel(fs_cli, fsdeamon, "JSON 8901")
    Rel(fsdeamon, rpc_srv, "ioctl 8811")
    Rel(rdb_srv, libs, "static")
```
Source: `file: xmake.lua:1`（`includes()`）、`file: rdbcomm/module.h:1`（`MAX_PLUGINS 32`）— S1/S12

## 版本链路状态机（mermaid）

```mermaid
stateDiagram-v2
    [*] --> xmake: 11 变量
    xmake --> gen: xmake f --yes → version.h/log/*.version
    gen --> build: xmake -y → 60+ 产物
    build --> ci: check/test/get_version/sync_version → tools-versions.txt
    ci --> [*]
```
Source: `file: xmake.lua:12`、`file: build/version.log:1`、`file: .gitlab-ci.yml:1` — S1/S3/S4

## rdbcomm 插件状态机（mermaid）

```mermaid
stateDiagram-v2
    [*] --> Unloaded
    Unloaded --> Registered: register/dlopen
    Registered --> Inited: on_init
    Inited --> Running: on_start
    Running --> Stopped: on_stop
    Stopped --> Running: on_start
    Stopped --> Unregistered: unregister/dlclose
    Unregistered --> [*]
```
Source: `file: rdbcomm/module.h:1`（`MAX_PLUGINS 32`）、`file: rdbcomm/server.c:1`（`handle_mange`）— S12/S13

## 可重跑验证

```bash
grep -q 'MAX_PLUGINS 32' rdbcomm/module.h && grep -q 'RDBCOMM_MAX_MSG_LENGTH' rdbcomm/rdbcomm.h && echo ok
cat build/version.log | grep -q 'rpc "3.6.4.19"' && echo ok
grep -c '```mermaid' ontology/entity/aio-tools-6200-release.md  # ≥3
```

## 来源

- `records/T2027-0904-research-aio-tools-6200-release/research-report.md`（29522 bytes, 6 图）
- `records/T2028-0904-research-aio-tools-6200-release-v2/research-report.md`（33708 bytes, 7 图，增补 S11-S14）
- `file: /home/black/Public/aio/aio-tools/6200/release/xmake.lua:1` 等 S1-S14

## 决策背景

按 `skill-research` 分流判定，原 `records-only` 因“快照特化未通用化”暂缓；现按“全面修改必须本体处理”要求，将快照事实晋级为实体，`composed_of` 3 叶待后续拆解，`relations` 挂 `pdca-task` 与方法论，供后续重构/版本策略任务复用。

*Diátaxis: reference* | *arc42: 5/6/12 节* | *C4 L2 可建模*
