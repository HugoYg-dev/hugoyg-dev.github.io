# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyyaml>=6.0.1",
#     "python-dotenv>=1.0.0",
# ]
# ///

"""
sync_cnblogs.py: 将博客文章自动化分发与增量同步至博客园 (cnblogs.com)。
基于标准 MetaWeblog XML-RPC 协议，支持图片自动上传图床、增量更新检测、草稿过滤与同步状态持久化。
"""

import argparse
import functools
import hashlib
import json
import mimetypes
import os
import re
import sys
import time
import xmlrpc.client
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
import yaml
from dotenv import load_dotenv


BLOG_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_POSTS_DIR = BLOG_ROOT / "src" / "content" / "posts"
DEFAULT_PUBLIC_DIR = BLOG_ROOT / "public"
DEFAULT_SYNC_STATE_FILE = BLOG_ROOT / ".cnblogs_sync.json"
KB_ASSETS_DIR = Path("/Users/ZHao/WorkSpace/knowledge-bank/assets")

# 预编译正则表达式常量
RE_FRONTMATTER = re.compile(r"^\s*---\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)(.*)", re.DOTALL)
RE_MD_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")


def retry_rpc(
    max_retries: int = 3,
    delay: float = 2.0,
    backoff: float = 2.0,
    exceptions: Tuple[type, ...] = (Exception,)
):
    """XML-RPC 网络请求重试装饰器，支持指数退避与重试日志记录。"""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        print(f"  [RPC RETRY] 接口 {func.__name__} 调用异常: {e}，正在进行第 {attempt}/{max_retries} 次重试 ({current_delay:.1f}s 后)...")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        print(f"  [RPC ERROR] 接口 {func.__name__} 达到最大重试次数 ({max_retries}): {e}")
            raise last_exception
        return wrapper
    return decorator


def compute_sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def compute_file_sha256(file_path: Path) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def load_sync_state(state_file: Path) -> Dict[str, Any]:
    if state_file.exists():
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARN] 读取博客园同步状态文件 {state_file} 失败: {e}")
    return {"version": 1, "posts": {}, "media": {}}


def save_sync_state(state_file: Path, state: Dict[str, Any]) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def parse_post(file_path: Path) -> Tuple[Dict[str, Any], str]:
    """解析博客文章的 Frontmatter 和正文，支持 UTF-8 BOM 及增强正则匹配。"""
    try:
        content = file_path.read_text(encoding="utf-8-sig")
    except Exception as e:
        print(f"[ERROR] 读取文章 {file_path.name} 失败: {e}")
        return {}, ""

    match = RE_FRONTMATTER.match(content)
    if match:
        fm_text = match.group(1)
        body_text = match.group(2)
        try:
            fm = yaml.safe_load(fm_text) or {}
            if isinstance(fm, dict):
                return fm, body_text.strip()
        except Exception as e:
            print(f"[WARN] Frontmatter 解析错误 ({file_path.name}): {e}")
    return {}, content.strip()


