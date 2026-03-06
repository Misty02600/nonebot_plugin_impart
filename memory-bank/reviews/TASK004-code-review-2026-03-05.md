# TASK004 代码审查报告（问题 + 方案）

**日期**: 2026-03-05
**审查范围**: `src/nonebot_plugin_impart`（重点：`yinpa/pk/dajiao/kaikou/suo/tian/query`）
**关注点**: 隐性 bug、边界情况、实现含糊点、冗余代码
**当前状态**: 已发现多处高风险问题；`pytest/basedpyright/ruff` 均通过，但测试覆盖不足以发现本次问题

---

## 1. 结论摘要

- 当前实现存在 **2 个严重问题（会导致功能错误或直接崩溃）**，建议优先修复。
- 存在 **3 个中高风险行为偏差**（与 TASK004 设计不一致或边界误判）。
- 存在 **若干实现含糊与冗余代码**，短期不一定崩溃，但会持续增加维护和回归风险。

---

## 2. 问题清单（按严重度）

## P0-1: `@` 目标哨兵值不一致，导致无 `@` 场景崩溃

**严重度**: P0（阻断）
**位置**:
- `src/nonebot_plugin_impart/bot/dependencies.py:95-109`
- `src/nonebot_plugin_impart/bot/handlers/suo.py:44-45`
- `src/nonebot_plugin_impart/bot/handlers/tian.py:44-45`
- `src/nonebot_plugin_impart/bot/handlers/yinpa.py:291-293`

**现象**:
- `get_at()` 无 `@` 时返回 `"寄"`。
- 多个 handler 却按 `"0"` 判断无目标。
- 最终会把 `"寄"` 走 `int(...)`，触发 `ValueError`（无 `@` 时直接炸）。

**影响**:
- `嗦牛子`、`舔小学`、`透/日群友` 在常见“无 @ 输入”场景下不稳定甚至不可用。

**修复方案**:
- 统一无 `@` 哨兵值，推荐全项目统一为 `"寄"`（已在 `query/injection` 使用）。
- 修正以下逻辑：
  - `suo.py`：`target_id = int(uid if at == "寄" else at)`
  - `tian.py`：同上
  - `yinpa.py`：`if at != "寄": return at`
- 增加一个公共 helper（可选）：`resolve_target_or_self(uid: str, at: str) -> int`，避免重复判断再漂移。

**验收标准**:
- 无 `@` 执行 `嗦牛子/舔小学/透群友` 不报错，且目标正确回落到自己或随机目标。

---

## P0-2: 雌堕判定对象错误，xnn 被反透路径不会触发雌堕

**严重度**: P0（规则错误）
**位置**:
- `src/nonebot_plugin_impart/bot/handlers/yinpa.py:153-201`
- `src/nonebot_plugin_impart/bot/handlers/yinpa.py:217-225`

**现象**:
- xnn 透男生或双 xnn 互透时，注入记录可能写到发起者自己（`uid`）。
- 但雌堕判定固定检查 `lucky_user`，未检查真实被注入者。

**影响**:
- xnn 发起者在“被反透/互透”分支中，即使累计注入量达阈值也不会雌堕。
- 与 TASK004 约定“最后一次注入使累计达阈值立即雌堕”冲突。

**修复方案**:
- 在 yinpa 结算时记录 `injection_targets: set[int]`（本次所有被注入对象）。
- 结算后遍历该集合逐个执行 `_check_ciduo(...)`。
- 双 xnn 场景下应检查双方，避免漏判。

**验收标准**:
- 反透和双 xnn 互透均能在达阈值时触发正确对象的雌堕。

---

## P1-1: 负值“榨群友目标必须男性”在目标未建档时误判

**严重度**: P1（高）
**位置**:
- `src/nonebot_plugin_impart/bot/handlers/yinpa.py:97-103`
- `src/nonebot_plugin_impart/infra/data_manager.py:77-82`

**现象**:
- 读取目标长度前未确保目标已建档。
- 未建档用户 `get_jj_length()` 回 `0.0`，被当作“非男性”，触发“无男性目标”提示。

**影响**:
- 新群、新用户比例高时，负值榨群友路径会频繁误判失败。

