# T0237 PRD — api/router 层：FastAPI 路由 + 集成测试

## 目标
实现 `/tmp/opencode/todo-fastapi/app/main.py`：FastAPI 应用，TODO CRUD 端点
（POST/GET /todos、GET/PUT/DELETE /todos/{id}），依赖注入 service 层。
依赖 T0236 service 层。

## 验收标准
- [ ] AC-1: main.py 定义 FastAPI app + 5 个 CRUD 端点
- [ ] AC-2: Pydantic 请求/响应模型（TodoCreate/TodoUpdate/TodoOut）
- [ ] AC-3: tests/test_api.py 用 TestClient 集成测试全部端点
- [ ] AC-4: 全量测试无回归

## Seam 分析
### 声明的测试接缝
- seam: tests/test_api.py -> app/main.py
