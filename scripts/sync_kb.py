# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyyaml>=6.0.1",
# ]
# ///

"""
sync_kb.py: 从个人知识库 (Obsidian Vault) 自动同步文章与图片到 Fuwari (Astro) 博客站。
支持 Frontmatter 格式校验与转换、WikiLinks 解链、图片资源自动搬运与路径重写、增量更新及监听模式。
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import yaml


# 默认路径配置
DEFAULT_SOURCE_DIR = Path("/Users/ZHao/WorkSpace/knowledge-bank/raw/out-blogs")
DEFAULT_ASSETS_DIR = Path("/Users/ZHao/WorkSpace/knowledge-bank/assets")
DEFAULT_TARGET_POSTS_DIR = Path(__file__).resolve().parent.parent / "src" / "content" / "posts"
DEFAULT_TARGET_ASSETS_DIR = Path(__file__).resolve().parent.parent / "public" / "posts" / "assets"
DEFAULT_STATE_FILE = Path(__file__).resolve().parent.parent / ".sync_state.json"

# 预编译正则表达式常量
RE_FRONTMATTER = re.compile(r"^\s*---\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)(.*)", re.DOTALL)
RE_DATE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
RE_H1_FIRST = re.compile(r"^#\s+(.+)$", re.MULTILINE)
RE_H1_LINE = re.compile(r"^#\s+(.+)$")
RE_WIKI_IMAGE = re.compile(r"!\[\[([^|\]]+)(?:\|([^\]]+))?\]\]")
RE_MD_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
RE_WIKILINK = re.compile(r"\[\[([^|\]]+)(?:\|([^\]]+))?\]\]")


def compute_sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def load_state(state_file: Path) -> Dict[str, Any]:
    if state_file.exists():
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARN] 读取状态文件 {state_file} 失败: {e}，将使用空状态。")
    return {"version": 1, "files": {}}


def save_state(state_file: Path, state: Dict[str, Any]) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def parse_frontmatter_and_body(content: str) -> Tuple[Dict[str, Any], str]:
    """解析 Markdown 文件中的 YAML Frontmatter 和正文，支持前导空白行与增强匹配。"""
    match = RE_FRONTMATTER.match(content)
    if match:
        fm_text = match.group(1)
        body_text = match.group(2)
        try:
            fm_data = yaml.safe_load(fm_text) or {}
            if isinstance(fm_data, dict):
                return fm_data, body_text
        except Exception as e:
            print(f"[WARN] Frontmatter YAML 解析错误: {e}")
    return {}, content


def parse_date_obj(val: Any) -> date:
    """将日期转换为 datetime.date 对象，确保 PyYAML 输出为未加引号的标准 YAML 日期 (2026-07-08)。"""
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val
    if isinstance(val, str):
        match = RE_DATE.search(val)
        if match:
            y, m, d = int(match.group(1)), int(match.group(2)), int(match.group(3))
            return date(y, m, d)
    return date.today()


def sanitize_frontmatter(
    fm: Dict[str, Any],
    body: str,
    file_path: Path
) -> Tuple[Dict[str, Any], str]:
    """
    清洗并规范化 Frontmatter 以符合 Fuwari / Astro 的 Zod Schema:
    title: string
    published: date
    updated: date (optional)
    draft: boolean (default false)
    description: string (optional)
    image: string (optional)
    tags: string[] (optional)
    category: string (optional)
    lang: string (optional)
    """
    # 1. 提取 title
    title = fm.get("title")
    if not title:
        # 尝试从正文首行 # 提取
        h1_match = RE_H1_FIRST.search(body.strip())
        if h1_match:
            title = h1_match.group(1).strip()
        else:
            title = file_path.stem

    # 2. 提取 published
    raw_pub = fm.get("published") or fm.get("created")
    if raw_pub:
        published = parse_date_obj(raw_pub)
    else:
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        published = parse_date_obj(mtime)

    # 3. 提取 updated (optional)
    updated = None
    if "updated" in fm and fm["updated"]:
        updated = parse_date_obj(fm["updated"])

    # 4. 提取 draft
    draft = bool(fm.get("draft", False))

    # 5. 提取 description
    desc = fm.get("description", "")
    if desc is None:
        desc = ""
    description = str(desc).strip()

    # 6. 提取 tags
    raw_tags = fm.get("tags", [])
    tags: List[str] = []
    if isinstance(raw_tags, str):
        raw_tags = [raw_tags]
    if isinstance(raw_tags, list):
        for t in raw_tags:
            if t is not None:
                t_str = str(t).strip().lstrip("#")
                if t_str and t_str not in tags:
                    tags.append(t_str)

    # 7. 提取 category
    category = fm.get("category", "")
    if category is None:
        category = ""
    else:
        category = str(category).strip()

    # 8. 提取 image
    image = fm.get("image", "")
    if image is None:
        image = ""
    else:
        image = str(image).strip()

    # 9. 提取 lang
    lang = fm.get("lang", "")
    if lang is None:
        lang = ""
    else:
        lang = str(lang).strip()

    new_fm = {
        "title": str(title).strip(),
        "published": published,
        "description": description,
        "tags": tags,
        "category": category,
        "draft": draft,
    }
    if updated:
        new_fm["updated"] = updated
    if image:
        new_fm["image"] = image
    if lang:
        new_fm["lang"] = lang

    return new_fm, title


def find_and_copy_asset(
    asset_name: str,
    source_md_dir: Path,
    kb_assets_dir: Path,
    target_assets_dir: Path,
    dry_run: bool = False
) -> Optional[str]:
    """在知识库 assets 目录或源文件同级中查找资源文件，并复制到博客静态资源目录。包含路径遍历安全防御。"""
    allowed_roots = [
        kb_assets_dir.resolve(),
        source_md_dir.resolve(),
    ]

    # 候选位置
    candidates = [
        kb_assets_dir / asset_name,
        source_md_dir / asset_name,
        source_md_dir / "assets" / asset_name,
        source_md_dir / "attachments" / asset_name,
    ]
    # 处理带相对路径的情况
    if "/" in asset_name or "\\" in asset_name:
        candidates.insert(0, source_md_dir / Path(asset_name))

    found_src: Optional[Path] = None
    for cand in candidates:
        try:
            resolved_cand = cand.resolve()
        except Exception:
            continue

        # 安全防御：严格校验候选路径是否位于允许的根目录白名单内，防止 ../ 路径逃逸
        if not any(resolved_cand.is_relative_to(root) for root in allowed_roots):
            continue

        if resolved_cand.exists() and resolved_cand.is_file():
            found_src = resolved_cand
            break

    if found_src:
        dest_filename = found_src.name
        dest_path = target_assets_dir / dest_filename
        if not dry_run:
            target_assets_dir.mkdir(parents=True, exist_ok=True)
            if not dest_path.exists() or dest_path.stat().st_mtime < found_src.stat().st_mtime:
                shutil.copy2(found_src, dest_path)
                print(f"  [ASSET] 复制静态资源: {found_src.name} -> {dest_path}")
        return f"/posts/assets/{dest_filename}"
    else:
        print(f"  [WARN] 未找到引用的附件图片: {asset_name}")
        return None


def transform_body(
    body: str,
    title: str,
    source_md_path: Path,
    kb_assets_dir: Path,
    target_assets_dir: Path,
    dry_run: bool = False
) -> str:
    """转换正文内容：移除重复 H1、转换 WikiLinks、搬运并替换图片路径。"""
    lines = body.splitlines()

    # 1. 移除与文章 Title 相同的首部 H1（防止 Fuwari 页面重复显示两遍大标题）
    clean_lines = []
    skipped_h1 = False
    for line in lines:
        if not skipped_h1:
            if not line.strip():
                continue
            h1_match = RE_H1_LINE.match(line.strip())
            if h1_match:
                h1_text = h1_match.group(1).strip()
                # 若首部 H1 与 Frontmatter Title 一致或相近，则跳过
                if h1_text == title or title in h1_text or h1_text in title:
                    skipped_h1 = True
                    continue
            skipped_h1 = True
        clean_lines.append(line)

    text = "\n".join(clean_lines).strip()

    # 2. 处理 Obsidian 图片引用: ![[image.png]] 或 ![[image.png|alt text]]
    def replace_wiki_image(match: re.Match) -> str:
        raw_target = match.group(1).strip()
        alias = match.group(2).strip() if match.group(2) else ""
        new_url = find_and_copy_asset(raw_target, source_md_path.parent, kb_assets_dir, target_assets_dir, dry_run)
        alt = alias or Path(raw_target).name
        if new_url:
            return f"![{alt}]({new_url})"
        return f"![{alt}]({raw_target})"

    text = RE_WIKI_IMAGE.sub(replace_wiki_image, text)

    # 3. 处理标准 Markdown 图片: ![alt](../assets/img.png) 或 ![alt](img.png)
    def replace_md_image(match: re.Match) -> str:
        alt = match.group(1)
        url = match.group(2).strip()
        # 跳过网络链接或绝对路径
        if url.startswith(("http://", "https://", "/", "data:")):
            return match.group(0)
        # 本地相对路径
        new_url = find_and_copy_asset(url, source_md_path.parent, kb_assets_dir, target_assets_dir, dry_run)
        if new_url:
            return f"![{alt}]({new_url})"
        return match.group(0)

    text = RE_MD_IMAGE.sub(replace_md_image, text)

    # 4. 处理 WikiLinks: [[Target|Alias]] -> Alias, [[Target]] -> Target
    def replace_wikilink(match: re.Match) -> str:
        target = match.group(1).strip()
        alias = match.group(2).strip() if match.group(2) else ""
        return alias if alias else target

    text = RE_WIKILINK.sub(replace_wikilink, text)

    return text + "\n"


def sync_single_file(
    source_file: Path,
    target_posts_dir: Path,
    kb_assets_dir: Path,
    target_assets_dir: Path,
    state: Dict[str, Any],
    force: bool = False,
    dry_run: bool = False
) -> bool:
    """同步单个 Markdown 文件。返回是否有更新。"""
    try:
        raw_content = source_file.read_text(encoding="utf-8-sig")
    except Exception as e:
        print(f"[ERROR] 读取文件 {source_file} 失败: {e}")
        return False

    current_hash = compute_sha256(raw_content)
    rel_key = source_file.name
    file_state = state.get("files", {}).get(rel_key, {})

    if not force and file_state.get("source_sha256") == current_hash:
        # 无变动，跳过
        return False

    print(f"[SYNC] 正在处理: {source_file.name}")

    fm, raw_body = parse_frontmatter_and_body(raw_content)
    clean_fm, title = sanitize_frontmatter(fm, raw_body, source_file)
    clean_body = transform_body(
        body=raw_body,
        title=title,
        source_md_path=source_file,
        kb_assets_dir=kb_assets_dir,
        target_assets_dir=target_assets_dir,
        dry_run=dry_run
    )

    # 组装目标 Markdown 内容
    fm_yaml = yaml.dump(
        clean_fm,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False
    ).strip()
    target_content = f"---\n{fm_yaml}\n---\n\n{clean_body}"

    target_file = target_posts_dir / source_file.name

    if dry_run:
        print(f"  [DRY-RUN] 将写入: {target_file}")
        print(f"  [DRY-RUN] Frontmatter: {clean_fm}")
    else:
        target_posts_dir.mkdir(parents=True, exist_ok=True)
        target_file.write_text(target_content, encoding="utf-8")
        print(f"  [SUCCESS] 已同步至: {target_file}")

        # 更新状态
        state.setdefault("files", {})[rel_key] = {
            "source_path": str(source_file),
            "target_file": source_file.name,
            "source_sha256": current_hash,
            "last_synced_at": datetime.now().isoformat(),
        }

    return True


def run_sync(
    source_dir: Path,
    assets_dir: Path,
    target_posts_dir: Path,
    target_assets_dir: Path,
    state_file: Path,
    force: bool = False,
    dry_run: bool = False
) -> int:
    """执行同步流程，返回同步更新的文件数。"""
    if not source_dir.exists():
        print(f"[ERROR] 知识库源目录不存在: {source_dir}")
        return 0

    state = load_state(state_file)
    md_files = sorted(list(source_dir.glob("*.md")) + list(source_dir.glob("*.mdx")))

    if not md_files:
        print(f"[INFO] 知识库源目录中未发现 Markdown 文件: {source_dir}")
        return 0

    print(f"[INFO] 扫描到 {len(md_files)} 篇文章，开始增量同步检查...")
    updated_count = 0

    for md_file in md_files:
        updated = sync_single_file(
            source_file=md_file,
            target_posts_dir=target_posts_dir,
            kb_assets_dir=assets_dir,
            target_assets_dir=target_assets_dir,
            state=state,
            force=force,
            dry_run=dry_run
        )
        if updated:
            updated_count += 1

    if not dry_run and updated_count > 0:
        save_state(state_file, state)

    print(f"[DONE] 同步完成。共更新 {updated_count} / {len(md_files)} 篇文章。")
    return updated_count


def watch_and_sync(
    source_dir: Path,
    assets_dir: Path,
    target_posts_dir: Path,
    target_assets_dir: Path,
    state_file: Path,
    interval_seconds: float = 2.0
) -> None:
    """轮询监听模式：实时监听源目录变动并自动触发增量同步。"""
    print(f"[WATCH] 已启动监听模式，正在监控: {source_dir} (轮询间隔: {interval_seconds}s)")
    print("[WATCH] 按 Ctrl+C 退出监听。")

    # 首次执行一次全量增量检查
    run_sync(source_dir, assets_dir, target_posts_dir, target_assets_dir, state_file)

    try:
        while True:
            time.sleep(interval_seconds)
            run_sync(source_dir, assets_dir, target_posts_dir, target_assets_dir, state_file)
    except KeyboardInterrupt:
        print("\n[WATCH] 已停止监听。")


def main() -> None:
    parser = argparse.ArgumentParser(description="个人知识库 (Obsidian) -> Fuwari 博客站自动同步工具")
    parser.add_argument(
        "--source",
        type=Path,
        default=Path(os.getenv("KB_SOURCE_DIR", str(DEFAULT_SOURCE_DIR))),
        help=f"Obsidian 文章源目录 (默认: {DEFAULT_SOURCE_DIR})"
    )
    parser.add_argument(
        "--assets",
        type=Path,
        default=Path(os.getenv("KB_ASSETS_DIR", str(DEFAULT_ASSETS_DIR))),
        help=f"Obsidian 附件目录 (默认: {DEFAULT_ASSETS_DIR})"
    )
    parser.add_argument(
        "--target-posts",
        type=Path,
        default=DEFAULT_TARGET_POSTS_DIR,
        help=f"博客文章目标目录 (默认: {DEFAULT_TARGET_POSTS_DIR})"
    )
    parser.add_argument(
        "--target-assets",
        type=Path,
        default=DEFAULT_TARGET_ASSETS_DIR,
        help=f"博客附件目标目录 (默认: {DEFAULT_TARGET_ASSETS_DIR})"
    )
    parser.add_argument(
        "--state-file",
        type=Path,
        default=DEFAULT_STATE_FILE,
        help=f"同步状态记录文件 (默认: {DEFAULT_STATE_FILE})"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="强制重新同步所有文章（忽略 Hash 校验）"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="演练模式：仅打印转换结果，不写入目标文件"
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="启动实时监听模式，自动检测变动并同步"
    )

    raw_argv = [arg for arg in sys.argv[1:] if arg != "--"]
    args = parser.parse_args(raw_argv)

    if args.watch:
        watch_and_sync(
            source_dir=args.source,
            assets_dir=args.assets,
            target_posts_dir=args.target_posts,
            target_assets_dir=args.target_assets,
            state_file=args.state_file,
        )
    else:
        run_sync(
            source_dir=args.source,
            assets_dir=args.assets,
            target_posts_dir=args.target_posts,
            target_assets_dir=args.target_assets,
            state_file=args.state_file,
            force=args.force,
            dry_run=args.dry_run,
        )


if __name__ == "__main__":
    main()
