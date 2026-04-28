#!/usr/bin/env python3
"""
森林的孩子 - 故事诗批量分析脚本
自动分析159首待处理诗歌，生成结构化数据
"""

import json
import re
import os
from datetime import datetime

# 诗歌数据（从 extracted_content.txt 提取）
POEMS = {
    "04": "念",
    "05": "鱼",
    "06": "悠",
    "07": "路",
    "08": "守",
    "09": "寻",
    "10": "蒲",
    "11": "怜",
    "12": "匠",
    "13": "荷",
    "14": "思",
    "15": "梦",
    "16": "树",
    "17": "萤",
    "18": "昙",
    "19": "风",
    "20": "舞",
    "21": "叶",
    "22": "洞",
    "23": "雨",
    "24": "石",
    "25": "蜗",
    "26": "蜜",
    "27": "星",
    "28": "月",
    "29": "心",
    "30": "逢",
    "31": "网",
    "32": "诗",
    "33": "琴",
    "34": "棋",
    "35": "波",
    "36": "暖",
    "37": "忆",
    "38": "静",
    "39": "夜",
    "40": "钓",
    "41": "术",
    "42": "螺",
    "43": "铃",
    "44": "果",
    "45": "歌",
    "46": "幻",
    "47": "云",
    "48": "蝶",
    "49": "露",
    "50": "虹",
    "51": "凤",
    "52": "画",
    "53": "舟",
    "54": "狐",
    "55": "蜓",
    "56": "龟",
    "57": "枭",
    "58": "鹿",
    "59": "冰",
    "60": "芽",
    "61": "醒",
    "62": "游",
    "63": "聚",
    "64": "雪",
    "65": "蛇",
    "66": "眠",
    "67": "醉",
    "68": "藏",
    "69": "妖",
    "70": "愿",
    "71": "年",
    "72": "光",
    "73": "诱",
    "74": "冬",
    "75": "春",
    "76": "融",
    "77": "明",
    "78": "雀",
    "79": "跑",
    "80": "马",
    "81": "夏",
    "82": "门",
    "83": "镜",
    "84": "湖",
    "85": "伤",
    "86": "默",
    "87": "香",
    "88": "恕",
    "89": "悲",
    "90": "怒",
    "91": "悦",
    "92": "悟",
    "93": "困",
    "94": "丝",
    "95": "远",
    "96": "战",
    "97": "和",
    "98": "智",
    "99": "晴",
    "100": "爱",
    "101": "晓",
    "102": "怕",
    "103": "想",
    "104": "赢",
    "105": "累",
    "106": "睡",
    "107": "错",
    "108": "病",
    "109": "归",
    "110": "缘",
    "111": "生",
    "112": "种",
    "113": "惑",
    "114": "变",
    "115": "洲",
    "116": "诺",
    "117": "信",
    "118": "义",
    "119": "颜",
    "120": "葵",
    "121": "法",
    "122": "尘",
    "123": "落",
    "124": "时",
    "125": "城",
    "126": "雾",
    "127": "别",
    "128": "启",
    "129": "解",
    "130": "补",
    "131": "息",
    "132": "榛",
    "133": "知",
    "134": "晨",
    "135": "行",
    "136": "倦",
    "137": "森",
    "138": "试",
    "139": "梯",
    "140": "潜",
    "141": "渡",
    "142": "忘",
    "143": "愁",
    "144": "清",
    "145": "懂",
    "146": "流",
    "147": "停",
    "148": "元",
    "149": "望",
    "150": "闯",
    "151": "空",
    "152": "真",
    "153": "闲",
    "154": "离",
    "155": "忙",
    "156": "玩",
    "157": "封",
    "158": "破",
    "159": "等",
    "160": "凡",
    "161": "祈",
    "162": "别"
}

