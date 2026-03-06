# Active Context - nonebot_plugin_impart

## Current Focus
TASK004 收尾完成 + yinpa matcher 拆分。251 项测试全通（119 unit + 91 integration + 2 smoke）。

## Recent Decisions
- **2026-03-06 R19-R21**: yinpa matcher 拆分 + 榨群友 bug 修复 + 边界测试补充
  - **Bug 修复**：`zha_matcher` 上的 `negative_world_guard` 错误地要求发起者为负值（应保留，之前误移除后恢复）
  - **Matcher 拆分**：原 `yinpa_matcher`/`zha_matcher` 合并 matcher 拆分为 6 个独立 matcher
    - `yinpa_matcher`（群友）、`yinpa_owner_matcher`（群主）、`yinpa_admin_matcher`（管理）
    - `zha_matcher`（群友）、`zha_owner_matcher`（群主）、`zha_admin_matcher`（管理）
  - **Regex 修改**：所有 matcher 支持尾部带 `@` 内容：`(?:\s+.*)?$`
  - **设计决策**：只有`群友`命令提取 `@` 目标，`群主/管理` 允许 `@` 输入但不提取（群主固定、管理随机）
  - 新增集成测试 9 项（从 9→18）：xnn 反转/双 xnn/squeeze/雌堕/管理@/群主@/群主自透/无管理
  - **TASK004 Bug #10 已解决**：日/透/榨 Matcher 拆分完成
- **2026-03-05 R18**: TASK002 实施完成
  - 归一化胜率 + 爆冷倍率 + 单边抛物线阻尼
  - xnn debuff 在归一化前应用，阻尼基于原始胜率
- **2026-03-05 R17**: 集成测试体系建立 + PK 挑战/xnn 测试大幅扩充（29 项 PK 测试）
- **2026-03-05 R16**: PK pipeline 重构 + TASK004 负值世界完成
- **2026-03-05 R14-R15**: yinpa pipeline 重构 + CD 统一

## Next Steps
- **TASK011**: Alconna + UniInfo 多平台适配重构（已建任务文件）
- 推进 TASK005-TASK009（多阶级/技能/联动/Buff/成就）
- 可选：将 pipeline handler 模式推广到其余 handler（dajiao/suo/tian/kaikou）

## Active Considerations
- 三层架构：core/（纯逻辑）→ infra/（DB/冷却/图表）→ bot/（handler/文案/依赖注入）
- Pipeline handler 模式已应用于 yinpa.py（6 matcher）和 pk.py（3 matcher）
- DI 缓存依赖：`RequesterCtx`/`TargetCtx`（yinpa）、`PkCtx`（pk）同一事件只解析一次
- 全局行为规格书：`game-design.md`（持续维护每条指令的详尽行为）
- TASK011 将把 `on_regex` 迁移到 Alconna，`GroupMessageEvent` 迁移到 `uninfo.Session`
