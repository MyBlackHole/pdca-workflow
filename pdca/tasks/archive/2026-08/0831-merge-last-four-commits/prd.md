# 合并最后四个提交统一为需求修改

## 背景

分支 `6.2.0.0/F/139` 当前相对 `origin/6.2.0.0/F/139`（基线 `fe9d4364`）有 4 个本地提交，分散为需求与 Bug 混杂：

| 序号 | hash | 类型 | 标题 | 版本递进 |
|------|------|------|------|----------|
| 1 | `740d55f0` | F-139 需求 | TLS 安全链路整合：TLS/mTLS 全栈实现、配置收口、mTLS fail-closed 与版本号归一 | libobk 1.0.0.0→1.0.0.1, rpc 3.6.4.19→3.6.4.20, dmsbtex 1.1.0.1→1.1.0.2, rdbcomm 1.0.1.8→1.0.1.9, tls_keygen 1.0.0.0→1.0.0.1, oss 新增 1.0.0.1 |
| 2 | `6195ba5d` | B-T0451 | libs/tls_keygen: 修复签发 UAF 与序列号硬编码 | tls_keygen 1.0.0.1→1.0.0.2 |
| 3 | `72fcbb22` | B-T0457 | libs/tls_keygen: 修复回退熵、类型UB与诊断缺失 | tls_keygen 1.0.0.2→1.0.0.3 |
| 4 | `a8be5f50` | F-T0458 | rdb-cfg: 优化 gen 显示参数可选值与值范围 | rdb_cfg 1.0.0.0→1.0.0.1 |

其中 B 类提交实为 F-139 需求的后置修复与增强，用户要求**统一归为需求形态**，合并为单一 `【F-xxx】` 提交，便于版本发布与归档。远程 `origin/6.2.0.0/F/139` 顶端 `9d1fcc69` 与本地 `740d55f0` 内容已分叉（本地 740d 已含 rdb-cfg 部分变更），合并后需以 `fe9d4364` 为基线重新整合。

## 目标

以 `fe9d4364` 为基线，将上述 4 提交的**所有文件变更** squash 合并为单一需求提交，提交信息按需求模板完整重写，版本一次性递进至最终态（与当前 HEAD 版本一致），并保持与远端一致可推送。

文件维度合并后涉及（`git diff fe9d4364..HEAD --stat` 的 15 个核心增量文件，以及 F-139 的 4000+ 文件全量）：
- `libs/rdb-config.c/h`、`libs/tls_keygen.c`、`libs/tests/*`
- `rdb-cfg/cli.c/h、rdb-cfg/main.c、rdb-cfg/cli_test.c、rdb-cfg/xmake.lua、rdb-cfg/version.in`
- `version.h.in、version.log.in、xmake.lua`
- 以及 F-139 全量（dmsbtex、fs-backup、libobk、libs、rpc、third_party 等）

## 验收标准

- [ ] AC-1：四提交已合并为单一提交，`git log --oneline fe9d4364..HEAD` 仅 1 条记录，类型为 `【F-xxx】` 需求，基线为 `fe9d4364`，`git diff fe9d4364..新HEAD` 与 `git diff fe9d4364..原a8be5f50` 内容一致（文件与行数一致）
- [ ] AC-2：提交信息符合需求模板：含 需求描述、需求背景、实现方案、影响范围、测试验证、版本变更、性能影响、风险评估、回滚方案、验收标准，且不再出现 `【B-xxx】` 前缀
- [ ] AC-3：版本一次性递进正确（相对 fe9d4364）：`libobk 1.0.0.0→1.0.0.1、rpc 3.6.4.19→3.6.4.20、dmsbtex 1.1.0.1→1.1.0.2、rdbcomm 1.0.1.8→1.0.1.9、tls_keygen 1.0.0.0→1.0.0.3、rdb_cfg 新增 1.0.0.1、oss 新增 1.0.0.1`，`xmake.lua` 与各 `version.in` 均一致
- [ ] AC-4：分支一致性：`git status` 干净，`git diff origin/6.2.0.0/F/139..HEAD` 的文件变更与本地 squash 前一致，推送后 `origin/6.2.0.0/F/139` 与本地一致（`force-with-lease` 后无偏离）
- [ ] AC-5：功能不回归：`xmake test` 51/51 通过（或当前基线通过数），`gen` 与 `tls-keygen` 关键路径人工抽样正常

## 非目标

- 不改变四个提交原有的文件实质内容，仅做提交层面的 squash 与信息重写
- 不引入新功能或修复，不改动 `hs_algorithm`、`sec_test` 等校验逻辑
- 不处理 `9d1fcc69` 与 `740d55f0` 分叉外的历史问题，仅以 squash 结果覆盖

## 关联本体节点

```
ontology:concept/pdca-task
```

## 风险

- squash 后需 `force-with-lease` 推送覆盖远端 `9d1fcc69`，需确认远端无他人新提交（当前仅用户本人分支）
- 合并提交信息需完整保留四次提交的版本变更与测试信息，避免遗漏
