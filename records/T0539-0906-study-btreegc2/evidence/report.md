# btree GC 全流程学习报告（T0539）

> 基于 T0493 B 向深挖 10 条（GC 即 check.c，无独立 gc.c）。
> 事实源为源码 `fs/btree/check.c`。

---

## 一、全景：GC 即 check

无独立 GC 文件，GC 就是全树扫描加标记清扫，兼做一致性校验。
核心矛盾：扫描与并发提交互相覆盖。
**可学**：合一遍历双重产出。

## 二、全序位点：引用前向搬移

phase>btree>level>pos 字典序，alloc/stripes 最先；排序定遍历序，
保证引用前向搬移不漏标（`gc_pos_btree`、`gc_pos_cmp`）。
**可学**：全序是增量正确根基。

## 三、单调水位发布

位点禁倒退；写序号锁发布，读无锁判已访问
（`gc_pos_set`、`gc_visited`）。
**可学**：发布订阅解耦。

## 四、提交补标：边走边对账

并发提交对已访问更新补跑触发器，不丢计数
（`bch2_trans_commit_run_gc_triggers`）。
**可学**：对账而非停机互斥。

## 五、自底向上与靶深度

按靶深度逐键设位加进度加标记，尾部超位封口；有触发器从叶起，
fsck 强制从叶（`bch2_gc_btree`）。
**可学**：方向封口显式。

## 六、mark 流水线与拓扑

换节点才验拓扑；修版本位图键；有更新预留提交重启；跑触发器重算
（`bch2_gc_mark_key`）；拓扑重写走 journal，先记日志再变异防重放
（`commit_topology_repair_log`）。
**可学**：分阶段；记后改。

## 七、持锁协同与记账

外层读写锁全程持有；入口排空异步父更新；插入断言持锁；尾部唤醒
阻塞分配（`bch2_check_allocations`）；分段启动比对收尾；gens 独立
通道；GC 后合并与预切分片（`bch2_gc_gens`、`bch2_merge_btree_nodes`）。
**可学**：持锁显式；分段协同。

## 八、设计启示

合一遍历、全序位点、单调水位、补标对账、自适应深度、记后改、持锁
显式、分段协同。

---

## 复核途径

- `grep -n "bch2_gc_btree\b\|gc_pos_set\|mark_key" fs/btree/check.c` 定位主流程。
