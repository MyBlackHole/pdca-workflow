# Triage Brief — squash-last-six-commits

- **category**: enhancement
- **scenario_type**: development
- **summary**: 将分支 6.2.0.0/F/139 最近六个提交合并为单个提交
- **current behavior**: 分支头部存在六个零散提交（TLS/mTLS 整合、rpc 安全开关收敛、oss HTTPS 开关化、oss 单测架构、tls-keygen SAN 修复），其中最早的一个已推送远程
- **desired behavior**: 六个提交压缩为一个提交，最终树内容与合并前完全一致，历史整洁
- **key interfaces**: git 历史改写（reset --soft / rebase）、远程推送策略（force-with-lease）
- **acceptance criteria**:
  - 运行 `git log --oneline -1` 得到用户确认的单一合并提交信息
  - 运行 `git diff <backup-ref> HEAD` 得到空输出（树内容不变）
  - 运行 `git log --oneline -7` 得到父提交为 `fe9d4364`
- **out of scope**: 不修改任何文件内容；不处理更早的历史；不自动 force push（除非用户明确确认）
- **information gaps**: 合并后的提交信息文本；是否接受 force push
- **dedup results**: 活跃任务中无同类 squash 任务
- **recommended next steps**: 向用户确认提交信息与 force push 策略后进入 Do
