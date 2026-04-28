# poem.html 版本记录

## v20260426_0651（当前版本）

**日期**：2026-04-26 06:51
**文件**：
- `platform/poem.html`（当前使用）
- `platform/poem_v20260426_0651_backup.html`（备份）
- `platform/data/build_poem_html.py`
- `platform/data/build_poem_html_v20260426_0651.py`（备份）

### 功能清单

| 功能 | 状态 |
|------|------|
| 原文展示（跳过标题行） | ✅ |
| 配图 Tab（`output-{char}/image.jpg`） | ✅ |
| 配乐 Tab（`output-{char}/audio.mp3`） | ✅ |
| 概述 | ✅ |
| 文化背景 | ✅ |
| 人物 | ✅ |
| 时间线 | ✅ |
| 价值观 | ✅ |
| 章节拆解 | ✅ |
| 文学手法 | ✅ |
| 上下翻页导航 | ✅ |
| 响应式（手机适配） | ✅ |

### 配图样式
- 显示完整图片，不裁剪
- 最大高度 60vh，保持比例缩放
- `object-fit: contain`

---

## 版本说明

### 命名规则
- `poem_v{日期}_{时间}_backup.html` - HTML 备份
- `build_poem_html_v{日期}_{时间}.py` - 生成脚本备份

### 恢复方法
如需回滚到某版本：
1. 找到对应备份文件
2. 复制覆盖 `poem.html`
3. 或用对应版本的 `build_poem_html.py` 重新生成
