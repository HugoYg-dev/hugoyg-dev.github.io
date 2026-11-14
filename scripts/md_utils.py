"""
md_utils.py: Markdown 代码块保护与链接/图片解析公共工具。
供 sync_kb.py 与 sync_cnblogs.py 复用，避免重复实现并消除正则回溯与嵌套边界缺陷。
"""

from bisect import bisect_left
from collections import defaultdict
import re
from typing import Callable, Dict, List, Optional, Tuple


_FENCE_OPEN_RE = re.compile(r"^[ ]{0,3}(`{3,}|~{3,})(.*)$")


def _is_fence_close(line: str, fence_char: str, fence_len: int) -> bool:
    stripped = line.rstrip("\r\n")
    idx = 0
    spaces = 0
    while idx < len(stripped) and stripped[idx] == " " and spaces < 3:
        idx += 1
        spaces += 1
    count = 0
    while idx < len(stripped) and stripped[idx] == fence_char:
        idx += 1
        count += 1
    if count < fence_len:
        return False
    while idx < len(stripped):
        if stripped[idx] not in (" ", "\t"):
            return False
        idx += 1
    return True


def _mask_inline_code_in_prose(text: str, add_token: Callable[[str], str]) -> str:
    """
    在非围栏正文文本中按 CommonMark 规则近线性扫描并屏蔽行内代码跨度 (`...` / ``...``)。
    预先索引各长度反引号序列位置并限制在当前段落内匹配，彻底消除回溯与多未闭合序列导致的二次方退化。
    """
    if "`" not in text:
        return text

    n = len(text)
    # 预索引反引号序列与段落空行边界
    runs_by_len: Dict[int, List[Tuple[int, int]]] = defaultdict(list)
    blank_positions: List[int] = [m.start() for m in re.finditer(r"\r?\n[ \t]*\r?\n", text)]

    idx = 0
    while idx < n:
        pos = text.find("`", idx)
        if pos == -1:
            break
        end = pos + 1
        while end < n and text[end] == "`":
            end += 1
        runs_by_len[end - pos].append((pos, end))
        idx = end

    out: List[str] = []
    i = 0
    while i < n:
        if text[i] != "`":
            next_tick = text.find("`", i)
            if next_tick == -1:
                out.append(text[i:])
                break
            out.append(text[i:next_tick])
            i = next_tick
            continue

        run_start = i
        while i < n and text[i] == "`":
            i += 1
        tick_len = i - run_start

        # 当前段落结束位置（下一个空行起点或文件末尾）
        b_idx = bisect_left(blank_positions, i)
        para_end = blank_positions[b_idx] if b_idx < len(blank_positions) else n

        candidates = runs_by_len[tick_len]
        c_idx = bisect_left(candidates, (i, 0))
        close_end: Optional[int] = None
        if c_idx < len(candidates) and candidates[c_idx][1] <= para_end:
            close_end = candidates[c_idx][1]

        if close_end is not None:
            out.append(add_token(text[run_start:close_end]))
            i = close_end
        else:
            out.append(text[run_start:i])

    return "".join(out)


