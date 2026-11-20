"""Record actual build versions; --strict also enforces the pinned CI toolchain."""
import argparse
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import importlib.metadata

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--strict', action='store_true')
    args = parser.parse_args()
    expected = json.loads((ROOT / 'build/toolchain.json').read_text(encoding='utf-8'))
    actual = {'python': platform.python_version(), 'pypdf': importlib.metadata.version('pypdf'),
              'pymupdf': importlib.metadata.version('PyMuPDF'),
              'fonttools': importlib.metadata.version('fonttools')}
    for tool in ('bun', 'node', 'pandoc'):
        output = subprocess.check_output([tool, '--version'], text=True, encoding='utf-8')
        actual[tool] = re.search(r'\d+(?:\.\d+)+', output).group()
    chrome = os.environ.get('CHROME_PATH')
    if chrome and os.name == 'nt':
        # Puppeteer reports the browser version consistently on Windows/Linux.
        actual['chrome'] = subprocess.check_output(
            ['bun', '-e', 'import p from "puppeteer";const b=await p.launch({executablePath:process.env.CHROME_PATH,headless:true});console.log((await b.version()).split("/").pop());await b.close()'],
            cwd=ROOT / 'build', text=True, encoding='utf-8').strip()
    elif chrome:
        actual['chrome'] = re.search(r'\d+(?:\.\d+)+', subprocess.check_output(
            [chrome, '--version'], text=True, encoding='utf-8')).group()
    failures = [f'{key}: {value} != {expected[key]}' for key, value in actual.items()
                if value != expected[key]]
    report = {'platform': platform.platform(), 'expected': expected, 'actual': actual,
              'differences': failures, 'scope': 'versions; fonts and OS can still affect layout'}
    output = ROOT / 'build/tmp/toolchain-check.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))
    if args.strict and failures:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