class CnblogsClient:
    def __init__(self, blog_id: str, username: str, api_key: str, endpoint: Optional[str] = None):
        self.blog_id = blog_id
        self.username = username
        self.api_key = api_key
        self.endpoint = endpoint or f"https://rpc.cnblogs.com/metaweblog/{blog_id}"
        self.server = xmlrpc.client.ServerProxy(self.endpoint)

    @retry_rpc(max_retries=3, delay=2.0, backoff=2.0)
    def _get_users_blogs_rpc(self) -> Any:
        return self.server.blogger.getUsersBlogs("", self.username, self.api_key)

    @retry_rpc(max_retries=3, delay=2.0, backoff=2.0)
    def _new_media_object_rpc(self, media_object: Dict[str, Any]) -> Any:
        return self.server.metaWeblog.newMediaObject(self.blog_id, self.username, self.api_key, media_object)

    @retry_rpc(max_retries=3, delay=2.0, backoff=2.0)
    def _edit_post_rpc(self, post_id: str, post_struct: Dict[str, Any], publish_flag: bool) -> Any:
        return self.server.metaWeblog.editPost(
            post_id,
            self.username,
            self.api_key,
            post_struct,
            publish_flag
        )

    @retry_rpc(max_retries=3, delay=2.0, backoff=2.0)
    def _new_post_rpc(self, post_struct: Dict[str, Any], publish_flag: bool) -> Any:
        return self.server.metaWeblog.newPost(
            self.blog_id,
            self.username,
            self.api_key,
            post_struct,
            publish_flag
        )

    def test_connection(self) -> bool:
        """测试 MetaWeblog 连接与身份验证（支持自动重试）。"""
        try:
            blogs = self._get_users_blogs_rpc()
            if blogs:
                print(f"[AUTH] 博客园身份验证成功！空间名称: {blogs[0].get('blogName')} ({blogs[0].get('url')})")
                return True
            print("[AUTH] 验证通过，但未找到对应的博客空间。")
            return True
        except Exception as e:
            print(f"[AUTH ERROR] 博客园身份验证失败: {e}")
            return False

    def upload_media(self, image_path: Path) -> Optional[str]:
        """上传本地图片到博客园图床（支持自动重试）。"""
        if not image_path.exists():
            print(f"[WARN] 图片文件不存在: {image_path}")
            return None

        mime_type, _ = mimetypes.guess_type(str(image_path))
        mime_type = mime_type or "image/png"

        try:
            with open(image_path, "rb") as f:
                media_bytes = f.read()

            media_object = {
                "name": image_path.name,
                "type": mime_type,
                "bits": xmlrpc.client.Binary(media_bytes),
            }
            res = self._new_media_object_rpc(media_object)
            if isinstance(res, dict) and "url" in res:
                print(f"  [MEDIA] 图片上传成功: {image_path.name} -> {res['url']}")
                return res["url"]
            print(f"  [MEDIA ERROR] 上传响应异常: {res}")
            return None
        except Exception as e:
            print(f"  [MEDIA ERROR] 上传图片 {image_path.name} 失败: {e}")
            return None

    def publish_post(
        self,
        title: str,
        body: str,
        categories: List[str],
        tags: List[str],
        post_id: Optional[str] = None,
        is_draft: bool = False
    ) -> Optional[str]:
        """发布新文章或更新已有文章（支持自动重试）。"""
        # 博客园支持通过在分类中包含 [Markdown] 来指示 Markdown 解析
        all_categories = list(categories)
        if "[Markdown]" not in all_categories:
            all_categories.append("[Markdown]")

        post_struct = {
            "title": title,
            "description": body,
            "categories": all_categories,
            "mt_keywords": ",".join(tags) if tags else "",
        }

        publish_flag = not is_draft

        try:
            if post_id:
                # 更新已有博文
                success = self._edit_post_rpc(post_id, post_struct, publish_flag)
                if success:
                    print(f"  [UPDATE SUCCESS] 已成功更新博客园文章 (PostID: {post_id})")
                    return post_id
                else:
                    print(f"  [UPDATE ERROR] 更新失败 (PostID: {post_id})")
                    return None
            else:
                # 发布新博文
                new_id = self._new_post_rpc(post_struct, publish_flag)
                print(f"  [PUBLISH SUCCESS] 已成功发布新文章至博客园 (PostID: {new_id})")
                return str(new_id)
        except Exception as e:
            print(f"  [API ERROR] 发布/更新博客园文章失败: {e}")
            return None


def resolve_local_image_path(src_url: str, post_file: Path) -> Optional[Path]:
    """
    解析 Markdown 中的图片路径对应的本地文件系统绝对路径。
    包含路径遍历安全防御：严格校验候选路径是否在允许的白名单目录内。
    """
    if src_url.startswith(("http://", "https://", "data:")):
        return None

    clean_src = src_url.lstrip("/")
    candidates = [
        DEFAULT_PUBLIC_DIR / clean_src,
        DEFAULT_PUBLIC_DIR / "posts" / "assets" / Path(src_url).name,
        post_file.parent / src_url,
        KB_ASSETS_DIR / Path(src_url).name,
    ]

    allowed_roots = [
        DEFAULT_PUBLIC_DIR.resolve(),
        post_file.parent.resolve(),
        KB_ASSETS_DIR.resolve(),
        DEFAULT_POSTS_DIR.resolve(),
    ]

    for cand in candidates:
        try:
            resolved_cand = cand.resolve()
        except Exception:
            continue

        # 安全防御：确保路径在允许的根目录白名单内，防止 ../ 等路径逃逸
        if not any(resolved_cand.is_relative_to(root) for root in allowed_roots):
            continue

        if resolved_cand.exists() and resolved_cand.is_file():
            return resolved_cand
    return None


