# 参与维护

## 提勘误

开 Issue 时请给出：章节与段落、`README.md` 中的证据基线版本、期望表述与实际表述、可核对的公开来源链接。
涉及事实的修改必须能回到 `AGENTS.md`、`README.md`、`docs/`、`lib/`、`test/` 或上游 release notes 的原文；无法核对的意见按"推测"标注。

## 本地构建与验收

```bash
(cd build && PUPPETEER_SKIP_DOWNLOAD=1 bun install --frozen-lockfile)
bash build/build.sh
python build/check_book.py
```

`check_book.py` 断言：源中 8 个 Mermaid 图块已渲染、PDF 无 Mermaid 源码字面量、EPUB 内嵌 SVG 不少于 17（8 Mermaid + 9 手绘板）、章节文档为 11、README 学习路径含通过标准、作者与 EPUB 元数据一致、封面逐字节匹配 `front.svg`。
提交前请跑完整流程；只改 Markdown 也需确认 PDF/EPUB 仍能生成。同一源码、工具链与 `SOURCE_DATE_EPOCH` 下，可比较两次 EPUB 的 SHA-256 验证字节可复现；跨工具链不承诺。

## 修改边界

- 正文只收录 `00`–`07` 章与附录 A/B；新文件要进入成书，必须同步 `build/build.sh` 的 `SRC` 白名单。
- Mermaid 图保留在源文件里；`build/tmp/` 下的副本由 `build/render_mermaid.py` 生成，不要手工编辑。
- `illustrations/front.svg` 与 `ch00.svg`–`ch07.svg` 由 `build/draw_illustrations.py` 生成；改插画请改生成器，不要直接提交生成物。
- 升级证据基线时同步更新 `README.md` 的版本行、`VERSIONS.md`，并逐条复核受影响的章节与附录。

## 风格

中文正文用直白的技术叙述：先给结论，再给命令或表格，最后说明失败现场与判读边界。
不写无法复现的"我试过据说"，也不用未经核对的第三方版本号。
