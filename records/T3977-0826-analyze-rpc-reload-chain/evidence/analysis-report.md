# Analysis Report — rpc 配置重载链路失效（T3977）

## 调研目标

厘清 rpc 配置生命周期全景，量化 RELOAD_CONFIG_CMD 对各安全消费点的真实效果，深度评价链路设计模式，产出修正设计与参数可维护性改进方向。

## 方法

一手源码逐行核验（rpc-config.cpp / rdb-config.c / main.cpp / rpc-server.cpp / rdbcomm）、消费点全量 grep、可达性交叉验证；每条结论附 file:line 或复跑命令。

## 发现

### 1. 数据流全景（含各层刷新时机）

```
                     ┌─[constructor 仅一次] rdb_auto_init→parse_config──→ _kv_stores[2]
                     │      (rdb-config.c:380)        (此后全仓库零调用 ✗)
 rdb.conf ───────────┤
                     └─[启动] rpc_init_config ─┬─ ini_parse(rpc handler 仅7键)→ g_rpc_config 业务字段
                       (rpc-config.cpp:141)    └─ sec_resolve_*(env+_kv_stores)→ mtls/audit/auth/
                                                                 tls_algorithm/cert_dir 字段
 env vars ────────────────→ sec_resolve 第1层（每次调用现读）

 [reload] RELOAD_CONFIG_CMD(main.cpp:453→308)
   └→ rpc_parse_config(rpc-config.cpp:86)
        ├─ ini_parse(7键) → 双缓冲新配置            ✓ 刷新
        ├─ audit/auth 重算(:110-119, 数据源store陈旧) △ 半刷新
        ├─ mtls/tls_algorithm/cert_dir              ✗ 完全不触及
        └─ 先发布 g_rpc_config(:105) 后回写字段(:110+) ⚠ 竞态窗口
```

同一 rdb.conf 被**两套解析器各取所需**：rpc ini_parse 只取 7 个业务键（debug/retry/check_data/keepalive/parallel/read_timeout/fsbackup_dev_path，rpc-config.cpp:39-56），libs ini_parse 把全部键收进 store 供 sec_resolve 分层取用——键的归属从任何单一文件都无法看出。

复核途径：`grep -n "MATCH\|sec_resolve" rpc/rpc-config.cpp`；`grep -rn "parse_config(" libs/rdb-config.c | grep -v static`。

### 2. 影响矩阵：安全消费点 × reload 后行为

