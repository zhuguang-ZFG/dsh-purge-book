#!/usr/bin/env python3
"""Print until TOC page labels agree with Chrome's actual named destinations."""
import argparse
from html import escape, unescape
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--chrome', required=True)
    args = parser.parse_args()
    html = ROOT / 'build/tmp/book.html'
    pdf = ROOT / 'dist/chaizha.pdf'
    original = html.read_text(encoding='utf-8')
    # Move the authored cover ahead of the title/TOC without duplicating its anchor.
    front = re.search(r'<div id="fig-front" class="book-figure">.*?</div>', original, re.S)
    if front is None:
        raise ValueError('Missing authored front plate')
    original = original[:front.start()] + '<h2 id="reading-notes">阅读说明</h2>' + original[front.end():]
    cover = ('<section id="print-cover" class="print-cover">' + front.group()
             + '<p class="cover-author">zhuguang-ZFG · 工程手记</p>'
             + '<p>2026-11-20 修订稿 · 双仓迁移案例</p>'
             + '<p><a href="#print-contents">目录</a> · <a href="#reading-notes">阅读说明</a></p></section>')
    original = original.replace('<body>', '<body>\n' + cover, 1)
    original = original.replace('<header id="title-block-header">',
                                '<div id="print-contents"><header id="title-block-header">', 1)
    original = original.replace('</nav>', '</nav></div>', 1)
    nav = re.search(r'<nav\b[^>]*id="TOC".*?</nav>', original, re.S)
    if nav is None:
        raise ValueError('Missing print TOC')
    anchors = re.findall(r'<a\b[^>]*href="#([^"]+)"[^>]*>.*?</a>', nav.group(), re.S)
    labels = {unquote(unescape(anchor)): '00' for anchor in anchors}
    commands = [args.chrome, '--headless', '--disable-gpu', '--no-pdf-header-footer',
                '--generate-pdf-document-outline', '--print-to-pdf=' + str(pdf), html.as_uri()]
    if os.environ.get('CI'):
        commands.insert(1, '--no-sandbox')
    for attempt in range(1, 5):
        def add_label(match):
            anchor = unquote(unescape(match.group(1)))
            number = labels[anchor]
            return match.group(0)[:-4] + '<span class="toc-page">' + escape(str(number)) + '</span></a>'
        toc = re.sub(r'<a\b[^>]*href="#([^"]+)"[^>]*>.*?</a>', add_label, nav.group(), flags=re.S)
        html.write_text(original[:nav.start()] + toc + original[nav.end():], encoding='utf-8', newline='\n')
        result = subprocess.run(commands, capture_output=True, timeout=90)
        if result.returncode:
            raise RuntimeError(result.stderr.decode('utf-8', 'replace'))
        reader = PdfReader(pdf)
        dests = {unquote(name).lstrip('/'): d for name, d in reader.named_destinations.items()}
        actual = {anchor: reader.get_destination_page_number(dests[anchor])+1 for anchor in labels}
        if actual == labels:
            (ROOT / 'build/tmp/toc-pages.json').write_text(
                json.dumps(actual, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
            print(f'Print TOC converged after {attempt} passes ({len(actual)} page labels)')
            return
        labels = actual
    raise RuntimeError('Print TOC page labels did not converge')


if __name__ == '__main__':
    main()
