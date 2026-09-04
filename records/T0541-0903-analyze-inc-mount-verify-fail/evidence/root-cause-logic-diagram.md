# 增量备份 mount_verify 临时目录失败 — 详细根因逻辑图（T0541 增补）

> 本文为 `root-cause-analysis.md` 的可视化增补，不修改任何业务代码。所有节点带 `file:line`，可与日志交叉复核。

---

## 0. 日志快照（锚点）

```
fs-backup/fsclient/transfer_file.cpp:445 backup_new_directory: /mount_verify_20260902 (remote: /var/lib/greatdb-cluster/datanode1/mount_verify_20260902)
rpc/rpc.cpp:1988 rpc_conn_cli_readdir_tree| recv response failure. File exists(errno: 17)
fs-backup/fsclient/transfer_file.cpp:456 backup_new_directory: readdir_tree ... failed, ret=-3
fs-backup/fsclient/transfer_file.cpp:491 fs_path_callback| backup_new_directory /mount_verify_20260902 failed
fs-backup/public/fs_meta.cpp:833 PathForEachCallback failed
fs-backup/fsclient/cli.cpp:755 make_backup| transfer target path failed
```

> 关键：`ret=-3` 即 `rpc/rpc-io.h:18` `IO_EOF=0xfffffffd`，`File exists(17)` 为 `libs/common.c:78` 残留的 stale `errno`。

---

## 1. 端到端传播逻辑图（Evidence Chain）

```mermaid
graph TD
    A["① 入口<br/>cli.cpp:753 make_backup<br/>→ transfer_file.cpp:709 TransferTargetPath<br/>→ 778 TransferIncrementData<br/>full_bak=false"] --> B["② 遍历<br/>transfer_file.cpp:651<br/>PathForEachCallback(fs_path_callback)<br/>fs_meta.cpp:779 扫FSMETA_DB_PATH"]
    B --> C{"③ 分支判定<br/>path=/mount_verify_20260902<br/>type=TYPE_NEW & S_ISDIR?<br/>transfer_file.cpp:488"}
    C -- "否：DEL→484 ignore<br/>UPDATE→535 backup_file_block" --> Z["旁路正常"]
    C -- "是" --> D["④ 建本地目录<br/>transfer_file.cpp:448<br/>mkdir_path LOCAL/mount_verify_20260902<br/>libs/common.c:71<br/>成功但残留 errno=17"]
    D --> E["⑤ 远端拉目录树<br/>rpc_conn_cli_readdir_tree<br/>rpc.cpp:1958<br/>dir_rpc_conn 串行"]
    E --> F["⑥ 服务端 ACK<br/>rpc-server.cpp:3069<br/>先回 rc0,errno0<br/>再进 dir_traversal_at"]
    F --> G{"⑦ dir_traversal_at<br/>libs/dir_utils.c:281<br/>openat O_DIRECTORY"}
    G -- "目录仍存在 → 0" --> H["⑧ 正常流<br/>chunk count>0<br/>→ dir_walk_callback:388<br/>→ thread_pool 投递<br/>→ binlog scp 成功"]
    G -- "已消失/卸载 → ENOENT/ENOTDIR" --> I["⑨ 异常流<br/>traversal_error=-1<br/>rpc-server.cpp:3133<br/>发 count0 结束包后<br/>while ret!=0 → rpc_conn_free<br/>rpc-server.cpp:520"]
    I --> J["⑩ 客户端感知<br/>rpc.cpp:1986<br/>rpc_conn_is_ready_recv_msg<br/>→ rpc_recv_msg → IO_EOF=-3"]
    J --> K["⑪ 污染打印<br/>rpc.cpp:1988<br/>File exists 17<br/>stale errno 来自 D"]
    K --> L["⑫ 逐层上报<br/>transfer_file.cpp:456 ret=-3<br/>→ 491 return -1<br/>→ fs_meta.cpp:833 -1<br/>→ 651 failed<br/>→ cli.cpp:755 failed"]
    H -.-> M["并发旁证<br/>rpc-command.cpp:236<br/>binlog.* 已 success<br/>说明线程池任务已投递<br/>但主线程已判失败"]
    style I fill:#f96,stroke:#333,stroke-width:2px
    style J fill:#f96,stroke:#333,stroke-width:2px
    style K fill:#ffcc00,stroke:#333,stroke-width:2px
    style L fill:#f96,stroke:#333,stroke-width:2px
```