**修复方案**:
- 在读取目标长度前调用 `await dm.ensure_user(int(lucky_user))`。
- 或在 `get_jj_length()` 明确区分“无用户”和“长度为 0”。

**验收标准**:
- 新用户作为目标时不会被错误拦截，行为与已建档用户一致。

---

## P1-2: 指令映射不完整，未注册“榨群友/榨群主/榨管理”

**严重度**: P1（功能缺失）
**位置**:
- `src/nonebot_plugin_impart/bot/handlers/yinpa.py:350-356`

**现象**:
- matcher 仅匹配 `日/透`，不匹配 `榨*` 指令。

**影响**:
- 与 TASK004 设计文档不一致，用户按文案输入会“指令无响应”。

**修复方案**:
- 扩展 regex：`^(日|透|榨)(群友|群主|管理)$`
- 保持内部分支逻辑不变，仅增加命令入口映射。

**验收标准**:
- `榨群友/榨群主/榨管理` 均可命中现有逻辑，效果与负值分支一致。

---

## P1-3: 配置与任务设计不一致 + 默认变量名疑似 typo

**严重度**: P1（配置偏差）
**位置**:
- `src/nonebot_plugin_impart/constants.py:4`（`DEFAULT_HOLE_NAME = "小学"`）
- `memory-bank/tasks/TASK004-negative-world.md:164,336`（历史设计曾提及 `hole_variable`）

**现象**:
- `hole_variable` 现已由产品口径确认“不需要该配置项”。
- 负值默认名称以产品口径为准：`DEFAULT_HOLE_NAME = "小学"`。

**影响**:
- 本项不再作为缺陷阻塞，仅需保证实现与产品口径一致。

**修复方案**:
- 删除 `hole_variable`，避免无效配置扩散。
- 统一默认名称为 `"小学"`，并在文档中注明该口径。

**验收标准**:
- 配置项与产品需求一致（无 `hole_variable`）。
- 默认名称稳定为 `"小学"`。

---

## P2-1: 负值挑战逻辑与正值逻辑耦合，存在“看似实现、实际不可达”的含糊点

**严重度**: P2（可维护性/正确性风险）
**位置**:
- `src/nonebot_plugin_impart/core/game.py:83-119`
- `src/nonebot_plugin_impart/bot/handlers/kaikou.py:61-68`
- `src/nonebot_plugin_impart/bot/handlers/tian.py:76-84`
- `src/nonebot_plugin_impart/bot/handlers/pk.py:281-316`

**现象**:
- `evaluate_challenge()` 阈值和状态机主要按正值路径定义。
- 负值 handler 复用这套状态并拼负值文案，部分分支可能难以触发或语义不准。

**影响**:
- 后续迭代极易出现“改了文案没改规则/改了规则没改文案”的偏移。

**修复方案**:
- 显式拆分为 `evaluate_positive_challenge` / `evaluate_negative_challenge`。
- 或在统一函数内增加 `world` 参数，状态机分支按世界区分。
- 先补单测锁定现行为，再重构，避免引入回归。

**验收标准**:
- 正负世界挑战状态机各自闭环，覆盖边界值测试（24.999/25/29.999/30）。

---

## P2-2: 冗余代码与潜在冗余依赖

**严重度**: P2
**位置**:
- 文案方法疑似未使用：`duel_texts.py:70,74,96,99`
- 文案类疑似未使用：`interaction_texts.py:109`（`ZhaMenuCopy`）
- 依赖疑似未使用：`pyproject.toml:13-14`（`uninfo/alconna`）

**影响**:
- 增加理解成本，后续读代码容易误判“已有功能”。

**修复方案**:
- 清理未引用方法/类，或补“预留用途”注释。
- 对依赖做一次最小化核对，移除未使用依赖以降低安装与安全面。

**验收标准**:
- `rg` 全仓库确认无死引用；依赖列表与实际 import 对齐。

---

## 3. 建议修复顺序（落地优先级）

1. **先修 P0**：`@` 哨兵统一 + 雌堕判定对象修正。
2. **再修 P1**：目标建档误判 + 榨指令入口补齐 + 配置字段与默认值纠正。
3. **最后处理 P2**：挑战状态机解耦、清理冗余代码和依赖。

