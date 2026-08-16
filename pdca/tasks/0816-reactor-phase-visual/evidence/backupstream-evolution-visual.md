# backupstream v65→v101 演进学习图文版：36 个提交的架构之旅

任务: T0297 图形化改造
源报告: T0295 evidence `git-history-learning-final.md`
范围: main 分支 v65→v101 共 36 个提交（v91 无独立提交，设计并入 v92）

> 一句话：从「全量目录队列」到「inotify leaf-sparse dirty journal」，从
> 「阻塞多线程 Agent」到「Reactor/事件域 + 有界 Work Pool」，从「无观测」
> 到「守恒分解可归因的 observability」——四轮演进，主线清晰。

---

## 1. 演进时间线：四轮架构主线的完整旅程

**主线 1：客户端目录队列 / dirty journal（v65-v74）**

```mermaid
timeline
    title 主线1：目录队列 → dirty journal
    v65 : root：catalog + 目录队列 + RSP/3
    v66 : trusted dirty feed（选择性增量）
    v67 : job 资源锁 + active_run 栅栏
    v68 : 64 目录组/256 id 批量
    v69 : fileid 反向索引（hardlink-safe）
    v70 : ★backup-dirtyd + inotify journal
    v71/72 : 自适应元数据并行
    v73 : 提交即成功的 identity 校验
    v74 : ★leaf-sparse journal（schema 1→2）
```

**主线 2：Agent 传输 Reactor/FSM 化（v75-v88）**

```mermaid
timeline
    title 主线2：阻塞多线程 → Reactor/FSM
    v75 : TREE 往返优化（能力位）
    v76 : ★per-EXEC 事件泵（修死锁）
    v77 : ★共享 EXEC 事件域（shard）
    v78 : 弹性会话池 + pidfd
    v79 : EXEC socket RX 移交 shard
    v80 : ★非阻塞 plain ingress
    v81 : control worker 让出
    v82 : System-RPC 执行/传输拆分
    v83 : ★TREE FSM 中立化
    v84 : ★FILE FSM
    v85 : ★RESTORE FSM
    v86 : 移除最后 TREE 阻塞桥
    v87 : ★Data Lane 迁移（service 表移除）
    v88 : ★EXEC 有界 launch pool（无 general session pool）
```

**主线 3：Observability 与离线诊断（v89-v101）**

```mermaid
timeline
    title 主线3：无观测 → 守恒可归因
    v89 : ★server-local trace（三级身份）
    v90 : ★JSONL + Prometheus 双平面导出
    v91/92 : ★backup-observe 离线消费
    v93 : client-requested session debug
    v94 : debug 会话配额
    v95 : ★backup-observe diagnose
    v96/97 : worker 四段边界
    v98/99 : ★256 回调历史 + source_kind
    v100 : CPU 保守分类
    v101 : ★512 相位历史 + 守恒分解
```

> 图例：三条 `timeline` 各回答"一条主线怎么演进"一个问题，合计覆盖 v65-v101
> 全部 36 个提交（v91 无独立提交，并入 v92）；★ 为架构分水岭。

---

> 图例：`timeline` 三段并列展示三条主线；★ 为架构分水岭（引入新模块/新模式）。
> 36 提交全量覆盖，无遗漏。

---

## 2. 架构分水岭：哪 12 个节点定义了演进

```mermaid
flowchart TD
    A["v65 root<br/>目录队列起点"] --> B["v70 ★backup-dirtyd<br/>inotify dirty journal"]
    B --> C["v74 ★leaf-sparse<br/>O(变更叶子) 扫描"]
    C --> D["v76/v77 ★事件泵→共享事件域"]
    D --> E["v80 ★非阻塞 plain ingress"]
    E --> F["v83/84/85 ★TREE/FILE/RESTORE FSM 中立化"]
    F --> G["v87/88 ★Data Lane 迁移 + launch pool<br/>无 general session pool"]
    G --> H["v89/90 ★trace + 双平面导出"]
    H --> I["v95 ★backup-observe diagnose"]
    I --> J["v98/99 ★256 回调历史 + source_kind"]
    J --> K["v101 ★512 相位历史 + 守恒分解"]
```

> 图例：`flowchart TD` 自上而下；每个节点是架构分水岭（★），
> 箭头表示演进方向，非依赖关系。

---

## 3. 主线一图流：四轮演进各自解决什么问题

### 主线 1：目录队列 → dirty journal（v65-v74）