def transform_outside_code(text: str, transform_fn: Callable[[str], str]) -> str:
    """
    先按 CommonMark 规则屏蔽围栏代码块（支持 3 个及以上反引号/波浪号与嵌套围栏）
    和行内代码跨度，再对剩余正文整体执行 transform_fn，最后无损还原代码片段。
    使用整体占位符而非分段切分，确保包含行内代码的链接标签（如 [`fn`](/posts/a/)）可被完整匹配。
    """
    if not text:
        return text

    # 选择正文里绝不会冲突的占位符前缀
    sentinel = "\x00MD_CODE_"
    while sentinel in text:
        sentinel = "\x00" + sentinel

    tokens: List[str] = []

    def add_token(raw: str) -> str:
        idx = len(tokens)
        tokens.append(raw)
        return f"{sentinel}{idx}\x00"

    lines = text.splitlines(keepends=True)
    masked_parts: List[str] = []
    prose_buf: List[str] = []

    in_fence = False
    fence_char = ""
    fence_len = 0
    fence_buf: List[str] = []

    def flush_prose() -> None:
        if prose_buf:
            masked_parts.append(_mask_inline_code_in_prose("".join(prose_buf), add_token))
            prose_buf.clear()

    for line in lines:
        if not in_fence:
            m = _FENCE_OPEN_RE.match(line.rstrip("\r\n"))
            if m:
                marker = m.group(1)
                info = m.group(2)
                # CommonMark: 反引号围栏的 info string 中不能包含反引号
                if marker[0] == "~" or "`" not in info:
                    flush_prose()
                    in_fence = True
                    fence_char = marker[0]
                    fence_len = len(marker)
                    fence_buf = [line]
                    continue
            prose_buf.append(line)
        else:
            fence_buf.append(line)
            if _is_fence_close(line, fence_char, fence_len):
                masked_parts.append(add_token("".join(fence_buf)))
                in_fence = False
                fence_char = ""
                fence_len = 0
                fence_buf = []

    if in_fence and fence_buf:
        masked_parts.append(add_token("".join(fence_buf)))
    else:
        flush_prose()

    masked_text = "".join(masked_parts)
    transformed = transform_fn(masked_text)

    if not tokens:
        return transformed

    token_re = re.compile(re.escape(sentinel) + r"(\d+)\x00")
    return token_re.sub(lambda m: tokens[int(m.group(1))], transformed)


def _find_matching_bracket(text: str, open_idx: int) -> int:
    """从 '[' 位置出发，查找配对的 ']'（支持嵌套方括号与反斜杠转义），未找到返回 -1。"""
    depth = 0
    i = open_idx
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "\\":
            i += 2
            continue
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return i
        elif ch == "\n" and i + 1 < n and text[i + 1] == "\n":
            return -1
        i += 1
    return -1


def _find_matching_paren(text: str, open_idx: int) -> int:
    """从 '(' 位置出发，查找配对的 ')'（支持 URL 中的平衡括号与尖括号目的地），未找到返回 -1。"""
    i = open_idx + 1
    n = len(text)
    depth = 1
    in_angle = False
    quote_char: Optional[str] = None

    while i < n:
        ch = text[i]
        if ch == "\\":
            i += 2
            continue
        if quote_char is not None:
            if ch == quote_char:
                quote_char = None
        elif in_angle:
            if ch == ">":
                in_angle = False
            elif ch == "\n":
                return -1
        else:
            if ch == "<" and i == open_idx + 1:
                in_angle = True
            elif ch in ('"', "'"):
                quote_char = ch
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    return i
            elif ch == "\n" and i + 1 < n and text[i + 1] == "\n":
                return -1
        i += 1
    return -1


def _split_link_destination(raw_inner: str) -> Tuple[str, str, bool]:
    """
    拆分 Markdown 链接括号内的 (url, rest_after_url, is_angle_wrapped)。
    例如 '/posts/foo_(v2)/ "title"' -> ('/posts/foo_(v2)/', ' "title"', False)
    """
    stripped_leading = raw_inner.lstrip()
    leading_ws = raw_inner[: len(raw_inner) - len(stripped_leading)]
    if stripped_leading.startswith("<"):
        end_angle = stripped_leading.find(">")
        if end_angle != -1:
            url = stripped_leading[1:end_angle]
            rest = stripped_leading[end_angle + 1 :]
            return url, rest, True

    # 非尖括号目的地：URL 到第一个空白符为止
    for idx, ch in enumerate(stripped_leading):
        if ch in (" ", "\t", "\r", "\n"):
            return leading_ws + stripped_leading[:idx], stripped_leading[idx:], False
    return raw_inner, "", False


