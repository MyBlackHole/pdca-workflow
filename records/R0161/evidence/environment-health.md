# T0161 环境健康检查

`python3 scripts/pdca-doctor.py --json` 返回 `valid=true`：文件系统、Python、Git 可用，57 个引用已检查且无缺失。

`PDCA_HOME` 当前由 repository fallback 提供；对外部项目执行时应设置：

```sh
export PDCA_HOME=/home/black/Documents/pdca-workflow
```

`agent.spawn` 与 `context.retrieve` 采用已声明 fallback，本任务未依赖它们的专用运行时能力。
