#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成内嵌全部162首诗歌目录的 index.html（主导航页）
"""
import json, os

# 读取完整分析数据（轻量版：只取导航需要的字段）
with open('C:/Users/ronal/WorkBuddy/20260322121323/platform/data/all_analysis.json', encoding='utf-8') as f:
    all_data = json.load(f)

# 构建导航数据（轻量）
nav_data = {}
for k, v in all_data.items():
    nav_data[k] = {
        'num': v['num'],
        'char': v['char'],
        'theme': v.get('overview', {}).get('theme', ''),
        'emotion': v.get('overview', {}).get('emotion_tone', ''),
        'chars': v.get('stats', {}).get('total_chars', 0),
        'status': 'completed'
    }

js_nav = json.dumps(nav_data, ensure_ascii=False, separators=(',',':'))

# 诗歌的分组（按主题/季节/情感）
groups = {
    '自然四季': [c for c in '秋春夏冬风雨雪雾冰融露虹云晴晨夜'],
    '森林生灵': [c for c in '羽鱼蒲萤蝶龟蛇鹿枭雀马蜗蜜螺铃狐蜓凤'],
    '草木花石': [c for c in '荷叶树枭芽落葵榛草花石'],
    '情感心境': [c for c in '爱怜悲悦怒恕愁悟困伤默念忆思梦静暖'],
    '人生哲思': [c for c in '路行渡流停望闯空真闲忙时光明年元凡'],
    '精神追求': [c for c in '诗琴棋画歌舞幻术智'],
    '成长故事': [c for c in '试梯潜补息知懂变信义诺法'],
]

html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>爱（AI）解题叶渡诗河 · 全篇导览</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#0d1f12;--bg2:#102016;--bg3:#152b1a;
  --accent:#52c276;--accent2:#76d896;--accent3:#a8e6c0;
  --text:#e8f5e9;--text2:#b2dfdb;--text3:#80cbc4;
  --gold:#f9d56e;--gold2:#fbe599;
  --card:#1e3a24;--card2:#243d2a;
}
body{background:var(--bg);color:var(--text);font-family:"Microsoft YaHei","PingFang SC",sans-serif;min-height:100vh;overflow-x:hidden}

/* 顶部 */
.header{
  background:linear-gradient(180deg,var(--bg2),var(--bg));
  padding:48px 24px 32px;text-align:center;
  border-bottom:1px solid rgba(82,194,118,0.15);
  position:relative;overflow:hidden;
}
.header::before{
  content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse at 50% -20%,rgba(82,194,118,0.1),transparent 60%);
  pointer-events:none;
}
.header-series{
  font-size:13px;letter-spacing:4px;color:var(--accent);
  text-transform:uppercase;margin-bottom:12px;
}
.header-title{
  font-size:clamp(24px,5vw,42px);font-weight:900;
  background:linear-gradient(135deg,var(--gold),var(--accent2),var(--gold2));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;margin-bottom:8px;
  filter:drop-shadow(0 0 20px rgba(249,213,110,0.2));
}
.header-subtitle{
  font-size:16px;color:var(--text3);margin-bottom:24px;letter-spacing:2px;
}
.header-desc{
  font-size:14px;color:var(--text3);max-width:560px;margin:0 auto 24px;line-height:1.8;
}
.stats-row{
  display:flex;justify-content:center;gap:24px;flex-wrap:wrap;margin-bottom:8px;
}
.stat-item{text-align:center}
.stat-num{
  font-size:32px;font-weight:900;color:var(--gold);
  font-variant-numeric:tabular-nums;
}
.stat-label{font-size:12px;color:var(--text3);letter-spacing:1px;margin-top:2px}

/* 搜索/筛选 */
.toolbar{
  display:flex;align-items:center;gap:12px;
  padding:16px 24px;background:rgba(13,31,18,0.95);
  border-bottom:1px solid rgba(82,194,118,0.1);
  flex-wrap:wrap;
}
.search-box{
  display:flex;align-items:center;gap:8px;
  background:var(--card);border:1px solid rgba(82,194,118,0.25);
  border-radius:20px;padding:6px 16px;
}
.search-box input{
  background:none;border:none;outline:none;
  color:var(--text);font-size:14px;width:160px;
}
.search-box input::placeholder{color:var(--text3)}
.filter-btn{
  background:var(--card);border:1px solid rgba(82,194,118,0.2);
  border-radius:16px;padding:6px 14px;font-size:13px;
  color:var(--text3);cursor:pointer;transition:all 0.2s;
}
.filter-btn:hover,.filter-btn.active{
  background:rgba(82,194,118,0.15);border-color:var(--accent);color:var(--accent);
}

/* 字河主体 */
.river-container{
  max-width:1200px;margin:0 auto;padding:32px 20px;
}
.river-title{
  font-size:13px;color:var(--text3);letter-spacing:3px;
  text-align:center;margin-bottom:24px;
}

/* 字格 */
.chars-grid{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(72px,1fr));
  gap:10px;
}
.char-btn{
  aspect-ratio:1;border-radius:14px;
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  cursor:pointer;border:1px solid transparent;
  transition:all 0.2s;position:relative;overflow:hidden;
  text-decoration:none;
}
.char-btn.done{
  background:linear-gradient(135deg,var(--card),var(--card2));
  border-color:rgba(82,194,118,0.35);
}
.char-btn.done:hover{
  transform:translateY(-3px) scale(1.05);
  border-color:var(--accent);
  box-shadow:0 8px 24px rgba(82,194,118,0.25);
  background:linear-gradient(135deg,var(--card2),#2e4d36);
}
.char-num{
  font-size:10px;color:var(--text3);margin-bottom:2px;
}
.char-word{
  font-size:28px;font-weight:700;
  color:var(--accent2);line-height:1;
  transition:color 0.2s;
}
.char-btn.done:hover .char-word{color:var(--gold)}
.char-theme{
  font-size:9px;color:var(--text3);margin-top:3px;
  opacity:0;transition:opacity 0.2s;
}
.char-btn.done:hover .char-theme{opacity:1}

/* 工具提示 */
.char-btn::after{
  content:attr(data-tooltip);
  position:absolute;bottom:-28px;left:50%;transform:translateX(-50%);
  background:rgba(0,0,0,0.8);color:var(--text);
  font-size:11px;padding:3px 8px;border-radius:4px;
  white-space:nowrap;pointer-events:none;opacity:0;
  transition:opacity 0.15s;z-index:10;
}
.char-btn:hover::after{opacity:1}

/* 分段标题 */
.section-divider{
  grid-column:1/-1;
  padding:8px 0 4px;
  font-size:12px;color:var(--accent);letter-spacing:3px;
  border-bottom:1px solid rgba(82,194,118,0.15);
  margin-top:12px;
}

/* 高亮搜索 */
.char-btn.hidden{display:none}
.char-btn.highlight .char-word{color:var(--gold)!important}
.char-btn.highlight{border-color:var(--gold)!important;box-shadow:0 0 16px rgba(249,213,110,0.3)}

/* 底部 */
.footer{
  text-align:center;padding:32px 16px;
  color:var(--text3);font-size:13px;
  border-top:1px solid rgba(82,194,118,0.1);
  line-height:2;
}

/* 手机适配 */
@media(max-width:480px){
  .chars-grid{grid-template-columns:repeat(auto-fill,minmax(56px,1fr));gap:7px}
  .char-word{font-size:22px}
  .toolbar{padding:10px 12px}
}
</style>
</head>
<body>

<header class="header">
  <div class="header-series">森林的孩子 · 故事诗系列</div>
  <div class="header-title">爱（AI）解题叶渡诗河</div>
  <div class="header-subtitle">每一个字，都是一个故事</div>
  <div class="header-desc">叶渡著 · 162首故事诗 · AI结构化解析 · 完整呈现</div>
  <div class="stats-row">
    <div class="stat-item"><div class="stat-num">162</div><div class="stat-label">总篇数</div></div>
    <div class="stat-item"><div class="stat-num" id="doneCount">162</div><div class="stat-label">已解析</div></div>
    <div class="stat-item"><div class="stat-num">8</div><div class="stat-label">分析维度</div></div>
    <div class="stat-item"><div class="stat-num">100%</div><div class="stat-label">完成率</div></div>
  </div>
</header>

<div class="toolbar">
  <div class="search-box">
    <span style="color:var(--text3)">🔍</span>
    <input type="text" id="searchInput" placeholder="搜索诗字…" oninput="filterPoems(this.value)">
  </div>
  <button class="filter-btn active" data-filter="all" onclick="setFilter('all',this)">全部</button>
  <button class="filter-btn" data-filter="自然四季" onclick="setFilter('自然四季',this)">自然四季</button>
  <button class="filter-btn" data-filter="森林生灵" onclick="setFilter('森林生灵',this)">森林生灵</button>
  <button class="filter-btn" data-filter="情感心境" onclick="setFilter('情感心境',this)">情感心境</button>
  <button class="filter-btn" data-filter="人生哲思" onclick="setFilter('人生哲思',this)">人生哲思</button>
  <button class="filter-btn" data-filter="精神追求" onclick="setFilter('精神追求',this)">精神追求</button>
</div>

<div class="river-container">
  <div class="river-title">· 点击任意汉字，进入诗篇解析 ·</div>
  <div class="chars-grid" id="charsGrid"></div>
</div>

<footer class="footer">
  <div>《森林的孩子》故事诗 · 叶渡 著</div>
  <div>爱（AI）解题叶渡诗河 · AI结构化解析平台</div>
  <div style="margin-top:8px;font-size:11px;color:var(--text3);opacity:0.6">共162篇 · 含原文、概述、文化背景、人物、时间线、价值观、章节拆解、文学手法</div>
</footer>

<script>
const NAV_DATA = __NAV_DATA__;

// 主题-汉字映射
const THEME_MAP = {
  '自然四季': '秋春夏冬风雨雪雾冰融露虹云晴晨夜'.split(''),
  '森林生灵': '羽鱼蒲萤蝶龟蛇鹿枭雀马蜗蜜螺铃狐蜓凤'.split(''),
  '草木花石': '荷叶树芽落葵榛'.split(''),
  '情感心境': '爱怜悲悦怒恕愁悟困伤默念忆思梦静暖'.split(''),
  '人生哲思': '路行渡流停望闯空真闲忙时光明年元凡'.split(''),
  '精神追求': '诗琴棋画歌舞幻术智'.split(''),
  '成长故事': '试梯潜补息知懂变信义诺法'.split(''),
};

function getCharTheme(char) {
  for (const [theme, chars] of Object.entries(THEME_MAP)) {
    if (chars.includes(char)) return theme;
  }
  return '';
}

let currentFilter = 'all';

function renderGrid(data) {
  const grid = document.getElementById('charsGrid');
  grid.innerHTML = '';
  const entries = Object.values(data).sort((a, b) => a.num - b.num);

  entries.forEach(p => {
    const numStr = String(p.num).padStart(2, '0');
    const theme = p.theme || getCharTheme(p.char) || '';
    const tooltip = p.chars ? `No.${p.num} · ${p.chars}字 · ${theme||p.emotion||''}` : `No.${p.num}`;
    const btn = document.createElement('a');
    btn.className = 'char-btn done';
    btn.href = `./poem.html?id=${numStr}`;
    btn.dataset.filter = theme;
    btn.dataset.char = p.char;
    btn.dataset.num = p.num;
    btn.dataset.tooltip = tooltip;
    btn.innerHTML = `
      <div class="char-num">${p.num}</div>
      <div class="char-word">${p.char}</div>
      <div class="char-theme">${theme}</div>`;
    grid.appendChild(btn);
  });
}

function filterPoems(query) {
  const q = query.trim();
  document.querySelectorAll('.char-btn').forEach(btn => {
    const char = btn.dataset.char || '';
    const num = btn.dataset.num || '';
    const matchSearch = !q || char.includes(q) || num.includes(q);
    const matchFilter = currentFilter === 'all' || btn.dataset.filter === currentFilter;
    btn.classList.toggle('hidden', !matchSearch || !matchFilter);
    btn.classList.toggle('highlight', q.length > 0 && char.includes(q));
  });
}

function setFilter(filter, el) {
  currentFilter = filter;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  if (el) el.classList.add('active');
  filterPoems(document.getElementById('searchInput').value);
}

// 初始化
renderGrid(NAV_DATA);

// 统计
const doneCount = Object.values(NAV_DATA).filter(p => p.status === 'completed').length;
document.getElementById('doneCount').textContent = doneCount;
</script>
</body>
</html>'''

html = html.replace('const NAV_DATA = __NAV_DATA__;', f'const NAV_DATA = {js_nav};')

output_path = 'C:/Users/ronal/WorkBuddy/20260322121323/platform/index.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

size = os.path.getsize(output_path)
print(f'index.html 生成完毕：{size//1024} KB')
print(f'导航数据包含 {len(nav_data)} 首诗歌')
