<div align="center">
  <!--
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  -->
  <a href="https://v2.nonebot.dev/store"><img src="./docs/NoneBotPlugin.svg" width="300" alt="logo"></a>
</div>

<div align="center">

# nonebot-plugin-impart

_✨ NoneBot2 银趴插件 Plus ✨_

<a href="./LICENSE">
</a>
<img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="python">
</div>

## 📖 介绍

nonebot-plugin-impart 是基于项目 [Special-Week/nonebot_plugin_impact](https://github.com/Special-Week/nonebot_plugin_impact) 的 NoneBot2 ~~银趴~~插件，经过大量重构与功能扩展，包含正值/负值双世界体系、挑战系统、PK 归一化胜率机制等。

### 核心特性

- **正值/负值双世界体系**：长度 ≤ 0 进入负值世界（"女孩子"状态），拥有完全独立的指令集和文案
- **PK 归一化胜率**：双方胜率参与判定 Wa/(Wa+Wb)，爆冷倍率、单边抛物线阻尼
- **登神长阶 / 深渊试炼**：长度/深度达 25cm 触发挑战，仅通过 PK 冲击 30cm
- **xnn 联动**：0 < 长度 ≤ 5 区间 PK 胜率减半，透群友概率被反透
- **雌堕事件**：xnn 状态下当日累计被注入 ≥ 500ml 触发剧情转变
- **精美图表渲染**：HTML/CSS + Jinja2 + Playwright 蜜桃粉主题排行榜与注入历史折线图
- **完善的测试体系**：254 项自动化测试（119 单元 + 94 集成 + 2 烟雾）

### 玩法一览

| 指令 | 世界 | 效果 | CD |
|:---:|:---:|:---:|:---:|
| 打胶/开导 | 正值 | 自己 +随机长度 | 300s |
| 开扣/挖矿 | 负值 | 自己 +随机深度 | 300s |
| 嗦牛子/嗦 | 正值 | @目标 +随机长度 | 300s |
| 舔小学/舔 | 负值 | @目标 +随机深度 | 300s |
| pk/对决 | 通用 | 归一化胜率对决，赢方+输方- | 60s |
| 击剑 | 正值 | 正值专用 PK | 60s |
| 磨豆腐/磨 | 负值 | 负值专用 PK | 60s |
| 日/透 群友 | 正值 | 选目标注入，支持@指定 | 3600s |
| 日/透 群主 | 正值 | 固定目标为群主 | 3600s |
| 日/透 管理 | 正值 | 随机选取管理员 | 3600s |
| 榨 群友 | 负值 | 榨取正值目标，支持@指定 | 3600s |
| 榨 群主 | 负值 | 固定目标为群主 | 3600s |
| 榨 管理 | 负值 | 随机选取管理员 | 3600s |
| 查询 | 通用 | @目标或自己的长度/深度与胜率 | 无 |
| 银趴排行榜 | 通用 | 精美图表排行榜 | 无 |
| 注入查询 | 通用 | 被注入量（支持历史折线图） | 无 |

## 💿 安装

<details open>
<summary>使用 nb-cli 安装（推荐）</summary>

    nb plugin install nonebot-plugin-impart

</details>

<details>
<summary>使用包管理器安装</summary>

    pip install nonebot-plugin-impart

打开 `pyproject.toml` 文件，在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_impart"]

</details>

## 🖇️ 迁移原插件数据库

如果先前使用 [nonebot_plugin_impact](https://github.com/Special-Week/nonebot_plugin_impact) 并想迁移数据：

1. 找到原数据库 `impact.db`（通常位于 `你的项目目录/data/impact/`）
2. 重命名为 `impart.db`
3. 使用 `nb localstore` 查看数据路径
4. 将 `impart.db` 放入对应的 `nonebot_plugin_impart` 文件夹中

## ⚙️ 配置

在 `.env` 文件中添加以下配置：

| 配置项 | 必填 | 默认值 | 说明 |
|:---:|:---:|:---:|:---|
| DJ_CD_TIME | 否 | 300 | 打胶/开扣 CD（秒） |
| PK_CD_TIME | 否 | 60 | PK/击剑/磨豆腐 CD（秒） |
| SUO_CD_TIME | 否 | 300 | 嗦牛子/舔小学 CD（秒） |
| FUCK_CD_TIME | 否 | 3600 | 透/榨群友 CD（秒） |
| PK_RAKE_RATIO | 否 | 0.5 | PK 赢家收益系数 |
| PK_WIN_RATE_K | 否 | 0.02 | PK 胜率变化基础量 |
| ISALIVE | 否 | False | 不活跃惩罚（超过 1 天未操作 -随机长度） |
| BAN_ID_LIST | 否 | 123456 | 透群友白名单（逗号分隔） |
| JJ_ALIASES | 否 | ["牛子","牛牛","newnew"] | 正值世界别名（随机选取） |
| HOLE_ALIASES | 否 | ["小学","蜜雪"] | 负值世界别名（随机选取） |

## 🎉 使用

使用 `银趴介绍` 或 `impart介绍` 指令获取完整命令列表。

### 指令表

| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:---:|:---:|:---:|:---:|:---|
| 开启银趴/禁止银趴 | 管理 | 否 | 群聊 | 开启或关闭群银趴功能 |
| 日/透 群友/管理/群主 | 群员 | 否 | 群聊 | 透群友时可@指定目标 |
| 榨 群友/管理/群主 | 群员 | 否 | 群聊 | 负值世界指令，榨群友时可@指定目标 |
| pk/对决 @用户 | 群员 | 否 | 群聊 | 归一化胜率 PK |
| 击剑 @用户 | 群员 | 否 | 群聊 | 正值专用 PK |
| 磨豆腐/磨 @用户 | 群员 | 否 | 群聊 | 负值专用 PK |
| 打胶/开导 | 群员 | 否 | 群聊 | 增加自己长度 |
| 开扣/挖矿 | 群员 | 否 | 群聊 | 增加自己深度（负值世界） |
| 嗦牛子/嗦 | 群员 | 否 | 群聊 | 增加@目标长度（未@则为自己） |
| 舔小学/舔 | 群员 | 否 | 群聊 | 增加@目标深度（未@则为自己，负值世界） |
| 查询 | 群员 | 否 | 群聊 | 查询@目标长度/深度与胜率 |
| 银趴排行榜/impart排行榜 | 群员 | 否 | 群聊 | 图表排行榜 |
| 注入查询/摄入查询 | 群员 | 否 | 群聊 | 查询被注入量（后接"历史"可查图表） |
| 银趴介绍/impart介绍 | 群员 | 否 | 群聊 | 输出命令列表 |

## ✨ 特别感谢
- [Special-Week/nonebot_plugin_impact](https://github.com/Special-Week/nonebot_plugin_impact) 提供的灵感与代码支持
