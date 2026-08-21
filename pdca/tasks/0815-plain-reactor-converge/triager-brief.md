# Triage Brief — 0815-plain-reactor-converge

- **category**: enhancement
- **scenario_type**: design
- **summary**: 分析 backupstream plain（非 TLS）路径的现状与瓶颈，产出一份"综合多维度提升"的优化方案文档（含基准与分阶段改造设计），供后续实施。
- **current behavior**: plain 路径仍为单 Reactor + 弹性阻塞 worker 池。控制帧（PING/TIME/SYS）已由 v81 接入非阻塞前端异步执行；但业务帧（TREE/FILE/restore/EXEC setup）仍整体占用一个阻塞 worker 直至整个事务结束；plain 事件处理未分片，单 Reactor 为吞吐天花板。
- **desired behavior**: 产出一份可执行的优化方案文档，覆盖吞吐（突破单 Reactor）、延迟（业务帧异步化）、线程/资源（阻塞 worker 收敛）三方面提升，并给出分阶段改造路径、基准口径与验收标准，经确认后作为后续实施任务的蓝图。
- **key interfaces**: plain ingress 非阻塞前端、reactor_group 分片基建、work_pool 公平调度、session pool 弹性 worker、TLS 异步执行域（tree/lane/control work pool）、现有 benchmark 脚本、AC-5 控制面判据。
- **acceptance criteria**: 方案文档存在并覆盖瓶颈/改造设计/分阶段路径/基准/验收/风险；改造设计可映射到具体模块概念；基准给出 plain 与 TLS 对比及预期收益；每项改造标注风险等级与独立验证方式。
- **out of scope**: 不实施任何源码改造（本任务仅产出方案文档）；不涉及 TLS 路径重构；不做数据面（Data Lane）架构重构。
- **information gaps**: plain 各业务 handler 的实测占用分布、TLS 异步执行域对 plain 的复用可行性细节、分片后连接归属与每会话排序约束。
- **dedup results**: 与 T0287（架构分析报告）不重复——T0287 产出现状架构报告，本任务产出性能优化方案；与 T0291/T0293（控制面优化）不重复——本任务聚焦业务帧异步化与分片；知识库 control-plane-nonblocking-ingress 仅覆盖控制面非阻塞，未覆盖业务帧异步化。
- **recommended next steps**: 完成现状基准采集 → 撰写优化方案文档 → 与用户确认方案 → 按确认结果拆分为实施子任务。
