# T0261 Triage Brief

- 分类：enhancement / research。
- 来源：T0260 Act partial 跟进，处理首个阻断点 P0。
- 已证实：23 个 task ID 冲突、5 个 event path mismatch、全量聚合 fail-closed。
- 未证实：原子 ID 分配缺失是否为唯一根因；可能还包含旧迁移、复制或 record 生命周期漂移。
- 查重：T0159 实现身份与聚合合约；T0166 加固时间线；均未验证当前跨任务 ID 冲突根因。
- 门禁：当前保持 Plan；不得自动写 final_confirmation 或进入 Do。
