# Triage Brief: T0298 neovim 配置优化分析

## 分类
- category: enhancement
- scenario_type: research（纯结论性调研，无代码产出，边界脚本裁决确认）

## Claim 验证（已实地采集事实）
- 配置规模: 16 个 lua/json 文件, 572 行；用户自定义 ~87 行插件配置 + 大量 options.lua
- 插件数: 33 个（含 NvChad 基础），冷启动 0.05-0.06s（已测 3 次）
- 加载策略: 全插件 lazy=true；自定义插件用 event/cmd/keys 触发，无强制加载
- 已发现潜在问题点:
  1. options.lua 末尾 BufWinEnter autocmd 用 pattern 过滤但 command 作用于当前缓冲区,
     且替换 `[\u0d]`（CR 字符），意图可能是移除 CR，但事件/命令语义错位
  2. options.lua 设置 `vim.auto_complete = true`（无效变量，应为 vim.o.completeopt 等）
  3. `vim.opt.syntax = "enable"` 应为 `vim.opt.syntax = "on"`（enable 非法）
  4. lspconfig 强制启动 4 个 servers（clangd/rust_analyzer/gopls/pyright），无 ft 门控
  5. conform 仅配 lua/stylua，format_on_save 被注释；treesitter fold 用 expr
  6. md-render.nvim 依赖已装（T0297 前置），git.lua 仅 9 行

## 查重
- knowledge 无 nvim/neovim/chezmoi 命中
- pdca tasks 无相关任务
- out-of-scope 未查（概念不同）

## 结论
ready-to-plan，进入 P1/P2 澄清与对齐。
