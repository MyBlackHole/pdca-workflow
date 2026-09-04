---
schema: pdca.asset/v1
id: ontology:domain/editor-config-neovim-config-audit
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/editor-config-neovim-config-audit/1.0.0
summary: neovim 配置体检方法论：检查清单与可执行命令
domain:
- ontology:domain/editor-config
relations:
  specializes:
  - ontology:domain/editor-config
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "运行 grep -q 'neovim 配置体检方法论：检查清单与可执行命令' ontology/domain/core/editor-config-neovim-config-audit.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'"
---


# neovim 配置体检方法论：检查清单与可执行命令

> 来源任务: T0298（neovim 配置优化分析）
> 适用: 对 NvChad/lazy.nvim 管理的 neovim 配置做系统性体检时。

## 检查清单（按优先级）

### 1. 配置正确性（高优先级，静默 bug 源）

| 检查项 | 手法 | 典型错误 |
|--------|------|---------|
| 无效变量 | grep `vim.auto_complete` 等非 neovim 选项 | `vim.auto_complete = true`（静默无效） |
| 非法值 | grep `vim.opt.syntax` 等取值合法性 | `syntax = "enable"`（应为 `"on"`） |
| autocmd 语义错位 | 检查 autocmd 的 pattern 与 command 是否作用于同一对象 | BufWinEnter pattern 过滤文件，但 command 对当前缓冲区做 `%s` 替换（每次进入窗口重复执行） |

关键判别：**pattern 决定触发条件，command/callback 作用对象要与 pattern 语义一致**。
如去 CR 应 `setlocal fileformat=unix`，而非在 BufWinEnter 反复 `%s/[\\u0d]//ge`。

### 2. 启动性能（低优先级，通常已优）

- 冷启动计时：`/usr/bin/time nvim --headless +q`（3 次取均值）。
- 启动加载插件数：lazy.nvim `require('lazy').stats()` 的 `loaded` 字段。
- **坑**：headless 下 lazy `startuptime` 恒为 0，不可靠；以 CLI 计时为准。
- RTP 精简：`lua/configs/lazy.lua` 的 `performance.rtp.disabled_plugins` 列表。

### 3. 加载策略（中优先级）

- 确认所有自定义插件用 `event/cmd/keys/ft` 触发，无强制加载。
- 高频事件（`event = { "BufRead" }`）对低使用频率插件可改 `cmd` 进一步延迟。

### 4. LSP 配置（高优先级）

- 检查 `vim.lsp.enable` 是否无 filetype 门控——每次开文件都会启动全部 servers
  尝试 attach。建议按 filetype 过滤或 autocmd 按需启动。
- 检查 servers 是系统二进制（`/usr/bin/`）还是 mason 管理；mason 仅 registries
  无服务端包时版本不受 neovim 控制。

### 5. Treesitter 隐式依赖（中优先级）

- 检查 parser 目录：`~/.local/share/nvim/site/parser/*.so` vs
  `nvim-treesitter/parser/`。
- 存在于 site 但配置未声明 `ensure_installed` 的 parser = 隐式依赖，
  `TSUpdate` 或清理 site 目录会丢失。典型：mermaid（md-render 需要）。

### 6. 插件冗余（低优先级）

- 逐插件核对：框架必需（base46/ui/volt/minty/menu）、依赖件（cmp-* / plenary /
  budoux）、功能件（按实际使用频率）。
- NvChad 附带件属框架运行必需，不可移。

## 可执行检查命令集

```bash
# 1. 语法检查所有 lua 配置
for f in $(find lua -name "*.lua") init.lua; do luac -p "$f" && echo "OK: $f"; done

# 2. 冷启动计时（3 次）
for i in 1 2 3; do /usr/bin/time -f "%e s" timeout 60 nvim --headless +q 2>&1 1>/dev/null; done

# 3. 启动加载插件数
nvim --headless "+lua print('loaded:', require('lazy').stats().loaded)" "+qa"

# 4. 无效变量/非法值扫描
grep -rn "vim.auto_complete\|syntax = \"enable\"" lua/options.lua

# 5. LSP 二进制归属（系统 vs mason）
for bin in clangd rust-analyzer gopls pyright-langserver; do which $bin; done

# 6. parser 目录对比（找隐式依赖）
ls ~/.local/share/nvim/lazy/nvim-treesitter/parser/ | grep -vE "$(ls ~/.local/share/nvim/site/parser/ | sed 's/\.so//' | tr '\n' '|')" 
```

## 报告形态

- 每项发现附 `file:line` 证据，可追溯。
- 建议按高/中/低优先级分类，每条含理由与预期收益。
- 标注验证方式（静态 grep / 可执行命令）。
- 纯体检不修改配置；采纳建议另建 development 任务。

## 适用范围

- 适用于 NvChad + lazy.nvim 架构的 neovim 配置（v0.12 实测）。
- 无效变量/非法值/autocmd 错位检查适用于任意 vim 配置。
- 结论限检查时点状态，配置变更后需重新体检。