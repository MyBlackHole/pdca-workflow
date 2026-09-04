---
schema: pdca.asset/v1
id: ontology:domain/core-discard-boundary-guards
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/core-discard-boundary-guards/1.0.0
summary: discard 边界守卫：open bucket 与设备可写
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "检查本文件 discard-boundary-guards 相关章节的定义完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空"
---


# discard 边界守卫：open bucket 与设备可写

来源：T0189-0802-discard-open-bucket-boundary（bcachefs 风格 Rust 存储引擎
discard/回收边界守卫）。

## 上下文与约束

T0191 建立的 discard worker 只处理队列公平性，不感知桶/设备的回收合法性：
allocate/reclaim/discard 三条路径此前对 open bucket（in-progress write
claim）与不可写设备无守卫，属性模型可构造出 open 桶被转 free 的非法状态。
engine-local 约束：守卫为内存态判定（BTreeSet），无真实设备热插拔，open/close
由显式公共 API 配对。

## 假设与行动

- **守卫错误码分层**（与既有体系一致，调用方可区分硬失败与轮转重试）：
  reclaim 拒绝 -16（live reference 类）、discard 拒绝 -11（未就绪轮转类，
  与 EAGAIN 同码）、allocate 拒绝 -1（设备无效类）。
- **检查顺序**：先状态验证（位置校验 → open/可写 → journal boundary），
  再执行副作用（backpointer 扫描 / 转 free 调用），与上游「先验证状态、
  再转 free」执行顺序一致（discard.c:320-365 区域）。
- **内存态建模**：`open_buckets: BTreeSet<(u64,u64)>` 对应 open_buckets 哈希
  （foreground.h:274-296，`bch2_bucket_is_open_safe` 跳过语义 discard.c:344-
  347/433-436/743）；`rw_devs: BTreeSet<u64>`（初始 [0]）对应 rw_devs 位图
  （background.c:1650-1667，`bch2_dev_get_ioref(WRITE)` discard.c:357-365）。
  均为 std 容器对应上游结构，不新增 bcachefs 不存在的结构体（约束 13）。
- **属性测试模型约束**：影子模型与引擎共享不变量——open 仅允许作用于非 free
  桶；不变量断言：open 桶不得转 free、state==2 必须 NEED_DISCARD、每 op 后
  verify_bucket_indexes。restart op 从磁盘重建模型（data_type 推导状态）。

## 结果与证据

- AC-1..AC-6 全部通过：6 定向测试（open 拒绝 / 不可写三路径拒绝 / fault 无
  半状态 / worker 轮转 open+ready / not_rw 轮转 / 恢复后可回收）+ 属性测试
  16 cases × 1..=40 op（0.69s）+ workspace 200 lib + 10 集成全绿，单文件
  +405 行。
- fault 注入（AC-3）：TransactionRestart 注入下 reclaim 重试成功（无半状态）；
  JournalWrite 注入下 flush_journal 失败后索引一致、恢复后 discard 成功、
  重启持久化引擎 verify 一致。
- 属性测试首版失败输入 [(5,0)]（free 桶 open）：诊断为**模型缺陷而非引擎
  缺陷**，修正模型限制后通过。

## 成功原因

- 错误码分层让三个守卫路径的失败语义可区分，与上游 dev_get_ioref 失败/
  EAGAIN 轮转语义一致。
- 检查顺序「先验证后副作用」保证守卫失败时不产生任何状态变更，配合 fault
  注入可验证「无半状态」。
- 属性测试中「模型与引擎共享不变量」约束（open 仅非 free 桶）把模型层错误
  与引擎层错误分离，minimal 失败输入能快速定位缺陷归属。

## 适用与不适用条件

- 适用：内存态守卫（回收/分配合法性判定）、显式配对 API（open/close）、
  属性模型 + 不变量断言的守卫验证。
- 不适用：真实设备热插拔/故障、I/O 队列中段撤销 open 的并发撤销语义；
  open/close 未配对时引擎不自动清理（与 bcachefs 随事务提交释放不同，
  engine-local 语义）。
- 设备级状态（rw）与桶级状态（open）的定向测试必须拆分：设备级变更
  （set_device_rw(0,false)）会污染同设备全部桶断言，无法在单测试内同时
  验证「同设备 open+ready」与「跨设备 not_rw」。

## 下一轮建议

- 引入多设备拓扑时，rw_devs 初始化改按 sb 成员推导（当前 [0] 硬编码）；
  open/close 配对增加泄漏检测（drop 时校验）。
- 「open/not_rw 桶不转 free」不变量可提升为公开断言工具，与 T0191 的
  「run 后队列空」合并为 worker 守卫断言套件供后续 allocator 变体复用。
