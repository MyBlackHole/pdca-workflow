# bcachefs journal 崩溃恢复专题学习报告（T0515）

> 精读 `fs/journal/`（约 9200 行）核心结构与流程；10 个 journal 相关
> 本体节点为辅。事实源为源码。

---

## 一、全景：journal 是什么

journal 是 bcachefs 的崩溃一致性中枢：所有 btree 更新先记日志再
落盘；崩溃后按 seq 重放。核心矛盾有三：**保序**（乱序重放即
corrupt）、**空间**（日志盘满即卡死写入）、**回收**（刷 pin 需耗
日志空间，超前回收即死锁）。

数据结构中枢（`fs/journal/types.h`）：
- `journal_buf`：双缓冲条目，closure 异步 IO。
- `journal_entry_pin_list`：pin 按 btree0-3/key_cache/other 分类
  双链表（unflushed/flushed），FIFO 索引。
- `journal_res`：预留（offset/u64s/seq）。
- `journal_space`：三视角（discarded/clean_ondisk/clean/total）。

**可学**：把"保序/空间/回收"三矛盾显式建模为三套机制，而非一锅烩。

## 二、写入路径：预留组装校验三段

1. **预留**（`journal_res_get_fast/slow`）：快路径无锁先判 offset
   与 watermark；失败复判加 must_open 重试；满且低水位就地直接
   回收（`journal.c`）。
2. **组装**（`bch2_journal_write_prep`）：丢弃空预留，翻转写缓冲键
   落盘，补齐缺失树根，追加时间超块尾缀（`write.c:656`）。
3. **校验分叉**：按加密与版本决定先验分支，组装 magic/version/
   nonce/csum（`bch2_journal_write_checksum:771`）。
4. **封条**：关闭先固化长度与末序号，超额直接紧急只读；错误值
   走泄漏 pin 保推进（`__journal_entry_close_one`）。
5. **降级级联**：无刷盘需求降级，有后继拼接到下一条，一次越过
   全部唤醒（`write.c:1041-1102`）。

**可学**：提交分预留组装校验三段，每段失败语义明确；错误路径保
推进（泄漏 pin）而非保优雅。

## 三、空间记账：三视角加短板仲裁

- 三视角：discarded/clean_ondisk/clean/total（`reclaim.c`）。
- Top-K 短板：逐盘算可用，取前 K 大，最小者为结果；K 取在线数
  与元数据副本较小值（`__journal_space_available`）。
- RAM/4 非对称钳制：总量钳常量，干净量随脏收缩；只钳总量不钳
  下一条，防推进卡死。
- 在途扣减：遍历未写条目扣减，不足借整桶对齐。
- 免刷三条件：落盘内存差距小且落盘占优可免刷。

**可学**：多视角记账必须显式定义游标；钳制非对称（保推进的不钳）；
异构成员取短板用 Top-K 而非最小值。

## 四、回收水位机：四条件加节拍线程

- 四条件或触发：空间/pin/写缓冲/开桶任一紧张即回收水位
  （`bch2_journal_set_watermark`）。
- 双指针推进：持锁按落盘序号前移脏指针，再触发丢弃排队
  （`bch2_journal_space_available:308-314`）。
- 节拍刷盘线程：取半桶半钉较大为目标；超时/中位/脏超标定最小量
  循环刷；按节拍睡，踢醒或空队唤醒（`__bch2_journal_reclaim`）。
- 满时就地回收：冻结时 workitem 不跑，直接干
  （`journal.c:924-931`）。

**可学**：水位多条件或语义；后台线程节拍睡加踢醒；冻结时就地干
而不等线程。

## 五、Pin 钉住：引用保持阻止推进

- 脏元数据对 seq 引用保持阻止末序号推进，与容量记账正交
  （`bch2_journal_pin_set`）。
- 分类型有序回刷：保活复制，按 btree/key_cache/other 分类
  （`journal_flush_pins`）。
- 刷 pin 需耗空间，超前于重放死锁，故遇未重放即停
  （`reclaim.c:778-784`）。
- 慢路径等待按最慢成员延迟算（刷提交要预刷全部读写成员）。

**可学**：引用保持必须显式 pin；回收与重放先后关系显式建模，
超前即停优于死锁后排查。

## 六、崩溃恢复：三区加黑名单

- 逆序找最新刷盘定三值：当前号、重放止、末序号；其间撕裂全标
  忽略交上层拉黑（`read.c:1172-1284`）。
- 黑名单保序：落盘新于最新日志则丢弃，序号永不复用并持久化
  （`seq_blacklist.c`）；区间合并加二分查询。
- 读副本仲裁：同盘同扇区返回，同盘异扇区报错，双副本皆好非全
  等报错，坏者被好者替换（`journal_entry_add`）。
- 条目边验边删：逐键校验，坏键置空移删（`journal_validate_key`）。

**可学**：恢复分三区定界；黑名单保序加永不复用；副本仲裁规则
显式；容器内坏键边验边删而非整丢。

## 七、生命周期：开关机状态机

- 循环开关条目，强制开关与刷等待判定，避免旧递归
  （`bch2_journal_cycle_locked`）。
- 停机置错唤醒防驻留；静默等落盘否则先关
  （`halt_locked`、`quiesce`）。
- 按序刷加单调刷盘号，错态回错防永等；超时打印
  （`flush_seq_async`、`flush_seq`）。
- 免刷区需特性门控；重写区间记覆盖；空预留强制落盘推进。

**可学**：开关机显式状态机；刷盘号单调；错态回错防永等。

## 八、设计启示（可学之处汇总）

1. 三矛盾显式建模三套机制，不一锅烩。
2. 提交分段，每段失败语义明确；错误路径保推进。
3. 记账多视角加非对称钳制；短板用 Top-K。
4. 水位多条件或；冻结就地干。
5. 引用保持显式 pin；超前即停。
6. 恢复三区定界；序号永不复用；坏键边验边删。
7. 状态机显式；刷盘号单调；错态回错。

---

## 复核途径

- `ls fs/journal/` 看 8 文件分工；`grep -n "struct journal" fs/journal/types.h` 看中枢。
- `sed -n 656,800p fs/journal/write.c` 看组装校验；`sed -n 1172,1290p fs/journal/read.c` 看三区恢复。
