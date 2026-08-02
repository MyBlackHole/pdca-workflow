# T0191 Triage Brief

## 分类

- 类型：enhancement
- 场景：development
- 父任务：T0190

## 查重与事实核验

- T0190 已实现单桶 in-flight 去重、EAGAIN 重试与重启再发现。
- 当前 worker 只按单个队列项执行，尚无多桶顺序、公平性和属性模型证据。
- 真实 block-device discard/设备队列不在本任务范围。

## 本地语义锚点

- `fs/alloc/discard.c:429-539`：need_discard btree 遍历、提交、重试和推进。
- `fs/alloc/discard.c:560-598`：going-ro、异步 worker 与 fastpath 调度边界。

## 推荐

先验证 engine-local 多桶调度公平性和重启收敛，再决定是否单独实现设备 I/O 适配层。
