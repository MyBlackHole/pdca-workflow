# neovim 配置优化分析：现有配置的优化空间与改进建议

任务 ID: T0298
场景类型: research
来源: 用户请求「分析 neovim 配置是否有优化空间」
创建: 2026-08-16

## 问题陈述

用户 neovim 配置（NvChad v2.5 + lazy.nvim，33 个插件）已使用一段时间，
希望系统分析是否存在优化空间：配置正确性、启动性能、加载策略、插件冗余、
LSP/treesitter 配置完整度。仅产出分析报告与改进建议清单，不改动配置。

## 目标

对现有 neovim 配置做全面体检，输出分优先级的优化建议清单，作为用户后续
决策的依据（是否采纳、是否创建改造任务）。

## 方案

1. **配置正确性检查**：无效变量（如 `vim.auto_complete`）、非法值
   （如 `vim.opt.syntax = "enable"`）、语义错位 autocmd（BufWinEnter 误用）。
2. **启动性能**：冷启动计时（已测 0.05-0.06s）、懒加载策略评估、
   NvChad 默认 `lazy=true` 全插件行为。
3. **加载策略**：event/cmd/keys 触发分布、是否有启动时强制加载项。
4. **LSP 配置**：4 个 servers（clangd/rust_analyzer/gopls/pyright）无 ft 门控
   每次启动强制 enable，评估是否应按 filetype 门控或延迟。
5. **Treesitter**：mermaid.so 在 site/parser 但当前配置未声明 mermaid 解析器；
   评估是否需要声明（md-render.nvim 依赖）。
6. **插件冗余**：33 个插件逐项评估必要性（如 vim-translator、fittencode、
   menu/volt/minty 等 NvChad 附带件）。
7. **产出**：按优先级（高/中/低）分类的建议清单报告。

## 用户故事

- 作为 neovim 用户，我想知道配置里有没有会引发潜在 bug 的写法
  （无效变量/错位 autocmd），以便及时修正。
- 我想知道启动性能和加载策略是否还有优化空间。
- 我想知道哪些插件是冗余或可替换的。
- 我想知道 LSP 与 treesitter 配置是否完整、是否有隐患。

## 实现/测试决策

- research 场景，无代码产出，仅分析报告（遵循边界裁决脚本结论）。
- 可执行检查（已执行）：
  - 15 个 lua 文件 `luac -p` 语法全部 OK
  - 冷启动 3 次计时 0.05-0.06s
  - 无残留 .cloning；mason 仅 registries 无服务端
  - 4 个 LSP 均在 /usr/bin，非 mason 安装
  - mermaid.so 存在于 site/parser（7月12日）
- 事实以 `~/.config/nvim` 当前状态为准；报告不改动任何配置。

## 验收标准

- [ ] AC-1: 报告覆盖配置正确性、启动性能、加载策略、LSP、treesitter、插件冗余 六方面
- [ ] AC-2: 每项发现均附配置文件:行号 证据，可追溯
- [ ] AC-3: 建议按高/中/低优先级分类，每条含理由与预期收益
- [ ] AC-4: 报告不修改任何配置（纯调研，无代码/配置产出）
- [ ] AC-5: 已用可执行检查（语法/计时/状态）核验的关键事实标注验证方式

## 范围外

- 不修改 neovim 配置（用户确认仅报告）。
- 不执行建议项（如需改造另建 development 任务）。
- 不评估颜色主题美观性（主观）。

## 备注

- 输入源：`~/.config/nvim` 全量配置、`~/.local/share/nvim/lazy/` 插件状态、
  `~/.local/share/nvim/mason`、系统路径 LSP 二进制。
- 前置事实：T0297 已为 md-render.nvim 安装 budoux.lua 依赖；配置经 chezmoi 管理。
- 输出位置：evidence 报告，登记到 T0298 record。