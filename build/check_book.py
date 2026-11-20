#!/usr/bin/env python3
"""成书产物验收：Mermaid 必须渲染为图，不得作为源码印进 PDF/EPUB。"""
from pathlib import Path
import json
import posixpath
import re
import sys
import unicodedata
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET
import zipfile

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "dist" / "chaizha.pdf"
EPUB = ROOT / "dist" / "chaizha.epub"
TOKENS = ("flowchart", "sequenceDiagram", "stateDiagram-v2", "participant", "subgraph")

failures = []
checks = []


def check(ok, message):
    print(("PASS " if ok else "FAIL ") + message)
    checks.append(message)
    if not ok:
        failures.append(message)


blocks = sum(
    len(re.findall(r"^```mermaid\s*$", f.read_text(encoding="utf-8"), re.M))
    for f in sorted(ROOT.glob("[0-7]*.md"))
)
check(blocks == 9, f"源中 Mermaid 图块为 9（实际 {blocks}）")

plates = sorted((ROOT / "illustrations").glob("*.svg"))
manifest = json.loads((ROOT / 'illustrations/manifest.json').read_text(encoding='utf-8'))
plate_keys = {entry['key'] for entry in manifest}
check(len(plate_keys) == len(manifest) and {p.stem for p in plates} == plate_keys,
      f"手绘插图与唯一清单一致（实际 {len(plates)}）")
source_text = '\n'.join(p.read_text(encoding='utf-8') for p in
                        [ROOT / 'README.md', *sorted(ROOT.glob('0[0-7]-*.md'))])
referenced_plates = re.findall(r'\]\(illustrations/([\w-]+)\.svg\)', source_text)
check(set(referenced_plates) == plate_keys and len(referenced_plates) == len(plate_keys),
      '全部手绘图在书稿中各引用一次')
plate_text = " ".join(" ".join(ET.parse(path).getroot().itertext()) for path in plates)
check(
    all(token not in plate_text for token in ("86 PATCHES", "25 LAYERS", "SELFCHECK", "REANCHOR", "NONCE")),
    "插图不残留旧版数量与功能标签",
)
check("59 PATCHES" in plate_text, "插图包含当前补丁数量")
baseline = json.loads((ROOT / "build/baseline.json").read_text(encoding="utf-8"))

reader = PdfReader(PDF)
pdf_page_texts = [page.extract_text() or "" for page in reader.pages]
pdf_text = "\n".join(pdf_page_texts)
for token in TOKENS:
    check(token not in pdf_text, f"PDF 无 Mermaid 源码字面量 {token!r}")
check("\\|" not in pdf_text, "PDF 无表格转义残留 \\|")
check(all(text.strip() for text in pdf_page_texts), f"PDF 无空白页（实际 {len(reader.pages)} 页）")
check('59 PATCHES' in pdf_page_texts[0] and '1.1 一次动作经过哪里' not in pdf_page_texts[0],
      'PDF 第一页为独立手绘封面，目录位于后页')


def flatten_outline(items):
    for item in items:
        if isinstance(item, list):
            yield from flatten_outline(item)
        else:
            yield item


def normalized(text):
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", text)).translate(
        str.maketrans({"“": '"', "”": '"', "„": '"', "‘": "'", "’": "'"})
    )


pdf_outline = list(flatten_outline(reader.outline))
check(len(pdf_outline) >= 11, f"PDF 书签 >= 11（实际 {len(pdf_outline)}）")
top_outline = {
    normalized(getattr(item, "title", ""))
    for item in reader.outline
    if not isinstance(item, list)
}
chapter_headings = []
for path in sorted(list(ROOT.glob("0[0-7]-*.md")) + list(ROOT.glob("附录*.md"))):
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            chapter_headings.append(line[2:].strip().replace("`", ""))
            break
