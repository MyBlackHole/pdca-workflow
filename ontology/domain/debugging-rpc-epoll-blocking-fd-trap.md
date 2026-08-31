---
schema: pdca.asset/v1
id: ontology:domain/debugging-rpc-epoll-blocking-fd-trap
type: domain
layer: Knowledge
status: active
summary: rpc-epoll 与业务层 fd 语义冲突：O_NONBLOCK ↔ 阻塞读
domain:
- ontology:domain/debugging
relations:
  specializes:
  - ontology:domain/debugging
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"
---


# rpc-epoll 与业务层 fd 语义冲突：O_NONBLOCK ↔ 阻塞读

## 现象

将 rpc-server 迁移到 rpc-epoll 调度层后，真实连接的大帧/长消息随机失败：
服务端日志出现 `EAGAIN` 半读、`rpc_recv` 返回 `-100/-200`、帧解析错位。

## 根因

- rpc-epoll 是 Reactor 模型：accept 后对 fd 执行 `set_nonblock`（`fcntl O_NONBLOCK`），
  以保证 EPOLL 事件循环不被阻塞。
- 业务层（`rpc_recv` / `readn`，libs/common.c 风格）是**阻塞语义**：
  内部 `while` 循环只处理部分 `read()` 返回，遇 `EAGAIN` 即中断/报错，
  不等待 EPOLL 唤醒。两层假设冲突，事件循环与业务层的 fd 状态互相破坏。

## 修复模式

- 在 `rpc_conn_handler` 上下文初始化（首个事件处理前）用
  `fcntl(F_GETFL)` 取 flags → `fcntl(F_SETFL, flags & ~O_NONBLOCK)` 恢复阻塞模式，
  保证调度层内的业务处理沿用既有阻塞 I/O 语义。
- 前提：调度层在 handler 运行期间不会要求该 fd 非阻塞
  （rpc-epoll 仅依赖 `EPOLLONESHOT` 重挂与 busy 标志，不依赖 fd 非阻塞态）。

## 验证

- 恢复阻塞前：集成测试上传/下载 16MB 失败（半读）。
- 恢复阻塞后：64 PASS / 0 FAIL，全量回归 18/18 通过。

## 适用范围与限制

- 适用于「非阻塞事件循环 + 阻塞语义业务层」混合架构的迁移；
- 若调度层与业务层对 fd 状态有竞争（业务长阻塞期间仍触发事件回调），
  此模式不适用，需改为业务层接帧缓冲（partial-read 状态机）。
