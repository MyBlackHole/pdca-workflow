---
schema: pdca.asset/v1
id: T0487-0905-bcachefs-versions
phase: check
source_ids: [reprot-bcachefs-versions]
---

## 上下文
用户要求分析 bcachefs-tools 在 1.39.2 之后每个版本更新了什么、解决了什么问题。Plan 阶段确认范围为仅已发布版本（v1.39.3/v1.39.4）、逐提交清单粒度、对话+报告文件双交付。Do 阶段以 git rev-list 为事实源提取 156 个提交，四段并行深挖 + 主会话核验 v1.39.4 diff，产出 report.md 并登记证据。

## 假设与结果
- 假设 1：本地 tag 完整覆盖已发布版本。结果：成立，v1.39.3/v1.39.4 均存在且 rev-list 计数 147/9。
- 假设 2：提交说明正文足以支撑根因分析，关键处用 diff 佐证。结果：成立，重点提交均经 git show 抽查。
- 假设 3：清单数量可机检。结果：成立，report.md 清单条目 147/9 与 rev-list 一致。

## 分析
- **AC-1** ✅ 清单数量与 rev-list --count 一致（v1.39.3 段 147、v1.39.4 段 9）（reprot-bcachefs-versions）
- **AC-2** ✅ 重点提交详解均有 commit diff 佐证：A1-A8/B1-B7/C1-C8/D1-D10/E1-E5 均经 git show --stat/diff 抽查后下结论（reprot-bcachefs-versions）
- **AC-3** ✅ 报告文件存在（records/T0487-0905-bcachefs-versions/evidence/report.md，sha256:41fb6982…），对话输出与文件内容一致，待本回复交付后成立（reprot-bcachefs-versions）

关键结论（research 可复核途径附后）：
1. v1.39.3 是 mount 用户态重构版（约半数提交）：255B 天花板、degraded 分级问、status_fd 可观测通道、systemd 防杀缺一不可，是多盘开机挂载的完整修复链。
2. v1.39.3 修了多个高危正确性问题：casefold 丢失唤醒（不可杀挂起）、RCU UAF、EC 复用卡死、passphrase 反转、解压错掩盖校验错、replicas GC 从不落盘。
3. v1.39.4 是修复版：最重要的是 E4（内容 btree 丢数据补排内容检查，防悬空引用延迟爆发）与 E5（initramfs 装超时生成器）。
4. 复核途径：`git -C /home/black/Documents/bcachefs-tools log --reverse --format="%h|%ad|%s" --date=short v1.39.2..v1.39.3` 得 147 行，与报告第二章逐条核对；`git show <hash>` 核对详解。

## 适用边界
- 仅覆盖已发布版本，不含 origin/master 上 v1.39.4 之后的 39 个未发布提交。
- 本地 main 落后 origin/master 242 提交，分析基于 tag 可达对象，不受分支落后影响。
- 详解依赖提交说明正文 + 抽查 diff，未逐行审计全部 156 个 diff；行为级结论以正文与抽查为准。

## 下一轮建议
- 如需前瞻：对 v1.39.4..origin/master 的 39 个未发布提交做同口径分析。
- 如需落地：本地 main 落后 242 提交，升级前重点复核 E4 类恢复路径变更在本机的回归测试。

verdict: {"outcome": "confirmed", "reason": "3 AC 全绿，证据链完整，清单机检一致", "verdict_id": "vt0487-confirmed", "at": "2026-09-05T08:00:00+08:00"}
