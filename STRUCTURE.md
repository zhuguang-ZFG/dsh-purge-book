# 仓库结构

## 书稿

| 路径 | 作用 |
| --- | --- |
| README.md | 书籍定位、当前基线、目录、学习路径与构建命令；也是前言源 |
| 00–07 章 Markdown | 八章正文；第 2 章文件为 02-五十九刀.md |
| 附录A-命令速查.md | 当前命令与状态、迁移差异、贯穿案例的完整校验 |
| 附录B-术语表.md | B.1 术语索引；B.2 固定提交的公开来源 |
| SOURCES.md | 本版源码定位、迁移勘误、文档冲突与验证边界 |
| 配图方案.md | 16 张随书插图的中英制作说明与图型约定，不进入正文 |
| VISUAL_REFERENCES.md | GitHub 视觉参考的固定提交、采用范围与依赖归属 |
| original-request.txt | 原始写作要求，不进入正文或构建产物 |

## 构建与验收

| 路径 | 作用 |
| --- | --- |
| build/build.sh | 生成前言、插图与 Mermaid SVG，用 pandoc 输出 EPUB/HTML，再由 Chrome 打印 PDF |
| build/render_mermaid.py | 在构建副本中把 Mermaid 块替换为 SVG 引用，保留可编辑源稿 |
| build/draw_illustrations.py | 编排章图、细节图，生成图片清单与独立插画册 |
| build/migration_illustrations.py | 名称迁移、共享路径与双重包装三张案例图 |
| build/detail_illustrations.py | 入口路径、备份版本、四项验收、回报处理四张细节图 |
| illustrations/manifest.json | 生成的手绘图清单；导航、画廊与验收共同读取 |
| build/navigation.lua | 为插图建立稳定锚点，生成 PDF/EPUB 共用翻阅索引 |
| build/finish_pdf.py | 按实际目的地生成 PDF 章节、常用入口与插图书签，保留原有链接 |
| build/print_pdf.py | 反复打印至纸本目录页码与最终 PDF 目的地一致 |
| build/finish_epub.py | 封装非线性原图页、修正原图与返回正文链接，保留 ZIP 元数据 |
| build/figure-notes.json | 全部 25 幅图的编号短标题与 EPUB 可重排读图说明 |
| build/sketchbook.py | 钢笔曲线、轻微笔触偏移、几何裁切排线、纸张纤维和马车人物等可复用图形 |
| build/render_ink.mjs | 用锁定的 perfect-freehand 将作者定义的中心线转为粗细变化的 SVG 轮廓 |
| build/gallery.html | 离线插画册模板：缩放、平移、翻图和键盘操作 |
| build/check_artwork.mjs | 浏览器检查插图文字、离线画廊交互和窄屏布局 |
| build/check_book.py | 检查成书章节、书签、图片、链接、基线标记、元数据及术语回指 |
| build/check_print.py | 最终 PDF 孤页、表格尾行和图区内中文实际字号 |
| build/check_epub_mupdf.py | 第二套 EPUB 引擎的重排、图片解码、字体回退和页面边界检查 |
| build/toolchain.json / build/check_toolchain.py | 固定工具版本、记录实际版本与差异 |
| build/baseline-pi.json / build/migration_contract.mjs | pi-purge 固定提交摘要与两种顺序的跨包假对象实验 |
| build/check_reading.mjs | epub.js 实际 EPUB 的窄屏、放大字号、翻页、索引与原图返回；打印图字号 |
| examples/label-task/ | 12 条虚构记录、故意缺项与正确输出、可重跑校验及文件摘要 |
| build/baseline.json | 固定仓库、提交、包版本、CLI 动作、59 条补丁及 25 个文件摘要 |
| build/check_reference.py | 核对本地参考源码与基线，并在禁止写盘和子进程的 Node 权限下执行离线组件实验 |
| build/reference_contract.mjs | 以纯函数与模拟会话检查提示词组装、防重入、补丁展示和团队事件 |
| build/metadata.yaml / build/style.css / build/epub.css | 书籍元数据、A4 打印与独立 EPUB 重排样式 |
| build/mermaid.json | 流程图手绘外观、固定随机种子、蓝绿暖纸色与中文字体回退 |
| build/tmp/ | 忽略提交的中间产物；含构建副本、SVG、HTML 和 reference-check.json |
| dist/ | chaizha.epub、chaizha.pdf，以及可离线放大和下载 SVG 的 illustrations.html |

参考源码检验可独立运行，需要指定参考仓库路径；CI 会检出两个固定提交并运行检查。它不安装插件，也不调用实际宿主 Apply。

## 插图与维护文件

illustrations/ 下 16 张 SVG 均由生成器输出。修改生成器或图形模块后重建并同步生成物；图内以中文标注解释关系，代码名称和排序数字保留原文。视觉沿用 FA-029 几何图解叙事 × C-03 普鲁士蓝，画布统一为 1200 × 660，采用钢笔曲线、局部排线与暖纸底色。标题和说明以 SVG title/desc 保留，正文图注只显示一次。

LICENSE 记录书稿许可；CREDITS.md 记录归属；CONTRIBUTING.md 说明维护流程；VERSIONS.md 保存书版本与证据基线历史；.github/workflows/build.yml 运行成书构建与验收。
