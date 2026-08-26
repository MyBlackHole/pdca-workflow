---
schema: pdca.knowledge/v1
topic: config
slug: compile-time-param-id-binding
source_record: records/T3979-0826-sec-get-param-api-refactor/conclusion.md
---

# 枚举参数 ID 编译期绑定：消灭配置身份漂移

## 范式
把"配置参数的身份"从运行期字符串名提升为编译期枚举 ID：
- `typedef enum { PARAM_xxx, ..., PARAM_COUNT } config_param_id_t;`
- 单一事实来源：`static const config_param_desc_t g_table[PARAM_COUNT]` 指定初始化器（漏项即少条目，可测），表按枚举索引 O(1)。
- 消费 API：`sec_get_int/bool/str(id)` 单参函数，内部遍历四层解析链（env > 专用 section > 全局兜底 section > def）。
- 删除"六参 sec_resolve_*(section,key,env,def,...)"式多参解析——它让注册表（元数据）与解析（逻辑）脱节，漂移只能靠测试事后发现。

## 反模式（已踩）
- 先建注册表元数据、再单独接解析（T3978）→ 表是死数据，name 字段冗余，易漂移。
- 注释声称"已同步"但未实测（T3979 Check 发现 rdb_config_test.c:384 注释仍含旧符号字面）→ 任何"已同步"断言必须以 grep 实证，而非信任。

## 适用边界
- 适用：参数集合固定、跨多模块共享同一解析语义（如 rdb.conf 安全参数）。
- 不适用：运行时动态增删参数的插件式配置。
- 安全参数默认 fail-closed：BOOL 任一层非法即返回 -1，不应静默降级。

## 复用触发
- 下次做配置类重构/新接入参数时，直接采用"枚举 ID + 单参 API + 四层链静态表"，跳过中间态。
- 属 T3977(缓存/热重载张力)、T3978(注册表脱节) 的同类配置治理脉络。