missing_bookmarks = [
    heading for heading in chapter_headings if normalized(heading) not in top_outline
]
check(not missing_bookmarks, f"PDF 顶层书签含全部章节（缺 {missing_bookmarks}）")
nav = json.loads((ROOT / 'build/tmp/navigation.json').read_text(encoding='utf-8'))
destinations = {unquote(name).lstrip('/'): dest for name, dest in reader.named_destinations.items()}
missing_anchors = [e['id'] for e in nav['entries'] if e['id'] not in destinations]
check(not missing_anchors, f'PDF 全部标题与插图锚点可达（缺 {missing_anchors}）')
check(reader.page_mode == '/UseOutlines', 'PDF 请求打开书签侧栏')
check({'常用书签', '插图索引', '阅读说明'}.issubset(top_outline), 'PDF 含常用书签、插图索引与阅读说明')


def matching_bookmark(title, target):
    dest = destinations.get(target)
    if dest is None:
        return False
    return any(item.title == title
               and reader.get_destination_page_number(item) == reader.get_destination_page_number(dest)
               and abs(float(item.top) - float(dest.top)) < .1
               for item in pdf_outline)


check(len(nav['shortcuts']) == 8 and all(matching_bookmark(e['title'], e['id']) for e in nav['shortcuts']),
      '八个常用书签跳到对应段落的实际位置')
figures = [e for e in nav['entries'] if e['kind'] == 'figure']
check(len(figures) == blocks + len(plates), '导航清单覆盖全部手绘图与流程图')
bad_targets = []
for entry in nav['entries']:
    dest = destinations.get(entry['id'])
    if dest is None:
        bad_targets.append(entry['id'])
        continue
    page = reader.get_destination_page_number(dest)
    label = entry['caption'] if entry['kind'] == 'figure' else entry['title']
    if normalized(label) not in normalized(pdf_page_texts[page]):
        bad_targets.append(entry['id'])
        other_pages = [i + 1 for i, text in enumerate(pdf_page_texts) if normalized(label) in normalized(text)]
        print('TARGET DIAGNOSTIC', json.dumps({'id': entry['id'], 'expected': label, 'page': page + 1,
              'found_on': other_pages, 'page_start': pdf_page_texts[page][:500]}, ensure_ascii=False))
check(not bad_targets, f'PDF 锚点目标页包含对应标题或完整图注（异常 {bad_targets}）')
check(all(matching_bookmark(e['short'], e['id'])
          and sum(item.title == e['short'] for item in pdf_outline) == 1 for e in figures)
      and len({e['short'] for e in figures}) == len(figures),
      '全部插图使用唯一的编号短书签，准确跳转且不重复')
toc_pages = json.loads((ROOT / 'build/tmp/toc-pages.json').read_text(encoding='utf-8'))
html = (ROOT / 'build/tmp/book.html').read_text(encoding='utf-8')
printed_labels = re.findall(r'<span class="toc-page">(\d+)</span>', html)
check(len(printed_labels) == len(toc_pages) and len(toc_pages) > 10
      and [int(n) for n in printed_labels] == list(toc_pages.values())
      and all(reader.get_destination_page_number(destinations[key])+1 == value
              for key, value in toc_pages.items()),
      '纸本目录全部页码来自最终 PDF 目的地，并与印刷标签一致')
check(all(normalized(f'拆闸 · {i+1}') in normalized(text)
          for i, text in enumerate(pdf_page_texts) if i), 'PDF 页脚页码与实际页序一致')

broken_pdf_links = []
link_count = 0
for page in reader.pages:
    for reference in page.get('/Annots', []):
        annot = reference.get_object()
        dest = annot.get('/Dest')
        action = annot.get('/A', {})
        if action.get('/S') == '/GoTo':
            dest = action.get('/D')
        if isinstance(dest, str):
            link_count += 1
            if dest not in reader.named_destinations:
                broken_pdf_links.append(dest)
check(link_count >= len(figures)+len(nav['shortcuts']) and not broken_pdf_links,
      f'PDF 内部链接仍可达（{link_count} 个，异常 {broken_pdf_links}）')
