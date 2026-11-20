#!/usr/bin/env python3
"""Catch orphan continuation pages and one-row table tails in the final PDF."""
import json
from pathlib import Path
import fitz
from pypdf import PdfReader
import re
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent


def main():
    doc = fitz.open(ROOT / 'dist/chaizha.pdf')
    report, failures, previous_headers = [], [], set()
    for index, page in enumerate(doc):
        # The running footer is outside the body; exclude it from page fill metrics.
        blocks = [b for b in page.get_text('blocks') if b[1] < page.rect.height - 50]
        text = ''.join(b[4] for b in blocks)
        bottom = max((b[3] for b in blocks), default=0)
        top = min((b[1] for b in blocks), default=bottom)
        sparse = bottom-top < 140 and len(text.strip()) < 250
        if sparse:
            failures.append(f'page {index+1}: sparse/orphan body ({len(text)} chars, {bottom-top:.0f}pt)')
        headers, fragments = set(), []
        for table in page.find_tables().tables:
            rows = table.extract()
            if not rows:
                continue
            header = tuple((cell or '').replace('\n', '') for cell in rows[0])
            headers.add(header)
            # A repeated header plus one row is the common orphan-table failure.
            orphan = header in previous_headers and len(rows) <= 2
            if orphan:
                failures.append(f'page {index+1}: continued table has only one body row')
            fragments.append({'rows':len(rows),'continued':header in previous_headers})
        previous_headers = headers
        report.append({'page':index+1,'chars':len(text),'bodyHeight':round(bottom-top,1),
                       'bodyBottom':round(bottom,1),'tables':fragments})
    # Measure the actual PDF glyph sizes within each figure, excluding code and
    # decorative English plate furniture. Captions remain part of the same region.
    reader = PdfReader(ROOT / 'dist/chaizha.pdf')
    destinations = {unquote(name).lstrip('/'): dest for name, dest in reader.named_destinations.items()}
    nav = json.loads((ROOT / 'build/tmp/navigation.json').read_text(encoding='utf-8'))
    normalize = lambda text: re.sub(r'\s+', '', text)
    figures = []
    for entry in nav['entries']:
        if entry['kind'] != 'figure':
            continue
        dest = destinations[entry['id']]
        number = reader.get_destination_page_number(dest)
        page = doc[number]
        top = page.rect.height-float(dest.top)
        spans = [s for b in page.get_text('dict')['blocks'] if b['type']==0
                 for line in b['lines'] for s in line['spans']]
        prefix = normalize(entry['caption'].split('：')[0])
        captions = [s for s in spans if normalize(s['text']).startswith(prefix)]
        assert captions, entry['id']+' missing caption'
        bottom = min(s['bbox'][3] for s in captions)
        labels = [s for s in spans if s['bbox'][1]>=top-1 and s['bbox'][3]<=bottom+1
                  and re.search(r'[\u4e00-\u9fff]',s['text'])]
        assert labels, entry['id']+' no Chinese labels in figure region'
        minimum = min(s['size'] for s in labels)
        if minimum < 8.5:
            failures.append(f"{entry['id']}: actual PDF Chinese label {minimum:.2f}pt")
        figures.append({'id':entry['id'],'page':number+1,'minPoints':round(minimum,2)})
    output = ROOT / 'build/tmp/reading-check'
    output.mkdir(parents=True, exist_ok=True)
    (output / 'print-report.json').write_text(json.dumps({'pages':report,'figures':figures,'failures':failures},
                                                        ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if failures:
        raise AssertionError('\n'.join(failures))
    print(f'PASS: {len(doc)} PDF pages; no orphan continuation page or single-row table tail; '
          f'{len(figures)} actual PDF figure regions have Chinese labels >=8.5pt.')


if __name__ == '__main__':
    main()
