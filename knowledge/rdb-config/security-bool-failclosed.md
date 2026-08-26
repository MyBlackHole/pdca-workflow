# 安全布尔开关 fail-closed 正确范式（rdb-config）

## 原则
安全相关的布尔开关（审计 / 鉴权 / mTLS）在任何解析失败、env 脏值、配置缺失时
都必须 **fail-closed**（默认处于更安全的状态：审计开启、鉴权开启、mTLS 开启），
绝不能 fail-open。

## 实现范式（与既有 mtls_enabled 一致）
- **参数声明**：用 `CFG_TYPE_BOOL`（非 `CFG_TYPE_INT`）。底层 `sec_walk_int`
  的 env / def 层改用 `parse_strict_int`，非法值返回 -1；`sec_walk_bool` 的
  def 层同样用 `sec_parse_strict_bool`，不可再走宽松 `atoi`。
- **消费者**：统一 `sec_get_bool(param)`。
  - *解析 / 初始化路径*（有错误返回通道）：`<0` 时直接 `return -1` 并写
    `err_msg` / `fprintf(stderr)`，启动期响亮失败。
  - *谓词路径*（无错误返回，如 `bool key_is_enabled(void)`、logger 审计判断）：
    直接 `return sec_get_bool(...) != 0;` 或 `if (!sec_get_bool(...))`，利用
    `-1 != 0` 为真的天然 fail-closed。

## 反模式（陷阱）
- **禁止掩盖错误**：不要写 `if (x < 0) x = 1;` 把 -1 改写成 1。这既掩盖了
  "配置读取出错 / 未配置"的状态，也违背"与 mtls_enabled 一致"的范式。
  `sec_get_bool` 返回 -1 时，`-1 != 0` 已经是 fail-closed，无需也不应改写。
- **禁止宽松 atoi**：INT 安全开关走 `atoi` 会把脏值静默降级为 0（fail-open），
  与 BOOL 开关的 fail-closed 形成内部不一致（T3980 HIGH-1 根因）。
- **测试覆盖盲区**：经公共 API（如 `rpc_init_config`）调用的开关，用旧
  `sec_get_int("2")` 宽松语义写的测试（断言 `== 2`、断言 `init == 0`）会漏检；
  必须为"非法 env → 响亮失败"补充用例。且 `grep sec_get_int(...)` 无法捕获这类
  经 API 调用的残留，需结合模块级测试（如 `rpc_config_test`）回归。
