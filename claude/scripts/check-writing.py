#!/usr/bin/env python3
"""Check Markdown against the writing-guidelines skill, and writing-for-agents.

Usage:
    check-writing.py <path>...        # files, or directories searched for *.md

Findings print as `file:line - issue`, grouped by file, errors before warnings.
Exit status is 1 when any error is found, so a hook or CI step can gate on it.

Errors are rules with one right answer. Warnings are rules that need a human to
confirm, so they report and never gate.

Prose only: fenced code blocks, inline code spans, tables, and front matter are
kept out of the prose rules, since a command line holds straight quotes, three
dots, and hyphens on purpose. Fenced blocks get their own rules (language tag,
placeholders, length).
"""

import re
import sys
from dataclasses import dataclass
from pathlib import Path

BANNED = ["easy", "easily", "simple", "simply", "quick", "quickly", "very", "just", "really"]
WEASEL = ["significantly", "many", "often", "typically", "generally", "usually", "various", "several"]
GENERIC_HEADINGS = {"overview", "notes", "caveats", "details", "introduction", "summary", "usage", "misc", "other"}
NEGATIONS = ["never", "don't", "do not", "avoid", "no need to"]
LINK_FILLER = {"here", "link", "this", "this link", "click here"}

BE_VERBS = r"(?:is|are|was|were|be|been|being)"
PASSIVE = re.compile(rf"\b{BE_VERBS}\s+(\w{{2,}}ed|done|made|given|taken|written|held|read|kept|built|sent)\b", re.I)
# Words ending in -ed that follow a be-verb without forming a passive.
PASSIVE_ALLOW = {"based", "used", "aged", "need", "indeed", "embed", "hundred", "wicked", "naked"}

LIST_ITEM = re.compile(r"^[-*+]\s|^\d+\.\s")
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
BLOCK_START = re.compile(r"^([-*+#>|<]|\d+\.|```|~~~)")
FENCE_OPEN = re.compile(r"^(`{3,}|~{3,})(.*)$")
INLINE_CODE = re.compile(r"(`+)(.+?)\1")
BARE_UNIT = re.compile(r"\b(\d+(?:\.\d+)?)\s?([kmgt]b|ms)\b", re.I)
PLACEHOLDER = re.compile(r"<[A-Z][A-Z_-]*>|\bxxx+\b|\byour-[a-z-]+\b|\bABC123\b")
MD_LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)")
BARE_URL = re.compile(r"(?<![(<`])https?://\S+")
UNITS_CANONICAL = {"kb": "KB", "mb": "MB", "gb": "GB", "tb": "TB", "ms": "ms"}

MAX_SNIPPET_LINES = 25
MAX_SNIPPET_COLUMNS = 80
MAX_SENTENCE_WORDS = 30
MAX_PARAGRAPH_SENTENCES = 4


@dataclass
class Finding:
    line: int
    message: str
    level: str


@dataclass
class Fence:
    line: int
    info: str
    body: list


@dataclass
class Blocks:
    prose: list  # [(lineno, raw)]
    fences: list  # [Fence]
    table_cells: list  # [(lineno, stripped)]
    front_matter_end: int  # 0 when the file has no front matter
    unclosed_fence: int = 0  # line of a fence that never closes, 0 when all close


def split_blocks(text):
    """Sort each line of the file into prose, a fence, a table row, or front matter."""
    lines = text.split("\n")
    blocks = Blocks([], [], [], 0)
    fence = None
    fence_marker = ""
    in_front_matter = False

    for i, raw in enumerate(lines, start=1):
        stripped = raw.strip()

        if i == 1 and stripped == "---":
            in_front_matter = True
            continue
        if in_front_matter:
            if stripped == "---":
                in_front_matter = False
                blocks.front_matter_end = i
            continue

        if fence is None:
            opened = FENCE_OPEN.match(stripped)
            if opened:
                fence_marker = opened.group(1)
                fence = Fence(i, opened.group(2).strip(), [])
                blocks.fences.append(fence)
                continue
        else:
            close = re.match(r"^(`{3,}|~{3,})\s*$", stripped)
            if close and close.group(1)[0] == fence_marker[0] and len(close.group(1)) >= len(fence_marker):
                fence = None
            else:
                fence.body.append(raw)
            continue

        if stripped.startswith("|"):
            if not re.fullmatch(r"[|\s:-]+", stripped):
                blocks.table_cells.append((i, stripped))
            continue

        blocks.prose.append((i, raw))

    blocks.unclosed_fence = fence.line if fence is not None else 0
    return blocks


