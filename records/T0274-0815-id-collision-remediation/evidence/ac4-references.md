# 引用链完整性验证（T0274 apply 后）

## 上下文感知引用替换结果

撞车组 T0214（CDM/报表树 与 RPC 树 纠缠）按引用者 slug 上下文判定归属：

| 引用者 | 归属链 | parent 处理 |
|---|---|---|
| 0804-report-subscheme-docs（→T0278） | CDM | T0214 → T0277（改向重分配方） |
| 0804-cdm-data-cli（→T0279） | CDM | T0214 → T0277（改向重分配方） |
| 0804-rpc-epoll-multireactor（保留 T0215） | RPC | 保持 T0214（指向保留方） |
| 0805-worker-adaptation | RPC | 保持 T0214（指向保留方） |
| T0216/T0218/T0219/T0220/T0221/T0222（跳过组） | — | 整组未改写 |

## 引用链终态（apply 后实际验证）

- `T0277`（cdm-report-center）：parent=None，children=`['T0278','T0216','T0279','T0218','T0219','T0220','T0221','T0222']`。
- `T0278`（report-subscheme-docs）：id=T0278，parent=T0277 ✓。
- `T0279`（cdm-data-cli）：id=T0279，parent=T0277 ✓。
- 保留方 `T0215`（rpc-epoll-multireactor）：id=T0215，parent=T0214 未改 ✓。
- 保留方 `T0214`（rpc-epoll-industrial-align）：id=T0214，parent=T0213 未改 ✓。
- 活跃任务 `0805-rpc-epoll-worker-supply-followup`：id=T0216、parent=T0215 未改 ✓。

## 悬空引用扫描

全库 142 个任务中悬空引用 7 处，全部为**既有遗留**（T0150-parquet-format-research → T0151-T0157 缺失），与本次重分配无关（该文件 apply 未触碰，git diff 无改动）。

## 幂等性

重复 apply 后 task.json 文件 digest 全库一致（无二次改写）。