---

## 4. 回归测试补充（必须新增）

## 4.1 指令目标解析
- 无 `@` 执行：`嗦牛子`、`舔小学`、`透群友`。
- `@all` 行为与无 `@` 一致处理。

## 4.2 雌堕触发
- 正常透触发雌堕（目标为 xnn，累计达阈值）。
- xnn 被反透触发雌堕（注入写入发起者时）。
- 双 xnn 互透，双方分别达阈值时的触发行为。

## 4.3 榨群友男性目标约束
- 目标未建档、已建档且正值、已建档且非正值三种分支。

## 4.4 指令映射
- `榨群友/榨群主/榨管理` 命中率测试。
- `日/透` 保持向后兼容。

## 4.5 配置与默认值
- `hole_variable` 默认值与环境变量覆盖。
- `DEFAULT_HOLE_NAME` 显示正确。

---

## 5. 当前验证信息

- `uv run pytest -q`: 通过（2 passed）。
- `uv run basedpyright`: 通过（0 errors）。
- `uv run ruff check src tests`: 通过。

**说明**: 现有测试主要是元数据与基础 fake event，未覆盖 TASK004 核心流程，因此“测试通过”不能代表本次问题不存在。

---

## 6. 最小修复包建议（可选）

如果按“最小风险、快速回归”方式修复，建议拆成 3 个 PR：

1. `fix(task004): unify at sentinel and prevent no-at crashes`
2. `fix(task004): correct ciduo target evaluation for reverse/xnn-both`
3. `feat(task004): add zha command aliases and hole config parity`

每个 PR 都附最小测试，先锁行为再改逻辑，降低交叉回归风险。

---

## 7. 待确认事项（统一收敛，等你回复）

> 说明：本章节用于记录“审查中仍不确定、需要你拍板”的点。后续所有 code review 的不确定项都先放在这里，不再直接按假设落代码。

### 7.1 `DEFAULT_HOLE_NAME` 默认值（已确认）

- 当前代码以产品口径为准：`DEFAULT_HOLE_NAME = "小学"`。
- `hole_variable` 已确认不需要，已从配置中移除。

### 7.2 负值挑战状态机拆分（P2-1）

- 现状：正负世界仍共用 `evaluate_challenge()`，已标注为后续重构项。
- 待你确认：是否现在就拆分 `evaluate_positive_challenge / evaluate_negative_challenge`，还是继续延后。

#### 7.2.A 对决指令“通用 + 世界专属”实现方案（新增）

- 目标：`pk/对决` 双世界通用；`击剑` 仅正值；`磨豆腐` 仅负值。
- 推荐做法：**不拆状态机，先拆“命令语义层”**，把“入口词是否合法”前置到 `pk_handler`。
- 已确认口径：`比划/比深度` 不保留。

实现步骤（最小改动）：

1) 在 `pk.py` 保留一个 matcher（统一冷却与对决逻辑），别名补齐 `磨豆腐`。
2) 在 handler 读取本次触发词（从消息纯文本首词提取）。
3) 建立三类别名集合：
  - `shared_aliases = {"pk", "对决"}`
  - `positive_only_aliases = {"击剑"}`
  - `negative_only_aliases = {"磨豆腐", "磨"}`
4) 在“同阵营检查”后、进入 `_do_positive_pk/_do_negative_pk` 前做入口校验：
  - 正值玩家使用负值专属词 → 拒绝并提示。
  - 负值玩家使用正值专属词 → 拒绝并提示。
  - 通用词照常放行。
5) 数值规则与状态机保持现状，不做拆分。

这样做的收益：

- 满足“通用词 + 世界专属词”需求；
- 不引入状态机重构风险；
- 命令约束集中在一个文件，后续扩词成本低。

当前状态：

- 已按上述集合落地；
- `比深度/比划` 已从别名中移除。

### 7.3 审查执行规则（流程约定）

- 建议固定流程：
  1) 先实现“确定项”；
  2) 将“不确定项”追加到本章节；
  3) 你回复后再二次修订。


