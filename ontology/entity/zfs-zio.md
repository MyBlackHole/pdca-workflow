---
schema: pdca.asset/v2
id: ontology:entity/zfs-zio
type: entity
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-13'
owl_versionIRI: http://pdca.local/ontology/zfs-zio/3.1.1
summary: ZFS ZIO 位图阶段与 transform 栈；已修正文内冲突，仅固定对照版本，采用仍需 claim-review
relations:
  specializes:
  - ontology:concept/domain-entity
  relates_to:
  - ontology:domain/zfs-crypto
  - ontology:pattern/research-diagram-methodology
attributes:
- name: pipeline_bitmap
  desc: 阶段位图与回调栈必须区分
  constraint: 在本页固定对照源码中核对 enum zio_stage 与 ZIO_READ_PIPELINE/ZIO_WRITE_PIPELINE；不可把回调虚构为阶段枚举。
  testable_signal: 逐项比较固定源码枚举、pipeline 定义与本页表格；字符串存在仅是定位，不证明主张成立。
  evidence_level: structure
- name: transform_stack
  desc: 保存缓冲区、可选回调与恢复；checksum 不作为 transform 入栈
  constraint: 对照 zio_push_transform、zio_pop_transforms 和 checksum 两个阶段函数，区分原缓冲区恢复与实际变换回调。
  testable_signal: 核对函数实参、字段赋值与回调条件；只命中 checksum 或 transform 词语不得判为通过。
  evidence_level: structure
revision: 3.1.1
authority: reference
semantic_kind: class
provenance:
  migration_review: focused_source_comparison_only; original_records_source_revision_unresolved
  pre_review_revision: 3.1.0
validation:
  claim_status: unverified
  adoption: claim_review_required
---

# ZFS ZIO：位图阶段与 transform 栈

## 本次修复的范围

旧版把 checksum 同时描述成“非栈校验”和“压入 checksum_func”，并混用阶段枚举、说明性状态和回调。本版撤下这套冲突状态机及未固定来源的数字、源码行号和反例推断，保留原 ID；原 3.1.0 字节在配套验证包的原始输入中保留，旧 records 不回写。

**以下仅以 OpenZFS `zfs-2.2.7`、commit `e269af1b3c7b1b1c000d05f147a2f75e5e72e0ca` 为明确对照基线。** 它不是原研究采用版本的推断，也不是“最新版本”声明。维护源码比对不等于正式 claim-review；全资产继续 unverified / claim_review_required，不能直接成为当前任务 oracle。

## 分开看两种机制

| 机制 | 固定对照源码中的含义 | 不应推出的结论 |
|---|---|---|
| `enum zio_stage` / pipeline 宏 | 阶段用不同 bit 表示，宏通过位或组合；例如 WRITE_COMPRESS、ENCRYPT、CHECKSUM_GENERATE 是独立写阶段 | 每次 I/O 都执行全部可能阶段，或每个阶段都向 transform 栈加一个节点 |
| `zio_push_transform` | 保存原 ABD、原 size、bufsize 和可为空的 transform 回调，链到栈顶，再切换当前 ABD/size | 调用 push 就现场执行传入回调 |
| `zio_pop_transforms` | 逐项取栈顶；回调非空才调用；bufsize 非零则释放当前 ABD；恢复原 ABD/size 并移除节点 | 按虚构压缩／加密／校验状态逐级回退，或按 `is_write` 参数决定回放 |
| checksum 生成／校验 | `zio_checksum_generate` 调用 compute；`zio_checksum_verify` 调用 error 检查并处理错误；这两个阶段函数不调用 push | 校验阶段压入一个 checksum 回调，稍后靠弹栈“撤销校验” |

依据：[阶段和宏 S1](https://github.com/openzfs/zfs/blob/e269af1b3c7b1b1c000d05f147a2f75e5e72e0ca/include/sys/zio_impl.h#L50-L270)、[push/pop S2](https://github.com/openzfs/zfs/blob/e269af1b3c7b1b1c000d05f147a2f75e5e72e0ca/module/zfs/zio.c#L280-L550)、[checksum S3](https://github.com/openzfs/zfs/blob/e269af1b3c7b1b1c000d05f147a2f75e5e72e0ca/module/zfs/zio.c#L4380-L4520)。S2 显示 `zio_pop_transforms` 只有 `zio_t *` 参数；不能从旧说明推导默认8层的深度上限。

## 用动作描述栈，不伪造源码状态

概念顺序是：**保存原缓冲区及可选回调 → 切换为当前缓冲区 → 相关 I/O／阶段处理 → 弹栈时按已保存条件执行回调并恢复缓冲区**。这是解释顺序，不是新的 C 枚举、完整 I/O 时序或所有分支的保证。

对照 S3 的写侧加密尾部，确实有 `zio_push_transform(..., NULL)`：保存与恢复缓冲区不要求存在逆向变换回调。对照 S2，`zio_decompress`、`zio_decrypt` 是回调函数；S1 的阶段枚举没有把它们分别列为 DECOMPRESS/DECRYPT 阶段。不要把“写时加密／压缩”和“读时逆变换”强行解释为同一条对称阶段状态机。

## 后续采用时的核验动作

先取得被研究对象的真实 commit 和文件，再比较阶段枚举、pipeline 宏、push 调用实参、pop 回调条件和 checksum 函数。对每条需要采用的结论保存源码定位、原始观察与适用范围；源码不同则重新核验，不替历史记录选择版本。

本次没有验证 VDEV 调度完整链、所有压缩算法／等级、ABD 边界、运行故障或性能。旧版这些扩展断言已从当前说明撤下，而不是被顺带认证；相关资产仍有各自未验证边界。维护回归只检查已知冲突表达不被重新引入、固定基线与未验证状态仍可见，不把字符串检查等同源码语义验证。
