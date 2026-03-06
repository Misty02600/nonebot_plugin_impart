# TASK011: Alconna + UniInfo 多平台适配重构

## 状态: Pending

## 概述
引入 `nonebot-plugin-alconna` 和 `nonebot-plugin-uninfo` 插件，对当前插件进行重构，摆脱对 OneBot V11 适配器的硬依赖，实现多平台适配。

## 目标
1. **命令系统迁移**: 将现有 `on_regex` / `on_command` 匹配器迁移至 Alconna 命令框架
2. **会话信息统一**: 使用 UniInfo（uninfo）替代直接依赖 `onebot.v11` 的 `GroupMessageEvent`、`Bot` 等类型，统一获取用户/群组信息
3. **多平台支持**: 适配完成后应可在 QQ（OneBot）、Telegram、Discord、KOOK 等平台运行
4. **消息构建统一**: 使用 `UniMessage` 替代 `MessageSegment.at()` 等 OneBot 特定消息段

## 涉及范围
- `bot/handlers/` — 所有 handler 的匹配器定义与消息构建
- `bot/dependencies.py` — 事件解析、用户信息获取、目标选择逻辑
- `core/rules.py` — 群组启用检查等规则
- `config.py` — 可能需要调整配置项
- `tests/` — 测试需同步迁移

## 关键变更点
- `on_regex(pattern)` → `on_alconna(Alconna(...))`
- `GroupMessageEvent` → `uninfo.Session`
- `event.user_id` → `session.user.id`
- `event.group_id` → `session.scene.id`
- `Bot.get_group_member_list()` → `uninfo` 接口或平台适配层
- `MessageSegment.at(uid)` → `UniMessage.at(uid)`

## 注意事项
- 需确认 `uninfo` 对各平台 "群成员列表" 查询的支持程度
- 榨/透命令的 `@` 目标提取逻辑需要用 Alconna 的 At 参数处理
- PK 等需要群成员列表的功能可能需要平台适配层兜底
- 数据库中现有 user_id 为 QQ 号（int），多平台后 id 格式可能不同，需考虑迁移策略

## 依赖
- 无强前置依赖，可独立进行
- 建议在其他功能扩展（TASK005-010）之前完成，避免后续重复迁移
