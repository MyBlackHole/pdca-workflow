# pgwrecover GIN 索引重放官方化

## 验收标准
- AC-1: ginxlog.c 全部 redo 例程逐行拷贝前端化, 编译 0 警告
- AC-2: 真实 PG18.4 GIN 索引负载样本(多值列+数组)端到端重放,
  产物与 PG 最终态语义级一致
- AC-3: RM_GIN_ID 接线 + pytest 回归
