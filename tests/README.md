# 当前验证入口

```bash
python3 scripts/check_release.py .
python3 -m unittest discover -s tests -v
```

安装工具与测试只依赖Python标准库（Python 3.10+、POSIX）；无API密钥、不会启动Codex/OpenCode、不会修改真实HOME。安装/登记/卸载测试使用临时目录，执行真实文件操作；文本测试只证明入口包含约定分支，不证明Agent遵守。

本轮覆盖发布摘要与八个入口、集中根、导出路径、只读预览、重复安装、显式更新、外来/修改文件保护、旧快照保留、集中项目登记及多工作区、不写业务目录、卸载保留记录、安装异常回滚和锁竞争。资源语义检查不是生产资源锁或仲裁实现。

[现场验收](host-acceptance.md)仍全部NOT_RUN。不要累计旧验证包数字，或把前一轮合成轨迹当本轮宿主结果。
