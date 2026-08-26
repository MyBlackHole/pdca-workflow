---
schema: pdca.asset/v1
id: T3978-0827-rdb-config-param-registry
phase: check
source_ids: [impl-evidence]
---

## 上下文

承 T3977 §5 的跟进开发任务：以集中式参数注册表解决 rdb config 参数不可发现/不可维护问题。经方案讨论（6 决策点）、设计评审、自我审查（6 处修正）、代码级评审四轮对齐后实施。

## 假设与结果

- 假设：注册表可在不动 sec_resolve 与 30+ 调用点的前提下落地，并以测试锚定与既有宏的一致性。
- 结果：成立。提交 `e7878e78`，xmake test 45/45 passed（原 44 零回归），Check 阶段独立编译链接 demo 复现 dump 双模式输出。

## 分析

- **AC-1** ✅ `config_param_desc_t` 九字段结构与 17 条静态条目落盘 rdb-config.h:136-158 / rdb-config.c:382-458（grep 计数 17，impl-evidence）
- **AC-2** ✅ Check 独立编译 dump_demo（脱离 xmake 以 inih 包静态库直链）：with_values=0 → static_len=2790；=1 → values_len=3044；行格式 `name type env layer2=[sec]key layer3=[sec]key default current desc` 与设计一致，cert_dir 默认值 `/opt/aio/cfg/certs/` 正确呈现（impl-evidence + 本 Check 复跑）
- **AC-3** ✅ registry_matches_macros 按 config_param_find(name) 定位断言宏一致（含全 mtls 参数 layer3 共享键遍历），篡改任一侧即红；find_api 用例含指针区间一致性断言（impl-evidence）
- **AC-4** ✅ param_registry_test/default 接入且全量 45/45 passed（impl-evidence）

实施中 TDD 实证捕获两处实现缺陷：格式串占位符不匹配（-Werror=format-extra-args 编译期拦截）、truncated 分支未累计长度（small_buffer_safe 运行期拦截）——红灯价值闭环。

附带收益：SBT_*_ENV 宏双定义收敛至 rdb-config.h 单一来源（T3975 登记项闭环）。

## 适用边界

- 注册表当前为元数据快照：新增参数须手工同步表条目（表↔调用点实参级漂移无法测试捕获，param_get(id) 演进可根治）。
- dump 的 current 为取样瞬间值，非跨 reload 一致性快照。
- rpc 业务 7 键未纳入本表（范围裁定为 rdb.conf 安全参数域）。

## 下一轮建议

- 后续任务：rpc_show_config / RELOAD 链路修复可直接消费 config_dump_params 与注册表。
- tls_algorithm 默认值分裂（#7/#9/#11/#15 NULL vs #9/13/17 SM4_GCM_SM3）建议产品侧裁决后统一。
