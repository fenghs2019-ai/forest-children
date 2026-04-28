#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成内嵌全部162首诗歌数据的 poem.html
"""
import json, os

# 读取完整分析数据
DATA_DIR = 'C:/Users/ronal/WorkBuddy/20260401002657/森林诗网/platform/data'
with open(f'{DATA_DIR}/all_analysis.json', encoding='utf-8') as f:
    all_data = json.load(f)

js_data = json.dumps(all_data, ensure_ascii=False, separators=(',',':'))

html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>爱（AI）解题叶渡诗河 · 诗篇详情</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#0d1f12;--bg2:#132a18;--bg3:#1a3520;
  --accent:#52c276;--accent2:#76d896;--accent3:#a8e6c0;
  --text:#e8f5e9;--text2:#b2dfdb;--text3:#80cbc4;
  --gold:#f9d56e;--gold2:#fbe599;
  --card:#1e3a24;--card2:#243d2a;
  --shadow:rgba(0,0,0,0.5);
}
body{background:var(--bg);color:var(--text);font-family:"Microsoft YaHei","PingFang SC",sans-serif;min-height:100vh;overflow-x:visible;overflow-y:auto;-webkit-animation:fixlayout 0.001s}@-webkit-keyframes fixlayout{0%{opacity:0.99}100%{opacity:1}}
window.onpageshow=function(e){if(e.persisted){location.replace(location.href+'&r='+Date.now())}};

/* 顶部导航 */
.top-nav{
  position:fixed;top:0;left:0;right:0;z-index:100;
  background:rgba(13,31,18,0.95);backdrop-filter:blur(10px);
  border-bottom:1px solid rgba(82,194,118,0.2);
  padding:12px 24px;display:flex;align-items:center;gap:16px;
}
.back-btn{
  display:flex;align-items:center;gap:6px;
  color:var(--accent);text-decoration:none;font-size:14px;
  padding:6px 14px;border:1px solid var(--accent);border-radius:20px;
  transition:all 0.2s;cursor:pointer;background:transparent;
}
.back-btn:hover{background:rgba(82,194,118,0.15)}
.nav-title{font-size:16px;color:var(--text2);font-weight:500}
.nav-subtitle{font-size:13px;color:var(--text3);margin-left:auto}

/* 英雄区 */
.hero{
  margin-top:60px;padding:60px 24px 40px;
  background:linear-gradient(135deg,var(--bg2),var(--bg3));
  text-align:center;border-bottom:1px solid rgba(82,194,118,0.15);
  position:relative;overflow:hidden;
}
.hero::before{
  content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse at 50% 0%,rgba(82,194,118,0.08),transparent 70%);
  pointer-events:none;
}
.poem-number{
  font-size:13px;color:var(--accent);letter-spacing:3px;
  text-transform:uppercase;margin-bottom:16px;
}
.poem-char-display{
  font-size:96px;font-weight:900;
  background:linear-gradient(135deg,var(--gold),var(--accent2),var(--gold2));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;
  line-height:1;margin-bottom:16px;
  text-shadow:none;
  filter:drop-shadow(0 0 30px rgba(249,213,110,0.3));
}
.poem-full-title{font-size:18px;color:var(--text2);margin-bottom:8px}
.poem-author{font-size:14px;color:var(--text3)}
.poem-stats-row{
  display:flex;justify-content:center;gap:32px;
  margin-top:24px;flex-wrap:wrap;
}
.stat-badge{
  background:rgba(82,194,118,0.1);border:1px solid rgba(82,194,118,0.25);
  border-radius:20px;padding:6px 18px;font-size:13px;color:var(--accent3);
}

/* 标签页 */
.tabs-container{
  position:sticky;top:60px;z-index:90;
  background:rgba(13,31,18,0.97);backdrop-filter:blur(10px);
  border-bottom:1px solid rgba(82,194,118,0.15);
}
.tabs{
  display:flex;overflow-x:auto;
  scrollbar-width:none;padding:0 16px;
}
.tabs::-webkit-scrollbar{display:none}
.tab{
  flex-shrink:0;padding:14px 20px;font-size:14px;
  color:var(--text3);cursor:pointer;
  border-bottom:2px solid transparent;
  transition:all 0.2s;white-space:nowrap;
}
.tab.active{color:var(--accent);border-bottom-color:var(--accent)}
.tab:hover{color:var(--accent2)}

/* 内容区 */
.content{max-width:840px;margin:0 auto;padding:40px 20px 80px}
.section{display:none}
.section.active{display:block}

/* 原文样式 */
.poem-text-box{
  background:var(--card);border:1px solid rgba(82,194,118,0.2);
  border-radius:16px;padding:40px;margin-bottom:24px;
  position:relative;
}
.poem-text-box::before{
  content:'"';position:absolute;top:20px;left:24px;
  font-size:60px;color:rgba(82,194,118,0.15);font-family:serif;line-height:1;
}
.poem-text{
  font-size:18px;line-height:2.4;
  white-space:pre-line;text-align:center;
  color:var(--text);letter-spacing:1px;
}
.poem-stanza-num{
  font-size:12px;color:var(--text3);text-align:center;
  margin-bottom:4px;letter-spacing:2px;
}

/* 通用卡片 */
.card{
  background:var(--card);border:1px solid rgba(82,194,118,0.15);
  border-radius:12px;padding:24px;margin-bottom:20px;
}
.card-title{
  font-size:13px;color:var(--accent);letter-spacing:2px;
  text-transform:uppercase;margin-bottom:16px;
  padding-bottom:10px;border-bottom:1px solid rgba(82,194,118,0.15);
  display:flex;align-items:center;gap:8px;
}
.card-title::before{content:'▶';font-size:10px}

/* 标签云 */
.tags{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
.tag{
  background:rgba(82,194,118,0.1);border:1px solid rgba(82,194,118,0.25);
  border-radius:20px;padding:4px 14px;font-size:13px;color:var(--accent3);
}
.tag.gold{
  background:rgba(249,213,110,0.1);border-color:rgba(249,213,110,0.3);
  color:var(--gold2);
}

/* 概述/背景 */
.info-row{
  display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px;
}
@media(max-width:560px){.info-row{grid-template-columns:1fr}}
.info-cell{
  background:var(--card2);border-radius:8px;padding:14px;
}
.info-label{font-size:12px;color:var(--text3);margin-bottom:6px}
.info-value{font-size:15px;color:var(--text)}

/* 人物卡片 */
.char-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px}
.char-card{
  background:var(--card2);border-radius:10px;padding:16px;
  border:1px solid rgba(82,194,118,0.1);
}
.char-name{font-size:16px;color:var(--gold2);margin-bottom:6px;font-weight:600}
.char-role{font-size:12px;color:var(--accent);margin-bottom:8px}
.char-desc{font-size:13px;color:var(--text2);line-height:1.6}

/* 时间线 */
.timeline{position:relative;padding-left:40px}
.timeline::before{
  content:'';position:absolute;left:14px;top:0;bottom:0;
  width:2px;background:linear-gradient(to bottom,var(--accent),transparent);
}
.timeline-item{
  position:relative;margin-bottom:28px;
}
.timeline-dot{
  position:absolute;left:-32px;top:4px;
  width:16px;height:16px;border-radius:50%;
  background:var(--accent);box-shadow:0 0 12px rgba(82,194,118,0.5);
  display:flex;align-items:center;justify-content:center;
}
.timeline-dot span{font-size:8px;color:#000;font-weight:bold}
.timeline-phase{
  font-size:13px;color:var(--accent);letter-spacing:1px;margin-bottom:6px;
}
.timeline-content{
  background:var(--card);border-radius:8px;padding:14px;
  border-left:3px solid var(--accent);
  font-size:14px;line-height:1.8;color:var(--text2);
}
.timeline-lines{
  font-size:15px;color:var(--text);line-height:2;
  border-bottom:1px solid rgba(82,194,118,0.1);margin-bottom:8px;
  padding-bottom:8px;white-space:pre-line;
}

/* 价值观 */
.value-main{
  font-size:18px;line-height:1.8;color:var(--gold2);
  text-align:center;padding:24px;
  background:linear-gradient(135deg,rgba(249,213,110,0.05),rgba(82,194,118,0.05));
  border-radius:12px;border:1px solid rgba(249,213,110,0.15);
  margin-bottom:20px;
}
.value-item{
  background:var(--card2);border-radius:8px;padding:14px;margin-bottom:10px;
  font-size:14px;color:var(--text2);line-height:1.7;
  border-left:3px solid var(--accent2);padding-left:16px;
}
.value-children{
  background:rgba(82,194,118,0.05);border-radius:12px;
  padding:20px;border:1px dashed rgba(82,194,118,0.2);
  font-size:15px;line-height:1.8;color:var(--accent3);text-align:center;
}

/* 章节 */
.chapter-item{
  background:var(--card);border-radius:10px;padding:20px;margin-bottom:16px;
  border:1px solid rgba(82,194,118,0.12);
}
.chapter-header{
  display:flex;align-items:center;gap:12px;margin-bottom:14px;
}
.chapter-num{
  width:32px;height:32px;border-radius:50%;
  background:var(--accent);color:#000;
  display:flex;align-items:center;justify-content:center;
  font-weight:bold;font-size:14px;flex-shrink:0;
}
.chapter-title{font-size:16px;color:var(--gold2);font-weight:600}
.chapter-stats{font-size:12px;color:var(--text3);margin-left:auto}
.chapter-text{
  font-size:15px;line-height:2.2;color:var(--text);
  white-space:pre-line;margin-bottom:12px;
  border-left:2px solid rgba(82,194,118,0.3);padding-left:14px;
}
.chapter-analysis{font-size:13px;color:var(--text2);line-height:1.6;font-style:italic}

/* 诗篇导航 */
.poem-nav{
  display:flex;justify-content:space-between;align-items:center;
  margin-top:48px;padding-top:24px;
  border-top:1px solid rgba(82,194,118,0.15);
}
.nav-poem-btn{
  display:flex;align-items:center;gap:8px;
  background:var(--card);border:1px solid rgba(82,194,118,0.2);
  border-radius:10px;padding:12px 20px;cursor:pointer;
  color:var(--text2);font-size:14px;transition:all 0.2s;
}
.nav-poem-btn:hover{background:var(--card2);border-color:var(--accent);color:var(--accent)}
.nav-poem-char{font-size:22px;color:var(--gold2);font-weight:bold}

/* 加载提示 */
.loading{
  display:flex;flex-direction:column;align-items:center;
  justify-content:center;height:50vh;gap:16px;
}
.loading-spinner{
  width:40px;height:40px;border:3px solid rgba(82,194,118,0.2);
  border-top-color:var(--accent);border-radius:50%;
  animation:spin 0.8s linear infinite;
}
@keyframes spin{to{transform:rotate(360deg)}}

.error-box{
  text-align:center;padding:60px 20px;color:var(--text3);
}
.error-char{font-size:60px;margin-bottom:16px}

/* 手法标签 */
.technique-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px}
.technique-card{
  background:var(--card2);border-radius:10px;padding:16px;
  border:1px solid rgba(82,194,118,0.1);text-align:center;
}
.technique-name{font-size:16px;color:var(--accent2);font-weight:600;margin-bottom:8px}
.technique-desc{font-size:13px;color:var(--text3);line-height:1.6}

/* 手机适配 */
@media(max-width:640px){
  .hero{padding:48px 16px 32px}
  .poem-char-display{font-size:72px}
  .content{padding:24px 16px 60px}
  .poem-text{font-size:16px}
  .tab{padding:12px 14px}
}

/* 配图配乐区 */
.media-container{display:grid;grid-template-columns:1fr;gap:24px;margin-top:20px}
.media-card{
  background:var(--card);border:1px solid rgba(82,194,118,0.2);
  border-radius:16px;overflow:hidden;
}
.media-header{
  background:rgba(82,194,118,0.1);padding:12px 20px;
  font-size:13px;color:var(--accent);letter-spacing:1px;
  border-bottom:1px solid rgba(82,194,118,0.15);
  display:flex;align-items:center;gap:8px;
}
.media-header::before{content:'♪'}
.poem-image{
  width:100%;
  max-height:60vh;
  object-fit:contain;
  display:block;
  border-radius:8px;
}
.audio-player{
  width:100%;padding:20px;background:var(--card2);
}
.audio-player audio{
  width:100%;height:40px;
  border-radius:20px;
}
.media-placeholder{
  padding:60px 20px;text-align:center;color:var(--text3);font-size:14px;
}

/* 配图配乐 section 顶部间距 */
#section-image, #section-audio{
  padding-top:20px;
}
</style>
</head>
<body>

<nav class="top-nav">
  <button class="back-btn" onclick="goBack()">← 返回诗河</button>
  <span class="nav-title" id="navTitle">爱（AI）解题叶渡诗河</span>
  <span class="nav-subtitle" id="navSubtitle"></span>
</nav>

<div id="heroSection" class="hero">
  <div class="poem-number" id="poemNumber">NO.001</div>
  <div class="poem-char-display" id="poemChar">·</div>
  <div class="poem-full-title" id="poemFullTitle">森林的孩子</div>
  <div class="poem-author">叶渡 著</div>
  <div class="poem-stats-row" id="poemStats"></div>
</div>

<div class="tabs-container">
  <div class="tabs" id="tabsBar">
    <div class="tab active" data-tab="text" onclick="switchTab('text')">原文</div>
    <div class="tab" data-tab="image" onclick="switchTab('image')">配图</div>
    <div class="tab" data-tab="audio" onclick="switchTab('audio')">配乐</div>
    <div class="tab" data-tab="overview" onclick="switchTab('overview')">概述</div>
    <div class="tab" data-tab="background" onclick="switchTab('background')">文化背景</div>
    <div class="tab" data-tab="characters" onclick="switchTab('characters')">人物</div>
    <div class="tab" data-tab="timeline" onclick="switchTab('timeline')">时间线</div>
    <div class="tab" data-tab="values" onclick="switchTab('values')">价值观</div>
    <div class="tab" data-tab="chapters" onclick="switchTab('chapters')">章节拆解</div>
    <div class="tab" data-tab="techniques" onclick="switchTab('techniques')">文学手法</div>
  </div>
</div>

<div class="content">
  <div id="section-text" class="section active"></div>
  <div id="section-image" class="section"></div>
  <div id="section-audio" class="section"></div>
  <div id="section-overview" class="section"></div>
  <div id="section-background" class="section"></div>
  <div id="section-characters" class="section"></div>
  <div id="section-timeline" class="section"></div>
  <div id="section-values" class="section"></div>
  <div id="section-chapters" class="section"></div>
  <div id="section-techniques" class="section"></div>
  <div id="poemNavBar"></div>
</div>

<script>
// ===== 内嵌数据 =====
const POEM_DATA = __POEM_DATA__;

// ===== 工具函数 =====
function getUrlParam(name) {
  const params = new URLSearchParams(window.location.search);
  return params.get(name);
}

function goBack() {
  window.location.href = 'index.html';
}

function switchTab(tab) {
  document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tab));
  document.querySelectorAll('.section').forEach(s => s.classList.toggle('active', s.id === 'section-' + tab));
}

function escapeHtml(s) {
  if (!s) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// ===== 渲染函数 =====
function renderPoem(poem) {
  if (!poem) {
    document.getElementById('section-text').innerHTML = `
      <div class="error-box">
        <div class="error-char">🍃</div>
        <div>未找到该诗篇，请返回诗河重新选择</div>
      </div>`;
    return;
  }

  // Hero 区
  const numStr = String(poem.num).padStart(3, '0');
  document.getElementById('poemNumber').textContent = 'NO.' + numStr;
  document.getElementById('poemChar').textContent = poem.char;
  document.getElementById('poemFullTitle').textContent = poem.full_title || ('森林的孩子·' + poem.char);
  document.title = '爱（AI）解题叶渡诗河 · ' + poem.char;
  document.getElementById('navSubtitle').textContent = 'NO.' + numStr + ' / 162';

  const stats = poem.stats || {};
  document.getElementById('poemStats').innerHTML = [
    stats.total_chars ? `<span class="stat-badge">${stats.total_chars} 字</span>` : '',
    stats.line_count ? `<span class="stat-badge">${stats.line_count} 行</span>` : '',
    stats.stanza_count ? `<span class="stat-badge">${stats.stanza_count} 节</span>` : '',
    poem.overview && poem.overview.theme ? `<span class="stat-badge">${poem.overview.theme}</span>` : '',
    poem.overview && poem.overview.emotion_tone ? `<span class="stat-badge">${poem.overview.emotion_tone}</span>` : '',
  ].join('');

  // 原文 - 跳过第一行标题
  const rawArr = poem.raw_lines || [];
  const textLines = rawArr.length > 0 ? rawArr.slice(1) : [];
  const stanzaCount = (poem.stats && poem.stats.stanza_count) || 1;
  const linesPerStanza = Math.ceil(textLines.length / stanzaCount);
  let textHtml = '';
  for (let i = 0; i < stanzaCount; i++) {
    const chunk = textLines.slice(i * linesPerStanza, (i + 1) * linesPerStanza);
    if (chunk.length === 0) continue;
    textHtml += `<div class="poem-stanza-num">第 ${i + 1} 节</div>
    <div class="poem-text">${escapeHtml(chunk.join('\\n'))}</div>
    ${i < stanzaCount - 1 ? '<br>' : ''}`;
  }
  document.getElementById('section-text').innerHTML = `
    <div class="poem-text-box">${textHtml}</div>`;

  // 配图
  const charFolder = 'output-' + poem.char;
  const imagePath = charFolder + '/image.jpg';
  const audioPath = charFolder + '/audio.mp3';
  document.getElementById('section-image').innerHTML = `
    <div class="card" style="margin-top:20px">
      <div class="card-title">配图</div>
      <img src="${imagePath}" alt="${escapeHtml(poem.char)}配图" class="poem-image"
           onerror="this.outerHTML='<div class=media-placeholder>暂无配图</div>'">
    </div>`;

  // 配乐
  document.getElementById('section-audio').innerHTML = `
    <div class="card" style="margin-top:20px">
      <div class="card-title">配乐朗诵</div>
      <div class="audio-player">
        <audio controls src="${audioPath}">
          您的浏览器不支持音频播放
        </audio>
      </div>
    </div>`;

  // 概述
  const ov = poem.overview || {};
  document.getElementById('section-overview').innerHTML = `
    <div class="card">
      <div class="card-title">内容摘要</div>
      <p style="line-height:1.9;font-size:15px;color:var(--text2)">${escapeHtml(ov.summary || poem.char + '，森林的孩子系列诗篇。')}</p>
    </div>
    <div class="info-row">
      <div class="info-cell"><div class="info-label">核心主题</div><div class="info-value">${escapeHtml(ov.theme || '-')}</div></div>
      <div class="info-cell"><div class="info-label">情感基调</div><div class="info-value">${escapeHtml(ov.emotion_tone || '-')}</div></div>
      <div class="info-cell"><div class="info-label">核心意象</div><div class="info-value">${escapeHtml(ov.core_image || poem.char)}</div></div>
      <div class="info-cell"><div class="info-label">所属系列</div><div class="info-value">${escapeHtml(poem.series || '森林的孩子')}</div></div>
    </div>
    <div class="card">
      <div class="card-title">关键词</div>
      <div class="tags">${(ov.keywords||[]).map(k=>`<span class="tag gold">${escapeHtml(k)}</span>`).join('')}</div>
    </div>`;

  // 文化背景
  const bg = poem.background || {};
  document.getElementById('section-background').innerHTML = `
    <div class="card">
      <div class="card-title">文化脉络</div>
      <p style="line-height:1.9;font-size:15px;color:var(--text2)">${escapeHtml(bg.cultural || '本诗承载着中国传统文化的深厚底蕴，与森林主题相辅相成。')}</p>
    </div>
    <div class="card">
      <div class="card-title">与森林主题的连接</div>
      <p style="line-height:1.9;font-size:15px;color:var(--text2)">${escapeHtml(bg.forest_connection || '')}</p>
    </div>
    <div class="card">
      <div class="card-title">系列位置</div>
      <p style="line-height:1.9;font-size:15px;color:var(--text2)">${escapeHtml(bg.series_position || '')}</p>
    </div>`;

  // 人物
  const chars = poem.characters || [];
  document.getElementById('section-characters').innerHTML = `
    <div class="card">
      <div class="card-title">登场角色（${chars.length}）</div>
      <div class="char-grid">
        ${chars.map(c => `
          <div class="char-card">
            <div class="char-name">${escapeHtml(c.name)}</div>
            <div class="char-role">${escapeHtml(c.role)}</div>
            <div class="char-desc">${escapeHtml(c.description || '')}</div>
          </div>`).join('')}
      </div>
    </div>`;

  // 时间线
  const tl = poem.timeline || [];
  document.getElementById('section-timeline').innerHTML = `
    <div class="card">
      <div class="card-title">叙事结构（${tl.length} 阶段）</div>
      <div class="timeline">
        ${tl.map((t, i) => `
          <div class="timeline-item">
            <div class="timeline-dot"><span>${i+1}</span></div>
            <div class="timeline-phase">${escapeHtml(t.phase)}</div>
            <div class="timeline-content">
              <div class="timeline-lines">${escapeHtml((t.lines||[]).join('\\n'))}</div>
              <div>${escapeHtml(t.description || '')}</div>
            </div>
          </div>`).join('')}
      </div>
    </div>`;

  // 价值观
  const val = poem.values || {};
  document.getElementById('section-values').innerHTML = `
    <div class="value-main">${escapeHtml(val.core || '在森林的世界里，每一个生命都值得被温柔对待。')}</div>
    <div class="card">
      <div class="card-title">延伸解读</div>
      ${(val.extended||[]).map(v => `<div class="value-item">${escapeHtml(v)}</div>`).join('')}
    </div>
    <div class="value-children">${escapeHtml(val.for_children || '')}</div>`;

  // 章节拆解
  const chs = poem.chapters || [];
  document.getElementById('section-chapters').innerHTML = `
    <div style="margin-bottom:20px">
      ${chs.map(c => `
        <div class="chapter-item">
          <div class="chapter-header">
            <div class="chapter-num">${c.index}</div>
            <div class="chapter-title">${escapeHtml(c.title)}</div>
            <div class="chapter-stats">${c.char_count||0} 字</div>
          </div>
          <div class="chapter-text">${escapeHtml((c.lines||[]).join('\\n'))}</div>
          <div class="chapter-analysis">${escapeHtml(c.analysis || '')}</div>
        </div>`).join('')}
    </div>`;

  // 文学手法
  const techs = poem.literary_techniques || [];
  const techDescs = {
    '拟人': '赋予自然物或动物以人的情感、行为，使形象生动',
    '比喻': '用熟悉事物比喻陌生事物，化抽象为具体',
    '排比': '用结构相似的句式反复强调，增强节奏感',
    '象征': '以具体事物寄托抽象意义，意在言外',
    '对话': '通过人物对话推动叙事，增加真实感',
    '意象叠加': '多个自然意象并置，营造丰富的诗境',
    '重复/复沓': '关键语句反复出现，强化情感与主题',
    '借景抒情': '通过描写自然景物来表达内心情感',
    '叙事抒情': '以叙述故事的方式融入情感，情理相融',
  };
  document.getElementById('section-techniques').innerHTML = `
    <div class="card">
      <div class="card-title">文学手法（${techs.length}）</div>
      <div class="technique-grid">
        ${techs.map(t => `
          <div class="technique-card">
            <div class="technique-name">${escapeHtml(t)}</div>
            <div class="technique-desc">${escapeHtml(techDescs[t] || '诗歌创作的重要表现手法')}</div>
          </div>`).join('')}
      </div>
    </div>
    <div class="card" style="margin-top:20px">
      <div class="card-title">综合赏析</div>
      <p style="line-height:1.9;color:var(--text2);font-size:15px">
        《${escapeHtml(poem.char)}》综合运用${escapeHtml(techs.join('、'))}等手法，
        以${escapeHtml((poem.overview&&poem.overview.emotion_tone)||'细腻')}的笔触，
        展现了${escapeHtml((poem.overview&&poem.overview.theme)||'生命')}主题的深度与广度。
        全诗${(poem.stats&&poem.stats.total_chars)||0}字，字字珠玑，
        以极简的文字承载了丰富的情感内涵，体现了叶渡创作的精妙之处。
      </p>
    </div>`;

  // 诗篇上下翻页
  renderPoemNav(poem.num);
}

function renderPoemNav(currentNum) {
  const keys = Object.keys(POEM_DATA).sort((a, b) => parseInt(a) - parseInt(b));
  const idx = keys.findIndex(k => parseInt(k) === currentNum);
  const prevKey = idx > 0 ? keys[idx - 1] : null;
  const nextKey = idx < keys.length - 1 ? keys[idx + 1] : null;
  const prev = prevKey ? POEM_DATA[prevKey] : null;
  const next = nextKey ? POEM_DATA[nextKey] : null;

  document.getElementById('poemNavBar').innerHTML = `
    <div class="poem-nav">
      <div>
        ${prev ? `<button class="nav-poem-btn" onclick="navigatePoem(${prev.num})">
          ← <span class="nav-poem-char">${escapeHtml(prev.char)}</span> 上一篇
        </button>` : '<div></div>'}
      </div>
      <button class="back-btn" onclick="goBack()" style="font-size:13px">回诗河</button>
      <div>
        ${next ? `<button class="nav-poem-btn" onclick="navigatePoem(${next.num})">
          下一篇 <span class="nav-poem-char">${escapeHtml(next.char)}</span> →
        </button>` : '<div></div>'}
      </div>
    </div>`;
}

function navigatePoem(num) {
  const key = String(num).padStart(2, '0');
  const poem = POEM_DATA[key] || POEM_DATA[String(num)];
  if (poem) {
    history.replaceState(null, '', `poem.html?id=${String(num).padStart(2,'0')}`);
    switchTab('text');
    window.scrollTo(0, 0);
    renderPoem(poem);
  }
}

// ===== 初始化 =====
function init() {
  const idParam = getUrlParam('id') || getUrlParam('num') || '01';
  const numInt = parseInt(idParam, 10);

  // 尝试多种key格式
  const poem = POEM_DATA[String(numInt).padStart(2, '0')]
            || POEM_DATA[String(numInt).padStart(3, '0')]
            || POEM_DATA[String(numInt)];

  if (poem) {
    renderPoem(poem);
  } else {
    document.getElementById('section-text').innerHTML = `
      <div class="error-box">
        <div class="error-char">🌿</div>
        <p>未找到编号 ${escapeHtml(idParam)} 的诗篇</p>
        <br>
        <button class="back-btn" onclick="goBack()">返回诗河</button>
      </div>`;
  }
}

init();
</script>
</body>
</html>'''

# 插入数据
html = html.replace('const POEM_DATA = __POEM_DATA__;', f'const POEM_DATA = {js_data};')

output_path = f'{DATA_DIR}/../poem.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

size = os.path.getsize(output_path)
print(f'poem.html 生成完毕：{size//1024} KB')
print(f'包含 {len(all_data)} 首诗歌的完整分析数据')
