# 插件行为规格书

本文档是 nonebot_plugin_impart 的**完整行为参考**——记录全局语义、每条指令的详尽行为、以及已确认的边界结果。
所有 handler 的实现应与本文档保持一致。

---

## 1. 全局语义与硬约束

### 1.1 世界判定（`core/world.py`）

| 条件 | 语义 |
|---|---|
| `length > 0` | 正值世界 |
| `length <= 0` | 负值世界（0 归负值） |
| `0 < length <= 5` | xnn 区间 |

### 1.2 零值保护（`infra/data_manager.py`）

以下写路径均保证"数据库最终不会存 0"：

1. `set_jj_length`：`jj_length + delta` 若为 `0.0`，改写 `-0.01`。
2. `set_jj_length_absolute`：传入值四舍五入后若为 `0.0`，改写 `-0.01`。
3. `execute_pk`：胜方和败方写入都用 SQL `CASE`，结果为 `0.0` 时改写 `-0.01`。
4. 挑战状态应用（`_apply_challenge_update`）中若 `length_delta` 后得 `0.0`，改写 `-0.01`。

### 1.3 挑战状态机（`core/game.py:evaluate_challenge`）

挑战按"绝对值量级"比较阈值（正负世界统一），阈值仍是 `25/30`。

| 条件 | 返回状态 | 数据副作用 |
|---|---|---|
| 非挑战、未完成、`25 <= |L| < 30` | `CHALLENGE_STARTED_LOW_WIN` | `is_challenging=True`，胜率 ×0.8 |
| 非挑战、未完成、`|L| >= 30` | `CHALLENGE_COMPLETED` | `challenge_completed=True` |
| 挑战中、未完成、`|L| < 25` | `CHALLENGE_FAILED_HIGH_WIN` | 胜率 ×1.25，退出挑战，长度惩罚（正值 -5；负值 +5） |
| 挑战中、未完成、`|L| >= 30` | `CHALLENGE_SUCCESS_HIGH_WIN` | 胜率 ×1.25，退出挑战，标记完成 |
| 挑战中、`25 <= |L| < 30` | `IS_CHALLENGING` | 无额外改动 |
| 已完成、`25 <= |L| < 30` | `CHALLENGE_COMPLETED` | 保持完成态 |
| 已完成、`|L| < 25` | `CHALLENGE_COMPLETED_REDUCE` | `challenge_completed=False`，长度惩罚（正值 -5；负值 +5） |
| `is_near_zero=True` 且 `L<=0` 或 `L>5` | `XNN_EXIT` | `is_near_zero=False` |
| 非负值、未 near-zero、`0<L<=5` | `LENGTH_NEAR_ZERO` | `is_near_zero=True` |
| 未标记 zero_or_neg、`L<=0` | `LENGTH_ZERO_OR_NEGATIVE` | `is_zero_or_neg=True` |
| 已标记 zero_or_neg、`L>0` | `NONE` | `is_zero_or_neg=False` |

> **架构说明**：纯判定逻辑在 `evaluate_challenge`（纯函数，不依赖 DB）。apply 逻辑提取为 `DataManager._apply_challenge_update` 共享方法，被 `update_challenge_status`（独立事务）和 `_evaluate_and_apply_challenge`（PK 事务内复用）共同调用。后续 TASK005 多阶级时，`evaluate_challenge` 需要泛化为支持多级阈值。

### 1.4 CD 模式（`infra/cooldown.py`）

| 行为 | CD 键 | 默认秒数 | 被哪些指令复用 |
|---|---|---|---|
| 打胶 CD | `_cd_data` | 300 | `打胶`、`开扣` |
| 嗦 CD | `_suo_cd_data` | 300 | `嗦牛子`、`舔小学` |
| PK CD | `_pk_cd_data` | 60 | `pk/对决/击剑/磨豆腐/磨` |
| 透群友 CD | `_ejaculation_cd` | 3600 | `日/透(群友|群主|管理)`、`榨(群友|群主|管理)` |

> **SUPERUSER bypass**：所有 CD 检查均在 `CooldownManager._check()` 内自动跳过 SUPERUSER。`CooldownManager.__init__` 接收 `superusers: frozenset[str]`，在 DI 初始化时从 `driver.config.superusers` 注入。

