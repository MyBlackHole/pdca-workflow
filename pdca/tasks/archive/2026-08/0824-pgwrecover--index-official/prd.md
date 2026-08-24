# pgwrecover HASH 索引重放官方化

## 验收标准
- AC-1: hash_xlog.c 全部 redo 例程逐行拷贝前端化, 编译 0 警告
- AC-2: 真实 PG18.4 hash 索引负载样本端到端重放, 产物与 PG 最终态
  经 verify_consistency.py 判定一致(hash 页面为位图/桶结构,
  采用字节级或语义级比对视页面类型)
- AC-3: pg_replay 主循环接线 RM_HASH_ID, pytest 回归通过
