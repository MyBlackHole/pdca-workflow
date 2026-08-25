# Dialogue Log

## 2026-08-25 Plan -> Do

- 用户报告：服务端开启 mTLS 后客户端不启用时报错不明确（result=0x8004 / exit 252），要求同时检查其他工具。
- Triage（T3956）：验证四模块问题点——rpc 两处裸 %x、libobk 裸 %x、rdbcomm/dmsbtex 静默失败；与 0822/0823 任务查重不重复；创建任务。
- Grill 三决策：码表归一 libs、退出码纳入范围、英文文案。终审批准（final_confirmation confirmed）。

## 2026-08-25 Do -> Check

- 路径 B（bugfix）TDD 三切片：
  1. libs hs_err_str + common.h 码归一（红→绿，hs_err_test）
  2. rpc 接入 + 退出码 -2（e2e S4 红→绿）
  3. rdbcomm 补日志（e2e S17 新增红→绿）、libobk/dmsbtex 接入
- 全量回归：e2e 17/17、mixed_mtls_integration AC1-7、rpc_own_handshake_test、rdbcomm/dmsbtex/libobk session tests 全过。
- 双轴审查 Blocking=0（libs/tls_cert.c 为遗留无关变更未纳入提交）。
- 证据 9 条登记 + convergence-map 校验 valid=true；commit b531ec02。
