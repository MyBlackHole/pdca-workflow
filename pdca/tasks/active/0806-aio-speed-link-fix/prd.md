# T0221 aio-speed 链接修复：do_is_dir/do_batch_list_dir_tree 声明无定义

## 问题陈述

aio-speed 目标链接失败：do_is_dir/do_batch_list_dir_tree 被引用但无定义（T0212 遗留，T0217 已确认 HEAD 同样失败）

## 验收标准（草案）
- [ ] AC-1: aio-speed 链接成功
- [ ] AC-2: 相关 rpc 测试回归通过
- [ ] AC-3: 全量构建无新失败
