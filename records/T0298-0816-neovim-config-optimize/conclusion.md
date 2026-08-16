---
schema: pdca.asset/v1
id: T0298-0816-neovim-config-optimize
phase: check
source_ids:
  - neovim-config-optimization-report-v2
---

## 上下文

用户请求分析 neovim 配置（NvChad v2.5 + lazy.nvim，33 插件）的优化空间。
本任务做全面体检（配置正确性/启动性能/加载策略/LSP/treesitter/插件冗余），
仅产出报告，不改配置。

## 假设与结果

假设：现有配置存在可优化的空间，且能通过静态+可执行检查定位。

结果：
- 发现 3 处确定正确性 bug（无效变量 `vim.auto_complete`、非法值
  `syntax="enable"`、BufWinEnter autocmd 语义错位反复执行 CR 替换）。
- 启动性能优秀（冷启动 0.05-0.06s，3/33 插件启动加载），无需优化。
- LSP 4 servers 无 filetype 门控，每次开文件全部尝试 attach。
- mermaid treesitter parser 为隐式依赖（site/parser 有，配置未声明）。
- 33 插件逐项核对无冗余。
- 建议按高/中/低优先级分类，每条附 file:line 证据。

## 分析

逐条 AC 判定：

- **AC-1** ✓：报告覆盖六方面（正确性/性能/加载策略/LSP/treesitter/插件冗余）。
- **AC-2** ✓：每项发现附 `file:line` 证据（报告含 12 处行号引用）。
- **AC-3** ✓：建议按高（3 处正确性 bug + LSP 门控）/中（mermaid 声明 +
  fittencode 延迟）/低（使用频率确认）三档分类。
- **AC-4** ✓：纯调研，未修改任何配置（仅生成报告文件）。
- **AC-5** ✓：可执行检查（luac 语法/冷启动计时/lazy stats/mason 目录/
  系统 LSP 二进制/parser 目录）已标注验证方式。

收敛验证：`validate-convergence.py` 返回 `valid: true`，无 issues。

## 适用边界

- 分析基于 2026-08-16 的 `~/.config/nvim` 状态；配置变更后需重新核验。
- headless 下 lazy 启动计时不可靠（startuptime=0），以 CLI 冷启动为准。
- 低优先级建议（插件使用频率）为推断，待用户确认。
- LSP 门控建议的实现方式（filetype 过滤 vs autocmd）未实测对比，属推断。
- 仅报告；采纳建议需另建 development 任务执行改造。

## 下一轮建议

- 如需采纳建议，创建 development 任务执行改造：
  修正 3 处正确性 bug + LSP 门控 + mermaid 声明 + fittencode 延迟加载。
- 改造后重新测量冷启动验证无回退。
- 若 vim-translator/fittencode 不再使用，可一并移除。