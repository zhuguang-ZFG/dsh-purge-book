# 参与维护

## 提勘误

请给出章节段落、书稿版次、参考提交、原表述、建议表述与可核对来源。本版基线固定在 build/baseline.json，不仅按包版本号识别。源码行为优先回到对应函数；发布说明中的目标、设计稿中的提案和组件实验结果分别标明。

当前参考树没有根 AGENTS.md，也没有 check:docs 脚本。不要把旧社区版本的检查合同套在新仓库上。来源与实现不一致时，把差异记入 SOURCES.md。

## 本地构建与验收

固定工具版本见 build/toolchain.json（pandoc 3.14、Chrome 157.0.8103.80、Bun 1.3.14、Python 3.13.14、Node 24.14.0）；EPUBCheck 需要 Java 17。Windows 下使用 Git Bash 运行构建脚本。

```bash
python -m pip install pypdf==6.21.2 PyMuPDF==1.28.0
(cd build && PUPPETEER_SKIP_DOWNLOAD=1 bun install --frozen-lockfile)
bash build/build.sh
python build/check_book.py
bun build/check_artwork.mjs
python build/check_print.py
bun build/check_reading.mjs
python build/check_epub_mupdf.py
python examples/label-task/verify.py
```

验收覆盖 9 个 Mermaid 图块、16 张手绘图、11 个 EPUB 正文章节、25 个非线性原图页，以及书签、链接、纸本目录页码、元数据、基线与术语回指。每图的编号短书签只出现一次；目标页内容和实际纵向位置都要对应。流程图全部标签须在 PDF 同一页可提取。

`check_print.py` 检查孤页、跨页表格末尾单行，以及最终 PDF 图区内的中文实际字号（至少 8.5 磅；装饰英文与代码不在此阈值内）。`check_reading.mjs` 用 epub.js 0.3.93 打开实际 EPUB：11 章分别在 320/390 像素与 100%/150% 字号下检查溢出、表格字段名、左对齐和图片；再检查 33 个索引跳转、25 个原图页与返回，以及向前/向后翻页。报告与截图写入 `build/tmp/reading-check/`。新增 22 个缺失字体回退场景；MuPDF 1.28.0 另在 320/390 像素与 16/24 磅下独立重排，核对图片解码、链接、中文与横向边界。长标识使用无新增字符的 span 分段换行，复制文字保持原样；表格采用不依赖媒体查询的字段卡。两套引擎检查不能替代 Apple Books、微信读书、Kindle 等各自的实机验收。

EPUB 包结构另用固定版本的 EPUBCheck 校验：

```bash
curl --fail --location https://github.com/w3c/epubcheck/releases/download/v5.4.0/epubcheck-5.4.0.zip -o build/tmp/epubcheck.zip
unzip -q build/tmp/epubcheck.zip -d build/tmp
java -jar build/tmp/epubcheck-5.4.0/epubcheck.jar dist/chaizha.epub
```

只改 Markdown 也需重建并抽查实际页面。同一源码、工具链与 SOURCE_DATE_EPOCH 下可比较 EPUB 的 SHA-256；跨工具链不承诺字节一致。

改动源码事实或证据基线时，还需把参考仓库检出到记录的提交，安装 Node.js 后运行：

```bash
python build/check_reference.py --reference /path/to/dsh-purge-safe --peer /path/to/pi-purge
python build/check_reference.py --reference /path/to/pi-purge --baseline build/baseline-pi.json
```

脚本检查两份固定提交与文件摘要；组件进程使用临时 DSH_HOME，同时由 Node 权限拒绝写盘和子进程。临时变量不限制宿主探测，实验不调用探测或 Apply。报告写入 build/tmp/reference-check.json 与 reference-pi-check.json；可在首次成书构建前独立运行。它不安装插件、不调用宿主 Apply，也不能证明真实宿主或模型效果。更新摘要前必须先复核源码差异，不能用重录摘要代替验收。

## 修改边界

- 成书输入由 build/build.sh 的 SRC 白名单控制；重命名或新增章节时同步目录和白名单。
- Mermaid 保留在源稿；build/tmp/ 下的构建副本不手改。
- 翻阅索引与 PDF 书签由 build/navigation.lua 和 build/finish_pdf.py 生成；新图须收录到正文，绘制时更新 illustrations/manifest.json，并在 build/figure-notes.json 补短标题与读图说明。改标题后核对常用入口匹配及 EPUB 跨章节链接。build/print_pdf.py 反复打印至目录页码与目的地一致，不手填页码。
- 打印和电子书分别修改 build/style.css 与 build/epub.css。EPUB 原图页由 build/finish_epub.py 封装为非线性阅读项，须同时保留返回正文入口；SVG 标签使用原生 text，不依赖 foreignObject。
- 改插画须改 build/draw_illustrations.py、build/detail_illustrations.py、build/migration_illustrations.py 或 build/sketchbook.py，再重建并同步 illustrations/ 与 dist/。主体笔触由锁定的 perfect-freehand 经 build/render_ink.mjs 输出；改查看器则改 build/gallery.html。运行 build/check_artwork.mjs 检查缩放、拖动、键盘和窄屏，并在 PDF 实际图幅下检查文字、箭头和排线；图注写入图片替代文本，避免另写重复说明。
- 升级基线时同步 README.md、VERSIONS.md、SOURCES.md、build/baseline.json、受影响正文、附录和配图方案。
- 当前 CI 检出两个固定提交，运行源码、离线实验和成书验收；工具版本固定并记录。远端 CI 是否成功须看实际运行记录。真实宿主测试必须记录版本、入口、路径、动作和结果，不能借用旧版本结论。

## 风格

中文采用直接的技术叙述。先交代现场与要判断的问题，再给命令、流程和证据；明确说明这些材料足以得出什么结论。保留事实的确定程度，不添加没有测量依据的效果数字。
