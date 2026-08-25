# pgwrecover BRIN 索引重放官方化

## 验收标准
- AC-1: brin_xlog.c 全部 redo 例程逐行拷贝前端化, 编译 0 警告
- AC-2: 真实 PG18.4 BRIN 负载样本端到端重放, 语义级一致
- AC-3: RM_BRIN_ID 接线 + pytest 回归