def strip_inline_code(line):
    return INLINE_CODE.sub(lambda m: "`" * len(m.group(0)), line)


def sentences(text):
    text = re.sub(r"\s+", " ", text).strip()
    return [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z(])", text) if s]


def check_typography(clean, err):
    """Rules with one right answer, on a line already stripped of inline code."""
    if "—" in clean or "–" in clean:
        err("em or en dash as punctuation; use a colon, a comma, or a period")
    if "..." in clean:
        err('"..." should be the ellipsis "…"')
    for match in BARE_UNIT.finditer(clean):
        number, unit = match.group(1), match.group(2)
        canonical = UNITS_CANONICAL[unit.lower()]
        if match.group(0) != f"{number} {canonical}":
            err(f'"{match.group(0)}" should be "{number} {canonical}"')
    if '"' in clean:
        err('straight double quotes; use curly quotes “ ”')


def check_fence(fence, err, warn):
    if not fence.info:
        err(fence.line, "code block missing language tag")
    if len(fence.body) > MAX_SNIPPET_LINES:
        warn(fence.line, f"code block of {len(fence.body)} lines; split past {MAX_SNIPPET_LINES} with prose between")
    for offset, raw in enumerate(fence.body, start=1):
        line = fence.line + offset
        if len(raw) > MAX_SNIPPET_COLUMNS:
            warn(line, f"code line of {len(raw)} columns; keep snippets within {MAX_SNIPPET_COLUMNS}")
        for match in PLACEHOLDER.finditer(raw):
            err(line, f'generic placeholder "{match.group(0)}"; use descriptive snake_case like your_access_token_here')


def check_links(clean, err, warn):
    for match in MD_LINK.finditer(clean):
        text = match.group(1).strip().lower()
        if text in LINK_FILLER:
            err(f'anchor text "{match.group(1)}"; name the destination')
        elif re.match(r"https?://", text):
            err(f"URL as anchor text; name the destination")
    if BARE_URL.search(clean):
        warn("bare URL; wrap it in a link whose text names the destination")


def check_file(path):
    text = path.read_text()
    lines = text.split("\n")
    blocks = split_blocks(text)
    out = []

    def err(line, msg):
        out.append(Finding(line, msg, "error"))

    def warn(line, msg):
        out.append(Finding(line, msg, "warning"))

    if blocks.unclosed_fence:
        err(blocks.unclosed_fence, "code block never closes")
    for fence in blocks.fences:
        check_fence(fence, err, warn)

    for line, cell in blocks.table_cells:
        check_typography(strip_inline_code(cell), lambda msg: err(line, msg))

    for line, raw in blocks.prose:
        clean = strip_inline_code(raw)
        stripped = clean.strip()
        if not stripped:
            continue

        check_typography(clean, lambda msg: err(line, msg))
        check_links(clean, lambda msg: err(line, msg), lambda msg: warn(line, msg))

        if re.fullmatch(r"-{3,}|\*{3,}|_{3,}", stripped):
            err(line, "horizontal rule between sections; use a heading")

        for word in BANNED:
            if re.search(rf"\b{re.escape(word)}\b", clean, re.I):
                err(line, f'banned word "{word}"')

        for word in WEASEL:
            if re.search(rf"\b{word}\b", clean, re.I):
                warn(line, f'weasel word "{word}"; give the number or the specific claim')

        heading = HEADING.match(stripped)
        if heading:
            title = heading.group(2).strip()
            words = re.findall(r"[A-Za-z][\w'-]*", title)
            if len(words) > 1:
                rest = [w for w in words[1:] if not re.fullmatch(r"[A-Z]{2,}s?", w)]
                capped = [w for w in rest if w[0].isupper() and not w.isupper()]
                if len(capped) >= 2 and len(capped) >= len(rest) / 2:
                    err(line, f'title case in heading "{title}"; use sentence case')
            if title.lower() in GENERIC_HEADINGS:
                warn(line, f'generic heading "{title}"; name what the section holds')
            continue

        if LIST_ITEM.match(stripped):
            continue

        if stripped.endswith("?"):
            warn(line, "rhetorical question")

        for phrase in NEGATIONS:
            if re.search(rf"(?<![\w-])({re.escape(phrase)})\b", clean, re.I):
                warn(line, f'negation "{phrase}"; state the target behaviour instead')
                break

        for match in PASSIVE.finditer(clean):
            if match.group(1).lower() in PASSIVE_ALLOW:
                continue
            warn(line, f'possible passive voice "{match.group(0)}"; name the actor')

        for sentence in sentences(clean):
            count = len(sentence.split())
            if count > MAX_SENTENCE_WORDS:
                warn(line, f"sentence of {count} words; the target is under 20")

    check_layout(lines, blocks, err, warn)
    return out