```mermaid
flowchart LR
    A["全量目录队列<br/>O(所有条目)"] --> B["trusted dirty feed<br/>成本→真实脏集"]
    B --> C["inotify journal<br/>backup-dirtyd 守护进程"]
    C --> D["leaf-sparse 扫描<br/>O(变更叶子)"]
    D --> E["成本：O(条目) → O(叶子)<br/>正确性：fail-closed 围栏"]
```

> 图例：自左向右为演进；最后为量化收益与正确性保证。

### 主线 2：阻塞多线程 → Reactor/事件域（v75-v88）

```mermaid
flowchart LR
    A["阻塞 worker 池<br/>每 socket 一线程"] --> B["事件泵 + 共享事件域<br/>socket 就绪归 Reactor"]
    B --> C["transport-neutral FSM<br/>TREE/FILE/RESTORE/Lane"]
    C --> D["有界 Work Pool<br/>只做工作，不持 socket"]
    D --> E["三类上下文严格分工<br/>Reactor 持 socket / Pool 算 / launch 设进程"]
```

> 图例：演进路径；最后节点为最终线程模型——网络所有权恒驻 Reactor。

### 主线 3：无观测 → 守恒可归因（v89-v101）

```mermaid
flowchart LR
    A["server-local trace<br/>boot/session/op 三级"] --> B["双平面导出<br/>JSONL + Prometheus"]
    B --> C["离线 diagnose<br/>confirmed/suspected"]
    C --> D["守恒分解<br/>callback+phase+residual==wait"]
    D --> E["不可见忙 → 精确归因<br/>如 post-drain 1100ms"]
```

> 图例：观测能力逐级增强；终点让"reactor 忙"变成可归因的具体相位。

---

## 4. 文档-代码漂移：一个必须记住的坑

ROUND 文档声称"删除"的模块，git 里**文件还在**——只是停止编译、成为死代码：

```mermaid
flowchart LR
    subgraph doc["ROUND 文档说"]
        D1["v86 删除 agent_tree_legacy"]
        D2["v87 删除 agent_plain_control"]
        D3["v88 删除 agent_session_pool"]
    end
    subgraph git["git 物理状态"]
        G1["文件仍在(402行)<br/>不在 Makefile/CMake"]
        G2["文件仍在(44行)<br/>接线移除"]
        G3["文件仍在(261行)<br/>仅移除编译引用"]
    end
    D1 --> G1
    D2 --> G2
    D3 --> G3
```

| 版本 | 文档声称 | git 实际 |
|------|---------|---------|
| v86 | 删除 `agent_tree_legacy.*` | 文件仍在（402 行），停止编译 |
| v87 | 删除 `agent_plain_control.*` | 文件仍在（44 行），接线移除 |
| v88 | 删除 `agent_session_pool.*` | 文件仍在（261 行），仅移除编译引用 |

> 图例：虚线为"文档语义 ↔ git 物理状态"对应；**阅读历史以编译产物为准，
> 而非源文件存在性**。这是 RSP/3「删除旧路径」在代码层的体现：
> dead-code 化而非物理删除。

---

## 5. 学习结论速记

```mermaid
flowchart TD
    L1["① 协议冻结：能力位协商，RSP/3 不变"] --> L7
    L2["② schema 递增不迁移：拒绝旧版本"] --> L7
    L3["③ 内存/并发有界：固定批量 + 懒加载池"] --> L7
    L4["④ 可重放不变量：catalog 先于 queue"] --> L7
    L5["⑤ 实测/故障驱动：先量化再优化"] --> L7
    L6["⑥ 权限/隐私边界：root-confined Agent"] --> L7
    L7["⑦ dead-code 化而非物理删除"]
```

> 图例：L1-L6 为六条设计纪律，汇入第 7 条（文档-代码漂移的根因）。

---

## 6. 适用范围与边界

- 结论限 v65-v101 当前版本；未来版本需重新核验。
- v91 无独立 git 提交（设计并入 v92 提交）。
- 个别模块行数（如 backup_agent.cpp -865）为 diff 统计，精确值以 git 为准。
- 「删除」表述为逻辑删除（停止编译接线），与 git 物理文件存在性不同。

---

## 参考资料

- 源报告（逐提交三要素事实源）: `records/T0295-0816-backupstream-git-history/evidence/git-history-learning-final.md`
- 知识沉淀: `knowledge/linux-epoll-eventloop/backupstream-v65-v101-arch-evolution.md`
- 仓库: `/home/black/Downloads/backupstream`（main 分支，v65-v101）