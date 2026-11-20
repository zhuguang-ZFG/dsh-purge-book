#!/usr/bin/env python3
"""Add non-linear image pages for portable EPUB original-image navigation."""
from html import escape, unescape
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
import posixpath
import re
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parent.parent


def wrap_tokens(text):
    """Expose safe visual break points without adding characters to copied code."""
    before, body = text.split('<body', 1)
    chunks = re.split(r'(<[^>]+>)', body)
    pre = False
    for index, chunk in enumerate(chunks):
        if index % 2:
            if re.match(r'<pre\b', chunk):
                pre = True
            elif chunk == '</pre>':
                pre = False
        elif pre:
            # Some engines do not honor pre-wrap. Inline boxes expose wrapping
            # even between short tokens while preserving spaces and newlines.
            chunks[index] = '\n'.join(
                ''.join('<span class="wrap-part">' + escape(line[i:i+6]) + '</span>'
                        for i in range(0, len(line), 6))
                for line in unescape(chunk).split('\n'))
        else:
            chunks[index] = re.sub(
                r'[A-Za-z0-9_./:@-]{12,}',
                lambda match: ''.join('<span class="wrap-part">' + match.group()[i:i+6] + '</span>'
                                      for i in range(0, len(match.group()), 6)), chunk)
    return before + '<body' + ''.join(chunks)


