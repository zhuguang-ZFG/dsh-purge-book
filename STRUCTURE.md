# 仓库结构

## 书稿

| 路径 | 作用 |
| --- | --- |
| `README.md` | 书籍定位、目录、学习路径、通过标准、构建命令；同时是 PDF/EPUB 的前言源 |
| `00`–`07-*.md` | 正文八章；按解锁顺序从"一句我不能"走到"车与马的回响" |
| `附录A-命令速查.md` / `附录B-术语表.md` | 随手查的命令、退出码、状态文件与术语 |
| `配图方案.md` | 每章插图的双语生图提示词与风格库说明，不进正文 |
| `original-request.txt` | 用户原始写作要求，不进正文、不随构建产物分发 |

## 构建与验收

| 路径 | 作用 |
| --- | --- |
| `build/build.sh` | 生成前言、插图与 Mermaid SVG，调用 pandoc 出 EPUB/HTML，再由 Chrome 打印 PDF |
| `build/render_mermaid.py` | 把源 Markdown 的 Mermaid 代码块替换为 SVG 图片引用，源文件保持可编辑 |
| `build/draw_illustrations.py` | 生成 `illustrations/front.svg` 与 `ch00.svg`–`ch07.svg`（可复现墨线抖动 + 轻二次描边） |
| `build/check_book.py` | 检查图块渲染、PDF 无 Mermaid 源码、EPUB 章节数与 README 通过标准 |
| `build/metadata.yaml` / `build/style.css` | 书籍元数据与排版 |
| `build/tmp/` | 中间产物，忽略提交；`figures/` 收 SVG，`src/` 收替换后的 Markdown |
| `dist/` | 随仓库分发的 `chaizha.epub` 与 `chaizha.pdf` |

## 插图

`illustrations/` 下的 SVG 是生成物，不手改；卷首 `front.svg` + 每章 `chNN.svg`，风格为 FA-029 几何图解叙事（Chris Ware）× C-03 普鲁士蓝，线条经可复现的墨线抖动与轻二次描边，得到手绘质感；图中仅用编号与拉丁字母，中文释义写在 Markdown 图注里。新增章节时，在生成器里加一个绘制函数，并在对应 Markdown 里加 `illustrations/chNN.svg` 引用。

## 社区文件

`LICENSE`（CC BY-NC-SA 4.0）、`CONTRIBUTING.md`（勘误与构建流程）、`VERSIONS.md`（书版本与证据基线）、`.github/workflows/build.yml`（构建与断言）。
