# bcachefs reconcile 编排专题学习报告（T0528）

> 基于 T0493 A 向深挖 10 条（九阶段/双沿/分型/闭环/扇出/路由/旁路/
> 唤醒/单线程/边界）。事实源为源码 `fs/data/reconcile/`。

---

## 一、全景：九阶段流水线

scan→hipri→normal→pending，每段分 btree/phys/normal；kick 变、
只读、限流中断本轮；干净走完全部才退；无 cookie 跳过 pending
（`work.c:reconcile_phases`）。
**可学**：后台重整固定流水线加中断条件，禁无序抢跑。

## 二、选项双沿打标

按选项映射六类扫描；pre 注册在途加 cookie，post 再加唤醒，析构
兜底；遇在途跳过，比对 cookie 删键防误删（`set_needs_scan_pre/post`）。
**可学**：选项传播双沿打标加 cookie 比对，禁全量重扫。

## 三、扫描分型

fs 全树、元数据仅内节点、device 反向定位、inum 单区间、stripes
只刷标志；cookie 编码类型（`reconcile_scan_encode`）。
**可学**：扫描按类型分流，各走各路。

## 四、pending 闭环

仅缺设备空间转 pending 继续；先预检；旋转介质摘链转 phys 重排
（`check_reconcile_pending_err`）。
**可学**：满目标转待定闭环而非丢弃。

## 五、物理扇出与路由

backpointer 天然有序；旋转盘每盘一线程；强制从该盘读；跳过在途
（`do_reconcile_phys_thread`）；三态路由加硬约束校验
（`rb_work_id`）。
**可学**：物理有序扇出；路由硬约束。

## 六、索引唤醒与线程

叶走位图树，内节点走扫描条目；kick 自增唤醒；欠账直接返不睡；
单主线程，phys 才派生工人；入口冲刷写缓冲，跨段排空 move IO；
与清运纠删硬边界串行（`bch2_reconcile_thread`）。
**可学**：唤醒无丢失；单主加短暂工人；边界串行化。

## 七、设计启示

固定流水线、双沿打标、分型扫描、 pending闭环、有序扇出、硬约束
路由、无丢失唤醒、边界串行。

---

## 复核途径

- `grep -n "reconcile_phases\|do_reconcile_phase\|rb_work_id" fs/data/reconcile/work.c fs/data/reconcile/trigger.h` 定位编排。