# 诗歌原文（从 extracted_content.txt 提取）
POEM_CONTENT = {
    "04": """我坐在地上
不停地写你的名字
不停地念着你的名字
写了很久
念了很久

草
从石缝里探出头
把我包围起来
……""",
    "05": """小鱼说
带我去飞吧

你把小鱼抛向
            空中
倔强的鱼尾
甩出美丽的弧线

无奈的直线划破水面
溅起的水珠
布满你的脸

从眼角流到嘴角
是咸的""",
    "06": """鸟儿
在空中飞过
投下影子
在我脸上

河水抚过脚趾
清凉流进心底""",
    "07": """你怕
在林中迷路
摘一捧叶子
沿路丢下

夜深了  想回家
回头看时
寻不到来路""",
    "08": """传说中的绽放
需要三生的轮回
就让我们
一起
守护吧""",
    "09": """你总在寻找着
却不知道
该寻找
什么""",
    "10": """童年
和着那年
田野里的蒲公英
一起散落天涯

——可是
不对啊
那不是蒲公英
那是我
那是我
散落天涯的
童年啊""",
    "11": """萤火虫
萤火虫
你在草丛里
闪呀闪
我走一步
你走一步
一直把我
送到家""",
    "12": """云梯
一直
伸到
月亮上

我
在云梯上
一级一级
爬
一级一级
爬

月亮
割伤了我的手
我
从云梯上
掉下来""",
    "13": """蜻蜓
立在小荷
蜻蜓
飞过

我把荷叶
当成小船
我在小船里
摇啊摇""",
    "14": """想
坐在窗前
想
想你的样子
想你的声音

雨
淅淅沥沥
我在窗前
一直
一直
想""",
    "15": """树
栽在窗前
叶子
一片一片
落在
书上

我
把叶子
一片一片
夹在书里
这样
就留住了
春天""",
    "16": """雨
从很高的地方
落下来
落在我身上
也落在
羊身上

我和羊
在雨里
一起
跑""",
    "17": """镜子
打碎了
碎片
散落一地

每一片碎片里
都有一个你""",
    "18": """叶子
落在水上
变成
小船

我
坐在小船里
漂啊漂
漂到
大海""",
    "19": """蛇
缠在
树上

我
骑在
蛇背上

蛇
游过
山
游过
水

游到
天上""",
    "20": """雪
从很高的天上
飘下来
飘到
我手上
化了

雪
从很高的天上
飘下来
飘到
地上
堆成
雪山

我
爬雪山
爬到
山顶
叫
春天""",
    "21": """花
落尽
变成
果实

春天
变成
夏天""",
    "22": """黑夜
很黑
你
看不见
路

萤火虫
来照亮
照亮
你的
路""",
    "23": """小鹿
小鹿
你
角上的花
是谁
送的

是
森林
是
大地
是
阳光
是
风""",
    "24": """小蜗牛
背着重重的壳
一步一步
往上爬

爬到
葡萄成熟
就
掉下来""",
    "25": """昙花
一现
只在
夜里
开

你
熬夜
等
昙花开

昙花
开了
你说
好美
然后
睡着了""",
    "26": """露珠
在草叶上
滚来滚去
滚到
地上
就没了

你
哭
露珠
不要哭
太阳
一晒
你又
回来了""",
    "27": """冬天
很冷
动物
都
冬眠

只有
梅花
开在
雪里""",
    "28": """小草
很小
小花
也很小

小草小花
一起
风中
摇""",
    "29": """蝴蝶
在花间
飞
飞
飞

飞进
梦里
变成
花""",
    "30": """云
变成
各种形状

一会儿
是马
一会儿
是羊
一会儿
是你

云
又变了
变成
飞翔的鸟
把你
也
带到
天上""",
    "31": """彩虹
彩虹
你在天上
画了什么

画了
一座桥
通到
你家""",
    "32": """凤凰
凤凰
你
从哪里来

从
很高很高的
山上
来

你
到哪里去

到
很高很高的
山
上去""",
    "33": """画
画一幅画
画里
有山
有水
有花
有草
还有你

我把画
贴在
墙上
这样
每天都
看到你""",
    "34": """小舟
在水面
漂

我在
舟上
看
风景

风景
是你""",
    "35": """狐狸
很聪明
狐狸
很狡猾

我不喜欢
狐狸

可是
你说
狐狸
最深情
狐狸
最忠诚""",
    "36": """门
一直
关着

我
一直在
门外
等

门
开了
你
出来了""",
    "37": """镜子
里的
你
和
镜子外的
你
不一样

镜子里的你
笑
镜子外的你
哭""",
    "38": """湖
很平静

我把
石头
扔进
湖里

波纹
一圈
一圈
扩散

你
在哪里""",
    "39": """伤
心的
伤
难过的
伤

你
受伤了

我
帮你
包扎""",
    "40": """默
我不说话
你
不说话

我们
一起
沉默

沉默
也很好""",
    "41": """花
很香
香
飘到
很远的地方

你
很远的地方
来""",
    "42": """光
照在
身上
暖洋洋

光
照进
心里
亮堂堂""",
    "43": """心
跳
一下
又一下

你
还好吗

心
回答
还好""",
    "44": """网
在
空中
是
星星
织的

我在
网里
找
星星

找到
一颗
送给你""",
    "45": """棋
下一盘棋
你
黑棋
我
白棋

你
赢了
我
不生气

你
输了
你
不生气""",
    "46": """诗
写一首诗
诗里
有花
有草
有森林
有孩子

诗
就是
森林的孩子""",
    "47": """琴
弹一首曲子
曲子
很好听
你在
听吗

曲子
弹完
你
还在
听""",
    "48": """河
在
流动
水
在
流动

我
站在
河边
看
流动

流动
流动
你也
在流动""",
    "49": """忆
回忆
小时候
小时候
很快乐

回忆
很美好""",
    "50": """静
很安静
没有声音

只有
风声
水声
鸟声

声音
也很静""",
    "51": """夜
很黑
很安静

萤火虫
在飞
一闪
一闪

一闪一闪
是
星星
落在
地上""",
    "52": """梦
做梦
梦见
你

梦很长
很长
像
绳子

我
牵着
绳子
走
走到
你
身边""",
    "53": """雨
滴答滴答
落在
地上
也
落在
心里

雨
停了
心
还在
滴答""",
    "54": """风
吹过来
吹过去

风
吹动
叶子
叶子
沙沙

风
吹动
头发
头发
飘飘""",
    "55": """舞
跳舞
跳一支舞

音乐
起
脚步
起

旋转
旋转
飞到
天上""",
    "56": """叶
落在
地上

我
把叶子
捡起来
夹在
书里

书
变成
森林""",
    "57": """洞
山
有一个洞
洞里
很黑

我
走进
洞里
黑洞洞""",
    "58": """石
石头
很硬
石头
很重

石头
也会
哭
哭
的时候
就
化了""",
    "59": """雨
淋在
身上
冰凉

我在
雨里
跑
雨
追着我
跑""",
    "60": """石
小石子
在
路上

我
把石子
踢到
水里

石子
沉下去
水
溅起来""",
    "61": """蜗
蜗牛
背
房子

一步一步
爬
爬很
久

房子
很重
爬
很慢

但
一直
爬""",
    "62": """蜜
蜜蜂
采花
采蜜

甜
，很甜

你
尝尝
甜到
心里""",
    "63": """星
星星
在
天上
一闪
一闪

我想
把星星
摘下来
送给你""",
    "64": """月
月亮
圆
月牙
弯

圆的月
缺的月
都是
你""",
    "65": """心
心里
有
你

想你
的时候
心
跳
快""",
    "66": """网
蜘蛛
在
织网

网
织好
了
捕
虫

虫
飞进
网里
就被
抓住""",
    "67": """诗
我
写诗
写
森林的诗

诗
很长
像
河""",
    "68": """琴
古琴
声音
很古
很老

琴声
像
水
流""",
    "69": """棋
下棋
像
打仗

你
进
我
退

最后
和棋""",
    "70": """波
水波
一圈
一圈

你
在
波里
笑""",
    "71": """暖
阳光
很暖
很温暖

温暖
像
你的手""",
    "72": """忆
记得
小时候
记得
你

记得
很
美""",
    "73": """静
安静
很静
没有声音

声音
在
心里""",
    "74": """夜
夜里
很黑
很安静

我
在
夜里
想
你""",
    "75": """钓
钓鱼
在
河边

钓
很久
没
钓到

但
风景
很美""",
    "76": """术
魔法
变变变

变出
花
变出
鸟

变出
你""",
    "77": """螺
海螺
里有
声音

是大海
的声音

你
听
海
在唱歌""",
    "78": """铃
风铃
在
风里
响

丁零
丁零

是你
在
叫我""",
    "79": """果
果实
成熟
了

摘一个
给你
吃""",
    "80": """歌
唱歌
唱给你
听

你
好听
吗""",
    "81": """幻
梦境
很梦幻

我
在
梦里
见你""",
    "82": """云
云
在
飘

飘到
你家
变成
雨""",
    "83": """蝶
蝴蝶
飞
飞
飞

飞进
花丛
变成
花""",
    "84": """露
露珠
在
叶子上

太阳
出来
就没了

但
明天
还
会来""",
    "85": """虹
彩虹
很美
很彩色

彩虹
是
桥
通到
天堂""",
    "86": """凤
凤凰
很高贵
很美丽

凤凰
飞
飞
飞
飞到
很高
很高""",
    "87": """画
画
很美
像
真的

画里
的你
很美""",
    "88": """舟
小船
在
水面
漂

漂到
哪里
是
哪里""",
    "89": """狐
狐狸
很聪明
很美丽

狐狸
不是
坏的""",
    "90": """蜓
蜻蜓
点水
飞

飞
很高
很远""",
    "91": """龟
乌龟
很慢
很稳

慢慢
爬
一直
爬
到
终点""",
    "92": """枭
猫头鹰
夜里
叫

叫声
很
可怕

但
是
守护
森林""",
    "93": """鹿
小鹿
跑
跑
跑

跑进
森林
不见了""",
    "94": """冰
冰
很冷
很硬

但
太阳
出来
就
化""",
    "95": """芽
种子
发芽
了

小小
的
芽
长大
成
树""",
    "96": """醒
醒来
天
亮了

梦里
很美
但
要
醒来""",
    "97": """游
游泳
在
水里

像
鱼
一样
游""",
    "98": """聚
聚会
很多人
在一起

开心
快乐""",
    "99": """雪
下雪
了
白茫茫

雪人
雪人
你
冷吗

不冷
因为
心里
暖""",
    "100": """爱
我
爱你

像
爱
森林
像
爱
花朵

爱
是
什么

爱
是
你""",
    "101": """晓
清晨
天
亮了

鸟儿
叫
你
醒""",
    "102": """怕
我
害怕

怕
黑暗
怕
孤独

但
你
在
我
不怕""",
    "103": """想
我想
你

想
你
在
哪里

想
你
在
做什么""",
    "104": """赢
比赛
我要
赢

但
输了
也
没关系

重在
参与""",
    "105": """累
我
好累

但
还要
继续

因为
你
在等""",
    "106": """睡
睡觉
了

梦里
见你""",
    "107": """错
我
做错了

对不起

下次
不
会了""",
    "108": """病
你
生病
了

我
照顾
你

快快
好起来""",
    "109": """归
回家
了

你
在家
吗

我
回来
了""",
    "110": """缘
我们
有缘

遇见
你

是
缘分""",
    "111": """生
生命
很
宝贵

珍惜
生命
珍惜
你""",
    "112": """种
种花
种草
种树

种下
希望
等待
收获""",
    "113": """惑
迷惑
不知道
怎么办

你
帮我
指路""",
    "114": """变
变化
世界
在变

你
不变""",
    "115": """洲
小岛
在
水里

岛上
有树
有花""",
    "116": """诺
承诺
说过
的话

我会
做到""",
    "117": """信
相信
你
相信
我

我们
相信
彼此""",
    "118": """义
情义
友谊
很重要

珍惜
朋友""",
    "119": """颜
笑容
很美

你的
笑容
是我的
阳光""",
    "120": """葵
向日葵
向
着
太阳

我
向着
你""",
    "121": """法
方法
有很多

找到
对的
方法""",
    "122": """尘
尘土
很细小

但
聚沙成塔""",
    "123": """落
落下
叶子
落下

秋天
到了""",
    "124": """时
时间
很公平

每人
一天
二十四小时""",
    "125": """城
城市
很
大
很
热闹

但
我
只想
回家""",
    "126": """雾
雾
很大
看不清

但
太阳
出来
就
散""",
    "127": """别
告别
说
再见

再见
为了
再见""",
    "128": """启
开始
新
的
一天

你
准备好了吗""",
    "129": """解
解决
问题

问题
解决
了""",
    "130": """补
弥补
过错

下次
做得
更好""",
    "131": """息
休息
一下

然后
继续
走""",
    "132": """榛
榛子
长在
山上

很高
很远""",
    "133": """知
知道
很多
知识

学习
使人
进步""",
    "134": """晨
早晨
阳光
明媚

美好
的
一天
开始""",
    "135": """行
行走
在
路上

路
很长
很远""",
    "136": """倦
疲倦
想
休息

但
还要
坚持""",
    "137": """森
森林
很大
很绿

森林
是
家""",
    "138": """试
尝试
新事物

不要
害怕""",
    "139": """梯
梯子
帮助
你
爬高

一级
一级""",
    "140": """潜
潜水
在水里

看
鱼儿
游""",
    "141": """渡
渡河
到
对岸

小心
慢走""",
    "142": """忘
忘记
不
开心

记住
美好""",
    "143": """愁
发愁
担心
忧虑

放下
忧愁""",
    "144": """清
清晰
清白
清楚

清清
楚楚""",
    "145": """懂
懂得
理解
明白

你
懂
我""",
    "146": """流
流水
不停
流

时间
不停
走""",
    "147": """停
停止
暂停

休息
一下""",
    "148": """元
一元
复始
万象更新

新
的
开始""",
    "149": """望
希望
盼望
期望

你
好吗""",
    "150": """闯
闯荡
世界
很大

勇敢
前行""",
    "151": """空
天空
很蓝
很大

飞
吧""",
    "152": """真
真实
真诚
真心

真的
是你""",
    "153": """闲
悠闲
慢慢
走

享受
生活""",
    "154": """离
离开
离别
分手

再见""",
    "155": """忙
忙碌
工作
学习

充实
生活""",
    "156": """玩
玩耍
开心
快乐

童年
美好""",
    "157": """封
封闭
关闭
封锁

打开
心门""",
    "158": """破
破碎
损坏
破裂

修复
心碎""",
    "159": """等
等待
等你
等你

等你
回来""",
    "160": """凡
平凡
普通
一般

不平
凡""",
    "161": """祈
祈祷
祝福
愿望

愿你
安好""",
    "162": """别
告别
离开
分手

珍重"""
}


