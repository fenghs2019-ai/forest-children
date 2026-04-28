#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量为162首诗歌生成结构化分析JSON
策略：基于原文内容，用规则+模式匹配生成标准化分析字段
"""

import json, re, os

# ===== 读取原始数据 =====
with open('C:/Users/ronal/WorkBuddy/20260322121323/platform/data/all_poems_raw.json', encoding='utf-8') as f:
    raw = json.load(f)

# ===== 读取已有精细分析（01/02/03） =====
existing = {}
for num, char in [('01','羽'), ('02','桥'), ('03','秋')]:
    path = f'C:/Users/ronal/WorkBuddy/20260322121323/platform/output-{char}/analysis.json'
    try:
        with open(path, encoding='utf-8') as f:
            existing[num] = json.load(f)
    except:
        pass

# ===== 自然语言分析辅助函数 =====

# 情感词库
EMOTION_MAP = {
    '思念': ['念', '忆', '想', '望', '忘', '梦', '远', '别', '离', '归'],
    '自然': ['秋', '风', '雨', '雪', '春', '冬', '夏', '月', '星', '云', '露', '虹', '冰', '融', '晴', '晨'],
    '生命': ['生', '芽', '树', '叶', '花', '草', '林', '森', '荷', '蒲', '葵', '榛', '落'],
    '情感': ['爱', '怜', '悲', '悦', '怒', '恕', '愁', '悟', '困', '惑', '伤', '默'],
    '动物': ['羽', '鱼', '蒲', '萤', '蝶', '龟', '蛇', '鹿', '枭', '雀', '马', '蜗', '蜜', '螺', '铃', '狐', '蜓', '凤'],
    '旅途': ['路', '行', '游', '渡', '闯', '跑', '流', '停', '潜', '梯', '空', '闲', '忙'],
    '哲思': ['桥', '守', '寻', '知', '智', '悟', '变', '法', '信', '义', '诺', '和', '真'],
    '时光': ['时', '年', '晓', '明', '夜', '眠', '醒', '醉', '梦', '静', '元', '光'],
    '成长': ['试', '学', '种', '累', '赢', '错', '病', '怕', '想', '懂', '缘', '补'],
    '精神': ['诗', '琴', '棋', '画', '歌', '舞', '幻', '艺', '术'],
}

# 情感色彩判断
EMOTION_POSITIVE = ['爱', '悦', '融', '明', '晴', '春', '芽', '醒', '光', '暖', '和', '乐', '游', '歌', '舞', '幸', '美']
EMOTION_NEGATIVE = ['悲', '怒', '困', '伤', '愁', '累', '病', '错', '怕', '藏', '封', '冰', '冬', '离', '别', '暗']
EMOTION_NEUTRAL  = ['静', '默', '思', '知', '真', '清', '闲', '停', '元', '凡', '时', '行']

def get_theme(char):
    for theme, chars in EMOTION_MAP.items():
        if char in chars:
            return theme
    return '人生'

def get_emotion_tone(char, text):
    if char in EMOTION_POSITIVE:
        return '温暖积极'
    elif char in EMOTION_NEGATIVE:
        if char in ['别', '离', '悲']:
            return '伤感深沉'
        return '深沉内敛'
    elif char in EMOTION_NEUTRAL:
        return '平静沉思'
    # 根据文本分析
    pos_count = sum(1 for w in ['快乐','幸福','美','爱','温暖','希望','笑','阳光'] if w in text)
    neg_count = sum(1 for w in ['悲','痛','泪','伤','哭','绝望','黑暗','冷'] if w in text)
    if pos_count > neg_count:
        return '温暖积极'
    elif neg_count > pos_count:
        return '伤感深沉'
    return '平静沉思'

def extract_characters(text, char):
    """从文本中提取人物角色"""
    chars_found = []
    # 常见角色词
    role_patterns = ['孩子', '小熊', '小鱼', '鸟儿', '老树', '萤火虫', '蝴蝶', 
                     '我', '你', '他', '她', '森林', '风', '雨', '月亮', '星星',
                     '小蜗牛', '小鹿', '小狐狸', '小龟', '老人', '母亲', '父亲',
                     '蜜蜂', '蜻蜓', '凤凰', '树精', '精灵', '花儿', '叶子']
    for rp in role_patterns:
        if rp in text:
            chars_found.append(rp)
    # 默认角色
    if not chars_found:
        if '我' in text and '你' in text:
            chars_found = ['我（叙述者）', '你（倾听者）']
        elif '我' in text:
            chars_found = ['我（叙述者）']
        else:
            chars_found = ['森林中的生命']
    return chars_found[:4]  # 最多4个

def split_into_stanzas(lines):
    """将行列表分成节"""
    if not lines:
        return []
    n = len(lines)
    if n <= 5:
        return [lines]
    elif n <= 10:
        mid = n // 2
        return [lines[:mid], lines[mid:]]
    elif n <= 16:
        s = n // 3
        return [lines[:s], lines[s:2*s], lines[2*s:]]
    else:
        # 4节
        s = n // 4
        return [lines[:s], lines[s:2*s], lines[2*s:3*s], lines[3*s:]]

def guess_timeline(char, text, stanzas):
    """推断时间线/叙事结构"""
    n = len(stanzas)
    # 基于主题
    theme = get_theme(char)
    
    templates = {
        1: [
            ['起点', '过程', '落点'],
            ['铺垫', '转折', '余韵'],
            ['观察', '感悟', '升华'],
        ],
        2: [
            ['起因', '经过', '结果'],
            ['出发', '旅途', '抵达'],
            ['现在', '回忆', '未来'],
        ],
        3: [
            ['相遇', '相处', '相别'],
            ['等待', '出现', '离去'],
            ['播种', '生长', '收获'],
        ],
    }
    
    t_idx = min(n-1, 2)
    t_list = templates.get(t_idx, templates[2])
    
    # 选择最匹配的模板
    if theme in ['思念', '离别']:
        tl = ['相遇', '离别', '思念'][:n] if n <= 3 else ['相遇', '相处', '转折', '思念']
    elif theme in ['自然', '生命']:
        tl = ['观察', '感受', '共鸣'][:n] if n <= 3 else ['初见', '凝视', '触动', '共鸣']
    elif theme in ['旅途', '成长']:
        tl = ['出发', '旅途', '抵达'][:n] if n <= 3 else ['起点', '历程', '困境', '突破']
    elif theme in ['哲思', '精神']:
        tl = ['提问', '思考', '感悟'][:n] if n <= 3 else ['铺垫', '疑惑', '探寻', '顿悟']
    else:
        tl = t_list[0][:n] if n <= 3 else ['铺垫', '发展', '高潮', '余韵']
    
    result = []
    for i, (stanza, tl_name) in enumerate(zip(stanzas, tl)):
        result.append({
            'phase': tl_name,
            'stanza_index': i + 1,
            'lines': stanza,
            'description': f'第{i+1}节：' + '、'.join(stanza[:2]) + ('……' if len(stanza) > 2 else '')
        })
    return result

def get_literary_techniques(char, text, lines):
    """分析主要文学手法"""
    techniques = []
    
    # 拟人
    personification_words = ['说', '问', '笑', '哭', '唱', '跑', '跳', '想', '爱', '恨', '守']
    natural_subjects = ['风', '雨', '树', '花', '叶', '月', '星', '云', '水', '石']
    for ns in natural_subjects:
        if ns in text:
            for pw in personification_words:
                if pw in text:
                    techniques.append('拟人')
                    break
            break
    
    # 比喻
    if '像' in text or '如' in text or '似' in text or '仿佛' in text:
        techniques.append('比喻')
    
    # 排比
    line_starts = [l[:1] for l in lines if l]
    if len(set(line_starts)) < len(line_starts) * 0.7 and len(lines) >= 3:
        techniques.append('排比')
    
    # 象征
    symbols = {'羽': '自由', '桥': '连接', '路': '人生', '树': '生命', '月': '思念', 
               '星': '希望', '风': '自由', '水': '时光', '火': '激情', '冰': '冷漠'}
    if char in symbols:
        techniques.append('象征')
    
    # 对话体
    if '——' in text or '？' in text or '！' in text:
        techniques.append('对话')
    
    # 意象叠加
    nature_count = sum(1 for w in ['风', '雨', '云', '月', '星', '花', '叶', '水', '山', '树'] if w in text)
    if nature_count >= 3:
        techniques.append('意象叠加')
    
    # 重复/复沓
    for i in range(len(lines)-1):
        if lines[i] == lines[i+1] or (len(lines[i]) > 2 and lines[i][:2] == lines[i+1][:2]):
            techniques.append('重复/复沓')
            break
    
    # 去重
    techniques = list(dict.fromkeys(techniques))
    
    # 至少保留2个
    if len(techniques) < 2:
        techniques = ['借景抒情', '叙事抒情'] if len(techniques) == 0 else techniques + ['借景抒情']
    
    return techniques[:5]

def get_core_value(char, theme, text):
    """提炼核心价值观"""
    value_map = {
        '思念': '爱与思念是人类最深刻的情感纽带，即使分离也无法割断',
        '自然': '自然是生命的底色，与自然和谐共处是最深的智慧',
        '生命': '生命在于成长与绽放，每一个存在都有其独特的价值',
        '情感': '情感是人类心灵的语言，真实地感受与表达是一种勇气',
        '动物': '万物有灵，每一个生命都值得被温柔对待',
        '旅途': '人生是一段旅途，过程比终点更重要',
        '哲思': '停下来思考，是对生命最深的尊重',
        '时光': '时光流逝，珍惜当下是最好的人生态度',
        '成长': '成长需要经历挫折与磨砺，这是生命的必经之路',
        '精神': '艺术与精神的追求，让生命超越平凡',
        '人生': '每一段经历都是人生的组成部分，值得被认真对待',
    }
    return value_map.get(theme, '在平凡中发现美，在细节中感受生命的温度')

def get_forest_connection(char, text):
    """分析与森林主题的连接"""
    forest_words = ['森林', '树', '林', '叶', '枝', '根', '花', '草', '鸟', '虫', '水', '山']
    connections = [w for w in forest_words if w in text]
    if not connections:
        return f'《{char}》以"{char}"为核心意象，通过自然万物的感悟，呼应"森林的孩子"系列的生命主题'
    return f'文中的"{connections[0]}"等意象，将人类情感与森林自然融为一体，是系列主题的有机组成'

# ===== 主分析函数 =====
def build_analysis(num, raw_data, existing_data=None):
    if existing_data:
        return existing_data
    
    char = raw_data['char']
    lines = raw_data['lines']
    text = raw_data['text']
    
    # 去标题行
    content_lines = [l for l in lines if l and not re.match(r'^\d+[.．]', l)]
    full_text = '\n'.join(content_lines)
    
    # 基础统计
    char_count = len(full_text.replace('\n','').replace(' ','').replace('\u3000','').replace('\xa0',''))
    
    # 分节
    stanzas = split_into_stanzas(content_lines)
    
    # 分析
    theme = get_theme(char)
    emotion_tone = get_emotion_tone(char, full_text)
    characters = extract_characters(full_text, char)
    timeline = guess_timeline(char, full_text, stanzas)
    techniques = get_literary_techniques(char, full_text, content_lines)
    core_value = get_core_value(char, theme, full_text)
    
    # 生成摘要
    summary = f'《{char}》是"森林的孩子"系列第{int(num)}篇故事诗，全诗约{char_count}字，{len(stanzas)}节，' \
              f'以"{char}"为核心意象，{emotion_tone}，主题围绕{theme}展开。'
    
    # 文化背景
    cultural_bg = {
        '思念': f'中国传统文学中，"思念"是永恒的主题，从《诗经》到现代诗，"{char}"字承载着深厚的文化积淀。',
        '自然': f'中国传统山水诗中，"{char}"是重要意象，历代诗人借此抒发情志，寄托哲思。',
        '生命': f'生命意象在中国诗歌中代表生生不息的精神，"{char}"在此意义下承载着对生命的礼赞。',
        '动物': f'中国文学中常以动物寄情，"{char}"所代表的生灵在民间文化和文学传统中有着丰富的象征意义。',
        '旅途': f'"行路"是中国古典诗歌的重要主题，"{char}"呼应了"路漫漫其修远兮"的人生求索精神。',
        '哲思': f'中国哲学强调天人合一，"{char}"在此体现了对人与自然、人与社会关系的深度思考。',
        '时光': f'时光主题在中国诗歌中源远流长，"逝者如斯夫"的感慨贯穿古今，"{char}"在此延续了这一传统。',
        '精神': f'中国传统文人重视精神修养，"{char}"代表的艺术与精神追求，体现了深厚的人文情怀。',
    }.get(theme, f'"{char}"作为本诗的核心意象，在中国传统文化中承载着丰富的意涵，与"森林的孩子"系列的生命主题相呼应。')
    
    # 构建标准分析结构
    analysis = {
        'id': num.zfill(3),
        'num': int(num),
        'char': char,
        'title': char,
        'full_title': '森林的孩子·' + char,
        'series': '森林的孩子',
        'author_note': '叶渡',
        
        # 原文
        'original_text': full_text,
        'raw_lines': content_lines,
        
        # 基础统计
        'stats': {
            'total_chars': char_count,
            'line_count': len(content_lines),
            'stanza_count': len(stanzas)
        },
        
        # 概述
        'overview': {
            'summary': summary,
            'theme': theme,
            'emotion_tone': emotion_tone,
            'core_image': char,
            'keywords': [char, theme] + list(set(w for w in ['爱','生命','自然','成长','时光'] if w in full_text))[:3]
        },
        
        # 文化背景
        'background': {
            'cultural': cultural_bg,
            'forest_connection': get_forest_connection(char, full_text),
            'series_position': f'本篇为系列第{int(num)}篇，在162首中承担着{"前期积累" if int(num)<=54 else "中期深化" if int(num)<=108 else "后期升华"}的功能。'
        },
        
        # 人物
        'characters': [
            {
                'name': c,
                'role': '主角' if i == 0 else '配角',
                'description': f'诗中的{c}，承载着故事的情感与主题'
            } for i, c in enumerate(characters)
        ],
        
        # 时间线/叙事结构
        'timeline': timeline,
        
        # 价值观
        'values': {
            'core': core_value,
            'extended': [
                f'主题"{theme}"：{core_value[:30]}……',
                f'情感基调"{emotion_tone}"：引导读者以{emotion_tone}的心态感受自然与生命',
                f'意象"{char}"：以单字凝练诗意，体现了诗歌语言的极致精炼'
            ],
            'for_children': f'告诉孩子们：{core_value[:40]}。在森林的世界里，每一个生命都有它的故事。'
        },
        
        # 章节拆解
        'chapters': [
            {
                'index': i + 1,
                'title': tl['phase'],
                'lines': tl['lines'],
                'text': '\n'.join(tl['lines']),
                'char_count': len(''.join(tl['lines'])),
                'analysis': f'第{i+1}节"{tl["phase"]}"：' + ('、'.join(tl['lines'][:2]) + ('……' if len(tl['lines']) > 2 else '') + f'，展现了{theme}主题的{["铺垫","发展","升华","余韵"][min(i,3)]}层次。')
            } for i, tl in enumerate(timeline)
        ],
        
        # 文学手法
        'literary_techniques': techniques,
        
        # 状态
        'status': 'completed'
    }
    
    return analysis

# ===== 执行分析 =====
all_analysis = {}

for k in sorted(raw.keys(), key=lambda x: int(x)):
    num_int = int(k)
    num_str = str(num_int).zfill(2)
    existing_data = existing.get(num_str)
    all_analysis[k] = build_analysis(k, raw[k], existing_data)

# ===== 保存完整分析数据 =====
with open('C:/Users/ronal/WorkBuddy/20260322121323/platform/data/all_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(all_analysis, f, ensure_ascii=False, indent=2)

print('分析完成！共 ' + str(len(all_analysis)) + ' 首')
print('文件大小：', os.path.getsize('C:/Users/ronal/WorkBuddy/20260322121323/platform/data/all_analysis.json') // 1024, 'KB')

# 打印几个样本
for k in ['04', '26', '100', '162']:
    a = all_analysis[k]
    print(f"\n{k}-{a['char']}: {a['stats']['total_chars']}字/{a['stats']['line_count']}行/{a['stats']['stanza_count']}节")
    print('  主题:', a['overview']['theme'], '/', a['overview']['emotion_tone'])
    print('  手法:', '/'.join(a['literary_techniques']))
