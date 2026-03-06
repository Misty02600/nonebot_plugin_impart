# [TASK004] - 负值世界设计

**Status:** Complete
**Added:** 2026-03-04
**Updated:** 2026-03-05
**Origin:** 从 TASK001 拆分

## Original Request

设计并实现负值世界完整玩法：负值语义、指令映射、正负值隔离、xnn 联动、雌堕机制、负值 PK、显示与帮助文案适配。

> 完整的逐指令行为规格已迁移至 [`game-design.md`](../game-design.md)。本文件仅记录 TASK004 的实施过程。

---

## TASK004 实施范围

TASK004 新增/修改的核心功能点：

1. **世界判定**：`core/world.py` 的 `LengthState`（`is_negative_world` / `is_xnn` / `is_positive_world`），零归负值。
2. **零值保护**：`data_manager.py` 全写路径保证不存 `0`，改写 `-0.01`。
3. **挑战状态机**：`evaluate_challenge` 支持负值世界（绝对值阈值，惩罚方向翻转）。
4. **负值指令映射**：`开扣/挖矿` → 负值打胶；`舔小学/舔` → 负值嗦；`磨豆腐/磨` → 负值 PK；`榨群友` → 负值透群友。
5. **正负隔离**：每条指令的世界校验 + PK 同阵营检查 + 入口词限制。
6. **xnn 联动**：debuff（PK 胜率 ×0.5）、loss 放大（×1.5）、floor（0.01）、进入/退出通知。
7. **雌堕机制**：`_check_ciduo` 按被注入者逐个判定，`should_trigger_ciduo` + `calc_ciduo_new_length`。
8. **负值 PK**：深度语义（胜者加深、败者变浅）+ 败者防翻正。
9. **显示适配**：查询显示深度+胜率、排行榜统一排序、帮助文本补充。

---

## /// 注释解决记录

### /// 1. 状态机拆分（原 1.3 设计备注）

> "update_challenge_status 目前耦合了读/评估/写/提交四步。现在不能直接执行吗，还有状态机的语义是不是不够清晰"

**决策**：纯判定逻辑已在 `evaluate_challenge` 中，无需进一步拆分函数本身。但 apply 逻辑存在重复——`update_challenge_status` 和 `_evaluate_and_apply_challenge` 有相同的字段赋值块。

**已执行**：
- 提取 `DataManager._apply_challenge_update(user, change)` 静态方法，两处共用
- `_ChallengeUpdate` 重命名为 `ChallengeUpdate`（公有 API）

### /// 2. PK matcher 拆分（原 2.6 设计备注）

> "当前三组触发词共用一个 on_command Matcher。你认为要不要拆分，如果要的话请执行。"

**决策**：是，拆分为 3 个 matcher + pipeline handler 模式（与 yinpa 一致）。

**已执行**：
- `pk_shared_matcher`（`pk`、`对决`）→ `[group_enabled_check, pk_cd_check, execute_general_pk]`
- `jijian_matcher`（`击剑`）→ `[group_enabled_check, pk_cd_check, positive_world_guard, execute_positive_pk]`
- `modofu_matcher`（`磨豆腐`、`磨`）→ `[group_enabled_check, pk_cd_check, negative_world_guard, execute_negative_pk]`
- 新增 `PkCtx` DI 依赖（定义于 pk.py 内部），缓存双方状态，解析时完成 @自己/存在性/同阵营校验
- 消除 `SHARED_PK_ALIASES` / `POSITIVE_ONLY_ALIASES` / `NEGATIVE_ONLY_ALIASES` 常量集合和 handler 内的入口词校验逻辑

### /// 3. SUPERUSER CD bypass（原 2.7 注释）

> "只有这一项的 superuser 能越过吗，其它项呢"

**决策**：所有 CD 统一支持 SUPERUSER bypass。

**已执行**：
- `CooldownManager.__init__` 新增 `superusers: frozenset[str]` 参数
- `CooldownManager._check()` 开头添加 `if uid in self._superusers: return True, 0.0`
- DI 初始化时注入 `frozenset(driver.config.superusers)`
- 移除 `yinpa_cd_check` 中的独立 superuser 检查

---

## 子任务状态

| ID | 描述 | 状态 | 备注 |
|---|---|---|---|
| 4.1 | 查询显示深度 | ✅ | 负值按绝对值显示 |
| 4.2 | 负值指令映射与别名 | ✅ | 开扣/舔/磨已接入 |
| 4.3 | 配置项 | ⏸ | `hole_variable` 仍未配置化（无需实现，舍弃） |
| 4.4 | 文案体系 | ✅ | progression/duel/interaction 三文件已接入 |
| 4.5 | xnn 机制 | ✅ | debuff、loss 放大、floor、通知均已落地 |
| 4.6 | 雌堕机制 | ✅ | `_check_ciduo` 按被注入者逐个触发 |
| 4.7 | PK 同阵营检查 | ✅ | 混阵营阻断 |
| 4.8 | 负值 PK | ✅ | 加深/变浅语义 + 防翻正 |
| 4.9 | 数据层适配 | ✅ | 全链路零值保护 |

**整体进度：100%**（仅 4.3 配置化为低优先级延后项）

---

## Progress Log

### 2026-03-04 (R1-R7)
- TASK004 从 TASK001 拆分为独立任务。

### 2026-03-05 (R8-R11)
- 语义模型与规则函数抽离（`LengthState` + `rules`）。
- handlers 全面改为按世界语义分支。
- 负值 PK、雌堕、xnn 机制接入主流程。

### 2026-03-05 (R12)
- 负值挑战判定支持（绝对值阈值）、负值 PK 防翻正、数据层零值保护、嗦目标世界校验。

### 2026-03-05 (R13)
- 修复嗦/舔发起者世界校验 bug、PK `Command()` 注入修复、排行榜触发词更新。
- 新增 Bug #9/#10/#11。

### 2026-03-05 (R14)
- 修复 Bug #8-#11：帮助文本、嗦文案、yinpa Matcher 拆分、查询胜率。
- CD 模式统一重构："校验通过后再 record"，消除 `clear_*` 回退。
- 删除 `dajiao.py` 不可达 xnn clamp。

### 2026-03-05 (R15)
- yinpa.py pipeline handler 重构：参考 jmdownloader 模式，拆为 6 个小型 handler + `RequesterCtx`/`TargetCtx` DI。

### 2026-03-05 (R16)
- 解决三条 `///` 注释：
  - 挑战状态 apply 逻辑 DRY 化（`_apply_challenge_update`）
  - PK 拆分为 3 matcher + `PkCtx` DI + pipeline handler
  - SUPERUSER CD bypass 全局化到 `CooldownManager._check()`
- 全局行为规格迁移至 `game-design.md`，TASK004 精简为实施记录。
