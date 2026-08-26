# PRD — 清理 rdb-config.c 多余代码

## 背景
T3979 将解析链路重构为 `sec_get_*(id)` + 枚举注册表后，`libs/rdb-config.{c,h}`
与 `libs/tests/param_registry_test.c` 中仍存在重构前的遗留噪声：
1. `config_param_desc_t.owner` 字段——定义存在、14 条表数据已填（如 `"shared"`），
   但 `sec_walk_*` 与 `config_dump_params` 从不读取，仅 `param_registry_test.c:71`
   做非空断言，属纯死字段（与 T3978 用户指出的 name 冗余为同类问题）。
2. `rdb-config.c:259` `/* ---- T3978 参数注册表本体 ---- */` banner 下方无任何代码，
   T3979 已覆盖，为空遗留注释。
3. `rdb-config.h:105` 注释称"完整复刻 sec_resolve 四层解析链"，而 sec_resolve_*
   已随 T3979 移除，描述已失实。
4. `config_get_int_env`（声明 header:83-94，定义 c:122-137）全仓库 0 调用
   （含测试），为死函数；但它是公开 API，删除有对外兼容性考量。

## 清理范围（见 task.json requirements.items）
- A/B/C 为确定项，无兼容性风险。
- D 为待决项：`config_get_int_env` 是否删除需用户确认。

## 验收（见 task.json acceptance.criteria）
AC-1 owner 零引用；AC-2 全量测试零回归；AC-3 config_get_int_env 按决断；
AC-4 注释清理无误导。

## 影响与风险
低。删死字段/死函数不改变任何运行时行为（无调用路径）。风险点仅在于
config_get_int_env 若被本仓库外消费者依赖——已确认本仓库内零引用，
删除安全；若作为对外库接口则需在 CHANGELOG 标注。

## 测试策略
依赖既有 `param_registry_test`（迁移 owner 断言后）与全量 `xmake test`
（45 用例）作为回归护栏；无新增测试必要（清理不改变行为）。