def check_layout(lines, blocks, err, warn):
    """Rules that read neighbouring lines: list intros, wrapping, blank lines, the opener."""
    prose_map = dict(blocks.prose)
    blank_run = 0
    first_heading = None
    opener_checked = False

    for idx, raw in enumerate(lines):
        line = idx + 1
        stripped = raw.strip()

        if not stripped:
            blank_run += 1
            if blank_run == 2 and line > blocks.front_matter_end + 1:
                err(line, "two blank lines in a row; one blank line separates blocks")
            continue
        blank_run = 0

        if LIST_ITEM.match(stripped):
            prev = lines[idx - 1].strip() if idx else ""
            if prev and not LIST_ITEM.match(prev) and not prev.endswith(":") and not prev.startswith("|"):
                err(line, "list introduced without a colon on the line above")

        if line not in prose_map:
            continue

        is_heading = bool(HEADING.match(stripped))
        if is_heading and idx and lines[idx - 1].strip():
            err(line, "heading without a blank line above it")

        if is_heading and first_heading is None:
            first_heading = line
            continue
        if first_heading is not None and not opener_checked:
            opener_checked = True
            if BLOCK_START.match(stripped):
                warn(line, "document opens without a summary paragraph after the title")

        plain = not BLOCK_START.match(stripped)
        if not plain:
            continue

        nxt = lines[idx + 1].strip() if idx + 1 < len(lines) else ""
        if nxt and not BLOCK_START.match(nxt) and (line + 1) in prose_map:
            err(line, "hard-wrapped paragraph; keep a paragraph on one source line")

        paragraph = sentences(strip_inline_code(stripped))
        if len(paragraph) > MAX_PARAGRAPH_SENTENCES:
            warn(line, f"paragraph of {len(paragraph)} sentences; split past {MAX_PARAGRAPH_SENTENCES}")


def collect(paths):
    files = []
    for arg in paths:
        p = Path(arg)
        if p.is_dir():
            files.extend(sorted(p.rglob("*.md")))
        elif p.is_file():
            files.append(p)
        else:
            print(f"no such path: {arg}", file=sys.stderr)
    return files


def main(argv):
    if not argv:
        print(__doc__)
        return 2

    files = collect(argv)
    errors = 0
    warnings = 0

    for path in files:
        findings = check_file(path)
        if not findings:
            print(f"\n## {path}\n\n✓ pass")
            continue
        findings.sort(key=lambda f: (f.level != "error", f.line))
        print(f"\n## {path}\n")
        for f in findings:
            mark = "" if f.level == "error" else "warn: "
            print(f"{path}:{f.line} - {mark}{f.message}")
            errors += f.level == "error"
            warnings += f.level == "warning"

    print(f"\n{errors} error(s), {warnings} warning(s), {len(files)} file(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
