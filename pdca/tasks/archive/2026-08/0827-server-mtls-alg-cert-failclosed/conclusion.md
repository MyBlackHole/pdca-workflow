# T3988 结论报告（conclusion）

- task_id: T3988
- record: T3988-0827-server-mtls-alg-cert-failclosed
- scenario_type: bugfix
- phase: check
- date: 2026-08-27

## 背景与目标
T3987 已让"mTLS 启用 + 证书整体缺失"启动失败（fail-closed）。本任务补齐精细化语义：
**服务端 mTLS 启用且显式指定算法时，若该指定算法对应的证书异常（缺失/损坏/不支持），
启动期必须以非 0 退出，不得 fallback 到另一算法的证书兜底成功**（即算法锁必须 fail-closed，
不能因"另一套证书还在"而变 fail-open）。

## 根因（实现前）
`libs/tls_cert.c:tls_cert_init_server` 恒按 `cert_dir` 自动构建 **SM4+AES 双算法链**
（`tls_cert_build_server_profiles` 硬编码两 profile，与文件是否存在无关）；单算法失败仅
`continue` 跳过（T0390"尽力收集、不连坐其他算法"）。因此指定 SM4 但 SM4 证书缺失、AES 正常时
仍整体成功 → 安全开关被另一算法静默兜底，等于 fail-open。

## 修复（Do 阶段）
- `libs/tls_cert.h`：`tls_cert_server_options_t` 新增 `const char *algorithm;`
- `libs/tls_cert.c`：`tls_cert_init_server` 新增算法分支——指定算法时仅加载该算法 profile，
  该 profile 的 `tls_cert_slot_create` 失败即 `tls_cert_cleanup` + `return ret`（整体失败，无跳过）；
  非法算法名 → `TLS_CERT_ERR_INVALID_PARAM`；空算法 → 保持原双算法链兼容。
- 四服务端 wiring：rdbcommd（server_boot.c）、aio-speedd（rpc/server_boot.cpp + main.cpp）、
  dm-ftp（dmsbtex/network.c）、sbt（libobk/lib/logic/oracleCmdTbl.c）均将自身算法配置传入
  `opts.algorithm`，使算法锁在启动 boot prepare 阶段即生效。

## 验收映射（AC → 证据）

| AC | 验收标准 | 证据 | 结果 |
|----|----------|------|------|
| AC-1 | rdbcommd 指定算法+该算法证书异常→启动失败 | rdbcommd-boot-test | PASS |
| AC-2 | aio-speedd 指定算法+该算法证书异常→启动失败 | aio-speedd-boot-test | PASS |
| AC-3 | dm-ftp 指定算法+该算法证书异常→prepare 失败 | dmsbtex-session-test | PASS |
| AC-4 | sbt 指定算法+该算法证书异常→prepare 失败 | libobk-session-test | PASS |
| AC-5 | 指定算法且证书正常→成功；非法算法名→失败；未指定算法+证书存在→成功（兼容） | libs-tls-cert-test | PASS |
| AC-6 | 单元/链接级覆盖（四服务端 + libs） | rdbcommd/aio-speedd/dmsbtex/libobk/libs 测试 | PASS |
| AC-7 | 全量构建无警告；既有 mTLS 集成测试无回归 | rdbcomm-handshake-test、mixed-mtls-integration | PASS |

## 双轴审查
- 安全轴（secure-coding）：新增算法分支使用 `strncpy` 长度受限并补 `\0`、`strcmp` 作用于已空检
  字符串（无空指针解引用）；错误日志固定格式串 + `%s`（无格式字符串漏洞）；fail-closed 路径在
  证书异常 / `slot_create` 失败时一律 `tls_cert_cleanup` 后返回错误（无 fallback、无 UAF、无泄漏）；
  非法算法名亦 fail-closed。**未发现安全缺陷，Blocking=0。**
- 质量轴（code-review-checklist）：复用既有 `tls_cert_slot_create` 与 profiles 结构，改动局部、
  未扩大攻击面；四服务端 wiring 仅透传有界字段；全量 `xmake build` 在 `-Werror` 下通过。
  **未发现质量问题，Blocking=0。**

## 测试执行摘要
- libs tls_cert_test：Passed 21 / Failed 0（含 `tls_cert_init_server_alg_failclosed`）
- rdbcommd boot test：PASS
- aio-speedd boot test：PASS
- dmsbtex session_test：ALL PASS（含 `[PASS] alg-locked cert fail (no downgrade)`）
- libobk session_test：PASS（含 `[PASS] alg-locked cert fail (no downgrade)`）
- 回归：rdbcomm_handshake_session_test ALL PASS；mixed_mtls_integration PASS
- convergence 校验：valid=true（覆盖 AC-1..AC-7）

## 总体结论
全部验收标准达成，双轴审查零阻塞，convergence 校验通过。**建议 verdict：confirmed**，
进入 Act 阶段提交（bugfix 路径）并归档。
