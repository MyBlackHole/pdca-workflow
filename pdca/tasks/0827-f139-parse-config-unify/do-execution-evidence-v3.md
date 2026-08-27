# T3985 Do 阶段执行证据（v3，含两项 Check 修复）

任务：统一 `rdb-config` `parse_config` 入口，消除启动期与运行期重复解析。

## 一、编译验证（xmake，全部 build ok）

| 目标 | 结果 |
|------|------|
| fsdeamon_config_test | build ok |
| rpc_config_test | build ok |
| rdb_config_test | build ok |
| fsdeamon | build ok（含本次 backup_helper ReloadConfig 签名改动 + reload 返回值检查） |
| fs-cli | build ok |
| aio-speedd | build ok |

## 二、行为测试

### 2.1 fsdeamon_config_test（AC-1/3/4/5）
9 个用例全绿，含 `repeated init no side-effect`、`reload keepalive refreshed=77`、
`check_data default=0 on ENOENT`、`invalid check_data rejects init (fail-closed)`。

### 2.2 rpc_config_test（AC-3/5）
9 passed, 0 failed（含 `reload_reresolves_sec_switches`、`init_invalid_audit_env_fails`、
`invalid_bool_fail_closed`）。

### 2.3 rdb_config_test（parse_config 底层未破坏）
仅 `rdb-config.h` 注释改动，行为不变，编译通过。

## 三、补充修复1：reload 点 init_config 返回值检查（Check 评审）
fs_source / backup_helper / unix_server 三处 reload 点新增的 `init_config` 调用原未检查返回值。
已补全：fs_source 中止 reload 并回报错误；backup_helper ErrorLog 后返回；unix_server 填充 msg
并置 status=1。重新编译 fsdeamon build ok。

## 四、补充修复2：BackupHelper::ReloadConfig 返回异常信息（Check 评审）
原 `void BackupHelper::ReloadConfig(const char *config_path)` 失败时仅 ErrorLog，且调用方
`reload_config` 分支无条件 `response["result"]="true"`，reload 失败也返回成功。已改为：
- 签名 `int BackupHelper::ReloadConfig(const char *config_path, char *err_msg, int len)`，
  `init_config` / `fsdeamon_init_config` 失败时 `snprintf(err_msg,...)` 写入异常信息并返回 -1，
  成功返回 0；
- 调用方（backup_helper.cpp `method=="reload_config"` 分支）按返回值设置
  `response["result"]`（true/false）并在失败时填 `response["error"]=err_msg`，
  异常信息经 unix socket JSON 响回报给客户端。
重新编译 fsdeamon build ok。

## 五、验收标准映射
- **AC-1** ✅ 去重无副作用（fsdeamon Case5）。
- **AC-2** ✅ 三模块 init 签名去 config_file，调用方无参，编译零残留。
- **AC-3** ✅ reload 刷新（fsdeamon Case4 / rpc_config_test）；reload 点返回值与异常信息现已正确传递。
- **AC-4** ✅ ENOENT 保留默认（fsdeamon Case5）。
- **AC-5** ✅ 安全 fail-closed / 强制 mTLS 语义无回归（fsdeamon Case2 / rpc_config_test 相关用例）。
