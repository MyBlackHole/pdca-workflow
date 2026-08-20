# 源码图解文档验证流程

> 来源：任务 T0300（0820-backupstream-arch-diagram），基于 backupstream 171.0.0 源码绘制 60 张 Mermaid 图后的沉淀经验。

## 适用场景

为大型 C++/Go 代码库产出以图表为主的分析文档（架构图 / 流程时序图 / 状态机图），需保证图表可渲染、引用真实、覆盖完整。

## 关键流程

### 1. 函数级前置分析
- 用探索子代理按模块分批做函数级结构分析，记录关键枚举值、状态机状态数、函数行号（如 `src/agent_plain_ingress.cpp:34` 的 11 态枚举）。
- 交叉核验：枚举定义与 README/docs 中的行为描述互相印证，防止「文档说 A、代码是 B」。

### 2. 全部图表语法校验（硬门禁）
- 提取文档中所有 ` ```mermaid ` 块，逐个用 mmdc 渲染校验：
  ```bash
  python3 - <<'EOF'
  import re
  content = open('DOC.md').read()
  blocks = re.findall(r'```mermaid\n(.*?)```', content, re.DOTALL)
  for i, b in enumerate(blocks, 1):
      open(f'/tmp/fig{i:02d}.mmd', 'w').write(b)
  EOF
  for f in /tmp/fig*.mmd; do
    mmdc -i "$f" -o "${f%.mmd}.svg" -b transparent >/dev/null 2>&1 \
      || echo "FAIL: $f"
  done
  ```
- 输出文件必须以 `.svg/.png/.md` 结尾，否则 mmdc 报「Output file must end with...」。

### 3. 源码引用存在性核验
- 正则提取文档中 `src/xxx.cpp` 引用，逐一 `os.path.exists` 校验。
- 发现缺失引用 = 写文档时用了猜测的文件名，必须改为真实文件名后再复验（T0300 修正了 8 个：`agent_restore_runtime.cpp`→`agent_restore_reactor.cpp`、`dirty_journal.cpp`→`client_dirty_journal.cpp`、`bounded_admission.cpp`→`bounded_admission.hpp` 等）。
- 教训：写入文档前先 `ls src/` 或 `find` 确认文件名，不要在 Plan 阶段就固化可能错误的引用。

### 4. Mermaid 语法易错点
- subgraph 标题 / 节点标签中避免裸 `,` `( )` `/` `:` 等保留字符：`subgraph 帧头[WireFrameHeader 16 字节, pack(1)]` 报 Parse error，应改为 `pack1`。
- flowchart 边标签用 `A -->|标签| B`，不要用 `A --> B: 标签`（后者在部分版本解析失败）。
- `A -- > text --> B` 形式会被误解析为链接方向，改用 `A -->|text| B`。

### 5. 覆盖率与图例规范
- 每张图必须含中文节点标签 + 一行 `**图例**：...`（grep 计数可核验：`grep -c '```mermaid'` 与 `grep -c '图例'` 相等）。
- 验收可测性设计：图表数量、章节标题、图例行、引用文件均可用 grep 复核。

## 边界

- 只面向源码快照，不承诺跟踪未来版本；无性能断言；不深入协议字节级细节时需明确标注。
- mmdc 逐图渲染 O(n) 次启动，60 图约 1-2 分钟，适合 Do 阶段末尾一次性校验。