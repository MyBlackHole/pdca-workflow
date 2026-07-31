# T0161 内容与导航审计

- `audit-skill-content.py --check-budget`：44 个 flow/skill asset 全部存在，`broken_references=0`，baseline 通过。
- audit 已接入 route、execution 和 invocation 的公共 document resolver；更新 baseline 不能掩盖这三类行为漂移。
- `generate-skills-index.py --check`：索引与 44 个实际 asset 一致。
- invocation document check：39 条显式调用边全部有声明且目标类型合法；3 个用户 alias 都指向 existing manual entry。
