# AC-5 证据：父子任务树与 DAG 校验

## 任务树

- T0381（父）0823-async-object-lifecycle：契约设计 + 守卫原语落地 + 压力测试基建
  - T0382 0823-async-lifecycle-tls-migrate：TLS 域迁移（dependencies: []）
  - T0383 0823-async-lifecycle-plain-migrate：plain/ingress/lane 域迁移（dependencies: []）
  - T0384 0823-async-lifecycle-runtime-converge：业务 runtime 标志/拆卸收编（dependencies: [T0382, T0383]）
  - T0385 0823-async-lifecycle-retire-old-api：删旧 API + 全局终验基线（dependencies: [T0382, T0383, T0384]）

## compute-frontier 校验输出

{"valid": true, "ready_set": ["T0381", "T0382", "T0383"], "completed": [], "batches": [["T0381", "T0382", "T0383"], ["T0384"], ["T0385"]]}

旧 API 删除按 wide-refactor 序列置于收尾子任务 T0385；expand 阶段（本任务）旧变体保留为薄封装且被完整测试套件覆盖。
