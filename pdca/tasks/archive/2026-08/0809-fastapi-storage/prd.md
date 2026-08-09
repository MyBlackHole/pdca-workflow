# T0235 PRD — storage 层：SQLAlchemy TODO 模型 + 数据访问

## 目标
实现 `/tmp/opencode/todo-fastapi/app/storage.py`：SQLAlchemy 2 TODO 模型 + CRUD 数据访问
（Session 依赖、SQLite 引擎工厂）。是 T0236 service 层的直接前置。

## 验收标准
- [ ] AC-1: storage.py 定义 Todo ORM 模型（id/title/completed/created_at）
- [ ] AC-2: 提供 create/get/list/update/delete 数据访问函数
- [ ] AC-3: SQLite 连接用环境变量 DATABASE_URL（测试用临时目录）
- [ ] AC-4: tests/test_storage.py 通过（round-trip CRUD + 数据一致性）
- [ ] AC-5: 全量测试无回归

## Seam 分析
### 声明的测试接缝
- seam: tests/test_storage.py -> app/storage.py
