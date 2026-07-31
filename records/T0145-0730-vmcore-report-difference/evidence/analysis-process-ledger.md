# 报告 A 分析过程账本（去敏）

## 来源

- 原始会话：`/home/black/ses_06dffb331ffe4IGZS3WxGNQQ5X.json`
- 会话 ID：`ses_06dffb331ffe4IGZS3WxGNQQ5X`
- SHA-256：`9b4a9c6c57e502b84fdf1c53563e3dc28526c686b38dd19ea9a6a3ee6925cb59`
- 消息数：34
- 会话模型元数据：`opencode/deepseek-v4-flash-free`

本账本不复制原始会话中的认证信息。

## 实际取证状态

| 顺序 | 动作 | 结果 | 能证明什么 |
|---|---|---|---|
| 1 | 远端列出 `/nbudata/vmcore/` | 成功 | vmcore、vmcore-dmesg.txt、messages.txt 存在 |
| 2 | 读取 vmcore-dmesg.txt 与 messages.txt | 成功 | panic 文本、寄存器文本、调用栈文本和日志时间线可用 |
| 3 | 用 `3.10.0-1160.119.1` vmlinux 启动 crash | 失败：文件不存在 | 没有取得 crash 交互证据 |
| 4 | 查找 vmlinux/kernel-debuginfo | 成功确认目标 debuginfo 未安装 | 目标版本 DWARF 不可用 |
| 5 | 用目标版本 `/boot/vmlinuz` 启动 crash | 失败：文件不存在 | 没有取得 crash 交互证据 |
| 6 | 尝试从压缩内核自行提取 ELF 后启动 crash | 失败：文件格式不受支持 | 没有取得 crash 交互证据 |
| 7 | 搜索互联网中的 `dm_softirq_done` UAF 和补丁 | 成功取得类比材料 | 只能形成候选假设，不能证明本 vmcore 命中该分支 |
| 8 | 生成报告 | 成功 | 报告由日志、类比补丁和模型推理合成 |

会话中没有成功执行以下能够裁定关键冲突的 crash 命令：

- `dis dm_softirq_done`
- `mod -s dm_mod`
- `struct -o dm_rq_target_io`
- `struct dm_rq_target_io <addr>`
- `vtop <addr>`
- faulting request、clone、gendisk、mapped_device 和 dm table 对象遍历

## 推理升级点

### 1. 将寄存器值直接绑定到 C 变量

会话没有反汇编和 DWARF，却把：

- `RBX=0` 解释为 `clone=NULL`；
- `RDI=ffffbd16abacc040` 解释为 `dm_rq_target_io *tio`；
- `RDI+8` 解释为 `tio->md`。

寄存器在优化、内联后的机器代码中不能仅按函数参数约定绑定到源码变量。T0144
后续反汇编证明 `RDI` 是由 `R13+8` 加载的 `tio->ti`，并非函数入口参数。

### 2. 从相似函数名选择了错误补丁

会话搜索到 `61febef40bfe`：

```text
dm-rq: don't dereference request payload after ending request
```

它确实描述 `dm_softirq_done()` 中另一类 UAF，但属于 `clone == NULL`/
request-payload 路径。会话随后用该补丁反向解释现场，没有先证明本次 fault
执行了该分支。

### 3. 将时间邻近提升为直接因果

日志存在 iSCSI/Actifio 事件，于是会话推演：

```text
iSCSI 全路径故障 → DM_MAPIO_KILL → clone=NULL → request payload UAF
```

但会话没有恢复 faulting request 的实际底层设备，也没有证明相关日志设备与
faulting dm 设备相同。

### 4. 把参考命令写入报告

报告末尾列出了目标 vmlinux 的 crash 命令，但该命令没有在会话中成功执行。
原始生成文件末尾还明确注明本次分析基于 dmesg/messages；Downloads 副本删除
了该限制说明，使读者更容易误认为报告已经执行 crash。

## 文件谱系

| 文件 | SHA-256 | 关系 |
|---|---|---|
| `/home/black/vmcore_analysis_report.md` | `7d383c55e2cf9b6b0d3c1d287930aac3f2c390d689f8db8bd5ca7ba5129eb99c` | 会话直接生成版本 |
| `/home/black/Downloads/vmcore_analysis_report.md` | `f087f00ae06379347d63462b0a4ee42f50ffb70ed52a9efeb56b6559147bc771` | 后续派生副本 |

派生副本的实质变化包括：

- 删除远端主机前缀；
- 删除“当前内核”行；
- 删除“未安装 kernel-debuginfo，本次基于 dmesg/messages 完成”的限制说明。

## 账本结论

报告 A 不是伪造日志，而是把有限日志中的真实现场与未经本 vmcore 验证的源码/
补丁类比混合后，过早升级成确定根因。其 panic 位置、寄存器原始值和日志事件
仍可作为候选输入；变量身份、执行分支、对象生命周期、直接设备与修复版本结论
必须重新取证。
