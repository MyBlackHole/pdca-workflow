# T0364 审查结论

## 任务结果

T0364 已确认（verdict: confirmed）：四模块（rdbcomm / libobk / dmsbtex / rpc）T0354–T0363 已 commit 的 TLS/mTLS 修改，经逐 commit 独立复核，无高 / 中危引入性缺陷，残留 LOW 项非阻塞。

## 审查范围

四模块 T0354–T0363 已 commit 的 TLS/mTLS 非握手配置 / 内存安全 / 结构体清理类 diff。握手字节序一致性（M5）由 T0363 单独覆盖，不在本任务逐行复核范围。

## 逐模块结论（证据 EVID-CODE-REVIEW）

- **T0356** libobk 握手栈溢出 / 帧长度修复：缓冲区按 header+body 总长分配、重叠拷贝改 memmove、短读即失败；修复正确（ASan 无内存错误）。
- **T0358** mTLS 参数严格解析（fail-closed）：strtol 全串 + strcmp 白名单；无 fail-open。
- **T0360** TLS 配置结构体死字段清理：五结构体删 22 字段 + 2 unused 函数，纯删除无行为变更；编译 + 六套测试 PASS 佐证无残留引用（版本号漏改由 T0361 修正）。
- **T0361** sec_resolve_bool 三态收敛：删 cli_mtls_set 六处，统一三态无 fail-open；顺修 SIGPIPE flaky。
- **T0354** rdbcomm 握手框架大重构：声明端到端测试 PASS；建议补充明文零握手直通路径回归覆盖。
- **T0359** 枚举 / map 收敛：四模块收敛到 libs 单一来源，删重复声明与死代码，修 include-guard 冲突。

## 风险评级（证据 EVID-REVIEW-REPORT）

- 高：0
- 中：0
- 低：4（空串当禁用、错误码前缀不统一、T0360 版本号漏改已由 T0361 修正、T0354 大重构回归覆盖建议）

## 标准化轴结论

死字段清理使结构体更小、拷贝链更短（正向）；错误码前缀四模块不统一属历史遗留（follow-up 候选）。

## 规范轴结论

T0358 fail-closed 达成；T0361 三态精简 + 统一 sec_resolve 达成；T0360 死字段清理达成。

## 数值

- T0356 libobk_session_test 往返 PASS；T0360 / T0361 六套测试 PASS；ASan 构建无内存错误。

## 遗留 / 残留 LOW 项（非阻塞，follow-up 候选）

1. 四模块错误码前缀归一到 libs 单一宏。
2. T0354 明文零握手直通路径补充端到端回归用例。
3. 空串 env / ini 值当前当 0（禁用，fail-closed 方向安全）；如需更严可显式拒绝。

## 收敛（AC）

- **AC-1**：审查覆盖四模块 T0354–T0363 全部已 commit TLS/mTLS 修改 — evidence: EVID-CODE-REVIEW ✓
- **AC-2**：确认无高 / 中危引入性缺陷 — evidence: EVID-CODE-REVIEW ✓
- **AC-3**：残留 LOW 级项清单明确且非阻塞 — evidence: EVID-REVIEW-REPORT ✓
