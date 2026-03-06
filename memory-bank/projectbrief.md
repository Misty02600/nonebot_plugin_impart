# Project Brief - nonebot_plugin_impart

## Overview
NoneBot2 银趴插件 Plus —— 一个基于 QQ 群聊的趣味"牛牛"模拟游戏插件。

## Core Requirements
- 群聊内的互动娱乐游戏，围绕虚拟"牛牛长度"展开
- 支持 PK 对决、打胶、嗦牛子、透群友、排行榜等玩法
- 独立发布的 PyPI 包，支持 OneBot v11 适配器
- 数据持久化存储（SQLite + SQLAlchemy 2.0 ORM）

## Architecture
- **分层架构**: core（纯业务逻辑） → infra（基础设施/数据库） → bot（NoneBot 集成/命令处理）
- **依赖注入**: 通过 NoneBot `Depends` 机制注入 DataManager、CooldownManager 等服务

## Tech Stack
- Python 3.10+
- NoneBot2 ≥ 2.4.3
- SQLAlchemy 2.0 (async, aiosqlite)
- nonebot-plugin-localstore (存储路径)
- nonebot-plugin-apscheduler (定时任务)
- nonebot-plugin-uninfo + nonebot-plugin-alconna (多平台支持)
- nonebot-plugin-htmlrender (Playwright 图表渲染)
- Jinja2 (图表 HTML 模板)

## Testing
- pytest + NoneBug 0.4.3 (NoneBot 专用测试框架)
- 226 项测试全通（162 单元 + 66 集成 + 2 烟雾）
- in-memory SQLite + DI monkeypatch
- ANY_MSG 通配哨兵跳过文案断言

## Current Game Mechanics
详见 systemPatterns.md
