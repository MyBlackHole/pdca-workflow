# ID 撞车清理：全链路重分配 23 组重复 task_id

## 问题

`task_identity.py` 统一身份入口引入前，历史任务重复分配 task_id。doctor `identity.duplicate_task_ids` 报告 23 组撞车，每组同一 task_id 被 2-3 个**真实独立任务**占用，各自有独立 task.json/record/归档状态。撞车根因全部为 `legacy`。身份唯一性是 identity 合约的核心（T0261 实现合约、T0262/T0263 观察上线效果），当前 `valid=False` 阻断体系健康度。

## 方案

对 12 组全归档可处置撞车执行全链路重分配：为"非主流"方分配新 ID（T0275-T0286），同步 task.json 的 `id`/`meta.record`、records 目录名、parent/children 引用链、归档目录名。11 组含活跃任务的撞车跳过，记录到处置报告"待办"段，待其归档后另立任务。

**主流方判定规则**（用于重分配裁决）：
1. 被其他任务作为 parent 引用（任务树主干）→ 保留原 ID。
2. 无引用时，record 格式规范（`Txxxx-slug`）优先；旧格式（`Rxxxx` 或裸 `Txxxx`）重分配。
3. 其余按创建时间早者保留。

## 用户故事

- 作为体系维护者，运行 doctor 时 identity 段不再报告 duplicate_task_ids，`valid=True`。
- 作为任务引用方，parent/children 链指向唯一任务，无歧义。

## 验收标准

- [ ] AC-1: 新增处置脚本 `scripts/remediate-id-collisions.py`，输入裁决表，对 12 组重分配方执行 task.json 的 `id`/`meta.record` 改写
- [ ] AC-2: 重分配同步 records 目录重命名（`records/<旧record>/` → `records/<新record>/`）
- [ ] AC-3: 重分配同步归档目录重命名（任务目录移动至新 ID slug 命名）
- [ ] AC-4: parent/children/dependencies 引用链中旧 ID 全局替换为新 ID，引用完整性通过 `ticket_dag`/校验器验证
- [ ] AC-5: 运行 doctor 后 `identity.duplicate_task_ids` 从 23 组降至 ≤12 组（仅剩活跃组待办）
- [ ] AC-6: 处置报告 `collision-remediation-report.md` 列明 12 组裁决明细 + 11 组待办及原因，存 records/ 下
- [ ] AC-7: 新增测试覆盖重分配脚本的幂等性与裁决表完整性，全量测试通过且无回归

## Seam 分析

### 声明的测试接缝
- seam: tests/test_remediate_id_collisions.py -> scripts/remediate-id-collisions.py

## 实现/测试决策

- 处置脚本必须**幂等**：重复运行不产生二次改写；执行前 dry-run 模式输出将改动的完整清单。
- 裁决表固化在 `scripts/remediate-id-collisions.py` 内（常量），测试断言其与 doctor 实况一致。
- records 重命名时同步校验 `manifest.jsonl` 内 file 路径与新 record 目录一致。
- 保留方 task.json 不改写（ID 不变），避免破坏任务树。
- 参考 T0210b 后缀先例与 task_identity.py 的唯一性校验，新 ID 分配须通过 ID 唯一性检查。

## 范围外

- 不处理 11 组含活跃任务的撞车（T0216/T0218/T0219/T0220/T0221/T0222/T0228/T0229/T0248/T0250/T0252），记录待办。
- 不修改任务内容（prd.md/clarifications/evidence）本身，仅 ID/record/目录/引用链。
- 不引入旧任务格式兼容逻辑（CONTEXT 约定）。

## 备注

- 来源：T0272 健康度诊断修复候选 highest 项（id_collision 23 组，阻断级）。
- 新 ID 分配 T0275-T0286 避开本任务 T0274。
