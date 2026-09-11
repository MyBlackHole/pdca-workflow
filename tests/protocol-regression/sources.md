# 机制参考与适用范围

核对日期：2026-09-12。这些来源只支持机制解释，不证明任意Agent宿主已具备能力；本版具体状态/期限策略是项目设计决定。无需安装以下工具作为PDCA运行依赖。

| 来源 | 核对位置/支持的内容 | 不支持的过强推断 |
|---|---|---|
| [gRPC Cancellation](https://grpc.io/docs/guides/cancellation/) | Cancelling an RPC Call on the Client Side：应用handler需要协作停止 | 发取消就一定没有在途副作用 |
| [etcd v3.6 concurrency API](https://etcd.io/docs/v3.6/dev-guide/api_concurrency_reference_v3/) | Lock/Unlock及lease所有权键 | 有协调锁就自动fence外部资源 |
| [Kleppmann：How to do distributed locking](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html) | 过期客户端、暂停和资源侧fencing问题 | 在Markdown里写epoch即可阻止旧写 |
| [Python graphlib](https://docs.python.org/3/library/graphlib.html) | 直接前置邻接、prepare查环及done推进 | 依赖DAG代表所有资源等待无死锁 |

本文不把动态网站当前产品功能声明为已测试。检索时网页可见版本并非用户部署版本；真实能力必须另行通过CAP/RESOURCE用实际后端验证。
