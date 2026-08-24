# 附录 B：关键函数逐条指令注释（AArch64）

任务：T0393 | 对象：GoldenDB xtrabackup 二进制 | 配套：appendix-followup-analysis.md 式取证报告(research-report.md)
通用约定：`bl`=函数调用(返回地址存 x30)；`cmp w0,#0xa` 中的 **0xa=10=DB_SUCCESS**(dberr_t 枚举值)；
`adrp+add/ldr` 组合=PC 相对访问全局区；`stp/ldp x29,x30`+`ret`=帧保存/恢复与返回；
AArch64 调用约定：参数依次经 x0,x1,x2,x3(x0 同时是 this)。

---

## 一、SysTablespace::read_lsn_and_check_flags —— retry×2 + doublewrite 恢复（★ 定制编入证据）

对照上游源码 fsp0sysspace.cc:529-561。

```asm
; 序言：开 496 字节栈帧，保存被调方保存寄存器
142e810: stp  x29, x30, [sp,#-496]!     ; 帧指针+返回地址压栈，sp-=496
142e814: mov  x29, sp                   ; 设定新帧基准
142e818: stp  x19, x20, [sp,#16]        ; 保存 callee-saved x19/x20
142e81c: ldr  x20, [x0,#16]             ; x20 = this->m_files 首元素地址 → Datafile* it
142e824: mov  x21, x0                   ; x21 = this (SysTablespace*)
142e828: ldrb w0, [x20,#68]             ; 取 it->m_exists 字节标志
142e82c: stp  x23, x24, [sp,#48]        ; 继续保存寄存器
142e830: cbz  w0, 142eb20               ; m_exists==0 → 跳 ut_a 断言失败块(对应上游 ut_a(it->m_exists))
142e834: ldrb w0, [x21,#80]             ; 取 SysTablespace 只读模式相关成员
142e838: mov  x22, x1                   ; x22 = flushed_lsn 出参指针(透传给 validate)
142e83c: mov  w1, #0                    ; read_first_page 第 2 参(read_only)=false 预置
142e840: cbz  w0, 142e868               ; 标志==0 → 走全局 srv_read_only_mode 分支
142e844: mov  x0, x20                   ; 分支 A: this(Datafile*)
142e848: bl   read_first_page           ; 第一次读取首页(read_only=false)
142e84c: cmp  w0, #0xa                  ; err == DB_SUCCESS ?
142e850: b.eq 142e884                   ; 成功 → 进入校验段
; ---- 读失败快速返回(非重试!): 恢复寄存器后直接 ret ----
142e854: ldp  x19, x20, [sp,#16]        ; ┐
142e858: ldp  x21, x22, [sp,#32]        ; │ 还原 callee-saved
142e85c: ldp  x23, x24, [sp,#48]        ; │
142e860: ldp  x29, x30, [sp],#496       ; │ 帧还原
142e864: ret                            ; ┘ return err   ←【读首页失败不重试】
142e868: adrp x0, ...                   ; 分支 B: 页基址
142e86c: ldr  x0, [x0,#1488]            ; 全局 srv_read_only_mode 地址
142e870: ldrb w1, [x0]                  ; 读其字节值作参数
142e874: mov  x0, x20
142e878: bl   read_first_page           ; 第一次读取(参数=全局只读模式)
142e87c: cmp  w0, #0xa                  ; 同样判 DB_SUCCESS
142e880: b.ne 142e854                   ; 失败 → 同一快速返回出口

; ===== 校验第 1 轮 =====
142e884: ldr  x0, [x20,#40]             ; it->first_page 缓冲指针
142e888: cbnz x0, 142eb50               ; 非空 → 异常/断言路径(缓冲应已被释放)
142e88c: ldr  w1, [x20,#52]             ; 参数1: it->m_space_id
142e890: mov  w3, #0                    ; 参数3: for_import=false
142e894: mov  x2, x22                   ; 参数2: flushed_lsn
142e898: mov  x0, x20                   ; this
142e89c: bl   validate_first_page       ; ★ 校验第 1 次
142e8a0: cmp  w0, #0xa                  ; DB_SUCCESS?
142e8a4: mov  w19, w0                   ; err 存入 w19 备份
142e8a8: b.eq 142e8e0                   ; 首验即成功 → 跳过 dblwr, 直接第 2 轮校验
; ---- 首验失败 → 从 doublewrite buffer 找 page 0 副本 ----
142e8ac: mov  w1, #0                    ; 参数: restore_page_no=0
142e8b0: mov  x0, x20
142e8b4: bl   restore_from_doublewrite  ; ★ dblwr 兜底(上游 mysqld 专用逻辑)
142e8b8: cmp  w0, #0xa                  ; 恢复动作自身成功?
142e8bc: b.eq 142e8e0                   ; 成功 → 第 2 轮校验
; ---- dblwr 也没有副本 → 关闭文件, 带原始错误码返回 ----
142e8c0: mov  x0, x20
142e8c4: bl   Datafile::close
142e8c8: mov  w0, w19                   ; 返回最初 validate 的错误码
142e8cc..142e8dc: (同 142e854 序言还原) + ret
; ===== 校验第 2 轮(dblwr 恢复后的复核) =====
142e8e0: ldr  w1, [x20,#52]             ; 与第 1 轮相同的三参数
142e8e4: mov  w3, #0
142e8e8: mov  x2, x22
142e8ec: mov  x0, x20
142e8f0: bl   validate_first_page       ; ★ 校验第 2 次
142e8f4: cmp  w0, #0xa
142e8f8: mov  w19, w0
142e8fc: b.ne 142e8c0                   ; 仍失败 → close + return err
; ---- 两轮通过 → space_id 一致性检查 ----
142e900: ldr  w1, [x20,#52]             ; Datafile::m_space_id
142e904: ldr  w0, [x21,#48]             ; SysTablespace::space_id
142e908: cmp  w1, w0
142e90c: b.eq 142eb38                   ; 相等 → 正常继续(读其余文件 LSN)
142e910..: (ios_base 构造序列)          ; 不等 → ib::error "wrong space ID"
```