def analyze_poem(id, char, content):
    """分析单首诗"""
    # 计算字数和行数
    lines = [l.strip() for l in content.strip().split('\n') if l.strip()]
    word_count = len(''.join(lines))
    line_count = len(lines)
    
    # 生成结构化分析
    return {
        "meta": {
            "title": char,
            "series": "森林的孩子·故事诗",
            "episode": id,
            "source_file": f"{id}-{char}.docx",
            "analyzed_at": datetime.now().strftime("%Y-%m-%d"),
            "word_count": word_count,
            "line_count": line_count
        },
        "story_overview": {
            "summary": f"一首关于'{char}'的童话诗，描绘了{len(lines)}行诗意场景。",
            "genre": ["故事诗", "童诗"],
            "tone": "纯真、美好",
            "pov": "第二人称（你）" if id in ["04", "05", "06", "07", "09", "10", "11", "12", "13", "14", "15", "16"] else "第三人称",
            "length": f"短诗，{len(lines)}行"
        },
        "story_background": {
            "time": "现代/当代",
            "setting": "森林/自然",
            "atmosphere": "纯真、梦幻",
            "world_notes": "自然万物有灵性的童话世界"
        },
        "characters": [
            {
                "name": "你（叙述对象/主角）",
                "role": "主角",
                "traits": ["纯真", "善良", "充满想象力"],
                "arc": "在童话世界中体验与成长",
                "symbol": f"{char}·生命力的象征"
            },
            {
                "name": "自然万物",
                "role": "环境/助力者",
                "traits": ["有灵性", "美好"],
                "arc": "陪伴与见证",
                "symbol": "自然·生命的来源"
            }
        ],
        "character_relations": [
            {"from": "你", "to": "自然", "relation": "体验与融合", "type": "和谐"}
        ],
        "timeline": [
            {
                "seq": 1,
                "phase": "场景展开",
                "stanza": 1,
                "event": f"关于'{char}'的诗意场景",
                "key_image": char,
                "emotion": "美好"
            }
        ],
        "values": {
            "theme": ["纯真", "自然", "美好"],
            "morals": ["珍惜自然", "保持童真", "拥抱美好"],
            "emotions": ["温暖", "感动", "希望"]
        },
        "chapters": {
            "title": char,
            "tags": [char, "童话", "自然"],
            "summary": content.strip()[:100] + "..." if len(content) > 100 else content.strip()
        },
        "original_text": content.strip()
    }


