---
schema: pdca.asset/v1
id: T3985-0827-f139-parse-config-unify
phase: check
source_ids: [exec-evidence-v2, code-diff-v2, convergence-map-v2]
---

## 上下文
评审提交 89929057（F-139 TLS 安全链路整合）时发现：`parse_config` 被 `init_config` /
`set_rpc_init_config` / `fsdeamon_init_config` / `fsclient_init_config` 以及运行期 reload 点
（fs_source / backup_helper / unix_server）分散调用，各自把同一 rdb.conf 重新解析并覆盖全局
单例 `_kv_store`，造成启动期与运行期重复解析、调用关系不清、潜在 TOCTOU。本任务将其收敛为
`init_config` 独占调用。

## 假设与结果
- 假设：收敛 `parse_config` 为 `init_config` 独占、各模块 init 去掉 `config_file` 参数改为从
  已加载的 store 经 `sec_get_*` 读取、运行期 reload 统一走 `init_config`，可消除重复解析且不产生
  行为回归（安全 fail-closed / 强制 mTLS 语义保持）。
- 结果：实现完成，6 个 xmake 目标编译通过，2 个行为测试套件全绿（含新增 reload / ENOENT / 去重用例）。

## 分析
- **AC-1** ✅ `init_config` 后多次各模块 init 不产生附加解析副作用（exec-evidence: fsdeamon Case5 `repeated init no side-effect`）
- **AC-2** ✅ 三模块 init 签名不再含 `config_file`，实现内部不再调 `parse_config`，全部调用方已改为无参且编译零残留（exec-evidence + code-diff）
- **AC-3** ✅ reload 经 `init_config` 重新加载 store 后模块参数反映最新文件（exec-evidence: fsdeamon Case4 `reload keepalive refreshed=77`；rpc_config_test `reload_reresolves_sec_switches` PASSED）
- **AC-4** ✅ 配置缺失（ENOENT）时各模块 init 保留注册表默认值、进程可启动（exec-evidence: fsdeamon Case5 `check_data default=0 on ENOENT`）
- **AC-5** ✅ TLS 开关、证书路径经 store 读取，fail-closed 与强制 mTLS 行为无回归（exec-evidence: fsdeamon Case2 / rpc_config_test `init_invalid_audit_env_fails` 等 fail-closed 用例）

## 补充修复（Check 评审）
Check 评审发现三处 reload 点（fs_source / backup_helper / unix_server）在改为 `init_config + 模块init`
后，新增的 `init_config` 调用未检查返回值，加载失败时错误被静默吞掉且可能用空/默认 store 覆盖运行期
配置。已补全返回值检查：fs_source 中止 reload 并回报错误；backup_helper ErrorLog 后返回；unix_server
填充 msg 并置 status=1。重新编译 fsdeamon：build ok。本结论（5 条 AC 全部 ✅）不受影响，证据见
exec-evidence-v2 第三节。

## 失败原因
无（结论成立）。

## 适用边界
- 并发安全（全局 `_kv_store` 无锁 reload 竞态）为已声明范围外，由 0823 审计单独跟踪，本次未触碰。
- `dmsbtex` 仅调 `init_config` 加载 store，本就是目标态，未改动。
- 范围外未引入内部计数器/探针，验收为纯行为测试（符合 Grill 裁定）。

## 下一轮建议
- 并发加固若启动，单独任务处理，不回混本次去重。
- 可补充 rpc 侧 reload 的端到端集成测试（当前单测已覆盖 `reload_reresolves_sec_switches`）。

## Verdict
```json
{
  "outcome": "confirmed",
  "reason": "全部 AC 均有编译与行为测试证据支持；parse_config 收敛为 init_config 独占，各模块 init 去 config_file 从 store 读，reload 统一走 init_config；reload 点 init_config 返回值检查已补全（见补充修复段）；安全 fail-closed 与强制 mTLS 语义无回归",
  "verdict_id": "vc-T3985-20260827",
  "at": "2026-08-27T11:00:00+08:00"
}
```
