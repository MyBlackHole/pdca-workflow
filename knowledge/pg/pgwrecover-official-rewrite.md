# pgwrecover 官方源码前端化重构（btree/heap WAL 重放）

## 背景
pgwrecover 自造简化 WAL 重放实现与 PG 官方语义存在系统性偏差
（btree 8 处、heap 操作码缺 10 种）。T0401 按"直接拷贝 PG 源代码逻辑，
补充缺失、删除不要"原则重构。

## 方法论：官方源码前端化三步法

1. **逐行拷贝**：从 REL_18_STABLE 拉 redo 源（nbtxlog.c/heapam_xlog.c/
   bufpage.c/xlogutils.c/nbtdedup.c/pruneheap.c/rmgrdesc/heapdesc.c/
   storage.c），保留函数结构、变量名、注释——便于上游 diff 对照升级
2. **机械替换**（仅三类）：
   - `elog(ERROR/PANIC)` → 前端版（stderr + exit，无 longjmp）
   - `palloc/pfree` → malloc/free（宏）
   - buffer manager → fe_buffer 层（XLogReadBufferForRedo* 全分支语义：
     FPI 恢复 / LSN 幂等 / RBM_ZERO 跳过幂等 / PageIsNew→InvalidBuffer）
3. **删除**后端设施：MemoryContext、InHotStandby 快照冲突、FSM 维护、
   relcache 失效、锁、btree_mask

## 关键语义锚点（自造实现最易错处）

| 锚点 | 官方语义 |
|------|---------|
| IndexTuple 来源 | `XLogRegisterBufData` → block data，**不是**主数据区偏移 |
| 页 LSN | redo 设为记录 **EndRecPtr**（非起始 LSN） |
| PageInit | `pd_pagesize_version = BLCKSZ \| 4`(0x2004)；btree 页 `pd_upper = pd_special - sizeof(BTPageOpaqueData)` 必须同步 |
| NEWROOT | blkref#2 是 meta 页 root 指针更新；payload 用 PageAddItem 标准布局 |
| XLOG_FPI (PG18) | FPI 独立为 XLOG rmgr 记录，需单独放行落页 |
| ENOENT | 从零重放场景按空页处理（write 侧 O_CREAT），禁止报错 |
| `%m` 格式串 | 前端错误路径下 dopr 有死循环风险——错误信息避免 %m |

## 验证口径（verify_consistency.py）

严格比对：lp 结构（off/flags/len）、MVCC 链（xmin/xmax/ctid）、
infomask 非 hint 位、t_bits、用户数据。
豁免（PG 设计不写 WAL，standby 重放产物同样如此，首次访问自动重建）：
pd_checksum、pd_lsn/prune_xid/flags、t_cid、
infomask hint 组（XMIN/XMAX COMMITTED|INVALID 0x0F00）、自由空间碎片。

## 已知边界
freeze plan(nplans>0) 无专项回归样本；VM/FSM 文件不输出；
逻辑解码操作为 no-op（同官方）。
