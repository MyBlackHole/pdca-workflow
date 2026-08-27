# T3985 Do 阶段执行证据

任务：统一 `rdb-config` `parse_config` 入口，消除启动期与运行期重复解析（init_config 独占 parse，各模块 init 去 config_file 参数从 store 读取，reload 走 init_config）。

## 一、编译验证（xmake，全部 build ok）

| 目标 | 说明 | 结果 |
|------|------|------|
| fsdeamon_config_test | fs-backup 配置单测 | build ok |
| rpc_config_test | rpc 安全开关/参数单测 | build ok |
| rdb_config_test | libs 参数注册表单测 | build ok |
| fsdeamon | fs-backup 守护进程主程序 | build ok |
| fs-cli | fs-backup 客户端主程序 | build ok |
| aio-speedd | rpc 服务端主程序 | build ok |

注：rpc/fs-backup 的 reload 点（fs_source.cpp / backup_helper.cpp / unix_server.cpp）
新增 `#include "rdb-config.h"`，编译均通过。

## 二、行为测试

### 2.1 fsdeamon_config_test（覆盖 AC-1/3/4/5）

```
ok:   init ok with valid config
ok:   check_data read=1
ok:   debug read=0
ok:   keepalive read=45
ok:   retry read=5
ok:   set_rpc_check_data propagated=1
ok:   set_rpc_keepalive propagated=45
ok:   set_rpc_retry propagated=5
ok:   invalid check_data rejects init (fail-closed)
ok:   init ok with empty fsdaemon section
ok:   check_data default=0
ok:   keepalive default=30
ok:   retry default=3
ok:   set_rpc_keepalive default propagated=30
ok:   reload init ok
ok:   reload init ok (2nd)
ok:   reload check_data refreshed=0
ok:   reload keepalive refreshed=77
ok:   init ok with missing config (ENOENT) -> defaults
ok:   check_data default=0 on ENOENT
ok:   keepalive default=30 on ENOENT
ok:   repeated init ok
ok:   repeated init no side-effect
ALL FSDEAMON CONFIG TESTS PASSED
```

### 2.2 rpc_config_test（覆盖 AC-3/5：reload 刷新 + fail-closed）

```
Running init_fills_sec_switches_from_store... PASSED
Running init_env_overrides_store... PASSED
Running init_invalid_audit_env_fails... PASSED
Running reload_reresolves_sec_switches... PASSED
Running tunables_read_from_aio_speedd... PASSED
Running invalid_bool_fail_closed... PASSED
Running out_of_range_tunable_fail_closed... PASSED
Running layer3_aio_speed_fallback... PASSED
Running env_overrides_section... PASSED

=== 9 passed, 0 failed ===
```

### 2.3 rdb_config_test（覆盖 parse_config 底层未破坏）

仅 `rdb-config.h` 增加注释，parse_config 实现未改；编译通过，行为不变。

## 三、验收标准映射

- **AC-1（去重无副作用）**：fsdeamon Case5 `repeated init no side-effect` ok；编译通过。
- **AC-2（签名去 config_file）**：config.h / rpc-config.h / rpc.h 签名已去 config_file；
  全部调用方（main / rpc-client.cpp / rpc/main.cpp / 测试）已改为无参，编译零残留。
- **AC-3（reload 刷新）**：fsdeamon Case4 `reload keepalive refreshed=77` ok；
  rpc_config_test `reload_reresolves_sec_switches` PASSED。
- **AC-4（ENOENT 保留默认）**：fsdeamon Case5 `check_data default=0 on ENOENT` ok。
- **AC-5（安全语义无回归）**：fsdeamon Case2 `invalid check_data rejects init (fail-closed)` ok；
  rpc_config_test `init_invalid_audit_env_fails` / `invalid_bool_fail_closed` PASSED；
  TLS 开关、证书路径、强制 mTLS 经 store 读取逻辑未改，fail-closed 语义保持。
