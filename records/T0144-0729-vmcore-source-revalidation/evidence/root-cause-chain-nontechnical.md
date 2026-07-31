# T0144 根因链路图（非技术版）

## 一句话结论

系统在更换 dm-19 的“存储路线表”时，本应关闭请求入口；但入口缺少一次维护状态检查，
一个请求拿着旧路线表出发。旧路线表随后被销毁，请求完成回来时再次查阅旧路线表，
因该内存已经不存在而导致内核崩溃。

## 根因主链

```mermaid
flowchart TD
    A["① dm-19 是一个虚拟磁盘<br/>底层实际走 NVMe 存储路径"] --> B
    B["② 一笔 I/O 请求进入<br/>请求记住当时的旧存储路线表<br/>(old dm_target)"] --> C
    C["③ 系统开始更新 dm-19 路线表<br/>按设计应暂停接收新请求"] --> D
    D["④ 请求入口缺少维护状态检查<br/>(未检查 DMF_BLOCK_IO_FOR_SUSPEND)"] --> E
    E["⑤ 暂停期间仍有请求进入<br/>并继续携带旧路线表执行"] --> F
    F["⑥ 系统安装新路线表<br/>随后销毁旧路线表"] --> G
    G["⑦ 底层 NVMe 请求完成返回<br/>仍按记录访问旧路线表"] --> H
    H["⑧ 旧路线表内存已被解除映射<br/>读取不存在的内存"] --> I
    I["⑨ Linux 内核触发 page fault<br/>服务器崩溃并生成 vmcore"]

    U["尚未确定：<br/>具体是哪项外部操作使暂停中的队列再次接收请求"] -. "触发条件未完全还原" .-> E

    classDef normal fill:#dbeafe,stroke:#2563eb,color:#111827;
    classDef defect fill:#fef3c7,stroke:#d97706,color:#111827,stroke-width:3px;
    classDef failure fill:#fee2e2,stroke:#dc2626,color:#111827,stroke-width:3px;
    classDef unknown fill:#f3f4f6,stroke:#6b7280,color:#111827,stroke-dasharray:5 5;

    class A,B,C,F,G normal;
    class D,E defect;
    class H,I failure;
    class U unknown;
```

## 正常设计与本次故障对比

```mermaid
flowchart LR
    subgraph N["正常情况"]
        N1["挂出维护标志"] --> N2["关闭请求入口"]
        N2 --> N3["等待在途请求全部完成"]
        N3 --> N4["更换路线表"]
        N4 --> N5["销毁旧路线表"]
        N5 --> N6["重新开放入口"]
    end

    subgraph F["本次故障"]
        F1["挂出维护标志"] --> F2["队列被再次开放"]
        F2 --> F3["入口未检查维护标志"]
        F3 --> F4["新请求携带旧路线表出发"]
        F4 --> F5["旧路线表被销毁"]
        F5 --> F6["请求完成时访问已销毁内存"]
        F6 --> F7["内核崩溃"]
    end

    classDef safe fill:#dcfce7,stroke:#16a34a,color:#111827;
    classDef bad fill:#fee2e2,stroke:#dc2626,color:#111827;

    class N1,N2,N3,N4,N5,N6 safe;
    class F1,F2,F3,F4,F5,F6,F7 bad;
```

## 为什么一个入口检查就能修复

```mermaid
flowchart TD
    A["请求到达 dm-19 入口"] --> B{"系统是否正在暂停/换表?"}
    B -- "是" --> C["不让请求继续<br/>放回队列等待"]
    C --> D["新路线表安装完成"]
    D --> E["请求重新进入<br/>取得新路线表"]
    B -- "否" --> E
    E --> F["正常下发到底层存储"]
    F --> G["正常完成"]

    X["结果：请求不会再携带旧路线表<br/>跨越旧表销毁时点"] -.-> G

    classDef guard fill:#fef3c7,stroke:#d97706,color:#111827,stroke-width:3px;
    classDef safe fill:#dcfce7,stroke:#16a34a,color:#111827;

    class B guard;
    class C,D,E,F,G,X safe;
```

修复本质：

```text
维护标志已置位
    → 请求入口立即让请求等待
    → 不记录旧路线表
    → 不向底层设备下发
    → 换表完成后重新尝试
    → 此时取得新路线表
```

## iSCSI 在图中的位置

```mermaid
flowchart LR
    A["崩溃前出现 iSCSI 设备事件"] --> B{"是否是本次请求的实际存储路径?"}
    B -- "否" --> C["本次请求实际走 nvme38n1<br/>排除 iSCSI 直接触发"]
    A -. "可能引发全局存储重配置" .-> D["是否间接促成 dm-19 换表?"]
    D --> E["缺少 iSCSI→multipathd→dm-19<br/>的完整操作记录"]
    E --> F["结论：间接关系未证实"]

    classDef fact fill:#dbeafe,stroke:#2563eb,color:#111827;
    classDef unknown fill:#f3f4f6,stroke:#6b7280,color:#111827,stroke-dasharray:5 5;

    class A,B,C fact;
    class D,E,F unknown;
```

## 面向管理和事故复盘的表述

| 层次 | 通俗表述 | 结论 |
|---|---|---|
| 直接原因 | 请求返回时访问了一张已经销毁的旧路线表 | 已证明 |
| 根本原因 | 存储请求入口没有在系统暂停换表时再次检查维护标志 | 已证明 |
| 促成条件 | 暂停期间队列被某个外部动作重新允许接收请求 | 机制明确，具体动作未确定 |
| 实际数据路径 | 本次故障请求走 `dm-19 → nvme38n1` | 已证明 |
| iSCSI | 不是本次请求的直接路径；是否间接促成换表无法确认 | 直接排除，间接未证实 |
| 修复方向 | 暂停标志置位时，把请求退回队列，换表后再试 | 与根因直接对应 |

