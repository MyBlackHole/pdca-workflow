---
schema: pdca.asset/v1
id: ontology:domain/core-reconcile-phased-orchestration
type: domain
layer: Knowledge
status: active
summary: reconcile九阶段流水线 + 选项双沿打标 + 物理有序扇出
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-move-unified-relocation-engine
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 后台数据重整编排、选项变更传播、多优先级任务调度场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/data/reconcile/work.c 在仓库中存在且含 reconcile_phases 定义"
- name: constraints
  desc: 编排前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认阶段顺序固定、cookie比对防误删、中断条件三条前提在引用代码中有对应实现"
---

# reconcile九阶段流水线编排

沉淀自 T0493（内核第五轮）。对照 bcachefs
`fs/data/reconcile/work.c`、`fs/data/reconcile/trigger.c`、
`fs/data/reconcile/trigger.h`、`fs/data/reconcile/format.h`、
`fs/opts.c`。

## 核心概念

1. **九阶段固定流水线**：scan → hipri → normal → pending，
   每段分 btree/phys/normal；kick 变化/going_ro/ratelimit 中断
   本轮；干净走完全部才退出；pending 段无 cookie 直接结束
   （`reconcile_phases`、`do_reconcile`）。
2. **选项变更双沿打标 + 半态保护**：按选项类型映射六类扫描；
   pre 注册在途并加 cookie，post 再加并唤醒，析构兜底解注册；
   扫描遇在途跳过，清键时比对 cookie 防误删中间态
   （`bch2_set_reconcile_needs_scan_pre/post`、
   `bch2_clear_reconcile_needs_scan`）。
3. **扫描分型各走各路**：fs 全树、metadata 仅内节点、device 走
   backpointer 反向定位、inum 只扫单文件区间、stripes 只刷新
   可拓宽标志；cookie 编码类型（`reconcile_scan_encode`）。
4. **满目标转 pending 闭环**：仅缺设备/空间不足转 pending 继续，
   其余透传；pending 先预检仍不可行跳过；旋转介质摘链转交
   phys 按 LBA 重排（`check_reconcile_pending_err`）。
5. **物理 LBA 有序扇出**：backpointer 天然有序；仅旋转在线盘
   每盘一线程并行消费；强制从该盘读；跳过在途更新防重入
   （`do_reconcile_phys_thread`）。
6. **三态路由与校验**：need_rb 空→none，pending>hipri>normal；
   pending 无 phys 镜像；validate 硬约束 pending 必 need_rb、
   hipri 必 replicas 位（`rb_work_id`）。
7. **无丢失唤醒范式**：kick 自增 + RCU 取线程唤醒；等待先置态
   再比对；hipri 欠账直接返回不睡；生产者含选项/设备/电源/
   sysfs（`bch2_reconcile_wakeup`、`reconcile_wait`）。
8. **单主线程 + 短暂工人**：常驻单 kthread，phys 阶段才派生闭包
   工人并回收；每 phase 入口冲刷写缓冲，跨 phase 排空 move IO；
   与 copygc/EC 硬边界串行化（`bch2_reconcile_thread`）。

## 复用指南

- 后台重整用固定阶段流水线 + 中断条件，禁止无序抢跑。
- 选项变更传播用双沿打标 + cookie 比对，禁止直接全量重扫。
- 满目标任务转 pending 闭环而非丢弃，下轮预检再入。
