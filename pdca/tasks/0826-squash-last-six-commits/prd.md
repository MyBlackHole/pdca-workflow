# 合并分支最后六个提交为单个提交

## 问题陈述

分支 `6.2.0.0/F/139` 上最近六个提交均属同一批 F-139/TLS 相关工作，历史碎片化，需合并（squash）为单个提交以保持历史整洁。

## 已知事实（triage 验证）

- 当前分支：`6.2.0.0/F/139`，工作区干净。
- 待合并的六个提交（新→旧）：
  1. `28848cf6` 【B-T3973】tls-keygen: 修复签发证书缺失 SAN 导致 TLS 客户端校验失败
  2. `ba187ae5` 【F-139】oss: Go 单测接入 xmake test 架构
  3. `a72580d9` 【F-139】oss: HTTPS 开关化——参数配置开启，默认 HTTP
  4. `69da290b` 【F-139】rpc: 安全开关随配置重载重新解析并补充进程上下文字段单测
  5. `1318f591` 【F-139】rpc/rdbcomm: sec_resolve 运行期调用收敛为各模块进程上下文字段
  6. `4ef9c5c1` 【F-139】TLS/mTLS 全栈实现与演进整合（**已推送至 origin**）
- 分支领先 `origin/6.2.0.0/F/139` 仅 5 个提交 ⇒ 第 6 个提交已在远程 ⇒ squash 改写本地历史后远程保持不变（用户已选择暂不推送）。

## 用户决策（澄清确认）

1. **提交信息**：采用自定义综合信息（见下方方案），概括六方面工作。
2. **推送策略**：仅本地改写，**不执行任何 push**；force push 留待用户手动处理。

## 方案

1. 建立备份引用：`git branch backup/pre-squash-T3974`（防回退）。
2. `git reset --soft HEAD~6` 将六个提交的变更收敛到暂存区。
3. 以综合信息一次性提交：

   ```
   【F-139】TLS 安全链路整合：TLS/mTLS 全栈实现、rpc 安全开关进程上下文化、
   oss HTTPS 开关化与 xmake 单测接入、tls-keygen SAN 修复
   ```

4. 验证树一致性：`git diff backup/pre-squash-T3974 HEAD` 必须为空。

### 备选方案与取舍

- *interactive rebase squash*：效果等同，但交互式编辑器流程更繁琐且易误操作；选 reset --soft 更简单可控。
- *git merge --squash*：适用于分支合并场景，对同一线性历史不适用。

## 范围外

- 不修改任何文件内容；不触碰更早历史；不执行 push（含 force push）。

## Seam 分析

本任务为 git 历史维护操作，无代码产物与单元测试；验证方式为 git 命令断言（AC-1~AC-3）。

### 声明的测试接缝

（无——纯 git 操作，无被测模块）

## 验收标准

- [ ] AC-1: 运行 `git log --oneline -1` 显示单一合并提交，信息为上述确认的综合版本
- [ ] AC-2: 运行 `git diff backup/pre-squash-T3974 HEAD` 输出为空（最终树内容与合并前完全一致）
- [ ] AC-3: 运行 `git log --oneline -7` 确认原六个提交已消失，合并提交的父提交为 `fe9d4364`
- [ ] AC-4: 运行 `git status` 工作区干净，且全程未发生任何 push（`git log origin/6.2.0.0/F/139 -1` 仍为 `28848cf6`）
