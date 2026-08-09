---
schema: pdca.asset/v1
id: T0234-0809-fastapi-app-verify
phase: check
source_ids: [convergence-map-v2, ready-set-valid, seam-contract-valid, app-tests-pass, bug-found, pdca-full-suite]
---

# Conclusion — FastAPI 应用验证 PDCA 流程

## 上下文

T0232（ready-set/词汇契约）与 T0233（seam 契约）的新机制此前仅在流程仓库
自身验证。本任务用**真实工程载体**（FastAPI + SQLAlchemy + SQLite TODO 应用，
外部项目 `/tmp/opencode/todo-fastapi/`）完整走 plan→do→check，实测新机制
在真实开发中的效果。

关键方向修正：用户明确"web 应用是测试 PDCA 的，不能放入本项目"——应用从
仓内 `apps/todo-fastapi/` 移出，改为**外部项目模式**（init-external.sh 接入），
任务/记录/证据仍留在 PDCA 中心仓库。

## 假设与结果

| 假设 | 结果 |
|------|------|
| ready-set 调度驱动真实拆解 | ✅ AC-4：compute-frontier valid=true，分批 [[T0235],[T0236],[T0237]]，storage 完成后 T0236 自动就绪 |
| seam 契约守护真实 PRD | ✅ AC-3：seam_contract.py 对 3 个 PRD 校验 valid=true（测试文件存在 + 模块一致） |
| TestClient 集成测试可发现真实 bug | ✅ AC-2：发现并修复 get_db 缺 commit 导致跨请求不可见的真实缺陷 |
| 词汇契约机制工作正常 | ✅ AC-5：拒绝 component/API/boundary、接受 module/interface/seam |
| 应用全量测试通过 | ✅ AC-2：storage 6 + service 10 + api 11 = 27 passed |
| PDCA 全量无回归 | ✅ AC-6：130 passed + 13 subtests |

## 分析（新机制实测发现）

1. **P3.5 seam 门禁在真实任务生效**：3 个子任务 PRD 各声明 1 个 seam，
   seam_contract.py 逐一校验通过——门禁对"PRD 声明 vs 实际代码"守护有效。

2. **ready-set 调度正确**：依赖链 T0235→T0236→T0237 串行，初始 ready=[T0235]，
   storage 完成后 T0236 自动 ready——分批调度与预期完全一致。

3. **集成测试捕获真实 bug**：TestClient 测试发现 create 后 GET/PUT 返回 404，
   根因 `get_db` 缺 `commit()`，跨请求事务未落盘。集成测试（真实请求链路）
   的价值得到实证。

4. **词汇契约适用范围边界**（重要发现）：check-design-vocab 的禁用词表
   （component/service/API/boundary）针对**接口设计文档**，但对普通 PRD 文本
   误报（T0234 PRD 自身含 component/service/API 词）。契约需限定场景
   （仅 design 文档），不应误用于需求文档。

5. **门禁对 PRD 格式的严格要求**：P6 转换要求 `## 验收标准` 精确标题 +
   schema 严格校验（meta.note 非法、status 枚举），真实任务第一次跑需修正
   格式——门禁真实阻止了不合规任务进入 Do。

6. **外部项目模式可行**：代码在 `/tmp/opencode/todo-fastapi/`，任务在 PDCA
   仓库，register-evidence 可登记外部文件（复制进 evidence），AGENTS.md 经
   init-external.sh 正确接入。

## 适用边界

- seam/ready-set/词汇契约三机制在真实 development 任务中全部可执行、有效。
- 词汇契约需要限定适用文档类型（设计文档，非需求文档）。
- 外部项目模式下代码与证据分离，register-evidence 以复制快照登记。

## 下一轮建议

- 修正 check-design-vocab 的适用场景限定（仅 design 文档，需求/PRD 不检查）。
- 将 seam_contract 集成到 CI 门禁（T0233 遗留建议）。
- 应用外部项目可保留作为后续机制验证的复用载体。
