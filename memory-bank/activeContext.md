# Active Context - nonebot_plugin_impart

## Current Focus
TASK002 已完成 — PK 胜率机制重设计。226 项测试全通（162 unit + 66 integration + 2 smoke）。

## Recent Decisions
- **2026-03-05 R18**: TASK002 实施完成
  - 3 个纯函数（`calc_normalized_win_probability`, `calc_pk_bonus`, `calc_win_rate_delta`）+ 2 个配置项
  - `_do_positive_pk` / `_do_negative_pk` 完全重写
  - `execute_pk` 支持动态 `winner_prob_delta` / `loser_prob_delta`（后向兼容）
  - 33 项新单元测试 + 集成测试断言更新 → 226 项全通
  - 关键设计决策：
    - xnn debuff 在归一化**前**应用：`W_eff = W × 0.5`，然后 `P = W_A_eff / (W_A_eff + W_B)`
    - bonus 使用 effective W：`max(1, W_loser_eff / W_winner_eff)`
    - 阻尼基于**原始胜率**（非 debuffed），因为 xnn debuff 不写 DB
    - 负值 PK 共用同一套系统（无 xnn debuff，自然跳过）
- **2026-03-05 R17**: 集成测试体系建立（66 项）+ 边缘用例扩充
  - NoneBug 基础设施：in-memory SQLite + DI monkeypatch + `_AnyMessage` 通配哨兵
  - 关键发现：`block=False` 不消费 `should_finished`；`TargetCtx` 需 `OB11Bot` base
- **2026-03-05 R16**: PK pipeline 重构 + TASK004 负值世界完成 + 全局行为规格 → `game-design.md`
- **2026-03-05 R14-R15**: yinpa pipeline 重构 + Bug #8-#11 + CD 统一

## Next Steps
- 推进 TASK005-TASK009
- 可选：将 pipeline handler 模式推广到其余 handler（dajiao/suo/tian/kaikou）
- 可选：更新查询/帮助命令的描述以反映新 PK 机制（TASK004 Bug #8/#11）

## Active Considerations
- 三层架构：core/（纯逻辑）→ infra/（DB/冷却/图表）→ bot/（handler/文案/依赖注入）
- Pipeline handler 模式已应用于 yinpa.py 和 pk.py：小型 handler → `handlers=[]` 组合 → guard 用 `matcher.finish()` 短路
- DI 缓存依赖：`RequesterCtx`/`TargetCtx`（yinpa）、`PkCtx`（pk）同一事件只解析一次
- 全局行为规格书：`game-design.md`（持续维护每条指令的详尽行为）