> **CD 记录时机**：`嗦/舔/PK/透/榨` 均采用"校验通过后再 record"模式——先完成全部前置校验（目标存在、世界匹配、阵营合法等），确认操作将会执行后才记录 CD 时间戳。这样失败路径无需 `clear_*` 回退。
> `打胶/开扣` 仍在 CD 检查后立即 record（创建新用户和挑战中场景消耗 CD 是有意设计）。

---

## 2. 逐指令详尽行为

### 2.1 群开关控制（`control.py`）

**触发**：`^(开始|开启|关闭|禁止)(银趴|impart)`，需 `SUPERUSER | GROUP_ADMIN | GROUP_OWNER`。
**行为**：

1. `开始/开启`：`set_group_allow(gid, allow=True)`，回复"功能已开启喵"。
2. `禁止/关闭`：`set_group_allow(gid, allow=False)`，回复"功能已禁用喵"。

> 其他玩法指令均经过 `group_enabled_check`，群未开启时直接结束，提示语为 `plugin_config.not_allow`。

### 2.2 打胶（`dajiao.py`）

**触发**：`^(打胶|开导)$`。

1. 若用户存在且负值，立即拦截 `wrong_world_negative()`。
2. 检查 `check_dj`，失败返回剩余秒数文案；成功后 `record_dj`。
3. 若用户不存在：建档（默认 `10.0`）并返回创建文案。
4. 读取旧长度，生成随机增量 `get_random_num()`（0.1 概率 1~2，0.9 概率 0~1）。
5. `update_challenge_status(uid)`；若返回 `IS_CHALLENGING`，只发挑战中提示并结束（本次不加长度）。
6. `set_jj_length(uid, +random_num)` 后读取新长度。
7. 若旧长度 `<25` 且新长度 `>=25`：再次 `update_challenge_status`，走"触发挑战"文案。
8. 否则走普通完成文案（包含本次增量与当前长度）。

### 2.3 开扣 / 挖矿（`kaikou.py`）

**触发**：`^(开扣|挖矿)$`。

1. 若用户存在且 `length > 0`，拦截 `wrong_world_positive()`。
2. 若用户不存在：先建档（默认正值 10.0），随后拦截 `wrong_world_positive()`。
3. 复用打胶 CD：`check_dj/record_dj`。
4. 读取旧长度、随机值，先跑 `update_challenge_status`；若 `IS_CHALLENGING`，挑战中文案并结束。
5. 执行 `set_jj_length(uid, -random_num)`（负增量=深度加深）。
6. 读取新长度并取 `new_depth=abs(new_length)`。
7. 若 `abs(old_length)<25<=new_depth`：二次更新挑战状态并发送"触发挑战"文案。
8. 否则发送普通完成文案（显示深度）。

### 2.4 嗦牛子（`suo.py`）

**触发**：`嗦牛子`，别名 `嗦`、`suo`。

1. `check_suo` 失败返回剩余秒数。
2. 目标 `@` 缺省时等于自己；生成 `pronoun`（你/TA）。
3. 目标不存在：建档目标，返回创建文案（不消耗 CD）。
4. 目标在负值世界：提示 `"{pronoun}已经是女孩子了，没有牛子可以嗦喵"`（不消耗 CD）。
5. 校验通过后 `record_suo(uid)`。
6. 随机增量后先 `update_challenge_status(target)`；若 `IS_CHALLENGING`，发送挑战中文案。
7. `set_jj_length(target, +random_num)`，读取新长度。
8. 若目标跨 `25` 阈值：二次更新挑战状态，触发挑战文案；否则普通完成文案。

### 2.5 舔小学（`tian.py`）

**触发**：`舔小学`，别名 `舔`。

1. 复用嗦 CD：`check_suo`，失败返回剩余秒数。
2. 目标缺省为自己，生成 `pronoun`。
3. 目标不存在：建档目标 + 回复"TA还不是女孩子哦，不能舔喵~"（不消耗 CD）。
4. 目标为正值：回复"TA还不是女孩子哦，不能舔喵~"（不消耗 CD）。
5. 校验通过后 `record_suo(uid)`。
6. 随机值后先 `update_challenge_status(target)`；若 `IS_CHALLENGING`，发送挑战中文案。
7. 计算旧深度 `abs(target_length)`，执行 `set_jj_length(target, -random_num)`。
8. 读取新深度，若跨 `25` 深度阈值则触发挑战文案，否则普通完成文案。

