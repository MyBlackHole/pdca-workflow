# 双轴代码审查报告（T0381 Do 阶段）

审查对象：9a0f531（后经 a589923、e8bbf11 两笔修复提交收口）

## 标准轴

- 硬违规 4（同一根因）：reactor.cpp:895/908/927、work_pool.cpp:532 超 .clang-format ColumnLimit:80 —— 已在 a589923 全部折行修复，style_check_ok 复验通过（8 行克隆=7 信息级、12 行=0）。
- 判断项：source_kind 钳制双处（submit 参数侧与 impl 内部，T0385 删旧时收敛为一处）；enqueue_impl 8 参 Data Clump（legacy 包装删除后自然消解）；priority↔flags 双向映射两处（迁移期有意保留）；backoff 裸魔数；guard 原语暂仅测试消费（有 T0382-T0385 迁移背书）。

## 规范轴

- Blocking = 0。
- (a) spec 缺失项 1 项已补：expand 契约断言旧接口存在 → test_legacy_variants_remain 落地（a589923）；"句柄校验守卫"由 guard 原语承载，口径澄清记录于本报告。
- (b) 范围蔓延：无实质蔓延（VERSION/CHANGELOG 为发布配套）。
- (c) 相悖项：guard 单原子字计数与 ADR"不引入引用计数"字面张力——ADR 否决的是热路径自动持引用的 refcount 基建，guard 为控制面显式窗口原语、零热路径接入，判定不构成违背。

## 审查后追加发现与修复

- TSan 揭示 WAIT 背压测试自身竞态（入队成功≠派发完成），按终态不变量重写断言（e8bbf11），TSan 连续 3 轮稳定通过。

## 门禁判定

标准轴硬违规修复后归零；规范轴 Blocking = 0。门禁通过。
