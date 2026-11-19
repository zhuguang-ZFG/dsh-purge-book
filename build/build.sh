#!/usr/bin/env bash
# 构建 PDF 与 EPUB：pandoc 负责 EPUB/HTML，Chrome headless 负责 PDF（避开 LaTeX）
set -euo pipefail
cd "$(dirname "$0")/.."

OUT=dist
mkdir -p "$OUT" build/tmp

# 前言 = README 去掉「目录」表格（打印版不需要文件清单）
awk '
  /^## 目录$/ { skip = 1; next }
  skip && /^## / { skip = 0 }
  !skip { print }
' README.md > build/tmp/preface.md

SRC=(build/tmp/preface.md 00-序章-从一个我不能说起.md 01-七道闸门.md 02-八十六刀.md 03-组装权之战.md 04-证据账本.md 05-红队指挥官.md 06-造车记.md 07-结语.md 附录A-命令速查.md 附录B-术语表.md)

# ---- EPUB ----
pandoc "${SRC[@]}" \
  --metadata-file=build/metadata.yaml \
  --toc --toc-depth=2 \
  --split-level=1 \
  --css=build/style.css \
  --epub-title-page=true \
  -o "$OUT/chaizha.epub"

# ---- HTML -> PDF（Chrome headless）----
pandoc "${SRC[@]}" \
  --metadata-file=build/metadata.yaml \
  --toc --toc-depth=2 \
  --standalone \
  --embed-resources \
  --css=build/style.css \
  -o build/tmp/book.html

CHROME="C:/Program Files/Google/Chrome/Application/chrome.exe"
[ -x "$CHROME" ] || CHROME="C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"

HTML_URI="file:///$(pwd -W | sed 's|^/||')/build/tmp/book.html"
"$CHROME" --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$(pwd -W)/$OUT/chaizha.pdf" "$HTML_URI" >/dev/null 2>&1

ls -la "$OUT"