### 2.6 PK（`pk.py`）

**触发**：三组 matcher，均需有 `@`（rule=`_has_at`）：
- 通用：`pk`、`对决`（正负世界均可）
- 正值专用：`击剑`
- 负值专用：`磨豆腐`、`磨`

#### 2.6.1 Pipeline 架构

```
pk/对决:   group_enabled_check → pk_cd_check → execute_general_pk
击剑:      group_enabled_check → pk_cd_check → positive_world_guard → execute_positive_pk
磨豆腐/磨: group_enabled_check → pk_cd_check → negative_world_guard → execute_negative_pk
```

`PkCtx` DI 依赖（定义于 pk.py 内部）在首次被 handler 引用时解析并缓存。解析过程中完成：
1. `@自己` 拒绝
2. 双方存在性校验（不存在则建档 + finish）
3. 读取双方长度与 `LengthState`
4. 同阵营校验（正负混合 → `pk_same_camp_fail()`）

CD 记录在 execute handler 内部（确保 PkCtx 已成功解析）。

#### 2.6.2 正值 PK 分支（TASK002 新系统）

**胜率判定（归一化 + xnn debuff）**：
1. 读取双方原始胜率 `uid_base_prob`、`target_base_prob`。
2. xnn debuff **在归一化前**分别应用：`calc_pk_effective_win_probability(base, state)` — xnn 时 ×0.5。
   - `uid_eff_w = uid_base_prob × 0.5`（若 uid 在 xnn）
   - `target_eff_w = target_base_prob × 0.5`（若 target 在 xnn）
3. 归一化：`P(uid赢) = uid_eff_w / (uid_eff_w + target_eff_w)`。双方均 0 时回退 0.5。
4. `random.random() < P` 判胜。

**长度结算（rake + 爆冷倍率）**：
5. 随机 `num = get_random_num()`（期望 ≈ 0.6）。
6. 爆冷倍率：`bonus = max(1, loser_eff_w / winner_eff_w)`（基于 effective W）。弱方赢时 bonus > 1。
7. 赢家获得 `length_increase = round(num × r × bonus, 3)`（r = `pk_rake_ratio`，默认 0.5）。
8. 输家损失 `length_decrease = calc_pk_loss_amount(num, loser_state)`（败方在 xnn 时 ×1.5）。

**胜率变化（单边抛物线阻尼）**：
9. 赢家 `winner_prob_delta = calc_win_rate_delta(w=winner_base, won=True, k=K)`
   - K = `pk_win_rate_k` 默认 0.02
   - 往 0 走（赢者 W < 0.5）→ 阻尼；往 0.5 走（赢者 W > 0.5）→ 全速
10. 输家 `loser_prob_delta = calc_win_rate_delta(w=loser_base, won=False, k=K)`
   - 往 1 走（输者 W > 0.5）→ 阻尼；往 0.5 走（输者 W < 0.5）→ 全速

> **重要**：阻尼基于**原始胜率**（非 effective），因为 xnn debuff 不写 DB。

**数据写入**：
11. `execute_pk(winner_id, loser_id, length_gain, length_loss, winner_prob_delta, loser_prob_delta)`
    - 胜率精度 6 位小数（`func.round(..., 6)`）
    - 长度精度 3 位小数
    - 同事务返回双方挑战状态
12. xnn 下限保护：败者新长度 `<0.01` 且旧状态 is_xnn → 强制设 `0.01`。
13. 拼接消息：胜负主文案 + 自己挑战分支 + 对手挑战分支 + xnn 进入/退出通知 + 当前胜率。

#### 2.6.3 负值 PK 分支（TASK002 新系统）

负值 PK **共用**正值 PK 的归一化 + 爆冷倍率 + 阻尼体系，但**无 xnn debuff**（负值世界不存在 xnn 区间）。

**胜率判定**：
1. 读取双方原始胜率，直接归一化（无 debuff）：`P = uid_base / (uid_base + target_base)`。

**长度结算**：
2. 爆冷倍率同正值：`bonus = max(1, loser_w / winner_w)`。
3. 胜者加深量 `depth_increase = round(num × r × bonus, 3)`。
4. 败者变浅量 `depth_decrease = num`（无 xnn 加重）。
5. `execute_pk` 参数：
   - `length_gain = -(depth_increase)`（胜者 length 更负）
   - `length_loss = -num`（败者 `length - (-num) = length + num`，向零变浅）

