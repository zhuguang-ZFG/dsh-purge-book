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

readme = (ROOT / "README.md").read_text(encoding="utf-8")
path_section = readme.split("## 学习路径", 1)[1].split("## ", 1)[0]
check("通过标准" in path_section, "README 学习路径含各阶段通过标准")

print(f"\n{len(failures)} 项失败" if failures else "\n全部通过")
sys.exit(1 if failures else 0)