def finish():
    path = ROOT / 'dist/chaizha.epub'
    staging = ROOT / 'build/tmp/chaizha-linked.epub'
    count = 0
    pages = []
    # Neat Reader 9.0.11 serves .svg as text/html. Keep vector originals, but
    # display lossless PNGs at three times their authored size in the EPUB.
    image_root = ROOT / 'build/tmp/epub-images'
    image_root.mkdir(parents=True, exist_ok=True)
    raster, jobs, digests = {}, [], {}
    with zipfile.ZipFile(path) as source:
        for name in source.namelist():
            if not name.endswith('.svg'):
                continue
            data = source.read(name)
            digest = hashlib.sha256(data).hexdigest()
            if digest not in digests:
                source_path = image_root / (digest + '.svg')
                source_path.write_bytes(data)
                svg = ET.fromstring(data)
                box = [float(v) for v in re.split(r'[,\s]+', svg.get('viewBox').strip())]
                assert len(box) == 4 and box[2] > 0 and box[3] > 0, name
                target_path = source_path.with_suffix('.png')
                jobs.append({'source': str(source_path), 'target': str(target_path),
                             'width': box[2], 'height': box[3]})
                digests[digest] = target_path
            raster[name] = (posixpath.splitext(name)[0] + '.png', digests[digest])
    manifest_path = image_root / 'render.json'
    manifest_path.write_text(json.dumps(jobs, ensure_ascii=False), encoding='utf-8')
    subprocess.run(['bun', str(ROOT / 'build/rasterize_epub.mjs'), str(manifest_path)],
                   cwd=ROOT, check=True)
    with zipfile.ZipFile(path) as source, zipfile.ZipFile(staging, 'w') as target:
        for info in source.infolist():
            data = source.read(info.filename)
            if info.filename.endswith('.xhtml'):
                text = data.decode('utf-8')
                if posixpath.basename(info.filename) == 'cover.xhtml':
                    # Nested SVG <image href="other.svg"> fails in some EPUB engines.
                    match = re.search(r'<image[^>]*xlink:href="([^"]+)"', text)
                    assert match, 'Missing cover image source'
                    text = re.sub(r'<svg\b.*?</svg>',
                                  '<img src="' + match.group(1) + '" alt="拆闸：DSH 破甲工程实录封面"/>',
                                  text, flags=re.S)
                    # The XHTML no longer embeds an inline SVG document.
                    text = text.replace('properties="svg"', '')
                doc = ET.fromstring(text)
                for figure in doc.iter():
                    if 'book-figure' not in figure.get('class', '').split():
                        continue
                    image = next(e for e in figure.iter() if e.tag.endswith('}img'))
                    links = [e for e in figure.iter()
                             if 'figure-original' in e.get('class', '').split()]
                    assert len(links) == 1, info.filename
                    old = escape(links[0].get('href'), quote=True)
                    count += 1
                    name = f'figure{count:02d}.xhtml'
                    new = name
                    text = text.replace('href="' + old + '"', 'href="' + new + '"')
                    title = escape(image.get('alt', '插图'))
                    back = escape(posixpath.basename(info.filename) + '#' + figure.get('id'), quote=True)
                    vector_src = image.get('src')
                    src = escape(posixpath.splitext(vector_src)[0] + '.png', quote=True)
                    page = ('<?xml version="1.0" encoding="utf-8"?>\n'
                            '<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" lang="zh-CN" xml:lang="zh-CN">'
                            '<head><title>' + title + '</title>'
                            '<meta name="viewport" content="width=device-width, initial-scale=1.0"/>'
                            '<style>body{margin:1em;font-family:sans-serif}img{max-width:100%;height:auto}'
                            'a{color:#245669}p{line-height:1.6}</style></head><body>'
                            '<p><a href="' + back + '">返回正文</a></p><img src="' + src
                            + '" alt="' + title + '"/></body></html>')
                    pages.append((name, page, info.date_time))
                text = re.sub(r'(<img\b[^>]*\bsrc=")([^"]+\.svg)(")',
                              lambda m: m[1] + posixpath.splitext(m[2])[0] + '.png' + m[3], text)
                text = re.sub(r'<colgroup>.*?</colgroup>', '', text, flags=re.S)
                wrapped = wrap_tokens(text)
                assert ''.join(ET.fromstring(text).itertext()) == ''.join(ET.fromstring(wrapped).itertext()), \
                    'EPUB wrapping must preserve every visible character, including copied commands'
                data = wrapped.encode('utf-8')
            if info.filename.endswith('.opf'):
                # Defer OPF writing until all non-linear image pages are known.
                package_info, package_data = info, data
                continue
            target.writestr(info, data)
            if info.filename in raster:
                image_name, image_path = raster[info.filename]
                png_info = zipfile.ZipInfo(image_name, date_time=info.date_time)
                png_info.compress_type = zipfile.ZIP_DEFLATED
                target.writestr(png_info, image_path.read_bytes())
        package = package_data.decode('utf-8')
        package = re.sub(r'(<item\b[^>]*media-type="application/xhtml\+xml"[^>]*?) properties="svg"',
                         r'\1', package)
        manifest = ''.join(f'<item id="figure-page-{i}" href="text/{name}" media-type="application/xhtml+xml"/>'
                           for i, (name, _, _) in enumerate(pages, 1))
        original_cover = re.search(r'<item\b[^>]*properties="cover-image"[^>]*/>', package).group()
        cover_href = re.search(r'href="([^"]+)"', original_cover).group(1)
        package = package.replace(original_cover, original_cover.replace(' properties="cover-image"', ''))
        package = re.sub(r'(<meta\b[^>]*name="cover"\s+content=")[^"]+("\s*/>)',
                         r'\g<1>raster-cover\2', package)
        for index, (name, _) in enumerate(raster.values()):
            href = posixpath.relpath(name, 'EPUB')
            is_cover = href == posixpath.splitext(cover_href)[0] + '.png'
            image_id = 'raster-cover' if is_cover else f'raster-{index}'
            properties = ' properties="cover-image"' if is_cover else ''
            manifest += f'<item id="{image_id}" href="{href}" media-type="image/png"{properties}/>'
        spine = ''.join(f'<itemref idref="figure-page-{i}" linear="no"/>' for i in range(1, count+1))
        package = package.replace('</manifest>', manifest + '</manifest>').replace('</spine>', spine + '</spine>')
        target.writestr(package_info, package.encode('utf-8'))
        for name, page, date in pages:
            info = zipfile.ZipInfo('EPUB/text/' + name, date_time=date)
            info.compress_type = zipfile.ZIP_DEFLATED
            target.writestr(info, page.encode('utf-8'))
    staging.replace(path)
    print(f'EPUB original-image links: {count}')


if __name__ == '__main__':
    finish()
