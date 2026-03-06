# System Patterns - nonebot_plugin_impart

## Architecture

```
src/nonebot_plugin_impart/
├── __init__.py              # 插件元数据 + 注册 handlers
├── config.py                # PluginConfig (Pydantic)
├── constants.py             # 全局常量（DEFAULT_JJ_NAME, DEFAULT_HOLE_NAME）
├── core/                    # 纯业务逻辑层（不依赖 NoneBot/DB）
│   ├── models.py            # SQLAlchemy ORM 模型 (UserData, GroupData, EjaculationData)
│   ├── game.py              # 游戏逻辑（随机数、挑战评估）
│   ├── world.py             # 长度语义模型（LengthState: is_xnn/is_positive_world/is_negative_world）
│   └── rules.py             # 规则常量与纯函数（雌堕/xnn debuff/clamp/归一化/爆冷/阻尼）
├── infra/                   # 基础设施层
│   ├── database.py          # 引擎+会话工厂+初始化
│   ├── data_manager.py      # DataManager（所有 CRUD）
│   ├── cooldown.py          # CooldownManager（内存冷却计时）
│   ├── chart_renderer.py    # ChartRenderer（HTML/CSS + Jinja2 + Playwright 图表渲染）
│   └── templates/charts/    # 图表模板（Jinja2 + CSS）
│       ├── bar_chart.jinja2 # 排行榜模板
│       ├── line_chart.jinja2# 注入历史折线图模板
│       └── style.css        # 蜜桃粉主题样式
└── bot/                     # NoneBot 集成层
    ├── __init__.py           # 导出 Dep 类型别名
    ├── dependencies.py       # 依赖注入：DataManagerDep, CooldownDep, DrawChartDep, RequesterCtx, TargetCtx
    └── handlers/             # 命令处理器
        ├── common.py         # 群启用前置检查
        ├── pk.py             # PK 对决（pipeline: cd_check → world_guard → execute，3 matcher）
        ├── dajiao.py         # 打胶（自增长度）
        ├── suo.py            # 嗦牛子（给他人增长度）
        ├── yinpa.py          # 透群友/群主/管理（pipeline: cd_check → world_guard → execute）
        ├── query.py          # 查询长度
        ├── rank.py           # 排行榜（使用 ChartRenderer）
        ├── injection.py      # 注入量查询（使用 ChartRenderer）
        ├── control.py        # 开关控制
        ├── help.py           # 帮助信息
        └── scheduled.py      # 定时任务（不活跃惩罚）
```

## Current Game Mechanics

### 核心数值
- **初始长度**: 10.0 cm
- **随机增量**: 90% 概率 [0, 1), 10% 概率 [1, 2)
- **胜率**: 初始 50%，PK 后单边抛物线阻尼调整（K=0.02，中心处有效 ±0.02，边界自然减速）
- **PK 胜率判定**: 归一化 Wa/(Wa+Wb)，双方胜率都参与
- **PK 赢家收益**: num × r × bonus（r=0.5，bonus=max(1, W_loser/W_winner)）
- **PK 输家损失**: num（xnn 时 ×1.5）

### 玩法
| 指令             | 效果                                 | CD    |
| ---------------- | ------------------------------------ | ----- |
| 打胶/开导        | 自己 +随机数                         | 300s  |
| 嗦牛子/嗦        | 目标 +随机数                         | 300s  |
| PK/对决          | 赢方 +num×r×bonus，输方 -num；胜率归一化+阻尼调整 | 60s   |
| 透群友/群主/管理 | 选择目标，注入脱氧核糖核酸           | 3600s |

### 状态区间与称号
| 长度范围 | 状态                         |
| -------- | ---------------------------- |
| ≥ 30     | ✨牛々の神✨（完成登神挑战后） |
| 25 ~ 30  | 登神长阶挑战区间             |
| 5 ~ 25   | 正常                         |
| 1 ~ 5    | xnn（小牛牛）                |
| 0 ~ 1    | 即将变成女孩子               |
| ≤ 0      | 已经变成女孩子               |

### 登神长阶挑战
- **触发**: 长度首次达到 25cm（PK/打胶/嗦都可触发）
- **进入效果**: 胜率变为当前的 80%，禁用"打胶"和"嗦"指令
- **成功条件**: 仅通过 PK 将长度提升至 ≥ 30cm
- **成功奖励**: 获得"牛々の神"称号，胜率恢复，指令解锁
- **失败条件**: PK 中长度跌至 < 25cm
- **失败惩罚**: 长度 -5cm，胜率恢复，指令解锁
- **完成后跌落**: 若已完成挑战但长度跌至 < 25cm，长度再 -5cm，需重新挑战

### 长度 ≤ 0 时（"女孩子"状态）
- 透群友时主语颠倒（被透）
- xnn 状态 (0 < length ≤ 5) 透群友有 50% 概率被反转

### 不活跃惩罚（可配置）
- 超过 1 天未操作且长度 > 1 的用户，随机减少 0~1 长度

## Design Patterns
1. **DataManager 模式**: 所有 DB 操作封装在单一管理器中
2. **依赖注入**: 通过 `Annotated[T, Depends(factory)]` 类型别名
3. **纯函数业务逻辑**: `core/game.py` 不依赖外部状态，便于测试
4. **语义状态模型**: `core/world.py` 的 `LengthState` 将原始 length 包装为语义属性（is_xnn/is_positive_world/is_negative_world），零归负值
5. **集中式规则函数**: `core/rules.py` 集中所有游戏规则常量和纯判定函数（should_trigger_ciduo, calc_pk_effective_win_probability, calc_normalized_win_probability, calc_pk_bonus, calc_win_rate_delta 等），handler 不内联规则逻辑
6. **Pipeline handler 模式**: 参考 jmdownloader 插件，将 monolithic handler 拆为小型 handler 函数通过 `handlers=[]` 组合为有序执行链——guard handler 用 `matcher.finish()` 短路，共享 handler 在不同 matcher 间复用
7. **DI 上下文依赖**: `RequesterCtx`/`TargetCtx` 通过 `Depends()` 缓存（同一事件处理周期内只解析一次），pipeline 中多个 handler 共享同一实例，替代 `T_State` dict
8. **前置检查 handler**: `common.py` 的 `group_enabled_check` 作为共享 guard handler
7. **图表渲染**: `ChartRenderer`（HTML/CSS + Jinja2 + Playwright）
   - 使用 Jinja2 模板引擎渲染 HTML
   - 通过 `page.goto(file://)` 加载临时 HTML 文件（保持字体相对路径有效）
   - 自适应内容高度后截图
   - 可爱蜜桃粉主题（Quicksand + Noto Sans SC 字体）
   - 排行榜：三段式布局（前5 + 你的位置 + 倒数5），支持金银铜牌和查询者高亮
   - 注入历史：SVG 折线图 + 数据明细表格
