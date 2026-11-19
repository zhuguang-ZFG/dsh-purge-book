#!/usr/bin/env python3
"""成书产物验收：Mermaid 必须渲染为图，不得作为源码印进 PDF/EPUB。"""
from pathlib import Path
import re
import sys
import zipfile

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "dist" / "chaizha.pdf"
EPUB = ROOT / "dist" / "chaizha.epub"
TOKENS = ("flowchart", "sequenceDiagram", "stateDiagram-v2", "participant", "subgraph")

failures = []


def check(ok, message):
    print(("PASS " if ok else "FAIL ") + message)
    if not ok:
        failures.append(message)


blocks = sum(
    len(re.findall(r"^```mermaid\s*$", f.read_text(encoding="utf-8"), re.M))
    for f in sorted(ROOT.glob("[0-7]*.md"))
)
check(blocks == 8, f"源中 Mermaid 图块为 8（实际 {blocks}）")

plates = sorted((ROOT / "illustrations").glob("*.svg"))
check(len(plates) == 9, f"手绘插图源文件为 9（实际 {len(plates)}）")

reader = PdfReader(PDF)
pdf_text = "\n".join(page.extract_text() or "" for page in reader.pages)
for token in TOKENS:
    check(token not in pdf_text, f"PDF 无 Mermaid 源码字面量 {token!r}")
check("\\|" not in pdf_text, "PDF 无表格转义残留 \\|")
check(len(reader.pages) >= 40, f"PDF 页数 >= 40（实际 {len(reader.pages)}）")

with zipfile.ZipFile(EPUB) as archive:
    names = archive.namelist()
    svg = [n for n in names if n.lower().endswith(".svg")]
    expected_svg = blocks + 9  # 8 Mermaid + 9 手绘板（卷首 + ch00–ch07）
    check(len(svg) >= expected_svg, f"EPUB 内嵌 SVG >= {expected_svg}（实际 {len(svg)}）")
    chapters = [n for n in names if re.match(r"EPUB/text/ch\d+\.xhtml$", n)]
    check(len(chapters) == 11, f"EPUB 章节文档为 11（实际 {len(chapters)}）")
    xhtml = "".join(
        archive.read(n).decode("utf-8", "replace") for n in names if n.endswith(".xhtml")
    )
    check("sourceCode mermaid" not in xhtml, "EPUB 无未渲染的 mermaid 代码块")
    check("\\|" not in xhtml, "EPUB 无表格转义残留 \\|")

    opf_name = next(n for n in names if n.endswith(".opf"))
    opf = archive.read(opf_name).decode("utf-8", "replace")
    metadata = (ROOT / "build" / "metadata.yaml").read_text(encoding="utf-8")
    author_match = re.search(r'^author:\s*"([^"]*)"', metadata, re.M)
    author = author_match.group(1).strip() if author_match else ""
    check(bool(author), "build/metadata.yaml 含作者署名")
    creator = re.search(r"<dc:creator[^>]*>(.*?)</dc:creator>", opf)
    creator_name = creator.group(1).strip() if creator else ""
    check(bool(creator_name), "EPUB dc:creator 非空")
    check(creator_name == author, f"EPUB 作者与 metadata.yaml 一致（{creator_name!r} / {author!r}）")

    cover_meta = re.search(r'<meta[^>]*name="cover"[^>]*>', opf)
    cover_id = re.search(r'content="([^"]+)"', cover_meta.group(0)) if cover_meta else None
    check(bool(cover_id), "EPUB 含 cover 元数据")
    cover_tag = ""
    if cover_id:
        cover_tag = next(
            (tag for tag in re.findall(r"<item\b[^>]*/>", opf) if f'id="{cover_id.group(1)}"' in tag),
            "",
        )
    check(bool(cover_tag), "cover 元数据指向清单条目")
    check('properties="cover-image"' in cover_tag, "封面条目声明 cover-image")
    href_match = re.search(r'href="([^"]+)"', cover_tag)
    cover_href = href_match.group(1) if href_match else ""
    check(cover_href.lower().endswith((".png", ".jpg", ".jpeg", ".gif")), f"封面为位图（{cover_href or '缺失'}）")
    cover_path = f"EPUB/{cover_href}"
    check(bool(cover_href) and cover_path in names, "封面文件存在于 EPUB")
    if cover_href and cover_path in names:
        head = archive.read(cover_path)[:8]
        check(
            head.startswith(b"\x89PNG\r\n\x1a\n")
            or head.startswith(b"\xff\xd8\xff")
            or head.startswith(b"GIF8"),
            "封面文件是有效位图",
        )

readme = (ROOT / "README.md").read_text(encoding="utf-8")
check("illustrations/front.svg" in readme, "README 引用卷首插画")
path_section = readme.split("## 学习路径", 1)[1].split("## ", 1)[0]
check("通过标准" in path_section, "README 学习路径含各阶段通过标准")

glossary = (ROOT / "附录B-术语表.md").read_text(encoding="utf-8")
glossary_rows = [
    line
    for line in glossary.splitlines()
    if line.startswith("|") and not line.startswith("| ---")
][1:]
bad_rows = []
for line in glossary_rows:
    cells = [cell.strip() for cell in re.split(r"(?<!\\)\|", line.strip())[1:-1]]
    if len(cells) != 3 or not all(cells):
        bad_rows.append(line)
check(not bad_rows, f"术语表每行 3 列且非空（异常 {len(bad_rows)} 行）")

chapter_texts = {
    int(path.name[:2]): path.read_text(encoding="utf-8")
    for path in ROOT.glob("0[0-7]-*.md")
}
unindexed = []
for line in glossary_rows:
    cells = [cell.strip() for cell in re.split(r"(?<!\\)\|", line.strip())[1:-1]]
    if len(cells) != 3:
        continue
    term, _, chapter = cells
    match = re.search(r"第\s*(\d+)\s*章", chapter)
    if not match:
        unindexed.append(term)
        continue
    stem = term.split("（", 1)[0].strip()
    candidates = {
        term,
        term.replace("`", ""),
        stem,
        re.split(r"\s*[+/]\s*", stem)[0].strip(),
    }
    if not any(
        candidate and candidate in chapter_texts.get(int(match.group(1)), "")
        for candidate in candidates
    ):
        unindexed.append(term)
check(not unindexed, f"术语表主章均可回指正文（异常 {len(unindexed)} 条：{unindexed}）")

print(f"\n{len(failures)} 项失败" if failures else "\n全部通过")
sys.exit(1 if failures else 0)