**胜率变化**：
6. 与正值相同的阻尼公式：`calc_win_rate_delta(w, won, k)`。

**边界保护**：
7. 败者防翻正：若执行后 `loser_length > 0`，强制设 `-0.01`。
8. 拼接消息：负值版胜负主文案 + 双方挑战状态附加文案 + 当前胜率。

### 2.7 日/透/榨 群友体系（`yinpa.py`）

**触发**：6 个独立 matcher（按目标类型 × 指令类型拆分）：

| Matcher | 正则 | 用途 |
|---|---|---|
| `yinpa_matcher` | `^(日\|透)(群友)(?:\s+.*)?$` | 透群友（支持 @指定目标） |
| `yinpa_owner_matcher` | `^(日\|透)(群主)(?:\s+.*)?$` | 透群主（固定目标） |
| `yinpa_admin_matcher` | `^(日\|透)(管理)(?:\s+.*)?$` | 透管理（随机选取） |
| `zha_matcher` | `^(榨)(群友)(?:\s+.*)?$` | 榨群友（支持 @指定目标） |
| `zha_owner_matcher` | `^(榨)(群主)(?:\s+.*)?$` | 榨群主（固定目标） |
| `zha_admin_matcher` | `^(榨)(管理)(?:\s+.*)?$` | 榨管理（随机选取） |

> **@ 行为**：所有 matcher 的正则均允许尾部带 `@` 内容（`(?:\s+.*)?$`），但仅 `群友` 命令在 `_select_member` 中提取 `@` 指定目标。`群主/管理` 命令中即使用户写了 `@`，也不影响目标选取逻辑。

#### 2.7.1 Pipeline 架构

```
日/透群友:   group_enabled_check → yinpa_cd_check → positive_world_guard → execute_tou
日/透群主:   group_enabled_check → yinpa_cd_check → positive_world_guard → execute_tou
日/透管理:   group_enabled_check → yinpa_cd_check → positive_world_guard → execute_tou
榨群友:      group_enabled_check → yinpa_cd_check → negative_world_guard → positive_target_guard → execute_zha
榨群主:      group_enabled_check → yinpa_cd_check → negative_world_guard → positive_target_guard → execute_zha
榨管理:      group_enabled_check → yinpa_cd_check → negative_world_guard → positive_target_guard → execute_zha
```

共享数据通过 DI 缓存：
- `RequesterCtx`：发起者的 uid / 群名片 / `LengthState`
- `TargetCtx`：目标的 user_id / 群名片 / 性别 / `LengthState`（解析时含目标选择逻辑）

#### 2.7.2 目标选择（`TargetCtx` DI 解析）

- `群主`：找 owner；若就是自己 → 拒绝"你透你自己?"；
- `管理`：从 admin 中选，优先非 ban；若仅自己或不存在 → 拒绝；
- `群友`：优先非 ban，兜底 ban，排除自己；若 `@` 指定则直接取该目标。

#### 2.7.3 负值分支（榨）

1. 向目标写入注入量：`insert_ejaculation(target, ejaculation)`。
2. 查询目标当日累计注入。
3. 输出 `ZhaReport.finish()`。
4. 不触发雌堕判定。

#### 2.7.4 正值分支（透）

按 xnn 与目标属性分 4 个子分支：

1. **双 xnn**：双方互相注入；`injection_targets={target, uid}`；文案 `xnn_both`。
2. **xnn 透女生**：注入目标；`injection_targets={target}`；文案 `squeeze`。
3. **xnn 透男生**：反透，注入自己；`injection_targets={uid}`；文案 `reversed`。
4. **普通透**：注入目标；`injection_targets={target}`；文案 `active`。

#### 2.7.5 雌堕检查（`_check_ciduo`）

仅在正值分支执行，遍历 `injection_targets` 每个 ID：

1. 读取目标长度与当日累计注入。
2. 条件：`target_state.is_xnn` 且 `today_injection >= 500`。
3. 新长度 `new = current - 5`（`calc_ciduo_new_length`，若结果为 0 则 `-0.01`）。
4. 以增量方式回写：`delta = new - current`，调用 `set_jj_length(target, delta)`。
5. 拼接 `CiduoEvent.announce()` 到额外文案。

### 2.8 查询（`query.py`）

**触发**：`查询`。

