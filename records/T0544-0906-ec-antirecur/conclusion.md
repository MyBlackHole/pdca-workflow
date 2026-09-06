---
schema: pdca.asset/v1
id: T0544-0906-ec-antirecur
phase: check
source_ids: [node-core-ec-rs-math, node-core-ec-rs-algorithm, node-core-ec-stripe-geometry, node-core-ec-stripe-alloc, node-core-ec-rs-principle, validate-output, ac3-verify, convergence-map-v3]
---

## 上下文
用户批评本体不符合实际问题与修复方案，要求问题驱动防复发闭环。

## 假设与结果
- 假设 1：真实提交可考。结果：成立，7 个提交 message 核实。
- 假设 2：子任务拆解合规。结果：成立，T2063/T2064 创建，children 已设。

## 分析
- **AC-1** ✅ 5节点补三段如下（5 node 证据）：
  1. rs-math：问题=7.2 改名致编译失败；修复=`a03937a2a` shim 宏映射新名到旧 API；防复发=条件编译隔离版本差异。
  2. rs-algorithm：问题=同上接口漂移；修复=垫片集中一处；防复发=不散落调用点。另超限封顶为设计决策（`raid_gen` BUG），无历史事故。
  3. stripe-geometry：问题=超大目标组折叠为无标签门误判全盘可建；修复=`9281beaa2` 前置拒绝；防复发=门控与执行共用拒绝谓词。
  4. stripe-alloc：问题a=原始偏移质心拖死小盘（1G 盘 26% vs 8G 盘 3%）；修复=`6cf75ca7c` 分数质心；防复发=质心定义写进注释。问题b=门控查冗余加 1 与实际拒绝（加 2 查域）不一致致空转；修复=`6a73af4a7` 双条件建模；防复发=门控与执行共用判定函数。问题c=同域多块损坏超冗余丢数据；修复=`707b0dbd6` 同域硬排除加限宽；防复发=正确性约束用硬失败不用偏好。问题d=离群重分配数组越界告警；修复=`97129d6bc` 边界收紧；防复发=越界警告零容忍。
  5. rs-principle：问题a=现网疏散时同条双块 extent 被误删一指针；修复=`90a55e64a` 按块号双键精确匹配；教训=身份须双键。问题b=修复中途退出时在途 IO 写已释放内存；修复=`bc66229c9` 先同步后释放；教训=teardown 与 setup 逆序。问题c=复用旧条长期累积漏出移除守卫视野；修复=`d6e40165c` fencing 全覆盖；教训=生命周期各阶段无例外。
- **AC-2** ✅ 三查 0 issues，validate 全绿（5 node + validate-output）
- **AC-3** ✅ 证据登记完成，Check 门禁通过（ac3-verify）

关键结论：7 个真实问题全部关联提交哈希，修复与防复发措施均有出处。
复核途径：`git show <hash>` 查提交原文；节点 Read 核对。

## 本体沉淀

决策：`ontology:ontology:domain/core-ec-rs-math` 等 5 节点（更新增补节）。

理由：问题驱动三段属可复用知识增量。来源 record `T0544-0906-ec-antirecur`。

## 适用边界
- 问题解读基于提交 message，未逐行审 diff；根因表述置信度次于机制本身。

## 下一轮建议
- 其他主题节点按此模式补问题驱动节。

verdict: {"outcome": "confirmed", "reason": "3 AC 全绿，7真实问题关联提交", "verdict_id": "vt0544-confirmed", "at": "2026-09-06T00:00:00+08:00"}
