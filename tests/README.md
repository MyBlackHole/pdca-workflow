# 当前验证入口

```bash
python3 -m unittest discover -s tests -v
git diff --check
```

测试需要 Python 3.10+ 标准库、POSIX shell 与 Git，无 API 密钥，不启动真实宿主，也不修改真实用户目录。

[安装器测试](test_install_script.py) 在临时 HOME 中运行真实 `install.sh`，使用可控 Git 替身验证：
集中 Git 根克隆、仅九个 catalog 运行入口进入发现目录、与其他 Skill 共存、同名冲突拒绝、
并发路径出现时安全停止，以及失败回滚不删除原有用户数据。它不证明真实网络克隆或宿主发现成功。

[文档与链接检查](test_skill_links.py) 覆盖当前维护入口、使用/安装文档、Skill、本体权威/契约与测试说明的相对链接，
并检查九入口发现面、逐阶段用户操作、Do-only Work Unit Contract、minimum sufficient context、
父 Do 不轮询监工，以及运行规则不再依赖 LOC/工时/置信度拆分阈值。

检查仍只证明静态定义和本地安装行为，不证明 Agent 实际遵守、原生 Agent 隔离、事件路由或资源后端。
资源语义检查也不是生产资源锁/仲裁实现。

[现场验收](host-acceptance.md) 仍全部 `NOT_RUN`。真实宿主发现、独立 Agent、
阶段交互、Work Unit 委派/返回和辅助建议授权需要在目标宿主现场验证；
不要把静态单测或合成轨迹描述为现场兼容性结论。
