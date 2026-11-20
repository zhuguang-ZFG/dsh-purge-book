#!/usr/bin/env python3
"""Add reader bookmarks using Chrome's named destinations, never guessed pages."""
import json
from pathlib import Path
from urllib.parse import unquote

from pypdf import PdfReader, PdfWriter
from pypdf.generic import Fit

ROOT = Path(__file__).resolve().parent.parent


def finish():
    path = ROOT / 'dist/chaizha.pdf'
    reader = PdfReader(path)
    nav = json.loads((ROOT / 'build/tmp/navigation.json').read_text(encoding='utf-8'))
    destinations = {unquote(name).lstrip('/'): dest
                    for name, dest in reader.named_destinations.items()}
    required = {entry['id'] for entry in nav['entries']}
    missing = sorted(required - destinations.keys())
    if missing:
        raise ValueError(f'PDF named destinations missing: {missing}')
    writer = PdfWriter(clone_from=reader)
    # Clone the whole document so tagged structure and link annotations survive.
    writer.root_object.pop('/Outlines', None)
    writer.page_mode = '/UseOutlines'
    writer.page_layout = '/OneColumn'
    targets = []

    def bookmark(title, target, parent=None, bold=False, opened=False):
        dest = destinations[target]
        page = reader.get_destination_page_number(dest)
        ref = writer.add_outline_item(title, page, parent=parent, bold=bold,
                                      is_open=opened, fit=Fit.xyz(dest.left, dest.top, 0))
        targets.append({'title': title, 'id': target, 'page': page+1})
        return ref

    writer.add_outline_item('封面', 0, fit=Fit.fit())
    bookmark('目录', 'print-contents', bold=True)
    quick = bookmark('常用书签', 'reader-index', bold=True, opened=True)
    for entry in nav['shortcuts']:
        bookmark(entry['title'], entry['id'], parent=quick)
    front = bookmark('阅读说明', 'reading-notes', bold=True)
    parents = {1: front}
    for entry in nav['entries']:
        if entry['kind'] == 'heading':
            level = entry['level']
            parent = parents.get(level-1) if level > 1 else None
            ref = bookmark(entry['title'], entry['id'], parent, bold=level == 1)
            parents = {k: v for k, v in parents.items() if k < level}
            parents[level] = ref
    figures = bookmark('插图索引', 'reader-index', bold=True)
    for entry in nav['entries']:
        if entry['kind'] == 'figure':
            bookmark(entry['short'], entry['id'], figures)
    staging = ROOT / 'build/tmp/chaizha-bookmarked.pdf'
    writer.write(staging)
    writer.close()
    staging.replace(path)
    (ROOT / 'build/tmp/pdf-navigation.json').write_text(
        json.dumps(targets, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'PDF navigation: {len(targets)+1} bookmarks; named destinations preserved')


if __name__ == '__main__':
    finish()
