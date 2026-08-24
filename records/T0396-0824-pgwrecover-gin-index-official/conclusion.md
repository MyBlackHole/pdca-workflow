---
schema: pdca.asset/v1
id: T0396-0824-pgwrecover-gin-index-official
phase: check
source_ids: [T0396-commit-6567f58]
---

## 上下文
GIN 索引(13)为静默缺口且分派不可达。按官方拷贝原则完成 ginxlog.c
前端化并端到端验证。

## 假设与结果
| 假设 | 结果 |
|------|------|
| ginxlog redo 可脱离 gin_private.h 拷贝 | ✅ 缺失 inline 手工补齐 |
| 数组多值负载触发 pending list 全路径 | ✅ UPDATE_META×1875+INSERT_LISTPAGE×11 |

## 分析
- **AC-1** ✅ ginxlog.c 全部 redo 例程逐行拷贝, 编译通过（commit 6567f58）
- **AC-2** ✅ 真实样本语义级一致（test_gin_index_official PASSED,
  applied=1886 含 UPDATE_META×1875/INSERT_LISTPAGE×11/DELETE 等）
- **AC-3** ✅ RM_GIN_ID 接线; 放行条件一次性补齐全部索引方法;
  HINT_MASK 增加 HEAP_COMBOCID 豁免（提交内含）

已知边界: posting tree 分裂(XLOG_GIN_SPLIT)与 pending list 溢出
创建 posting tree(XLOG_GIN_CREATE_PTREE)在本样本中经 FPI 路径覆盖,
独立增量路径待更强负载回归。

## 适用边界
GIN 数据页恢复; COMBOCID/hint 位豁免口径与 standby 一致。

## 下一轮建议
GIST/SPGIST/BRIN 同模式推进; GIN SPLIT/CREATE_PTREE 独立增量样本。

## 附: SP-GiST 依赖分析（下会话直接可用）
- spgxlog.c redo 自包含度高: fillFakeState 构造 fake SpGistState
  (仅 isBuild/redirectXid/deadTupleStorage 三字段被访问)
- 需本地化: spgxlog.h 全部 xl_spg* 结构、SpGistDeadTuple/State 裁剪版、
  SPGIST_* 常量、SGDTSIZE、cmpOffsetNumbers、spgPageIndexMultiDelete
  (spgdoinsert.c)、SpGistInitBuffer(spgutils.c)、spgUpdateNodeLink
  (spgist.h inline)、SpGistInitPage
- WIP 半成品: /tmp/spgist-wip/fe_spgist_aux.c|h (未完成勿用)
- 工作量预估: 与 GIN 相当(1 会话)
