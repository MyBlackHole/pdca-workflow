# T0236 PRD — service 层：TODO 业务逻辑/校验

## 目标
实现 `/tmp/opencode/todo-fastapi/app/service.py`：TODO 业务规则（title 非空校验、completed
翻转、404 语义）。依赖 T0235 storage 层，是 T0237 api 层前置。

## 验收标准
- [ ] AC-1: service.py 提供 TodoService（依赖 storage 数据访问）
- [ ] AC-2: 校验规则：title 非空、超长拒绝；不存在的 id 抛 NotFound
- [ ] AC-3: tests/test_service.py 通过（业务规则 + 与 storage 集成）
- [ ] AC-4: 全量测试无回归

## Seam 分析
### 声明的测试接缝
- seam: tests/test_service.py -> app/service.py