**要点**：
1. `cmp w0,#0xa` 反复出现 = 与 `DB_SUCCESS`(枚举值 10) 比较。
2. retry×2 在机器码中被编译器**全展开为两段直线代码**（validate#1 → fail? dblwr → validate#2 → fail? return），
   无运行期循环头——此前"回边→0x142e854"的说法需修正：**0x142e854 是读失败的公共序言恢复点，不是循环回边**。
   语义与上游 `for(retry=0;retry<2;++retry)` 等价，实现为空间换时间的 if-else 展开。
3. `read_first_page` 出现两次是**只读模式参数的两个分支**各一次调用，不是读了两次首页。

---

## 二、Datafile::validate_first_page 主干 —— 单次读取、单次判定、四出口

```asm
; ---- 读首页(唯一一次) ----
1422710: bl   read_first_page
1422714: cmp  w0, #0xa                  ; 成功?
142271c: b.eq 1422140                   ; 成功 → 跳校验链头部
         (失败路径: strlen/_M_append 等 string 操作 = 拼 "Cannot read first page" 文案
          → 经共享日志出口输出 → free_first_page → 返回)

; ---- checksum 判定段 ----
14229c0: mov  w0, w1                    ; 参数: space_id
14229c8: bl   fsp_is_checksum_disabled  ; 该表空间是否禁用校验(仅系统临时表空间)
14229cc: strb w0, [x29,#720]            ; skip_checksum 局部变量落栈
         (构造 BlockReporter: 栈上填 check_lsn/read_buf/page_size/skip 四字段,
          0x14229d0-0x14229f0 的 adrp/str 序列即成员写入)
14229f4: bl   BlockReporter::is_corrupted   ; ★ 唯一一次损坏判定
14229f8: uxtb w0, w0                    ; 返回值 bool 清洗到 0/1
14229fc: cbz  w0, 1422a10               ; 未损坏 → 跳加密 key 检查段
1422a00: adrp x23, ...                  ; ┐ 装载错误文案地址
1422a04: add  x23, x23, #0xba8          ; ┘ ("Checksum mismatch")
1422a08: b    14221bc                   ; → 共享错误打印块(ib::error ER_IB_MSG_399)
                                        ;   该块最终 free_first_page + 返回 DB_ERROR
                                        ;   【这就是生产日志那行报错的机器码源头】

; ---- 未损坏 → 加密信息检查段 ----
1422a10: ldr  w0, [x20,#64]             ; flags
1422a14: ubfx x0, x0, #13, #1           ; 提取 bit13 = FSP_FLAGS_GET_ENCRYPTION
1422a18: eor  w0, w0, #1                ; 取反
1422a1c: orr  w3, w21, w0               ; 与 for_import 组合
1422a20: cbnz w3, 14230e4               ; 非加密表(或 import 场景) → 跳过密钥段
         (后续: fsp_header_get_encryption_key / Encryption::get_master_key_id /
          OSDecodeAES ×8 —— GoldenDB 私有密钥解码定制)
```

