# T0189 Convergence Map

记录：`T0189-0802-discard-open-bucket-boundary`

## 收敛判据 → 证据映射

| 收敛判据 | 证据 | 状态 |
|---|---|---|
| AC-1 实现前对照上游源码 | ev-ac1（ac1-source-anchors.md） | 满足 |
| AC-2 discard 边界守卫：need_discard + journal boundary + 设备可写 + 无 open/live reference 才转 free | ev-ac2（代码：allocate/reclaim/discard 三处门禁 + 定向测试） | 满足 |
| AC-3 索引与 generation 同事务、故障无半状态 | ev-ac3（fault 注入测试：TransactionRestart/JournalWrite + 重启一致） | 满足 |
| AC-4 错误路径全覆盖：EEXIST/EAGAIN/JournalWrite/TransactionRestart/process 重启 | ev-ac4（worker 轮转测试 + fault 测试 + proptest restart op） | 满足 |
| AC-5 属性验证：open/live/discard 未完成不复用 | ev-ac5（open_bucket_discard_model_protects_open_from_reuse，16 cases） | 满足 |
| AC-6 全量验证门禁：workspace 测试 + fmt + 变更范围 | ev-ac6（lib 200/200、集成 10/10、fmt 通过、单文件 +405） | 满足 |
| A4 代码审查 0 blocking | review-report.md | 满足 |

## 未收敛项

- 无。两项 LOW 观察（rw_devs 初始 [0] 硬编码、open_bucket 不校验位置）作为后续技术债记录，不阻塞收敛。