1. 目标为 `@对象` 或自己。
2. 目标不存在：建档并发送创建文案。
3. 获取长度和胜率。
4. 目标长度 `<=0`：显示"深度=abs(length)"文案及胜率；绝对值 `>=30` 用 `abyss_lord`，否则 `girl`。
5. 目标长度 `>0`：`>=30`=god，`>5`=normal，`<=5`=near_girl；均附带胜率信息。

### 2.9 排行榜（`rank.py`）

**触发**：`^(银趴|impart)(排行榜|排名|榜单|rank)`（忽略大小写）。

1. 获取全量长度降序数据（正负统一排序）。
2. 数据 `<5` 直接拒绝展示。
3. 自己未建档则建档并返回提示。
4. 构建展示集合：前 5、后 5、中间（若本人不在两端则取上下各 1）。
5. 逐人拉取昵称+头像（失败时用默认昵称）。
6. 调 `draw_bar_chart` 返回图片 + "你的排名为X喵"。

### 2.10 注入查询（`injection.py`）

**触发**：`注入查询`，别名 `摄入查询`、`射入查询`。

1. 目标为 `@对象` 或自己。
2. 读取目标全历史注入数据。
3. 若参数含"历史/全部"：
   - 无数据 → 历史总量 0；
   - 仅 1 天数据 → 仅给总量；
   - 多天数据 → 拉昵称+头像并绘制折线图（`draw_line_chart`）。
4. 否则返回"当日总被注射量"。

### 2.11 帮助（`help.py`）

**触发**：`^(银趴|impart)(介绍|帮助)$`。
**行为**：原样发送 `plugin_config.usage`（已包含正负世界全部指令说明）。

> **注意**：`config.py` 的 `usage` 默认值中 PK 描述仍为旧版（"随机数/2"、"胜率±1%"）。TASK004 Bug #8 待修正。

---

## 3. 已确认边界结果

| 场景 | 当前行为 | 结论 |
|---|---|---|
| 任意写路径得到 `0` | 强制改写 `-0.01` | ✅ |
| 正负混阵营 PK | 直接拒绝（不消耗 CD） | ✅ |
| 正值指令误用于负值（打胶） | 直接拦截 | ✅ |
| 负值指令误用于正值（开扣） | 直接拦截 | ✅ |
| 嗦到负值目标 | 拦截（不消耗 CD） | ✅ |
| 舔到正值目标 | 拦截（不消耗 CD） | ✅ |
| 负值 PK 败者翻正 | 强制钳到 `-0.01` | ✅ |
| xnn PK 失败过低（正值） | xnn floor 钳到 `0.01` | ✅ |
| 雌堕触发目标为 xnn 且注入够量 | `current-5` 生效，含零值保护 | ✅ |
| 正值玩家输入"榨群友" | 被 `zha_matcher` 匹配，世界校验拒绝 | ✅ |
| 负值玩家输入"透群友" | 被 `yinpa_matcher` 匹配，世界校验拒绝 | ✅ |
| 负值玩家输入"击剑" | 被 `jijian_matcher` 匹配，PkCtx 同阵营 + world guard 拒绝 | ✅ |
| 正值玩家输入"磨豆腐" | 被 `modofu_matcher` 匹配，PkCtx 同阵营 + world guard 拒绝 | ✅ |
| PK 无 @ | matcher rule `_has_at` 阻止触发 | ✅ |
| PK @自己 | PkCtx 解析时拒绝"你不能pk自己喵"（不消耗 CD） | ✅ |
| SUPERUSER 所有 CD | `CooldownManager._check()` 自动 bypass | ✅ |
| PK 双方胜率都参与判定 | 归一化 Wa/(Wa+Wb)，不再只看发起方 | ✅ |
| PK 胜率边界保护 | 单边抛物线阻尼，数学上不可能到达 0 或 1，无需 clamp | ✅ |
| PK 弱方赢得更多 | 爆冷倍率 max(1, W_loser/W_winner)，只加赢不加输 | ✅ |
| PK xnn 双方都应用 debuff | 双方独立检查 is_xnn，在归一化前分别 ×0.5 | ✅ |
| PK 胜率阻尼基于原始值 | 阻尼用 base W，非 xnn-debuffed W（debuff 不写 DB） | ✅ |
| 负值 PK 无 xnn debuff/clamp | 负值世界 is_xnn=False，自然跳过 | ✅ |