def replace_markdown_images(text: str, replacer: Callable[[str, str], Optional[str]]) -> str:
    """
    替换标准 Markdown 图片 ![alt](url [title])，支持 URL 内嵌平衡括号及保留可选 title。
    replacer(alt, url) 返回新 url（替换目的地）或 None（保持原文不动）。
    """
    out: List[str] = []
    i = 0
    n = len(text)

    while i < n:
        pos = text.find("![", i)
        if pos == -1:
            out.append(text[i:])
            break
        # 检查前置反斜杠是否被转义
        bs = 0
        j = pos - 1
        while j >= 0 and text[j] == "\\":
            bs += 1
            j -= 1
        if bs % 2 == 1:
            out.append(text[i : pos + 2])
            i = pos + 2
            continue

        close_bracket = _find_matching_bracket(text, pos + 1)
        if close_bracket == -1 or close_bracket + 1 >= n or text[close_bracket + 1] != "(":
            out.append(text[i : pos + 2])
            i = pos + 2
            continue

        close_paren = _find_matching_paren(text, close_bracket + 1)
        if close_paren == -1:
            out.append(text[i : pos + 2])
            i = pos + 2
            continue

        alt = text[pos + 2 : close_bracket]
        raw_inner = text[close_bracket + 2 : close_paren]
        raw_url, rest, is_angle = _split_link_destination(raw_inner)
        clean_url = raw_url.strip()

        new_url = replacer(alt, clean_url)
        out.append(text[i:pos])
        if new_url is None:
            out.append(text[pos : close_paren + 1])
        else:
            dest = f"<{new_url}>" if is_angle else new_url
            out.append(f"![{alt}]({dest}{rest})")
        i = close_paren + 1

    return "".join(out)


def replace_markdown_links(text: str, replacer: Callable[[str, str], Optional[str]]) -> str:
    """
    替换标准 Markdown 超链接 [label](url [title])（排除图片 ![...](...)），
    支持 label 内嵌方括号（如 [![alt](/img.png)](/posts/foo/)）以及 URL 内嵌平衡括号（如 /posts/foo_(v2)/）。
    replacer(label, url) 返回新 url（替换目的地）或 None（保持原文不动）。
    """
    out: List[str] = []
    i = 0
    n = len(text)

    while i < n:
        pos = text.find("[", i)
        if pos == -1:
            out.append(text[i:])
            break

        # 跳过图片起始符 '![' 以及被反斜杠转义的 '\['
        if pos > 0 and text[pos - 1] == "!":
            bs = 0
            j = pos - 2
            while j >= 0 and text[j] == "\\":
                bs += 1
                j -= 1
            if bs % 2 == 0:
                out.append(text[i : pos + 1])
                i = pos + 1
                continue
        else:
            bs = 0
            j = pos - 1
            while j >= 0 and text[j] == "\\":
                bs += 1
                j -= 1
            if bs % 2 == 1:
                out.append(text[i : pos + 1])
                i = pos + 1
                continue

        close_bracket = _find_matching_bracket(text, pos)
        if close_bracket == -1 or close_bracket + 1 >= n or text[close_bracket + 1] != "(":
            out.append(text[i : pos + 1])
            i = pos + 1
            continue

        close_paren = _find_matching_paren(text, close_bracket + 1)
        if close_paren == -1:
            out.append(text[i : pos + 1])
            i = pos + 1
            continue

        label = text[pos + 1 : close_bracket]
        raw_inner = text[close_bracket + 2 : close_paren]
        raw_url, rest, is_angle = _split_link_destination(raw_inner)
        clean_url = raw_url.strip()

        new_url = replacer(label, clean_url)
        out.append(text[i:pos])
        if new_url is None:
            out.append(text[pos : close_paren + 1])
        else:
            dest = f"<{new_url}>" if is_angle else new_url
            out.append(f"[{label}]({dest}{rest})")
        i = close_paren + 1

    return "".join(out)
