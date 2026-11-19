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

reader = PdfReader(PDF)
pdf_text = "\n".join(page.extract_text() or "" for page in reader.pages)
for token in TOKENS:
    check(token not in pdf_text, f"PDF 无 Mermaid 源码字面量 {token!r}")
check("\\|" not in pdf_text, "PDF 无表格转义残留 \\|")
check(len(reader.pages) >= 40, f"PDF 页数 >= 40（实际 {len(reader.pages)}）")

with zipfile.ZipFile(EPUB) as archive:
    names = archive.namelist()
    svg = [n for n in names if n.lower().endswith(".svg")]
    check(len(svg) >= blocks, f"EPUB 内嵌 SVG >= {blocks}（实际 {len(svg)}）")
    chapters = [n for n in names if re.match(r"EPUB/text/ch\d+\.xhtml$", n)]
    check(len(chapters) == 11, f"EPUB 章节文档为 11（实际 {len(chapters)}）")
    xhtml = "".join(
        archive.read(n).decode("utf-8", "replace") for n in names if n.endswith(".xhtml")
    )
    check("sourceCode mermaid" not in xhtml, "EPUB 无未渲染的 mermaid 代码块")
    check("\\|" not in xhtml, "EPUB 无表格转义残留 \\|")

readme = (ROOT / "README.md").read_text(encoding="utf-8")
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
