# Progress - nonebot_plugin_impart

## What Works
- 完整的 PK、打胶、嗦牛子、透群友、排行榜、注入查询等核心玩法
- 登神长阶挑战系统（25cm → 30cm）
- 长度 ≤ 0 的"女孩子"状态与主语颠倒
- 不活跃惩罚定时任务
- 清晰的三层架构（core / infra / bot）
- **精美图表输出**（HTML/CSS + Jinja2 + htmlrender 方案）
  - 可爱蜜桃粉主题排行榜（三段式布局，金银铜牌，高亮查询者）
  - 注入历史折线图（SVG 图表 + 数据明细）
- **TASK002 PK 胜率机制重设计**（2026-03-05 已完成）
  - 归一化胜率 Wa/(Wa+Wb)、爆冷倍率 max(1,Wb/Wa)、单边抛物线阻尼
  - 正值/负值 PK 共用同一套系统
  - 3 个纯函数 + 2 个配置项 + handler 重写 + 数据层适配
- **TASK004 负值世界**（2026-03-06 基本完成）
  - 语义模型、规则函数、文案体系、负值指令映射
  - 正负隔离（世界校验 + 同阵营 PK）
  - xnn 联动（debuff/loss 放大/floor/通知）、雌堕机制
  - 日/透/榨 Matcher 已拆分为 6 个独立 matcher（群友/群主/管理 × 透/榨）
- **完善的测试体系**（251 项测试全通）
  - 119 单元测试（core 纯逻辑：world、game、rules、cooldown）
  - 91 集成测试（NoneBug E2E matcher 测试）
    - dajiao 10、kaikou 7、pk 29、suo_tian 16、query 11、yinpa 18
  - 2 烟雾测试（插件元数据 + 事件创建）
  - 集成测试基础设施：in-memory SQLite + DI monkeypatch + ANY_MSG 通配哨兵

## What's Left to Build
- ~~TASK002~~: ✅ PK 胜率机制重设计（已完成 2026-03-05）
- ~~TASK004~~: ✅ 负值世界设计（已完成 2026-03-06）
- **TASK005**: 多阶级与称号系统（5阶级挑战引擎 + 称号）
- **TASK006**: 技能系统（正负各5技能 + 吸取回正）
- **TASK007**: 透群友联动（正值透→+长度、负值榨→深度比较食物链）
- **TASK008**: 扩展 Buff 与事件系统（6 个子系统）
- **TASK009**: 成就系统（8 个成就）
- **TASK010**: 数值平衡与集成测试
- **TASK011**: Alconna + UniInfo 多平台适配重构

## Current Status
- **TASK003** 已完成（2026-03-03）：图表输出美化
- **TASK001** 已归档（2026-03-04）：拆分为 TASK004-TASK010
- **TASK004** 已完成（2026-03-06）：语义模型 + 规则函数 + 全部 handler 重构 + matcher 拆分
- **TASK002** 已完成（2026-03-05）：归一化胜率 + 爆冷倍率 + 单边抛物线阻尼
- **集成测试扩充**（2026-03-06）：91 项 E2E matcher 测试全通

## Known Issues
- **TASK004 Bug #8（🟢）**: `help.py` 的 `usage` 文案中 PK 描述仍为旧版措辞（"随机数/2"、"胜率±1%"），应更新
- **TASK004 Bug #9（🟢）**: `suo.py` 嗦到负值目标拒绝文案待优化
- **TASK004 Bug #11（🟢）**: `query.py` 查询补充胜率/文案（部分已完成，胜率已显示）
- ~~Bug #10~~: ✅ 日/透/榨 Matcher 拆分完成（2026-03-06）
