# 快照删除执行专题学习报告（T0533）

> 精读 `fs/snapshots/delete.c` 执行细节；避开 T0519 语义层。
> 事实源为源码。

---

## 一、全景：删除是四段流水线

迁移死键、熔断校验、逐叶提交、置空收尾。入口持恢复运行锁，出口
清进度数组关运行标志（`__bch2_delete_dead_snapshots:1452`）；拒删
转零不报错；完事放行快照检查限流。
**可学**：删除是流水线，入口出口状态机完整。

## 二、v2 索引范围删

有内容必有同快照 inode，先扫 inode 按号删各树区间；Eytzinger 判
 dying，活终点单跳迁移（`delete_dead_snapshot_keys_v2:978`、
 `snapshot_id_dying:831`）。
**可学**：索引快路加单跳迁移，禁止逐键爬树。

## 三、dying 下迁合并

有活孩子搬键到活槽，损伤双存归并；无活叶直接删
（`bch2_delete_dead_snapshot_key:862`）。
**可学**：迁移合并原子，删建同事务。

## 四、落盘四段序

迁移、熔断校验、逐叶提交、置空；墓碑按版本置删；不碰派生记账
（`delete_dead_snapshots_locked`）。
**可学**：分阶段落盘，熔断停全删。

## 五、子卷收尾三步

子孙改挂父，清主置删同事务，unlink 挂钩异步清页缓存
（`subvolume.c`）。
**可学**：收尾三步缺一留下尾巴。

## 六、设计启示

流水线完整、索引快路、单跳迁移、原子合并、分段落盘、三步收尾。

---

## 复核途径

- `sed -n 1452,1500p fs/snapshots/delete.c` 看主循环出入口。
- `grep -n "snapshot_id_dying\|delete_dead_snapshot_keys_v2" fs/snapshots/delete.c` 定位索引。
