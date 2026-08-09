# T0234 PRD — FastAPI TODO 应用验证 PDCA 流程

## 问题陈述

T0232（ready-set/词汇契约）与 T0233（seam 契约）的新机制已在流程仓库自身
通过契约测试验证，但**从未在真实工程场景实测**。用户要求开发一个新项目
（FastAPI 应用）作为验证载体，用完整 PDCA 周期（plan→do→check→act）跑一遍，
实测新机制在真实开发中的效果与问题。

## 方案

- 应用：独立外部目录 `/tmp/opencode/todo-fastapi/`，FastAPI + SQLAlchemy 2 + SQLite，TODO 待办 CRUD。
- 拆解：按 **router / service / storage** 三模块拆 3 个子任务，每模块一个 seam，
  验证 P3.5 seam 确认 + P4 ready-set 并行调度。
- 词汇契约：接口设计文档启用 `check-design-vocab.py`（拒绝 component/service/
  boundary/API 词）。
- 测试：pytest + FastAPI TestClient（httpx）集成测试。
- 范围：实现 + 测试 + 机制验证，不含 CI/部署/文档完善。
- 环境：应用独立 venv（`.venv/`），依赖声明于 `requirements.txt`。

## 验收标准

- [ ] AC-1: 应用目录 `/tmp/opencode/todo-fastapi/` 含 main/storage/service 三模块 + venv + requirements
- [ ] AC-2: TODO CRUD 全部端点（create/list/get/update/delete）通过 TestClient 集成测试
- [ ] AC-3: 三个 seam 的契约测试全部通过（seam_contract.py 校验测试文件存在且与声明模块一致）
- [ ] AC-4: ready-set 拆解产出依赖图校验 valid（compute-frontier.py）
- [ ] AC-5: 接口设计文档词汇契约通过（check-design-vocab 无违规）
- [ ] AC-6: 全量测试（PDCA 仓库 + 应用）无回归

## 设计决策（用户确认）

- TODO 应用（非认证多模块）；SQLite + SQLAlchemy（非裸 sqlite3）
- 仓内 apps/（非独立目录）；TestClient 集成测试
- 三模块拆解（非单任务）；词汇契约启用
- 范围=实现+机制验证（不含 CI/部署）

## 关键取舍

- SQLite 文件用临时目录（测试隔离），生产用环境变量 DATABASE_URL
- storage 层返回 dataclass/ORM 对象，service 层做业务校验，router 层只做 HTTP 映射

## Seam 分析

### 声明的测试接缝
- seam: tests/test_storage.py -> app/storage.py
- seam: tests/test_service.py -> app/service.py
- seam: tests/test_api.py -> app/main.py

## 范围外

- 用户认证、分页、前端、部署、CI、文档完善
