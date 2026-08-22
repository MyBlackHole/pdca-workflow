# T0364 代码审查证据（逐 commit 复核）

## 审查范围
四模块（rdbcomm / libobk(sbt) / dmsbtex / rpc）T0354–T0363 已 commit 的 TLS/mTLS 相关 diff。
握手字节序一致性由 T0363 覆盖，本任务聚焦非握手配置 / 内存安全 / 结构体清理部分。

## 逐 commit 复核

### T0356 (582c380) libobk mTLS 握手栈溢出 / 帧长度修复
- 客户端 resp 缓冲区改为 `sizeof(activeioHeader) + OBK_HS_RESP_BODY_SIZE`，按 header+body 总长分配；
- `_recv(io, resp, sizeof(resp), NULL)` 读满总长，短读即失败；
- `memmove(resp, resp + sizeof(activeioHeader), OBK_HS_RESP_BODY_SIZE)` 替代重叠 memcpy，消除 UB；
- `ca_cn` 提取改用 `OBK_HS_MAX_NAME`，长度绑定单点宏；
- 6 个失败分支补分类 ErrorLog（role/stage/cert_dir/ca_cn/algorithm）。
- 结论：修复正确。ASan 构建无内存错误；变异测试（回退发送长度至旧值）确认用例判别力；libobk_session_test 往返用例 PASS。

### T0358 (12fe729) mTLS 参数严格解析（fail-closed）
- `strtol` 全串校验仅 0/1，否则拒绝；
- 算法名 `strcmp` 精确白名单（SM4/AES 两规范名），删 sm2/ed25519 别名；
- config init 校验算法名为规范名。
- 结论：fail-closed 正确。风险：旧部署写 sm2/ed25519 别名将导致启动失败（设计意图）。

### T0360 (0ef0f8d) TLS 配置结构体死字段清理
- 五结构体共删 22 字段 + 2 个 unused 函数；纯删除，无行为变更；
- 全部填充代码 / 拷贝链删除；编译 + 六套测试 PASS。
- 注意：commit 声明版本递增因漏改 xmake.lua 未落地，由 T0361 修正（历史遗漏已闭环）。
- 结论：清理正确，无运行时引用残留（编译 + 测试佐证）。

### T0361 (4f0e880) sec_resolve_bool 三态收敛
- libs 新增 sec_resolve_bool()：分层同 sec_resolve_int，每层取原始串严格校验仅 "0"/"1"，非法返回 -1 哨兵；
- 六处删 cli_mtls_set，载体字段直接承载最终值（rdbcomm-main 经 copts.mtls_enabled 一字段三用：配置打底→getopt 覆盖→校验消费）；
- dmsbtex/libobk 删 T0358 临时 parse_bool_env，改走 sec_resolve_bool，获 ini [security] tls_enable 支持；
- rpc/main.cpp `case 1030` 解析 `--mtls-enable`：`strtol` + 全串 `*end != '\0'` + 仅 0/1，无 fail-open；
- rdbcomm/rdbcommd `mtls_enabled` 初值 sec_resolve_bool 打底，CLI 覆盖，`<0` 启动失败；
- 顺修 dmsbtex_session_test 缺失 SIGPIPE 忽略（偶发 exit=141 flaky）。
- 结论：三态收敛正确，无配置绕过。

### T0354 (d495dcc) rdbcomm 握手框架大重构
- 三项目明文零握手直通；握手内嵌消息循环；rdbcomm/io.c 删除 264 行，msg.c 重构。
- 结论：声明端到端测试 PASS。建议：补充明文零握手直通路径的回归覆盖证据（高风险删改）。

### T0359 (aa8de18/21ce23a/839eb7e) 枚举 / map 收敛
- 四模块算法枚举 / map 收敛到 libs 单一来源，删重复声明；
- 删 dm_hs 死代码；修 common.h guard 冲突。
- 结论：与 T0363 握手白名单一致性结论一致，无分歧枚举。

## 总体结论
无高 / 中危引入性缺陷。栈溢出修复、严格解析、死字段清理、三态收敛、枚举收敛均正确；rpc CLI 解析严格无 fail-open。
