# T0173 Triage Brief

## 分类

- category: enhancement
- scenario_type: development
- 来源：用户「下一步推荐」请求 + T0168 AC-7 拆解表 P2/P3（测试补充）方向

## 查重结果

- `pdca/tasks/**/task.json`：无 reclaim 压力测试任务（0801-btree-commit-space-check-fix
  为 T0169 缺陷修复本身，不含该回归测试）；T0170-0172 已归档/提交的属性测试不含 reclaim 触发
- `knowledge/`：无 reclaim 相关条目
- 结论：不重复

## Claim 验证

- 属性测试零触发 reclaim：核对 4 个属性测试源码，均无 reclaim_journal/request_reclaim 调用；
  8MB journal 区、~120 组 ops 不足以触发 high watermark 后台回收 —— 成立
- T0169 修复场景（reclaim 裁剪后恢复丢键）已有确定性回归测试，但属性层面无持续验证 —— 成立

## 信息缺口

- reclaim 生效的断言方式（reclaim_status vs on-disk last_seq）待 P1/P2 澄清
- 触发频率与 crash 参数组合待设计

## 推荐下一步

1. 首选：T0173 reclaim 压力属性测试（本次 triage 已建骨架）
2. 备选（T0168 拆解表 P1）：seq 环回/黑名单机制（D2）、interior split 对齐
3. 备选：属性测试套件并入 CI/回归脚本

## 日期

2026-08-01
