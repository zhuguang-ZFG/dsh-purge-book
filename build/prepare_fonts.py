#!/usr/bin/env python3
"""Prepare pinned TrueType Chinese fonts with only the book's Unicode mappings.

Noto maps several ideographs and CJK radicals to the same glyph. Chrome can
choose the radical in PDF ToUnicode maps; SVG text has no ActualText fallback.
Subsetting to authored characters removes those unused aliases at the source.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import urllib.request

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parent.parent
COMMIT = '165c01b46ea533872e002e0785ff17e44f6d97d8'
URL = (f'https://raw.githubusercontent.com/notofonts/noto-cjk/{COMMIT}/'
       'Sans/Variable/TTF/Subset/NotoSansSC-VF.ttf')
SHA256 = 'd68bafcb48a2707749396aa12bbbd833cb70401f3a9a689fd2902c7e0d295964'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, help='Already downloaded official font (hash checked)')
    args = parser.parse_args()
    output = ROOT / 'build/tmp/fonts'
    output.mkdir(parents=True, exist_ok=True)
    source = args.source or output / 'NotoSansSC-VF.source.ttf'
    if not source.exists():
        with urllib.request.urlopen(URL, timeout=90) as response:
            data = response.read()
        if hashlib.sha256(data).hexdigest() != SHA256:
            raise ValueError('Official font SHA-256 mismatch')
        source.write_bytes(data)
    if hashlib.sha256(source.read_bytes()).hexdigest() != SHA256:
        raise ValueError('Official font SHA-256 mismatch')

    # Explicit, small source sets: never traverse temporary trees or user data.
    paths = sorted([*ROOT.glob('*.md'), *ROOT.glob('illustrations/*.svg'),
                    *ROOT.glob('build/*.py'), *ROOT.glob('build/*.lua')])
    corpus = ''.join(path.read_text(encoding='utf-8') for path in paths)
    if any('\u2e80' <= char <= '\u2fff' for char in corpus):
        raise ValueError('Review authored radical characters before subsetting')
    unicode_points = set(map(ord, corpus))
    original = TTFont(source, recalcTimestamp=False)
    report = {'source': URL, 'source_sha256': SHA256, 'license': 'SIL OFL 1.1',
              'corpus_sha256': hashlib.sha256(corpus.encode('utf-8')).hexdigest(), 'fonts': []}
    for weight, name in ((400, 'Regular'), (700, 'Bold')):
        font = instantiateVariableFont(deepcopy(original), {'wght': weight},
                                       inplace=True, updateFontNames=True)
        options = subset.Options()
        options.name_IDs = [0, 1, 2, 3, 4, 5, 6, 13, 14, 16, 17]
        options.name_legacy = True
        options.name_languages = ['*']
        subsetter = subset.Subsetter(options=options)
        subsetter.populate(unicodes=unicode_points)
        subsetter.subset(font)
        path = output / f'NotoSansSC-{name}.ttf'
        font.save(path)
        with TTFont(path) as saved:
            cmap = saved.getBestCmap()
            assert not any(0x2E80 <= value <= 0x2FFF for value in cmap)
            assert all(ord(char) in cmap for char in '门车马齐见户角')
        report['fonts'].append({'file': path.name, 'weight': weight,
                                'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    original.close()
    (output / 'font-report.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Prepared pinned Noto Sans SC Regular/Bold; unused radical aliases removed')


if __name__ == '__main__':
    main()