def process_and_upload_images(
    body: str,
    post_file: Path,
    client: Optional[CnblogsClient],
    state: Dict[str, Any],
    dry_run: bool = False
) -> str:
    """提取文章中的本地图片，上传至博客园图床并替换正文中的链接。"""
    media_cache = state.setdefault("media", {})

    def replace_image(match: re.Match) -> str:
        alt = match.group(1)
        url = match.group(2).strip()

        local_img = resolve_local_image_path(url, post_file)
        if not local_img:
            return match.group(0)

        # 计算图片哈希以使用图床缓存
        img_hash = compute_file_sha256(local_img)
        if img_hash in media_cache:
            remote_url = media_cache[img_hash]
            return f"![{alt}]({remote_url})"

        if dry_run or client is None:
            print(f"  [DRY-RUN MEDIA] 将上传本地图片: {local_img.name}")
            return match.group(0)

        remote_url = client.upload_media(local_img)
        if remote_url:
            media_cache[img_hash] = remote_url
            return f"![{alt}]({remote_url})"

        return match.group(0)

    # 替换 Markdown 图片语法
    return RE_MD_IMAGE.sub(replace_image, body)


def sync_single_post(
    post_file: Path,
    client: Optional[CnblogsClient],
    state: Dict[str, Any],
    force: bool = False,
    dry_run: bool = False,
    include_draft: bool = False
) -> bool:
    """同步单篇博客文章到博客园。"""
    fm, body = parse_post(post_file)
    title = fm.get("title") or post_file.stem
    draft = bool(fm.get("draft", False))

    if draft and not include_draft:
        print(f"[SKIP DRAFT] 跳过草稿文章: {post_file.name}")
        return False

    # 计算文章内容哈希（包含 Frontmatter 和正文）
    try:
        raw_content = post_file.read_text(encoding="utf-8-sig")
    except Exception as e:
        print(f"[ERROR] 读取文件 {post_file} 失败: {e}")
        return False

    content_hash = compute_sha256(raw_content)

    post_record = state.setdefault("posts", {}).get(post_file.name, {})
    existing_post_id = post_record.get("cnblogs_post_id")

    if not force and existing_post_id and post_record.get("content_sha256") == content_hash:
        # 内容未变动且已同步
        return False

    action = "更新" if existing_post_id else "发布"
    print(f"[SYNC CNBLOGS] 准备{action}: {post_file.name} -> 《{title}》 (PostID: {existing_post_id or '新文章'})")

    # 处理图片转存
    processed_body = process_and_upload_images(
        body=body,
        post_file=post_file,
        client=client,
        state=state,
        dry_run=dry_run
    )

    tags = fm.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]
    tags = [str(t).strip() for t in tags if t]

    categories = []
    cat = fm.get("category")
    if cat:
        categories.append(str(cat).strip())

    if dry_run or client is None:
        print(f"  [DRY-RUN] 将{action}文章:")
        print(f"    - Title: {title}")
        print(f"    - Categories: {categories}")
        print(f"    - Tags: {tags}")
        print(f"    - PostID: {existing_post_id or '(待新建)'}")
        return True

    res_post_id = client.publish_post(
        title=title,
        body=processed_body,
        categories=categories,
        tags=tags,
        post_id=existing_post_id,
        is_draft=draft
    )

    if res_post_id:
        state["posts"][post_file.name] = {
            "cnblogs_post_id": res_post_id,
            "title": title,
            "content_sha256": content_hash,
            "last_synced_at": datetime.now().isoformat(),
            "is_draft": draft,
        }
        return True

    return False


def run_sync(
    posts_dir: Path,
    client: Optional[CnblogsClient],
    state_file: Path,
    target_filename: Optional[str] = None,
    force: bool = False,
    dry_run: bool = False,
    include_draft: bool = False
) -> int:
    """扫描并同步所有文章至博客园。"""
    state = load_sync_state(state_file)

    if target_filename:
        target_file = posts_dir / target_filename
        if not target_file.exists():
            print(f"[ERROR] 指定的文章不存在: {target_file}")
            return 0
        files = [target_file]
    else:
        files = sorted(list(posts_dir.glob("*.md")) + list(posts_dir.glob("*.mdx")))

    if not files:
        print(f"[INFO] 未找到待同步的博客文章: {posts_dir}")
        return 0

    print(f"[INFO] 扫描到 {len(files)} 篇博客文章，检查博客园同步状态...")
    updated_count = 0

    for pf in files:
        ok = sync_single_post(
            post_file=pf,
            client=client,
            state=state,
            force=force,
            dry_run=dry_run,
            include_draft=include_draft
        )
        if ok:
            updated_count += 1

    if not dry_run and updated_count > 0:
        save_sync_state(state_file, state)

    print(f"[DONE] 博客园同步完成。共同步/更新 {updated_count} / {len(files)} 篇文章。")
    return updated_count