**要点**：`ubfx x0,x0,#13,#1` 直接印证 Flags 位布局中 bit13=ENCRYPTION（生产案例
16417 解码 ENCRYPTION=0 的依据在机器码层可复核）。整个函数从读到判是单程直线，
四个 `free_first_page` 出口分别服务不同失败类别。

---

## 三、fil_open_for_xtrabackup —— 校验失败即放弃（零重试主证据）

```asm
; ---- 栈对象(Datafile 及多个 std::string)清零初始化 ----
1409de0: sub  sp, sp, #0x2a0            ; 开 672B 栈帧
1409df0: stp  x29, x30, [sp,#-64]!
         (1409e04-1409e78: 连续 stp xzr / strb wzr —— 成员零初始化;
          1409de4 mov w4,#0x33 等预置常量属局部结构初值)

1409e7c: bl   Datafile::set_name
1409e88: bl   Datafile::set_filepath
1409e8c: mov  w1, #1                    ; read_only=true
1409e94: bl   Datafile::open_read_only
1409e98: cmp  w0, #0xa                  ; 打开成功?
1409e9c: mov  w20, w0                   ; err 暂存 w20 (此后成为返回值寄存器)
1409ea0: b.eq 1409ec8                   ; 成功 → 校验段
1409ea4: mov  x0, x19
1409ea8: bl   Datafile::shutdown        ; 失败 → 清理
         ...(恢复寄存器)...
         ret                            ; return w20   【打开失败出口】

; ---- 首页校验(仅一次) ----
1409ec8: mov  w3, #0                    ; for_import=false
1409ecc: add  x2, x29, #0x48            ; &flush_lsn (栈出参)
1409ed0: mov  w1, #-1                   ; ★ space_id = SPACE_UNKNOWN(0xffffffff)
1409ed4: mov  x0, x19                   ; this
1409ed8: bl   validate_first_page       ; 唯一一次校验
1409edc: cmp  w0, #0x45                 ; == DB_PAGE_IS_BLANK(69)?
1409ee0: b.eq 1409ea4                   ; 全零页 → shutdown; 此时 w20 仍=10(DB_SUCCESS)
                                        ;  ⇒ 借道 shutdown 但以 DB_SUCCESS 返回 = 豁免放行
1409ee4: cmp  w0, #0xa                  ; == DB_SUCCESS?
1409ee8: b.eq 1409ef8                   ; 成功 → 注册段
1409eec: mov  w20, w0                   ; 其他错误(Checksum mismatch 属此类)
1409ef0: b    1409ea4                   ; → shutdown + 以错误码返回  【零重试放弃点】

; ---- 注册段(仅校验通过可达) ----
1409ef8: ldr  w0, [x29,#132]            ; file.space_id()
1409efc: bl   fil_space_get             ; 已注册?
1409f00: cbz  x0, 1409f0c               ; 未注册 → 继续
1409f04: mov  w20, #0x2a                ; =42 = DB_TABLESPACE_EXISTS
1409f08: b    1409ea4                   ; shutdown + 返回"已存在"
1409f0c: bl   os_file_get_size          ; 文件大小 → n_pages
         (后续: fil_space_create → fil_node_create → fil_space_open/close)
```