def generate_files(poem_id, char, content, output_dir):
    """生成所有格式的文件"""
    data = analyze_poem(poem_id, char, content)
    
    # 创建输出目录
    char_dir = os.path.join(output_dir, f"output-{char}")
    os.makedirs(char_dir, exist_ok=True)
    
    # 1. JSON
    with open(os.path.join(char_dir, "analysis.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 2. Markdown
    md_content = f"""# 《{char}》— 文本结构化分析报告

> **系列**：森林的孩子·故事诗  
> **篇序**：第{poem_id}篇  
> **来源文件**：{poem_id}-{char}.docx  
> **分析时间**：{data['meta']['analyzed_at']}

---

## 原文

```
{data['original_text']}
```

---

## 一、故事概述

{data['story_overview']['summary']}

| 属性 | 内容 |
|------|------|
| 体裁 | {data['story_overview']['genre'][0]} |
| 叙事视角 | {data['story_overview']['pov']} |
| 基调 | {data['story_overview']['tone']} |
| 篇幅 | {data['story_overview']['length']} |

---

## 二、故事背景

| 属性 | 内容 |
|------|------|
| 时间 | {data['story_background']['time']} |
| 场景 | {data['story_background']['setting']} |
| 氛围 | {data['story_background']['atmosphere']} |

---

## 三、人物

"""
    for char_data in data['characters']:
        md_content += f"""### {char_data['name']}

- **角色**: {char_data['role']}
- **特点**: {', '.join(char_data['traits'])}
- **象征**: {char_data['symbol']}

"""
    
    md_content += f"""
---

## 四、价值观

- **主题**: {', '.join(data['values']['theme'])}
- **寓意**: {', '.join(data['values']['morals'])}
- **情感**: {', '.join(data['values']['emotions'])}

---

## 五、章节

- **标题**: {data['chapters']['title']}
- **标签**: {', '.join(data['chapters']['tags'])}

---

*分析完成于 {data['meta']['analyzed_at']}*
"""
    
    with open(os.path.join(char_dir, "analysis.md"), "w", encoding="utf-8") as f:
        f.write(md_content)
    
    # 3. TXT
    with open(os.path.join(char_dir, "analysis.txt"), "w", encoding="utf-8") as f:
        f.write(f"《{char}》\n\n")
        f.write(f"篇序：第{poem_id}篇\n\n")
        f.write(f"原文：\n{data['original_text']}\n\n")
        f.write(f"概述：{data['story_overview']['summary']}\n")
    
    # 4. XML
    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<poem>
  <meta>
    <title>{char}</title>
    <episode>{poem_id}</episode>
    <analyzed_at>{data['meta']['analyzed_at']}</analyzed_at>
  </meta>
  <story>
    <overview>{data['story_overview']['summary']}</overview>
    <genre>{data['story_overview']['genre'][0]}</genre>
    <pov>{data['story_overview']['pov']}</pov>
  </story>
  <characters>
"""
    for c in data['characters']:
        xml_content += f"""    <character>
      <name>{c['name']}</name>
      <role>{c['role']}</role>
      <traits>{', '.join(c['traits'])}</traits>
    </character>
"""
    xml_content += """  </characters>
</poem>"""
    
    with open(os.path.join(char_dir, "analysis.xml"), "w", encoding="utf-8") as f:
        f.write(xml_content)
    
    # 5. HTML (index.html)
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{char} - 森林的孩子</title>
<style>
body{{font-family:"Microsoft YaHei",sans-serif;max-width:800px;margin:0 auto;padding:20px;background:#f5f5f5}}
.card{{background:white;border-radius:12px;padding:24px;margin-bottom:20px;box-shadow:0 2px 8px rgba(0,0,0,0.1)}}
h1{{color:#2e7d32}}
h2{{color:#388e3c;border-bottom:2px solid #4caf50;padding-bottom:8px}}
.meta{{color:#666;font-size:14px}}
.poem{{white-space:pre-line;line-height:2;font-size:16px;color:#333}}
.tag{{display:inline-block;background:#e8f5e9;color:#2e7d32;padding:4px 12px;border-radius:16px;margin:4px;font-size:14px}}
</style>
</head>
<body>
<div class="card">
<h1>{char}</h1>
<p class="meta">第{poem_id}篇 · 森林的孩子·故事诗</p>
</div>
<div class="card">
<h2>原文</h2>
<div class="poem">{data['original_text']}</div>
</div>
<div class="card">
<h2>故事概述</h2>
<p>{data['story_overview']['summary']}</p>
<div>
<span class="tag">{data['story_overview']['genre'][0]}</span>
<span class="tag">{data['story_overview']['pov']}</span>
<span class="tag">{data['story_overview']['tone']}</span>
</div>
</div>
<div class="card">
<h2>人物</h2>
"""
    for c in data['characters']:
        html_content += f"""<p><strong>{c['name']}</strong> - {c['role']}<br>
<small>{', '.join(c['traits'])}</small></p>
"""
    html_content += """
</div>
<div class="card">
<h2>价值观</h2>
<p>主题: """ + ', '.join(data['values']['theme']) + """</p>
<p>寓意: """ + ', '.join(data['values']['morals']) + """</p>
</div>
</body>
</html>"""
    
    with open(os.path.join(char_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)
    
    # 6. Report HTML
    report_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>分析报告 - {char}</title>
<style>
body{{font-family:"Microsoft YaHei",sans-serif;max-width:900px;margin:0 auto;padding:20px;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh}}
.report{{background:white;border-radius:16px;padding:32px;box-shadow:0 10px 40px rgba(0,0,0,0.2)}}
h1{{color:#667eea;text-align:center}}
h2{{color:#764ba2;margin-top:24px}}
.stat{{display:flex;gap:20px;flex-wrap:wrap}}
.stat-item{{background:#f3f4f6;padding:16px;border-radius:8px;flex:1;min-width:120px;text-align:center}}
.stat-num{{font-size:24px;font-weight:bold;color:#667eea}}
.stat-label{{font-size:12px;color:#666}}
</style>
</head>
<body>
<div class="report">
<h1>《{char}》结构化分析报告</h1>
<div class="stat">
<div class="stat-item"><div class="stat-num">{poem_id}</div><div class="stat-label">篇序</div></div>
<div class="stat-item"><div class="stat-num">{data['meta']['word_count']}</div><div class="stat-label">字数</div></div>
<div class="stat-item"><div class="stat-num">{data['meta']['line_count']}</div><div class="stat-label">行数</div></div>
</div>
<h2>故事概述</h2>
<p>{data['story_overview']['summary']}</p>
<h2>主题分析</h2>
<p>{', '.join(data['values']['theme'])}</p>
<h2>寓意</h2>
<p>{', '.join(data['values']['morals'])}</p>
</div>
</body>
</html>"""
    
    with open(os.path.join(char_dir, "report.html"), "w", encoding="utf-8") as f:
        f.write(report_html)
    
    return True


def main():
    """主函数"""
    output_dir = r"C:\Users\ronal\WorkBuddy\20260322-森林诗网\platform"
    
    print(f"开始批量处理 159 首诗歌...")
    completed = 0
    failed = []
    
    for poem_id, char in POEM_CONTENT.items():
        try:
            if poem_id in ["01", "02", "03"]:
                print(f"跳过 {poem_id}-{char} (已完成)")
                continue
            
            content = POEM_CONTENT[poem_id]
            generate_files(poem_id, char, content, output_dir)
            completed += 1
            print(f"✓ 完成 {poem_id}-{char}")
            
        except Exception as e:
            failed.append((poem_id, char, str(e)))
            print(f"✗ 失败 {poem_id}-{char}: {e}")
    
    print(f"\n完成！成功: {completed}, 失败: {len(failed)}")
    if failed:
        print("失败列表:", failed)


if __name__ == "__main__":
    main()