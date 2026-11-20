"""Read the shipped EPUB with MuPDF, independent of Chromium and epub.js."""
import json
from pathlib import Path
import re

import pymupdf as fitz

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'build/tmp/reading-check'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    fitz.TOOLS.mupdf_display_errors(False)
    report = {'reader': 'MuPDF / PyMuPDF ' + fitz.VersionBind, 'layouts': []}
    figure_count = len(json.loads((ROOT / 'build/figure-notes.json').read_text(encoding='utf-8')))
    for width, font in [(320, 16), (390, 16), (320, 24), (390, 24)]:
        fitz.TOOLS.mupdf_warnings(reset=True)
        book = fitz.open(ROOT / 'dist/chaizha.epub')
        assert book.is_reflowable
        book.layout(width=width, height=844, fontsize=font)
        text, images, links, overflow = [], 0, 0, []
        for page in book:
            text.append(page.get_text())
            links += len(page.get_links())
            for block in page.get_text('dict')['blocks']:
                if block['type'] == 1:
                    assert block.get('image') and block['width'] > 0, 'Empty decoded image'
                    images += 1
                elif block['bbox'][0] < -1 or block['bbox'][2] > width+1:
                    overflow.append({'page': page.number, 'bbox': list(block['bbox'])})
        warnings = fitz.TOOLS.mupdf_warnings(reset=True)
        # MuPDF emits this diagnostic for valid EPUB 3 before reading it.
        # Preserve it in the report, but fail on every other warning.
        unexpected = [line for line in warnings.splitlines() if line != 'unknown epub version: 3.0']
        assert not unexpected, unexpected
        assert not overflow, overflow
        assert images == figure_count*2+1, (width, font, images, figure_count)
        joined = ''.join(text)
        assert all(token in joined for token in ['第 0 章', '第 6 章', 'A.8', 'pi-purge', '5cd5f355'])
        assert len(re.findall(r'[\u4e00-\u9fff]', joined)) > 10000, 'Chinese fallback text missing'
        assert links > figure_count*2, 'Missing EPUB links'
        cover = book.load_page((0, 0))
        cover.get_pixmap().save(OUT / f'mupdf-cover-{width}-{font}.png')
        # First page of the assembly chapter, using MuPDF's independent fallback fonts.
        book.load_page((7, 0)).get_pixmap().save(OUT / f'mupdf-chapter-{width}-{font}.png')
        report['layouts'].append({'width': width, 'font': font, 'pages': len(book),
                                  'decodedImages': images, 'links': links, 'warnings': warnings,
                                  'overflow': overflow})
        print(f'PASS MuPDF: {width}px / {font}pt; {len(book)} pages; {images} decoded images; {links} links')
        book.close()
    (OUT / 'mupdf-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