**要点**：
1. `mov w1,#-1` = 上游 `SPACE_UNKNOWN` 实参，与源码 fil0fil.cc:11727 一致。
2. `cmp w0,#0x45` 中 **0x45=69=DB_PAGE_IS_BLANK**；豁免的实现方式是"借道
   shutdown 但保留 w20=DB_SUCCESS 返回"，机器码语义与源码注释
   ("zero-filled page restored from redo later")完全吻合。
3. `mov w20,#0x2a`(42=DB_TABLESPACE_EXISTS) 印证重复打开检测。
4. **Checksum mismatch 错误(非 BLANK 非 SUCCESS)落入 1409eec→1409ea4：
   一次调用即终止，全程无第二次 validate_first_page。**

---

## 四、Tablespace_files::open_ibds —— 遍历循环 ≠ 重试循环

```
140a1a8 / 140a1f0   ← 外层 map 迭代回边(遍历 ibd_paths 的 for)
140a1c8/204/238     std::string 构造(拼完整路径)
140a244  bl  fil_open_for_xtrabackup      ← 循环体内直呼下一个文件
140a594  fil_assign_new_space_id          ← GoldenDB 定制符号
```

判别逻辑：回边目标指向的是**迭代器推进代码**（回到循环条件判断），
而非 fil_open_for_xtrabackup 的重入。循环变量是"下一个文件"，
失败文件的返回值未被捕获（调用后无 cmp/b.eq 检查序列紧随）——
**忽略返回值**的机器码形态。

---

## 五、xb_fil_cur_read —— 对照组：拷贝路径的重试机器码

```asm
da904c:  bl   xtrabackup_io_throttling   ; ← read_retry 回边目标(IO 限速)
         (重载游标字段: buf_read/buf_npages/buf_offset 归零)
da90b8:  bl   os_file_read_no_error_handling_func   ; 第 1 次整块读取
         (解密/解压预处理...)
da927c:  bl   BlockReporter::is_corrupted
da9284:  cbz  w0, da91e4                 ; 页完好 → 前进到下一页
         ; ---- 损坏处理 ----
da9288:  ldrb w0,[x28,#1200]             ; cursor->is_system?
         (系统表空间且命中 doublewrite 页范围 → 跳过, 对应 fil_cur.cc:391)
da9298:  ldr  x0,[x29,#136]              ; 取 retry_count
da929c:  subs x0, x0, #1                 ; retry_count--
da92a0:  str  x0,[x29,#136]              ; 写回
da92a4:  b.eq da93fc                     ; 减到 0 → 跳"10 次耗尽"报错退出
da92b4:  bl   msg                        ; "Database page corruption detected at page N, retrying..."
da92b8:  movz x2,#0xe100                 ; ┐ 0x5F5E100 = 100,000,000 ns
da92c0:  movk x2,#0x5f5,lsl #16          ; ┘ = 100ms → sleep_for(100ms)
         (回跳 read_retry → 重新整块读取)
da9358:  bl   os_file_read_no_error_handling_func   ; 重试时的再次读取
```

**要点**：`subs x0,#1 / b.eq` 就是源码 `if (--retry_count == 0)`；
立即数 0x5F5E100=10⁸ 纳秒精确对应 `milliseconds(100)`。
对照组成立：同一二进制内拷贝路径具备完整重试机制，扫描路径没有——
证明这是设计取舍而非工具能力缺失。

---

## 汇总：三条路径的机器码级行为矩阵

| 路径 | 读取次数 | 校验次数 | dblwr 兜底 | 失败动作 |
|------|---------|---------|-----------|----------|
| backup 扫描(validate_first_page @fil_open_for_xtrabackup) | 1 | 1 | 无(0 次调用) | shutdown+return err，文件出局 |
| backup 对 ibdata(read_lsn_and_check_flags)★定制编入 | 1(两分支) | **2** | **restore_from_doublewrite(0)** | 双败才 close+return |
| backup 拷贝(xb_fil_cur_read) | ≥2(首读+重读) | 每页 1 | 无 | 10 次耗尽才报错 |

图例：★ 为 GoldenDB 对上游 HOTBACKUP 编译范围的定制改动点。
