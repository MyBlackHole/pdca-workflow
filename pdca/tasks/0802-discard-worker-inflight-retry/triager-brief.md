# T0190 Triage Brief

## 分类

- 类型：enhancement
- 场景：development
- 父任务：T0189

## 本地源码核验

- `fs/alloc/discard.c:116-143`：discard in-flight 集合返回 EEXIST/EAGAIN 并限制并发。
- `fs/alloc/discard.c:145-219`：提交 discard 后由 endio/事务完成状态收束。
- `fs/alloc/discard.c:429-539`：need_discard worker 遍历、重试、journal commit 与推进。
- `fs/alloc/discard.c:560-598`：going-ro、异步 worker 与 fastpath 调度边界。

## 查重

T0189 已完成 engine-local boundary、need_discard 索引和受控 discard API；in-flight 去重、
EEXIST/EAGAIN worker 调度尚未实现，未发现同范围活动任务。

## 推荐

只实现可测试的 engine-local worker 状态机和重试边界，不接入真实 block-device TRIM。