| # | 消费点 | 数据来源 | reload 后行为 |
|---|--------|---------|--------------|
| 1 | 握手 mTLS 开关 rpc-server.cpp:284,400 | g_rpc_config->mtls_enabled | **不生效**（reload 不触及该字段） |
| 2 | 算法锁定 rpc-server.cpp:261-270 | tls_algorithm | **不生效** |
| 3 | 证书目录 rpc-server.cpp:310,361 | cert_dir | **不生效** |
| 4 | 审计判定 rpc-server.cpp:522,995 | audit_enabled | **半生效**：env 层新值可见；ini 经 store 读到旧快照（rdb-config.c:380 后 store 零刷新） |
| 5 | key 验证 rdbcomm/server.c:695 | server_opts.auth_enabled（rdbcommd-main.c:276 启动解析一次） | **不生效**（rdbcomm 无 reload 机制，属另一模块语义） |
| 6 | rpc 侧 auth_enabled | rpc-config.cpp:110,198 写入 | **死字段**：rpc/*.cpp 运行期零读取（grep 全仓库验证），写而不读 |

结论：T3968"重载时安全开关重新解析"裁定实际只对 audit/auth 的 env 层成立；五类安全消费中三类完全失效、一类半失效、一类为死代码。

复核途径：`grep -rn "auth_enabled" --include="*.cpp" rpc/ | grep -v config\|test`（空输出=死字段）；上表各行号直查。

### 3. 发布竞态语义分级

`rpc-config.cpp:104-119`：先 `config_index=tmp; g_rpc_config=p_config;` 发布，后回写 audit/auth。

- **标准层面**：无锁无非原子地"发布指针→写成员"，与读者构成 C++ 数据竞争（UB）。
- **x86 TSO 实际表现**：新缓冲在拷贝期已含旧 audit/auth 值（:91 `*p_config=*g_rpc_config`），窗口内读者看到"新业务字段+旧开关值"，最终收敛——瞬态不一致而非撕裂。
- **业务危害**：审计判定在窗口期（微秒级）按旧开关执行；低概率、低危害，但 sanitizer（TSAN）必报，且随字段增多窗口线性变长。
- **定级**：MEDIUM——修复成本低（回写完成后发布），但属标准 UB 应消除。

### 4. 设计模式深度审查（五模式）

| 模式 | 实现 | 与热重载相容性 | 评价 |
|------|------|--------------|------|
| 双缓冲快照发布 | `_kv_stores[2]`(rdb-config.c) 与 `_config[2]`(rpc-config.cpp) 两套同型 | 部分相容：写入侧双缓冲就绪，但槽位数=2 且读者无宽限——慢读者跨两次 reload 时第三次 reload 重写其正持有的槽（rdb-config.c:178 仅防指针撕裂） | 方向正确、实现不完整；缺世代计数或宽限机制 |
| constructor 隐式初始化 | rdb_auto_init(rdb-config.c:380) | **根本不相容**：加载时机不可控、全仓库无第二调用点=结构性"只读一次"、err 参数被丢弃 | 热重载失效的第一根因；应暴露显式 refresh 入口 |
| 四层解析链 sec_resolve | env→tool-section→global-section→default(rdb-config.c:259-307) | 相容（每层现查 store/env，store 一旦刷新即自动生效） | 分层设计本身良好；缺陷在 int 层 atoi fail-open 与 bool 层 strict 分裂（T3975 已录）、以及依赖 store 刷新这一缺失前提 |
| 进程上下文字段缓存 | T3968"解析一次存字段，运行期只读" | **根性张力**：缓存即快照、快照即过时。裁定试图以"重载时重算部分字段"调和，但覆盖不全+数据源未刷 | 缓存优化目标合理；缺"缓存失效通知"配套机制——这是本缺陷的设计层根因 |
| 全局裸指针切换单例 | g_rpc_config 裸指针赋值发布 | 不相容：非原子、无 release/acquire 语义 | 最简 RCU 但缺关键件；C++11 起可用 atomic<rpc_config*> 或 shared_ptr atomic load/store |

**根因链**：constructor 单次加载（无失效入口）→ 上下文缓存放大（快照定格）→ reload 只修可见面（ini 字段）→ 安全键三层断裂。

### 5. 配置参数可发现性审计（用户指认："根本不知道到底有什么参数"）

**键定义三处分散**：

1. `libs/rdb-config.h:21-30` 宏定义安全键 10 个（security.tls_enable/auth_enable/audit_enable/ciphersuites/cert_dir、auth.enable、tool.mtls_enable/tls_algorithm…）
2. `rpc/rpc-config.cpp:39-52` MATCH 硬编码字符串业务键 7 个
3. 消费点直接字符串/独立宏（AIO_SPEEDD_MTLS_ENABLE_ENV 等 env 名散落 rpc/dmsbtex/libobk 各头文件）

**show 覆盖度**：rpc_show_config 输出 8 字段 vs 结构体 20+ 字段；sec 层全部键（store 内容）零展示——运维无法从任何运行时接口得知"有哪些参数、当前生效值、来自哪一层"。

**文档**：docs/ 仅 adr；无参数参考文档；libs/tests/rdb_config_test.c 用合成键（"a"/"abc"/"hello"），测试不能当文档。

**根因**：无单一参数注册表/schema——键的名称、层级、类型、默认值、说明五类信息分散于宏定义/handler 分支/调用实参/结构体四处。

复核途径：`grep -c snprintf <(sed -n '/rpc_show_config/,/^}/p' rpc/rpc-config.cpp)`=8；`grep -rn "define SEC_" libs/rdb-config.h`。

### 6. 修正方案对比（fail-closed 权衡）

**方案 A：完整热重载**
1. `process_reload_cmd`（main.cpp:308）在调 rpc_parse_config 前先调 libs `parse_config(path,...)` 刷新 _kv_stores
2. `rpc_parse_config` 补齐 mtls_enabled/tls_algorithm/cert_dir 重解析（mtls 沿用 init 的 fail-closed 校验语义：sec_resolve_bool<0 → 报错拒绝本次 reload，保持旧配置）
3. 回写全部派生字段完成后才发布 g_rpc_config（消除竞态）
- ✓ 符合 T3968 裁定意图；✓ sec_resolve 四层无需改动（store 刷新后自动生效）；✗ 并发复杂度最高；✗ 运行期降级 mTLS 需评估安全策略（建议：reload 仅允许 0→1 升级，1→0 降级需 CLI 重启——fail-closed 取向）

**方案 B：安全键冻结**
reload 时解析新旧安全键集合，差异即告警并拒绝本次 reload；文档化"安全开关仅启动期生效"。
- ✓ 实现最简、并发零新增、绝对 fail-closed；✗ 与 T3968 裁定相悖（需重新裁定）；✗ 运维需重启才能调整开关

**推荐：A 为主干 + 降级限制**。理由：T3968 已裁定热重载意图；上下文缓存架构已定型，补"失效通知"比推翻缓存更经济；配合第 7 节注册表改造后维护成本可控。

### 7. 推荐方案函数级落地要点（供修复任务引用）

```
1. rpc/main.cpp process_reload_cmd:308
   + 先 parse_config(path, err, len)（libs），失败即返回 status=1
   + 再 rpc_parse_config(path, err_msg, len)
2. rpc/rpc-config.cpp rpc_parse_config:86
   + :105 发布前移除 audit/auth 回写 → 移到 ini_parse 之后、发布之前
   + 补 mtls_enabled = sec_resolve_bool(...)（<0 → err+return -1 整体拒绝）
   + 补 tls_algorithm/cert_dir = sec_resolve_str(...)
   + config_index=tmp 与 g_rpc_config=p_config 合并为最后一步
3. libs/rdb-config.c
   + parse_config 放开为公开可重入（已是公开符号，验证双缓冲线程约束即可）
   + 可选：世代计数器供读者宽限（防 A 方案 reload 风暴下槽位复用撕裂）
4. rpc/rpc-config.cpp rpc_show_config
   + 追加 sec 层键展示（或由注册表驱动全量输出）
5. 测试：rpc_config_test 补 reload 三断言（mtls 拒绝非法值保持旧值/store 层新键生效/竞态窗口消失）
```

**参数注册表改造要点**（跟进任务输入）：
五元组 `{section, key, layer(tool/global/env), type(int/bool/str), default}` 单表驱动三件事——do_parse_config 自动分发（消灭 MATCH 硬编码）、show 全量输出、markdown 参数文档生成。盘点基础见第 5 节。

## 结论

T3968 热重载裁定因三层断裂实际落空（三类消费失效/一类半生效/一死字段）；根因是 constructor 单次加载与上下文缓存的快照定格缺"失效通知"配套；推荐方案 A（完整热重载+降级限制）并以参数注册表改造为前置基建。

## 参考资料

- rpc/rpc-config.cpp:35-56,86-121,141-206 · libs/rdb-config.c:176-260,380 · rpc/main.cpp:308-330,453
- 消费点：rpc-server.cpp:261-400,522,995 · rdbcomm/server.c:695 · rpc-client.cpp:662-703
- T3968（裁定引入）/ T3975（发现）/ T3977（本分析）