baseline_markers = (baseline["commit"], baseline["package"], baseline["version"], baseline["host_target"], "五十九刀", "dsh-purge-safe --status")
missing_pdf_markers = [value for value in baseline_markers if normalized(value) not in normalized(pdf_text)]
check(not missing_pdf_markers, f"PDF 包含本版基线与入口（缺 {missing_pdf_markers}）")
normalized_pages = [normalized(text) for text in pdf_page_texts]
for chapter in sorted(ROOT.glob("0[0-7]-*.md")):
    count = len(re.findall(r"^```mermaid\s*$", chapter.read_text(encoding="utf-8"), re.M))
    for number in range(1, count + 1):
        source = ROOT / "build/tmp/figures" / f"{chapter.stem}-{number}.svg"
        diagram = ET.parse(source).getroot()
        labels = [
            normalized("".join(item.itertext()))
            for item in diagram.iter()
            if item.tag.rsplit("}", 1)[-1] in ("text", "foreignObject")
        ]
        labels = [label for label in labels if label]
        check(
            bool(labels) and any(all(label in page for label in labels) for page in normalized_pages),
            f"PDF 流程图标签完整且在同一页：{source.stem}",
        )

with zipfile.ZipFile(EPUB) as archive:
    names = archive.namelist()
    svg = [n for n in names if n.lower().endswith(".svg")]
    expected_svg = blocks + len(plates)
    check(len(svg) >= expected_svg, f"EPUB 内嵌 SVG >= {expected_svg}（实际 {len(svg)}）")
    chapters = [n for n in names if re.match(r"EPUB/text/ch\d+\.xhtml$", n)]
    check(len(chapters) == 11, f"EPUB 章节文档为 11（实际 {len(chapters)}）")
    xhtml = "".join(
        archive.read(n).decode("utf-8", "replace") for n in names if n.endswith(".xhtml")
    )
    check("sourceCode mermaid" not in xhtml, "EPUB 无未渲染的 mermaid 代码块")
    check("\\|" not in xhtml, "EPUB 无表格转义残留 \\|")

    documents = {name: ET.fromstring(archive.read(name)) for name in names if name.endswith(".xhtml")}
    cover_doc = documents['EPUB/text/cover.xhtml']
    check(any(item.tag.endswith('}img') for item in cover_doc.iter())
          and not any(item.tag.endswith('}image') for item in cover_doc.iter()),
          'EPUB 封面直接引用图片，不使用引擎兼容性较差的嵌套 image')
    all_code = [item for doc in documents.values() for item in doc.iter() if item.tag.endswith('}code')]
    check(any('dsh-purge-safe --status' in ''.join(item.itertext()) for item in all_code)
          and '\u200b' not in ''.join(''.join(doc.itertext()) for doc in documents.values()),
          'EPUB 排版分段不插入零宽字符，命令复制文字保持原样')
    epub_text = " ".join(" ".join(doc.itertext()) for doc in documents.values())
    missing_epub_markers = [value for value in baseline_markers if normalized(value) not in normalized(epub_text)]
    check(not missing_epub_markers, f"EPUB 包含本版基线与入口（缺 {missing_epub_markers}）")
    embedded_svg = {archive.read(name) for name in svg}
    check(all(b'foreignObject' not in data for data in embedded_svg),
          'EPUB 全部 SVG 使用原生文字，无 foreignObject 依赖')
    missing_plates = [path.name for path in plates if path.read_bytes() not in embedded_svg]
    check(not missing_plates, f"EPUB 全部手绘图与当前源文件一致（缺 {missing_plates}）")

    ids = {name: {item.get("id") for item in doc.iter() if item.get("id")} for name, doc in documents.items()}
    broken_links = []
    for name, doc in documents.items():
        for item in doc.iter():
            for attr in ("href", "src"):
                reference = item.get(attr)
                if reference is None:
                    continue
                link = urlsplit(reference)
                if link.scheme or link.netloc:
                    continue
                target = posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(link.path))) if link.path else name
                if target not in names or (link.fragment and target in ids and unquote(link.fragment) not in ids[target]):
                    broken_links.append(f"{name}: {reference}")
    check(not broken_links, f"EPUB 本地链接与目录锚点可达（异常 {broken_links}）")
    all_ids = set().union(*ids.values())
    reading_notes = [element for doc in documents.values() for element in doc.iter()
                     if 'figure-reading' in element.get('class', '').split()]
    original_links = [element for doc in documents.values() for element in doc.iter()
                      if 'figure-original' in element.get('class', '').split()]
    check(len(reading_notes) == len(figures) == len(original_links)
          and all(len(list(note.iter('{http://www.w3.org/1999/xhtml}li'))) >= 2
                  for note in reading_notes),
          'EPUB 每幅图都有可重排读图说明和有效原图入口')
    cells = [element for doc in documents.values() for element in doc.iter()
             if element.tag.endswith('}td')]
    check(bool(cells) and all(any('cell-label' in child.get('class', '').split()
                                 for child in cell.iter()) for cell in cells),
          'EPUB 表格正文每格保留窄屏字段名')
    css = '\n'.join(archive.read(name).decode('utf-8') for name in names if name.endswith('.css'))
    check('@page' not in css and 'text-align: justify' not in css
          and '@media (max-width: 600px)' in css,
          'EPUB 使用独立重排样式，不带打印尺寸与两端对齐')
    check(all(e['id'] in all_ids for e in nav['entries']), 'EPUB 保留全部导航锚点')
    figure_links = [item.get('href') for doc in documents.values() for item in doc.iter()
                    if item.get('href') and unquote(urlsplit(item.get('href')).fragment).startswith('fig-')]
    check({unquote(urlsplit(link).fragment) for link in figure_links} == {e['id'] for e in figures},
          'EPUB 翻阅索引链接覆盖全部插图')

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
    identifier_match = re.search(r'^identifier:\s*"([^"]+)"', metadata, re.M)
    book_identifier = identifier_match.group(1).strip() if identifier_match else ""
    check(bool(book_identifier), "build/metadata.yaml 含固定书籍标识")
    epub_identifier = re.search(r"<dc:identifier[^>]*>(.*?)</dc:identifier>", opf)
    check(
        bool(epub_identifier and epub_identifier.group(1).strip() == book_identifier),
        "EPUB dc:identifier 与 metadata.yaml 一致",
    )


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
    check(cover_href.lower().endswith(".png"), f"封面有无损 PNG 兼容图（{cover_href or '缺失'}）")
    check('media-type="image/png"' in cover_tag, "封面条目声明 PNG 媒体类型")
    cover_path = f"EPUB/{cover_href}"
    check(bool(cover_href) and cover_path in names, "封面文件存在于 EPUB")
    if cover_href and cover_path in names:
        check(
            archive.read(cover_path).startswith(b'\x89PNG\r\n\x1a\n')
            and (ROOT / "illustrations" / "front.svg").read_bytes() in embedded_svg,
            "EPUB 封面兼容图有效，卷首 SVG 源文件逐字节保留",
        )
    png_names = [n for n in names if n.endswith('.png')]
    check(len(png_names) == len(svg), 'EPUB 每张 SVG 都有无损兼容图')

readme = (ROOT / "README.md").read_text(encoding="utf-8")
check("illustrations/front.svg" in readme, "README 引用卷首插画")
path_section = readme.split("## 学习路径", 1)[1].split("## ", 1)[0]
check("通过标准" in path_section, "README 学习路径含各阶段通过标准")

glossary = (ROOT / "附录B-术语表.md").read_text(encoding="utf-8")
glossary_section = glossary.split("## B.1 术语", 1)[1].split("## B.2", 1)[0]
glossary_rows = [
    line
    for line in glossary_section.splitlines()
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

print(f"\n{len(checks) - len(failures)} 项通过，{len(failures)} 项失败")
sys.exit(1 if failures else 0)