def show_status(posts_dir: Path, state_file: Path) -> None:
    """显示当前本地文章与博客园的同步映射状态。"""
    state = load_sync_state(state_file)
    posts = state.get("posts", {})
    files = sorted(list(posts_dir.glob("*.md")) + list(posts_dir.glob("*.mdx")))

    print("\n================== 博客园文章同步状态 ==================")
    print(f"{'文件名':<35} | {'博客园 PostID':<15} | {'最后同步时间'}")
    print("-" * 75)
    for f in files:
        rec = posts.get(f.name)
        if rec:
            post_id = rec.get("cnblogs_post_id", "未知")
            synced_at = rec.get("last_synced_at", "未知")[:19]
            print(f"{f.name:<35} | {post_id:<15} | {synced_at}")
        else:
            print(f"{f.name:<35} | {'[未同步]':<15} | -")
    print("========================================================\n")


def main() -> None:
    # 尝试加载环境变量与 .env
    load_dotenv(dotenv_path=BLOG_ROOT / ".env")
    load_dotenv(dotenv_path=BLOG_ROOT / ".env.local")

    parser = argparse.ArgumentParser(description="博客文章 -> 博客园 (Cnblogs) MetaWeblog 自动同步工具")
    parser.add_argument("--file", type=str, help="仅同步指定的文件名 (如 hello-world.md)")
    parser.add_argument("--force", action="store_true", help="强制重新同步/更新（忽略 Hash 校验）")
    parser.add_argument("--dry-run", action="store_true", help="演练模式：预览待同步内容，不真正调用 API 发帖")
    parser.add_argument("--include-draft", action="store_true", help="包含 draft: true 的草稿文章")
    parser.add_argument("--status", action="store_true", help="查看所有文章的博客园同步映射状态")
    parser.add_argument("--test-auth", action="store_true", help="测试博客园 API 凭证与连接状态")

    raw_argv = [arg for arg in sys.argv[1:] if arg != "--"]
    args = parser.parse_args(raw_argv)

    if args.status:
        show_status(DEFAULT_POSTS_DIR, DEFAULT_SYNC_STATE_FILE)
        return

    blog_id = os.getenv("CNBLOGS_BLOG_ID")
    username = os.getenv("CNBLOGS_USERNAME")
    api_key = os.getenv("CNBLOGS_API_KEY") or os.getenv("CNBLOGS_PASSWORD")
    endpoint = os.getenv("CNBLOGS_ENDPOINT")

    if args.dry_run:
        print("[INFO] 演练模式 (dry-run)，将跳过实际网络发帖。")
        run_sync(
            posts_dir=DEFAULT_POSTS_DIR,
            client=None,
            state_file=DEFAULT_SYNC_STATE_FILE,
            target_filename=args.file,
            force=args.force,
            dry_run=True,
            include_draft=args.include_draft
        )
        return

    if not blog_id or not username or not api_key:
        print("[ERROR] 缺少博客园 API 凭证配置！")
        print("请在 .env 文件中设置以下环境变量：")
        print("  - CNBLOGS_BLOG_ID  (如: hugoyang)")
        print("  - CNBLOGS_USERNAME (如: hugoyang)")
        print("  - CNBLOGS_API_KEY  (博客园后台 MetaWeblog 访问令牌)")
        print("\n提示：您可以参考 .env.example 进行配置。")
        print("或者添加 --dry-run 参数进行免凭证本地演练预览。")
        sys.exit(1)

    client = CnblogsClient(
        blog_id=blog_id,
        username=username,
        api_key=api_key,
        endpoint=endpoint
    )

    if args.test_auth:
        ok = client.test_connection()
        sys.exit(0 if ok else 1)

    run_sync(
        posts_dir=DEFAULT_POSTS_DIR,
        client=client,
        state_file=DEFAULT_SYNC_STATE_FILE,
        target_filename=args.file,
        force=args.force,
        dry_run=False,
        include_draft=args.include_draft
    )


if __name__ == "__main__":
    main()
