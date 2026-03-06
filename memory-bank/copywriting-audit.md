# nonebot_plugin_impart 文案总审表

> 自动生成于 2026-03-06。列出插件中 **所有面向用户发送的文案** 及其发送点（handler / DI / config），
> 附带当前集成测试覆盖状态和待改进标记。

---

## 目录

1. [配置项文案（config.py）](#1-配置项文案configpy)
2. [正值成长文案（progression_texts.py）](#2-正值成长文案progression_textspy)
3. [负值成长文案（progression_texts.py）](#3-负值成长文案progression_textspy)
4. [正值对决文案（duel_texts.py）](#4-正值对决文案duel_textspy)
5. [负值对决文案（duel_texts.py）](#5-负值对决文案duel_textspy)
6. [交互/事件文案（interaction_texts.py）](#6-交互事件文案interaction_textspy)
7. [Handler 内联文案（尚未迁入 texts 模块）](#7-handler-内联文案尚未迁入-texts-模块)
8. [集成测试覆盖缺口分析](#8-集成测试覆盖缺口分析)

---

## 1. 配置项文案（config.py）

| ID | 配置键 | 文案内容 | 发送点 | 集成测试 |
|----|--------|---------|--------|---------|
| C01 | `not_allow` | `群内还未开启impart游戏, 请管理员或群主发送"开始银趴", "禁止银趴"以开启/关闭该功能` | `common.py → group_enabled_check` 所有 handler 前置 | ✅ test_dajiao::test_group_not_enabled |
| C02 | `usage` | 多行帮助文本（见 config.py） | `help.py → help_handler` | ❌ 无 |

---

## 2. 正值成长文案（progression_texts.py）

### 2.1 打胶 (dajiao)

| ID | 函数/方法 | 文案模板 | 发送点 | 集成测试 |
|----|----------|---------|--------|---------|
| D01 | `dajiao_cd(remaining)` | `你已经打不动了喵, 请等待{remaining}秒后再打喵` | `dajiao.py` CD 检查 | ✅ test_cd_blocks_second_dajiao |
| D02 | `DajiaoCopy.create()` | `你还没有创建{jj_name}, 咱帮你创建了喵, 目前长度是10cm喵` | `dajiao.py` 新用户 | ✅ test_new_user_creation |
| D03 | `DajiaoCopy.challenging()` | `你的{jj_name}长度在任务范围内，不允许打胶，请专心与群友pk！` | `dajiao.py` 挑战中状态 | ✅ test_is_challenging_blocks_dajiao |
| D04 | `DajiaoCopy.finish()` | `打胶结束喵, 你的{jj_name}很满意喵, 长了{delta}cm喵, 目前长度为{length}cm喵` | `dajiao.py` 正常结算 | ✅ test_normal_dajiao_changes_length |
| D05 | `DajiaoCopy.trigger_challenge()` | `打胶结束喵...{botname}检测到你的{jj_name}长度超过25cm，已为你开启✨"登神长阶"✨...` | `dajiao.py` 触发挑战 | ✅ test_challenge_trigger_at_25 |

### 2.2 嗦牛子 (suo)

| ID | 函数/方法 | 文案模板 | 发送点 | 集成测试 |
|----|----------|---------|--------|---------|
| S01 | `suo_cd(remaining)` | `你已经嗦不动了喵, 请等待{remaining}秒后再嗦喵` | `suo.py` CD 检查 | ✅ test_suo_cd_blocks |
| S02 | `SuoCopy.create()` | `{pronoun}还没有创建{jj_name}喵, 咱帮{pronoun}创建了喵, 目前长度是10cm喵` | `suo.py` 目标不存在 | ✅ test_suo_creates_new_target |
| S03 | `SuoCopy.challenging()` | `{pronoun}的{jj_name}长度在任务范围内，不准嗦！请专心与群友pk！` | `suo.py` 目标挑战中 | ✅ test_suo_target_is_challenging |
| S04 | `SuoCopy.finish()` | `{pronoun}的{jj_name}很满意喵, 嗦长了{delta}cm喵, 目前长度为{length}cm喵` | `suo.py` 正常结算 | ✅ test_suo_normal_increases_length |
| S05 | `SuoCopy.trigger_challenge()` | `{pronoun}的{jj_name}很满意喵, 嗦长了{delta}cm喵...已为{pronoun}开启✨“登神长阶”✨...` | `suo.py` 触发挑战 | ✅ test_suo_triggers_challenge |

### 2.3 查询 (query) — 正值

| ID | 函数/方法 | 文案模板 | 发送点 | 集成测试 |
|----|----------|---------|--------|---------|
| Q01 | `QueryCopy.create()` | `{pronoun}还没有创建{jj_name}喵, 咱帮{pronoun}创建了喵, 目前长度是10cm喵` | `query.py` 新用户 | ✅ test_query_new_user |
| Q02 | `QueryCopy.god()` | `✨牛々の神✨\n{pronoun}的{jj_name}目前长度为{length}cm喵\n{pronoun}的当前胜率为{prob}%` | `query.py` length≥30 | ✅ test_query_god_title |
| Q03 | `QueryCopy.normal()` | `{pronoun}的{jj_name}目前长度为{length}cm喵\n{pronoun}的当前胜率为{prob}%` | `query.py` 5<length<30 | ✅ test_query_normal |
| Q04 | `QueryCopy.near_girl()` | `{pronoun}快要变成女孩子啦！\n{pronoun}的{jj_name}目前长度为{length}cm喵...` | `query.py` 0<length≤5 | ✅ test_query_near_girl |

---

## 3. 负值成长文案（progression_texts.py）

### 3.1 开扣/挖矿 (kaikou)

| ID | 函数/方法 | 文案模板 | 发送点 | 集成测试 |
|----|----------|---------|--------|---------|
| K01 | `kaikou_cd(remaining)` | `你已经扣不动了喵, 请等待{remaining}秒后再扣喵` | `kaikou.py` CD 检查 | ✅ test_cd_blocks_second_kaikou |
| K02 | `KaikouCopy.challenging()` | `深渊的试炼尚未结束！请专心与群友去磨豆腐吧喵！` | `kaikou.py` 挑战中 | ✅ test_is_challenging_blocks_kaikou |
| K03 | `KaikouCopy.finish()` | `挖矿结束喵, 你的{hole_name}很满意喵, 挖深了{delta}cm喵, 目前深度为{depth}cm喵` | `kaikou.py` 正常结算 | ✅ test_normal_kaikou_increases_depth |
| K04 | `KaikouCopy.trigger_challenge()` | `挖矿结束喵...{botname}检测到你的{hole_name}深度超过25cm，已为你开启🕳️「深渊试炼」🕳️...` | `kaikou.py` 触发挑战 | ✅ test_challenge_trigger_at_depth_25 |

### 3.2 舔小学 (tian)

| ID | 函数/方法 | 文案模板 | 发送点 | 集成测试 |
|----|----------|---------|--------|---------|
| T01 | `tian_cd(remaining)` | `你已经舔不动了喵, 请等待{remaining}秒后再舔喵` | `tian.py` CD 检查 | ❌ 无独立测试（通过共享 CD 间接覆盖） |
| T02 | `TianCopy.challenging()` | `深渊的试炼尚未结束！请专心与群友磨豆腐喵！` | `tian.py` 目标挑战中 | ✅ test_tian_target_is_challenging |
| T03 | `TianCopy.finish()` | `{pronoun}的{hole_name}很满意喵, 舔深了{delta}cm喵, 目前深度为{depth}cm喵` | `tian.py` 正常结算 | ✅ test_tian_normal_increases_depth |
| T04 | `TianCopy.trigger_challenge()` | `{pronoun}的{hole_name}很满意喵, 舔深了{delta}cm喵...已为{pronoun}开启🕳️「深渊试炼」🕳️...` | `tian.py` 触发挑战 | ✅ test_tian_challenge_trigger_at_depth_25 |

### 3.3 查询 (query) — 负值

| ID | 函数/方法 | 文案模板 | 发送点 | 集成测试 |
|----|----------|---------|--------|---------|
| NQ01 | `NegQueryCopy.abyss_lord()` | `🕳️深淵の主🕳️\n{pronoun}的{hole_name}目前深度为{depth}cm喵\n...胜率为{prob}%` | `query.py` depth≥30 | ✅ test_query_abyss_lord |
| NQ02 | `NegQueryCopy.girl()` | `{pronoun}已经是女孩子啦！\n{pronoun}的{hole_name}目前深度为{depth}cm喵...` | `query.py` 负值depth<30 | ✅ test_query_girl |

---

## 4. 正值对决文案（duel_texts.py）

### 4.1 PK 基本

| ID | 函数/方法 | 文案模板 | 发送点 | 集成测试 |
|----|----------|---------|--------|---------|
| PK01 | `pk_cd(remaining)` | `你已经pk不动了喵, 请等待{remaining}秒后再pk喵` | `pk.py → pk_cd_check` | ✅ test_pk_cd_blocks |
| PK02 | `PkCopy.create()` | `你或对面还没有创建{jj_name}喵, 咱帮忙创建了喵, 初始{jj_name2}长度为10cm喵` | `pk.py → _get_pk_ctx` | ✅ test_pk_new_users_created |
| PK03 | `PkCopy.win()` | 正常: `对决胜利喵, 你的{jj_name}增加了{inc}cm喵, 对面则在你的阴影笼罩下减小了{dec}cm喵` | `pk.py → _do_positive_pk` | ✅ test_positive_pk_win |
| PK03b | `PkCopy.win()` 爆冷 | 4 条随机文案（以弱胜强/化险为夷/惊人力量/大意没闪） | `pk.py → _do_positive_pk` bonus>1 | ❌ 无独立测试 |
| PK04 | `PkCopy.lose()` | 正常: `对决失败喵, 在对面{jj_name2}的阴影笼罩下你的{jj_name}减小了{dec}cm喵, 对面增加了{inc}cm喵` | `pk.py → _do_positive_pk` | ✅ test_positive_pk_lose |
| PK04b | `PkCopy.lose()` 爆冷 | 3 条随机文案（以弱胜强/绝境逆袭/轻敌了） | `pk.py → _do_positive_pk` bonus>1 | ❌ 无独立测试 |
| PK05 | `PkCopy.probability()` | `\n你的胜率现在为{prob}喵` | `pk.py → _do_positive_pk` 拼接到结尾 | ✅ 随 win/lose 测试覆盖 |

### 4.2 正值挑战状态（自己）

| ID | 函数/方法 | 文案模板 | 发送点 | 集成测试 |
|----|----------|---------|--------|---------|
| PK06 | `PkCopy.self_challenge_start()` | `{botname}检测到你的{jj_name}长度超过25cm，已为你开启✨“登神长阶”✨...` | `pk.py → _build_self_challenge_msg` 赢+CHALLENGE_STARTED | ✅ test_positive_pk_self_challenge_trigger |
| PK07 | `PkCopy.self_challenge_success()` | `🎉恭喜你完成登神挑战🎉\n你的{jj_name}长度已超过30cm，授予你🎊“牛々の神”🎊称号...` | `pk.py → _build_self_challenge_msg` 赢+SUCCESS | ✅ test_positive_pk_self_challenge_success |
| PK08 | `PkCopy.self_challenge_failed()` | `很遗憾，登神挑战失败，别气馊啦！\n你的{jj_name}长度缩短了5cm喵...` | `pk.py → _build_self_challenge_msg` 输+FAILED | ✅ test_positive_pk_self_challenge_failed |
| PK09 | `PkCopy.self_fall()` | `很遗憾，你跌落神坛，别气馊啦！\n你的{jj_name}长度缩短了5cm喵...` | `pk.py → _build_self_challenge_msg` 输+COMPLETED_REDUCE | ✅ test_positive_pk_self_fall_from_god |

### 4.3 正值挑战状态（对方）

| ID | 函数/方法 | 文案模板 | 发送点 | 集成测试 |
|----|----------|---------|--------|---------|
| PK10 | `PkCopy.opp_challenge_failed()` | `由于你对决的胜利，{botname}检测到TA的{jj_name}长度已不足25cm，很遗憾，TA的登神挑战失败...` | `pk.py → _build_opponent_challenge_msg` 赢+FAILED | ✅ test_positive_pk_opp_challenge_failed |
| PK11 | `PkCopy.opp_fall()` | `由于你对决的胜利，{botname}检测到TA的{jj_name}长度已不足25cm，TA跌落神坛...` | `pk.py → _build_opponent_challenge_msg` 赢+COMPLETED_REDUCE | ❌ 无 |
| PK12 | `PkCopy.opp_challenge_start()` | `由于你对决的失败...{botname}检测到TA的{jj_name}长度超过25cm，已为TA开启✨“登神长阶”✨` | `pk.py → _build_opponent_challenge_msg` 输+STARTED | ✅ test_positive_pk_opp_challenge_trigger |
| PK13 | `PkCopy.opp_challenge_success()` | `🎉恭喜你帮助TA完成登神挑战🎉\nTA的{jj_name}长度超过30cm，授予TA🎊"牛々の神"🎊称号` | `pk.py → _build_opponent_challenge_msg` 输+SUCCESS | ❌ 无 |

### 4.4 xnn 通知

| ID | 函数/方法 | 文案模板 | 发送点 | 集成测试 |
|----|----------|---------|--------|---------|
| PK14 | `xnn_enter()` | `\n你醒啦, 你已经变成xnn了！\n你当前的对决胜率减少50%...` | `pk.py → _build_xnn_notification` 输+LENGTH_NEAR_ZERO | ✅ test_positive_pk_xnn_enter_on_loss |
| PK15 | `xnn_self_exit()` | `\n恭喜你成功挟脱了xnn状态喵！` | `pk.py → _build_xnn_notification` XNN_EXIT(自己) | ✅ test_positive_pk_xnn_self_exit_on_win |
| PK16 | `xnn_opp_enter()` | `\n对方已经变成xnn了喵！` | `pk.py → _build_xnn_notification` 赢+对方LENGTH_NEAR_ZERO | ✅ test_positive_pk_opp_xnn_enter |
| PK17 | `xnn_opp_exit()` | `\n对方已挣脱xnn状态喵！` | `pk.py → _build_xnn_notification` 对方XNN_EXIT | ❌ 无 |

---

## 5. 负值对决文案（duel_texts.py）

### 5.1 磨豆腐 PK 基本

| ID | 函数/方法 | 文案模板 | 发送点 | 集成测试 |
|----|----------|---------|--------|---------|
| NP01 | `NegPkCopy.win()` | 正常: `对决胜利喵, 你的{hole_name}加深了{inc}cm喵, 对面则在你的吞噬下变浅了{dec}cm喵` | `pk.py → _do_negative_pk` | ✅ test_modofu_negative_pk |
| NP01b | `NegPkCopy.win()` 爆冷 | 4 条随机文案（绝境觉醒/深渊回应/黑暗蚕食/小看深渊） | `pk.py → _do_negative_pk` bonus>1 | ❌ 无独立测试 |
| NP02 | `NegPkCopy.lose()` | 正常: `对决失败喵, 在对面的侵蚀下你的{hole_name}变浅了{dec}cm喵, 对面加深了{inc}cm喵` | `pk.py → _do_negative_pk` | ✅ 通过 test_negative_pk_via_shared_matcher（路由到负值） |
| NP02b | `NegPkCopy.lose()` 爆冷 | 3 条随机文案（绝境觉醒/深渊回应/反噬轻敌） | `pk.py → _do_negative_pk` bonus>1 | ❌ 无独立测试 |
| NP03 | `NegPkCopy.probability()` | `\n你的pk胜率现在为{prob}喵` | `pk.py → _do_negative_pk` 拼接到结尾 | ✅ 随 win/lose 测试覆盖 |

### 5.2 负值挑战状态（自己）

| ID | 函数/方法 | 文案模板 | 发送点 | 集成测试 |
|----|----------|---------|--------|---------|
| NP04 | `NegPkCopy.self_challenge_start()` | `{botname}检测到你的{hole_name}深度超过25cm，已为你开启🕳️「坠入深渊」🕳️...` | `pk.py → _build_neg_self_challenge_msg` | ✅ test_negative_pk_self_challenge_trigger |
| NP05 | `NegPkCopy.self_challenge_success()` | `🎉恭喜你完成深渊挑战🎉\n你的{hole_name}深度已超过30cm，授予你🎊“深淵の主”🎊称号...` | `pk.py → _build_neg_self_challenge_msg` | ✅ test_negative_pk_self_challenge_success |
| NP06 | `NegPkCopy.self_challenge_failed()` | `很遗憾，深渊挑战失败，别气馊啦！\n你的{hole_name}深度减少了5cm喵...` | `pk.py → _build_neg_self_challenge_msg` | ✅ test_negative_pk_self_challenge_failed |
| NP07 | `NegPkCopy.self_fall()` | `很遗憾，你从深渊边缘跌落了，别气馊啦！\n你的{hole_name}深度减少了5cm喵...` | `pk.py → _build_neg_self_challenge_msg` | ✅ test_negative_pk_self_fall_from_abyss |

### 5.3 负值挑战状态（对方）

| ID | 函数/方法 | 文案模板 | 发送点 | 集成测试 |
|----|----------|---------|--------|---------|
| NP08 | `NegPkCopy.opp_challenge_failed()` | `由于你对决的胜利...深渊拒绝了弱者……TA的深渊挑战失败...` | `pk.py → _build_neg_opponent_challenge_msg` | ❌ 无 |
| NP09 | `NegPkCopy.opp_fall()` | `由于你对决的胜利...深渊拒绝了弱者……TA从深渊边缘跌落了...` | `pk.py → _build_neg_opponent_challenge_msg` | ❌ 无 |
| NP10 | `NegPkCopy.opp_challenge_start()` | `由于你对决的失败，深渊的力量在涌动...已为TA开启🕳️「坠入深渊」🕳️` | `pk.py → _build_neg_opponent_challenge_msg` | ❌ 无 |
| NP11 | `NegPkCopy.opp_challenge_success()` | `🎉恭喜你帮助TA完成深渊挑战🎉\nTA的{hole_name}深度超过30cm，授予TA🎊"深淵の主"🎊称号` | `pk.py → _build_neg_opponent_challenge_msg` | ❌ 无 |

---

## 6. 交互/事件文案（interaction_texts.py）

### 6.1 透群友菜单

| ID | 函数/方法 | 文案模板 | 发送点 | 集成测试 |
|----|----------|---------|--------|---------|
| Y01 | `YinpaMenuCopy.member()` | `现在咱将随机抽取一位幸运群友\n送给{user_card}色色！` | `yinpa.py → execute_tou` 群友 | ✅ test_tou_positive_normal |
| Y02 | `YinpaMenuCopy.reverse_member()` | `{botname}发现你是xnn~现在咱将{user_card}\n送给{target_card}色色！` | `yinpa.py → execute_tou` xnn反转 | ✅ test_tou_xnn_reversed |
| Y03 | `YinpaMenuCopy.xnn_both()` | `{botname}发现你俩都是xnn喵~现在咱将{user_card}\n送给{target_card}色色！` | `yinpa.py → execute_tou` 双xnn | ✅ test_tou_xnn_both |
| Y04 | `YinpaMenuCopy.owner()` | `现在咱将把群主\n送给{user_card}色色！` | `yinpa.py → execute_tou` 群主 | ✅ test_tou_qunzhu_variant |
| Y05 | `YinpaMenuCopy.admin()` | `现在咱将随机抽取一位幸运管理\n送给{user_card}色色！` | `yinpa.py → execute_tou` 管理 | ✅ test_tou_admin_at_allowed |
| Y06 | `YinpaMenuCopy.reverse_owner()` | `{botname}发现你是xnn~现在咱将{user_card}\n送给群主色色！` | `yinpa.py → execute_tou` xnn透群主 | ❌ 无 |
| Y07 | `YinpaMenuCopy.reverse_admin()` | `{botname}发现你是xnn~现在咱将{user_card}\n送给随机一位管理色色！` | `yinpa.py → execute_tou` xnn透管理 | ❌ 无 |

### 6.2 透群友结算

| ID | 函数/方法 | 文案模板 | 发送点 | 集成测试 |
|----|----------|---------|--------|---------|
| Y08 | `YinpaReport.active()` | `好欸！{req_user_card}(uid)用时{seconds}秒\n给 {target_card}(target_id) 注入了{ejaculation}毫升...` | `yinpa.py → execute_tou` 正常透 | ✅ test_tou_positive_normal |
| Y09 | `YinpaReport.reversed()` | `好欸！{target_card}(target_id)用时{seconds}秒\n给 {req_user_card}(uid) 注入了...` | `yinpa.py → execute_tou` xnn被反透 | ✅ test_tou_xnn_reversed |
| Y10 | `YinpaReport.squeeze()` | `好欸！{target_card}(target_id)用时{seconds}秒\n把 {req_user_card}(uid) 榨到腿软...` | `yinpa.py → execute_tou` xnn透女生 | ✅ test_tou_xnn_squeeze_female |
| Y11 | `YinpaReport.xnn_both()` | `好欸！{req_user_card}和{target_card}贴贴蹭蹭了{seconds}秒\n...互相注入...` | `yinpa.py → execute_tou` 双xnn | ✅ test_tou_xnn_both |

### 6.3 榨群友

| ID | 函数/方法 | 文案模板 | 发送点 | 集成测试 |
|----|----------|---------|--------|---------|
| Z01 | `ZhaMenuCopy.member()` | `现在咱将随机抽取一位幸运群友\n送给{user_card}榨汁！` | `yinpa.py → execute_zha` 群友 | ✅ test_zha_negative_normal |
| Z02 | `ZhaMenuCopy.owner()` | `现在咱将把群主\n送给{user_card}榨汁！` | `yinpa.py → execute_zha` 群主 | ✅ test_zha_owner_at_allowed |
| Z03 | `ZhaMenuCopy.admin()` | `现在咱将随机抽取一位幸运管理\n送给{user_card}榨汁！` | `yinpa.py → execute_zha` 管理 | ❌ 无 |
| Z04 | `ZhaReport.finish()` | `好欸！{req_user_card}(uid)用时{seconds}秒\n把 {target_card}(target_id) 榨出了{ejaculation}毫升...` | `yinpa.py → execute_zha` 正常结算 | ✅ test_zha_negative_normal |
| Z05 | `zha_no_male_target()` | `找不到男孩子送给你涩涩了喵，群友全是白河豚喵~` | `yinpa.py → positive_target_guard` 目标非正值 | ✅ test_zha_target_negative_blocked |

### 6.4 雌堕事件

| ID | 函数/方法 | 文案模板 | 发送点 | 集成测试 |
|----|----------|---------|--------|---------|
| EV01 | `CiduoEvent.announce()` | `{user_card}(uid)被注入了太多脱氧核糖核酸...\n{user_card}的{jj_name}彻底萝缩消失了♥\n取而代之的是一个深度{depth}cm的{hole_name}♥\n{user_card}已经完全雌堕, 变成了女孩子♥` | `yinpa.py → _check_ciduo` | ✅ test_tou_ciduo_trigger |

### 6.5 世界校验 / Guard 提示

| ID | 函数/方法 | 文案模板 | 发送点 | 集成测试 |
|----|----------|---------|--------|---------|
| G01 | `wrong_world_positive()` | `你还不是女孩子哦~` | `kaikou.py` 正值用开扣 | ✅ test_positive_world_blocks_kaikou |
| G02 | `wrong_world_negative(jj_name)` | `你没有{jj_name}喵，请使用「开扣/挖矿」指令喵` | `dajiao.py` 负值用打胶 | ✅ test_negative_world_blocks_dajiao |
| G03 | `wrong_world_use_zha(jj_name)` | `你没有{jj_name}喵，请使用「榨群友」指令` | `yinpa.py → positive_world_guard` 负值用透 | ✅ test_tou_negative_blocked |
| G04 | `pk_self_target()` | `你不能pk自己喵` | `pk.py → _get_pk_ctx` @自己 | ✅ test_pk_self_rejected |
| G05 | `pk_positive_only()` | `女生请使用「磨豆腐/磨」或「pk/对决」喵` | `pk.py → positive_world_guard` 负值用击剑 | ✅ test_jijian_negative_blocked |
| G06 | `pk_negative_only()` | `男生请使用「击剑」或「pk/对决」喵` | `pk.py → negative_world_guard` 正值用磨 | ✅ test_modofu_positive_blocked |
| G07 | `pk_same_camp_fail()` | `你们不在同一个世界喵！` | `pk.py → _get_pk_ctx` 阵营不同 | ✅ test_pk_cross_camp_rejected |
| G08 | `suo_target_negative(pronoun, jj_name)` | `{pronoun}是女生，没有{jj_name}可以嗦喵` | `suo.py` 目标负值 | ✅ test_suo_negative_target_blocked |
| G09 | `tian_target_not_negative(pronoun)` | `{pronoun}是男生，不能舔喵~` | `tian.py` 目标正值/新用户 | ✅ test_tian_positive_target_blocked |

### 6.6 目标选择（dependencies.py → _get_target_ctx）

| ID | 函数/方法 | 文案模板 | 发送点 | 集成测试 |
|----|----------|---------|--------|---------|
| TS01 | `target_not_found(action)` | 透: `找不到可以下手的目标喵~`<br>榨: `找不到可以榨的目标喵~` | `dependencies.py → _get_target_ctx` | ❌ 无 |
| TS02 | `self_target_owner(action)` | 透: `你透你自己?`<br>榨: `你榨你自己?` | `dependencies.py → _get_target_ctx` 群主自透 | ✅ test_tou_self_target_owner |
| TS03 | `no_admin_target(action)` | 透: `喵喵喵 找不到群管理!`<br>榨: `喵喵喵 找不到可榨的群管理!` | `dependencies.py → _get_target_ctx` 无可选管理 | ✅ test_tou_no_admin_target |

---

## 7. Handler 内联文案（尚未迁入 texts 模块）

以下文案仍硬编码在 handler 中，尚未收归 texts 模块统一管理：

| ID | 位置 | 文案内容 | 说明 |
|----|------|---------|------|
| **H01** | `yinpa.py:47` | `f"你已经榨不出来任何东西了, 请先休息{remaining}秒"` | 透/榨 CD 提示。与其他 CD 文案（dajiao_cd/suo_cd/pk_cd/kaikou_cd/tian_cd）风格不一致，可考虑提取为 `yinpa_cd(remaining)` |
| **H02** | `yinpa.py:76` | `"你还不是女孩子喵，请使用「日/透群友」指令"` | 正值玩家用"榨"时的阻断。应提取为 `wrong_world_use_tou()` 或整合到 `wrong_world_positive()` |
| **H03** | `rank.py:28` | `"目前记录的数据量小于5, 无法显示rank喵"` | 数据不足 |
| **H04** | `rank.py:35` | `f"你还没有创建{pick_jj_alias()}看不到rank喵, 咱帮你创建了喵, 目前长度是10cm喵"` | 新用户查排行 |
| **H05** | `rank.py:115` | `f"你的排名为{user_rank}喵"` | 排名输出 |
| **H06** | `control.py:30` | `"功能已开启喵"` | 开关控制 |
| **H07** | `control.py:33` | `"功能已禁用喵"` | 开关控制 |
| **H08** | `injection.py:48` | `f"{label}历史总被注射量为0ml"` | 历史注入为空 |
| **H09** | `injection.py:56` | `f"{label}历史总被注射量为{total}ml"` | 不足 2 天数据 |
| **H10** | `injection.py:72` | `f"{label}历史总被注射量为{total}ml"` | 有图表结果 |
| **H11** | `injection.py:75` | `f"{label}当日总被注射量为{ejaculation}ml"` | 当日查询 |

---

## 8. 集成测试覆盖缺口分析

### 8.1 覆盖统计

| 类别 | 总文案数 | 已覆盖 | 未覆盖 | 覆盖率 |
|------|---------|--------|--------|--------|
| 正值成长 (打胶/嗦/查询) | 9 + 4 | 11 | 2 | ~ 85% |
| 负值成长 (开扣/舔/查询) | 6 + 2 | 7 | 1 (T01) | ~ 88% |
| 正值 PK + xnn | 17 | 12 | 5 | ~ 71% |
| 负值 PK | 11 | 6 | 5 | ~ 55% |
| 透群友 | 11 | 9 | 2 (Y06/Y07) | ~ 82% |
| 榨群友 | 5 | 4 | 1 (Z03) | ~ 80% |
| Guard/校验 | 9 | 9 | 0 | 100% |
| 目标选择哨兵 | 3 | 2 | 1 (TS01) | ~ 67% |
| 雌堕事件 | 1 | 1 | 0 | 100% |
| Handler 内联 | 11 | 0 | 11 | 0% |
| 配置项 | 2 | 1 | 1 (help) | 50% |

### 8.2 建议补充的测试（按优先级排序）

#### 🔴 高优先级 — 核心业务路径

| 编号 | 测试场景 | 涉及文案 ID | 说明 |
|------|---------|-------------|------|
| ~~T-01~~ | ~~PK 挑战触发~~ | PK06 | ✅ test_positive_pk_self_challenge_trigger |
| ~~T-02~~ | ~~PK 挑战成功~~ | PK07 | ✅ test_positive_pk_self_challenge_success |
| ~~T-03~~ | ~~PK 挑战失败~~ | PK08 | ✅ test_positive_pk_self_challenge_failed |
| ~~T-04~~ | ~~PK 跌落神坛~~ | PK09 | ✅ test_positive_pk_self_fall_from_god |
| ~~T-05~~ | ~~负值 PK 挑战~~ | NP04-NP07 | ✅ 4 项负值挑战测试已全覆盖 |
| ~~T-06~~ | ~~雌堕事件触发~~ | EV01 | ✅ test_tou_ciduo_trigger |
| ~~T-07~~ | ~~xnn 进入/退出通知~~ | PK14-PK16 | ✅ 3 项 xnn 测试已覆盖 |

#### 🟡 中优先级 — 分支/变体

| 编号 | 测试场景 | 涉及文案 ID | 说明 |
|------|---------|-------------|------|
| ~~T-08~~ | ~~xnn 透群友（被反转）~~ | Y02, Y09 | ✅ test_tou_xnn_reversed |
| ~~T-09~~ | ~~双 xnn 互透~~ | Y03, Y11 | ✅ test_tou_xnn_both |
| ~~T-10~~ | ~~xnn 透女生（squeeze）~~ | Y10 | ✅ test_tou_xnn_squeeze_female |
| **T-11** | xnn 透群主 / xnn 透管理 | Y06, Y07 | xnn 发起者用群主/管理命令的反转菜单 |
| ~~T-12~~ | ~~嗦牛子目标正在挑战中~~ | S03 | ✅ test_suo_target_is_challenging |
| ~~T-13~~ | ~~嗦牛子触发目标挑战~~ | S05 | ✅ test_suo_triggers_challenge |
| ~~T-14~~ | ~~舔小学目标正在挑战中~~ | T02 | ✅ test_tian_target_is_challenging |
| **T-15** | PK 爆冷文案（bonus > 1） | PK03b/PK04b/NP01b/NP02b | 弱胜强随机文案 |
| **T-18** | PK 对手跌落神坛 | PK11 | 赢方导致对手从已完成挑战跌落 |
| **T-19** | PK 对手触发挑战成功 | PK13, NP11 | 输方导致对手完成挑战 |
| **T-20** | 对手 xnn 退出通知 | PK17 | 对方挣脱 xnn |
| **T-21** | 榨管理菜单 | Z03 | 榨管理目标选择 |
| **T-22** | 目标找不到（target_not_found） | TS01 | 群友全在 ban list 等极端情况 |

#### 🟢 低优先级 — 辅助功能/管理

| 编号 | 测试场景 | 涉及文案 ID | 说明 |
|------|---------|-------------|------|
| **T-16** | 帮助命令 | C02 | `银趴介绍` 输出帮助文本 |
| **T-17** | 排行榜数据不足 | H03 | 数据量 < 5 |
| **T-18** | 排行榜新用户 | H04 | 未注册查排行 |
| **T-19** | 注入查询（当日/历史/空） | H08-H11 | 注入查询子命令 |
| **T-20** | 开启/关闭控制 | H06-H07 | 管理员控制回复 |
| **T-21** | 目标选择哨兵消息 | TS01-TS03 | 群主自透/无管理/无目标 |

---

## 附注：文案风格 TODO

以下是代码中已标记的待优化项：

1. **interaction_texts.py**: `xnn_self_exit` / `xnn_opp_exit` — "退出的文案不太好，有待优化"
2. **interaction_texts.py**: `wrong_world_positive` — "和 wrong_world_negative 风格一致"（前者无 jj_name 参数，过于简单）
3. **interaction_texts.py**: PK 对方阵营不符时 — "对于对方不符合Pk性别的文案呢，可以说对方没有jj/hole，不能pk"
4. **interaction_texts.py**: `tian_target_not_negative` — "男生也要说没有hole可以舔喵。此外把所有男孩子女孩子改为男生女生"
5. **duel_texts.py**: `NegPkCopy` — "此处文案还需要优化，不要全是深渊抽象，由于是女同磨豆腐/互扣，可以具现一点"
6. **H01**: 透/榨 CD 文案 `"你已经榨不出来任何东西了"` 与其他 CD 提示风格不一致
7. **H02**: `"你还不是女孩子喵，请使用「日/透群友」指令"` 尚未迁入 texts 模块