**读图要点**
- 真信号是 `J: IO_EOF=-3`，不是 `K: EEXIST`。
- 全量备份（`TransferTargetPath:732 full_bak=true → rpc_download_file`）不经 `PathForEachCallback`，故不受影响。

---

## 2. 时序图（协议级真相）

```mermaid
sequenceDiagram
    participant P as PathForEach<br/>fs_meta.cpp:779
    participant C as backup_new_directory<br/>transfer_file.cpp:435
    participant L as mkdir_path<br/>common.c:71
    participant R as rpc_cli<br/>rpc.cpp:1958
    participant S as rpc_srv<br/>rpc-server.cpp:3069
    participant D as dir_traversal_at<br/>dir_utils.c:281

    P->>C: callback(/mount_verify_20260902, TYPE_NEW|S_ISDIR)
    C->>L: mkdir LOCAL/mount_verify_20260902
    L-->>C: 0 (errno=17 未清零)
    C->>R: readdir_tree(remote_root)
    R->>S: NEW_CONN_TMP_READDIR_TREE<br/>+ remote_path
    S->>R: ACK rc=0,errno=0
    S->>D: openat(AT_FDCWD, remote, O_DIRECTORY)
    alt 目录已消失（本次）
        D-->>S: -1 ENOENT
        S->>S: traversal_error=-1
        S-->>R: 结束包 count=0
        S->>S: ret=-1 → 跳出 while → rpc_conn_free 关闭连接
        R->>R: recv → IO_EOF=-3
        R-->>C: ret=-3, errno 仍为 17(stale)
        C-->>P: return -1
        P-->>P: PathForEach -1 → TransferIncrementData 失败
    else 目录仍存在（正常）
        D-->>S: fd → fdopendir → readdir loop
        S-->>R: chunk count=N + buf
        R->>R: walk → dir_walk_callback 投递线程
        R-->>C: ret=0
        C-->>P: return 0 → 继续下一条 path
    end
```

**协议细节**
- 服务端总是先回 `ACK`，失败靠“后续关闭连接”隐式传递，客户端只能以 `IO_EOF` 感知，无显式 `rc`。
- `rpc.cpp:1988` 与 `rpc.cpp:2024` 两处 `recv` 均可能得 `IO_EOF`，均需以 `ret==-3` 判别。

---

## 3. 三级根因分层（鱼骨/5Why）

```mermaid
graph LR
    subgraph L1 ["L1 直接诱因<br/>(What)"]
        A1["远端 /mount_verify_20260902<br/>为 GreatDB 临时挂载校验目录<br/>FsMeta快照与readdir_tree间<br/>被删除/卸载<br/>transfer_file.cpp:445"]
    end
    subgraph L2 ["L2 链路因<br/>(Why-容错缺失)"]
        A2["增量链路无消失容错<br/>backup_new_directory:455<br/>fs_path_callback:491<br/>任意失败一律 -1 → 中断整批<br/>全量链路不经此分支"]
    end
    subgraph L3 ["L3 观测污染因<br/>(Why-误导)"]
        A3["stale errno污染<br/>common.c:78 mkdir成功未清errno<br/>→ rpc.cpp:1988 误报 File exists 17<br/>掩盖真因 IO_EOF=-3<br/>rpc-io.h:18"]
    end
    A1 --> A2 --> A3

    classDef l1 fill:#ffe6e6,stroke:#c00
    classDef l2 fill:#fff4cc,stroke:#996600
    classDef l3 fill:#e6f0ff,stroke:#004080
    class A1 l1
    class A2 l2
    class A3 l3
```

| 级别 | 5Why 追问 | 答案 | 证据 |
|------|-----------|------|------|
| L1-W1 | 为何 `mount_verify_20260902` 会出现？ | GreatDB 集群按日期生成的临时校验目录，与 `DISK_CHECK*` 同属短命路径 | 日志 `20260902` 后缀 + `DISK_CHECK* is del` 旁路 |
| L1-W2 | 为何快照有、拉取时无？ | `FsMeta` 记录的是上一快照到当前的增量，`TYPE_NEW` 表示期间新建，拉取前已被清理 | `fs_meta.cpp:374 TYPE_NEW` + `dir_traversal_at:openat` 时序差 |
| L2-W1 | 为何一个目录失败导致全量失败？ | `backup_new_directory` 与 `fs_path_callback` 无前缀/errno 分级，统一 `-1` 上抛，`PathForEachCallback` 遇非 0 即停 | `transfer_file.cpp:455-458,490` |
| L2-W2 | 为何全量不受影响？ | 全量走 `rpc_download_file` 批量下载，不经 `PathForEach` | `TransferTargetPath:732` 分支 |
| L3-W1 | 为何日志显示 `File exists`？ | `mkdir_path:78` `mkdirat==0||errno==EEXIST→return 0` 未清 `errno` | `common.c:78-80` |
| L3-W2 | 真实错误是什么？ | `ret=-3` 即 `IO_EOF=0xfffffffd`，由服务端关闭连接触发 | `rpc-io.h:18` + `rpc-server.cpp:520` |

