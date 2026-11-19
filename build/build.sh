#!/usr/bin/env bash
# 构建 PDF 与 EPUB：pandoc 负责 EPUB/HTML，Chrome headless 负责 PDF（避开 LaTeX）
set -euo pipefail
cd "$(dirname "$0")/.."

OUT=dist
mkdir -p "$OUT" build/tmp

# Pandoc 的 EPUB 时间戳取版次日期（UTC 零点）；调用者可显式覆盖。
if [ -z "${SOURCE_DATE_EPOCH:-}" ]; then
  SOURCE_DATE_EPOCH="$(python3 - <<'PY'
from datetime import datetime, timezone
from pathlib import Path
import re

metadata = Path("build/metadata.yaml").read_text(encoding="utf-8")
date = re.search(r'^date:\s*"([^"]+)"', metadata, re.M).group(1)
print(int(datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()))
PY
)"
fi
export SOURCE_DATE_EPOCH

# 前言 = README 去掉：重复书名标题、文件清单表、「构建 PDF / EPUB」小节、配图说明与配图方案引用
awk '
  /^# 拆闸/ { if (!seen1) { seen1 = 1; next } }
  /^## ——DSH/ { if (!seen2) { seen2 = 1; next } }
  /^## 目录$/ { skip = 1; next }
  /^## 构建 PDF \/ EPUB$/ { skip = 1; next }
  skip && /^## / { skip = 0 }
  /^- \*\*配图\*\*/ { next }
  !skip {
    gsub(/想给文章配图：直接翻 `配图方案\.md`，提示词可复制进任意生图工具。/, "")
    print
  }
' README.md > build/tmp/preface.md

SRC=(build/tmp/preface.md 00-序章-从一个我不能说起.md 01-七道闸门.md 02-八十六刀.md 03-组装权之战.md 04-证据账本.md 05-红队指挥官.md 06-造车记.md 07-结语.md 附录A-命令速查.md 附录B-术语表.md)

# ---- Chrome 定位（Windows / Linux 通用）----
if [ -z "${CHROME_PATH:-}" ]; then
  for candidate in \
    "C:/Program Files/Google/Chrome/Application/chrome.exe" \
    "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" \
    /usr/bin/google-chrome /usr/bin/chromium /usr/bin/chromium-browser; do
    if [ -x "$candidate" ]; then CHROME_PATH="$candidate"; break; fi
  done
fi
[ -n "${CHROME_PATH:-}" ] || { echo "未找到 Chrome/Edge" >&2; exit 1; }
export CHROME_PATH

SANDBOX_FLAGS=()
if [ -n "${CI:-}" ]; then SANDBOX_FLAGS+=(--no-sandbox); fi

# ---- Mermaid 预渲染：源文件保留可编辑代码，pandoc 只消费 build/tmp/src 副本 ----
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NATIVE="$ROOT"
if command -v cygpath >/dev/null 2>&1; then NATIVE="$(cygpath -m "$ROOT")"; fi
case "$NATIVE" in
  /*) URI_ROOT="file://$NATIVE" ;;
  *)  URI_ROOT="file:///$NATIVE" ;;
esac

# ---- 章插图：源文件在 illustrations/，先生成再复制到 figures/ 供 pandoc 解析 ----
python3 "$NATIVE/build/draw_illustrations.py"
mkdir -p "$NATIVE/build/tmp/figures"
cp "$NATIVE"/illustrations/*.svg "$NATIVE/build/tmp/figures/"

# EPUB 直接封装 SVG 源文件，避免封面文字随构建机字体栅格变化。
COVER="$NATIVE/illustrations/front.svg"
python3 "$NATIVE/build/render_mermaid.py" \
  --out "$NATIVE/build/tmp/src" --figures "$NATIVE/build/tmp/figures" "${SRC[@]}"
for i in "${!SRC[@]}"; do SRC[$i]="build/tmp/src/$(basename "${SRC[$i]}")"; done

# ---- EPUB ----
pandoc "${SRC[@]}" \
  --metadata-file=build/metadata.yaml \
  --resource-path=build/tmp/figures \
  --toc --toc-depth=2 \
  --split-level=1 \
  --css=build/style.css \
  --epub-title-page=true \
  --epub-cover-image="$COVER" \
  -o "$OUT/chaizha.epub"

# ---- HTML -> PDF（Chrome headless）----
pandoc "${SRC[@]}" \
  --metadata-file=build/metadata.yaml \
  --resource-path=build/tmp/figures \
  --toc --toc-depth=2 \
  --standalone \
  --embed-resources \
  --css=build/style.css \
  -o build/tmp/book.html

HTML_URI="$URI_ROOT/build/tmp/book.html"
"$CHROME_PATH" --headless --disable-gpu "${SANDBOX_FLAGS[@]}" --no-pdf-header-footer \
  --generate-pdf-document-outline \
  --print-to-pdf="$NATIVE/$OUT/chaizha.pdf" "$HTML_URI" >/dev/null 2>&1

ls -la "$OUT"
