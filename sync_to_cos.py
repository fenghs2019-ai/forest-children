#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
森林诗网 → 腾讯云COS 增量同步脚本
功能：只上传 git 自上次同步以来有变动的文件
用法：python sync_to_cos.py
依赖：pip install cos-python-sdk-v5 python-dotenv
"""
import os
import sys
import json
import subprocess
from pathlib import Path

# ── 配置 ──────────────────────────────────────────────
# 请填入你的腾讯云密钥（建议写入同目录 .env 文件，勿提交到 Git）
SECRET_ID     = os.getenv('COS_SECRET_ID',     '填入你的 SecretId')
SECRET_KEY    = os.getenv('COS_SECRET_KEY',    '填入你的 SecretKey')
BUCKET        = os.getenv('COS_BUCKET',         'forestchildren2015-1327727959')
REGION        = os.getenv('COS_REGION',         'ap-beijing')

# 同步哪些目录（相对于仓库根目录）
SYNC_DIRS = ['.', 'output-*']

# 跳过这些文件/文件夹
SKIP_PATTERNS = ['.git', '.github', '.gitignore', '.env',
                 '__pycache__', '*.py', '*.md', '*.zip', 'node_modules']

# 状态文件（记录上次同步的 commit hash）
STATE_FILE = Path(__file__).parent / '.sync_state.json'

# ── 工具函数 ──────────────────────────────────────────
def log(msg, ok=True):
    print(f"{'✅' if ok else '⚠️'} {msg}")

def run(cmd, capture=True):
    return subprocess.run(cmd, shell=True, capture_output=capture,
                         text=True, encoding='utf-8')

def matches_skip(path, skip_list):
    """判断路径是否命中跳过规则"""
    name = os.path.basename(path)
    for p in skip_list:
        if p.startswith('*.'):
            if name.endswith(p[1:]):
                return True
        elif p in path:
            return True
    return False

def get_changed_files():
    """获取上次同步以来所有有变更的文件列表（来自 git）"""
    state_file = STATE_FILE
    if state_file.exists():
        last_commit = json.loads(state_file.read_text(encoding='utf-8')).get('commit', '')
    else:
        last_commit = 'HEAD~1'  # 第一次运行，与上一个 commit 比

    if last_commit == 'HEAD~1':
        # 第一次运行，改用 HEAD~1 作为基准（避免冲突）
        result = run(f'git log --oneline -2')
        commit_count = len(result.stdout.strip().splitlines())
        if commit_count < 2:
            last_commit = 'HEAD~0'  # 只有一个 commit，改用全部文件

    result = run(f'git diff --name-only {last_commit} HEAD')
    files = [f.strip() for f in result.stdout.splitlines() if f.strip()]

    # 也包含新文件（untracked）
    result2 = run('git ls-files --others --exclude-standard')
    untracked = [f.strip() for f in result2.stdout.splitlines() if f.strip()]
    files = list({f for f in files + untracked})

    return files

def upload_file(client, local_path, cos_key):
    """上传单个文件到 COS，自动识别 Content-Type"""
    ext = Path(cos_key).suffix.lower()
    TYPE_MAP = {
        '.html': 'text/html; charset=utf-8',
        '.css':  'text/css; charset=utf-8',
        '.js':   'application/javascript',
        '.json': 'application/json',
        '.png':  'image/png',
        '.jpg':  'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif':  'image/gif',
        '.svg':  'image/svg+xml',
        '.ico':  'image/x-icon',
        '.xml':  'application/xml',
        '.txt':  'text/plain; charset=utf-8',
        '.mp3':  'audio/mpeg',
        '.mp4':  'video/mp4',
    }
    ct = TYPE_MAP.get(ext, 'application/octet-stream')
    cos_key = cos_key.replace('\\', '/')

    try:
        with open(local_path, 'rb') as f:
            client.put_object(Bucket=BUCKET, Body=f, Key=cos_key, ContentType=ct)
        log(f"上传成功: {cos_key}")
        return True
    except Exception as e:
        log(f"上传失败: {cos_key} → {e}", ok=False)
        return False

# ── 主流程 ───────────────────────────────────────────
def main():
    # 1. 凭证检查
    if SECRET_ID == '填入你的 SecretId':
        print("❌ 请先配置 COS 密钥！")
        print("   方法一：在本脚本同目录创建 .env 文件，写入：")
        print("     COS_SECRET_ID=你的ID")
        print("     COS_SECRET_KEY=你的KEY")
        print("   方法二：直接修改脚本顶部的 SECRET_ID / SECRET_KEY 变量")
        sys.exit(1)

    # 2. 获取变更文件
    changed = get_changed_files()
    if not changed:
        log("没有检测到变更，跳过同步")
        sys.exit(0)

    changed = [f for f in changed if not matches_skip(f, SKIP_PATTERNS)]
    log(f"发现 {len(changed)} 个变更文件")

    # 3. 连接 COS
    try:
        from qcloud_cos import CosConfig, CosS3Client
        config = CosConfig(Region=REGION, SecretId=SECRET_ID, SecretKey=SECRET_KEY)
        client = CosS3Client(config)
        log("已连接到腾讯云 COS")
    except Exception as e:
        log(f"COS 连接失败: {e}", ok=False)
        sys.exit(1)

    # 4. 逐个上传
    success = 0
    failed = 0
    repo_root = Path(__file__).parent.resolve()

    for rel_path in changed:
        local = repo_root / rel_path
        if not local.is_file():
            continue

        ok = upload_file(client, str(local), rel_path)
        if ok:
            success += 1
        else:
            failed += 1

    # 5. 记录同步状态
    result = run('git rev-parse HEAD')
    current_commit = result.stdout.strip()
    STATE_FILE.write_text(json.dumps({'commit': current_commit}, ensure_ascii=False), encoding='utf-8')

    print(f"\n{'='*40}")
    log(f"同步完成！成功 {success} 个，失败 {failed} 个")
    log(f"当前 commit: {current_commit[:8]}")
    log(f"腾讯云地址: https://{BUCKET}.cos.{REGION}.myqcloud.com")
    if failed > 0:
        sys.exit(1)

if __name__ == '__main__':
    main()