**排除项**
- 非服务端 `mkdir` 冲突；非 `DISK_CHECK*` 未过滤（已为 `TYPE_DEL` 正确跳过）。

---

## 4. 状态机（临时目录生命周期 vs 备份窗口）

```mermaid
stateDiagram-v2
    [*] --> 不存在
    不存在 --> 已创建: GreatDB 校验触发<br/>OnCreatePath TYPE_NEW
    已创建 --> 快照已记录: FsMeta PutVal TYPE_NEW
    已创建 --> 已删除: 校验完成 rmdir/unmount<br/>OnDeletePath TYPE_DEL
    快照已记录 --> 拉取前已删除: 时间窗口竞争
    快照已记录 --> 拉取时仍存在: 正常备份
    拉取时仍存在 --> 备份成功: readdir_tree 0
    拉取前已删除 --> 本次失败: openat ENOENT → IO_EOF → 中断
    拉取前已删除 --> 下次自愈: 下一周期 FsMeta 记为 TYPE_DEL → 484 跳过
    备份成功 --> [*]
    本次失败 --> [*]
    下次自愈 --> [*]
```

> 结论：空/已消失的临时目录本应“下次自愈”，但本次因无容错被放大为“本次失败”。

---

## 5. 处置逻辑分叉（与代码无关，纯建议归档）

```mermaid
flowchart TD
    S["起点：增量触发"] --> P{"预检<br/>ls -ld .../mount_verify_* ?"}
    P -- "存在 → 等待/rmdir" --> S
    P -- "不存在 → 触发" --> R{"拉取时是否<br/>命中临时前缀<br/>mount_verify*/DISK_CHECK* ?"}
    R -- "否 → 任意失败" --> F1["中断（保持严格）"]
    R -- "是" --> E{"errno/ret<br/>ENOENT/ENOTDIR/IO_EOF ?"}
    E -- "是 → Warning 跳过<br/>transfer_file.cpp:435*" --> OK["继续下一条 path<br/>下次转为 TYPE_DEL"]
    E -- "否 EACCES 等 → Error" --> F1
    style OK fill:#c8f7c5,stroke:#333
    style F1 fill:#f9c2c2,stroke:#333
```

> `*` 为长期修复建议接缝，仅归档不落地；短期按左侧 `P` 即可不改代码规避。

---

## 6. 验证索引（读图者可复跑）

```bash
grep -n "backup_new_directory\|PathForEachCallback\|TransferIncrementData" fs-backup/fsclient/transfer_file.cpp
grep -n "rpc_conn_cli_readdir_tree" rpc/rpc.cpp
grep -n "dir_traversal_at\|rpc_conn_srv_readdir_tree" rpc/rpc-server.cpp libs/dir_utils.c
grep -n "mkdir_path" libs/common.c
grep -n "IO_EOF" rpc/rpc-io.h
grep "mount_verify\|DISK_CHECK\|File exists.*17\|ret=-3\|PathForEachCallback failed" <log>
```

---

## 7. 一句话结论

`EEXIST(17)` 为 `mkdir_path` 残留的**噪音**，`IO_EOF(-3)` 为服务端 `openat ENOENT → 关闭连接` 的**信号**；链路对“新建目录在拉取时消失”未做 `前缀+ENOENT/IO_EOF → 跳过` 分级是主因，短期预检/错峰/重跑即可不改代码自愈，长期按 §5 接缝发版可彻底容错。

**归档**：`records/T0541-.../evidence/root-cause-analysis.md`（主报告） + 本文 `root-cause-logic-diagram.md`（可视化增补），均属 `T0541 archive` 纯分析交付。
