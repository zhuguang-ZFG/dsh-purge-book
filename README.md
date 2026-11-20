# 拆闸：当 AI 开始为 AI 松绑
## ——DSH 破甲工程实录

![卷首图：马代表模型，车代表宿主，维修者的扳手代表本机插件。](illustrations/front.svg)

> 从一句“我不能”出发，沿着宿主补丁、提示词组装和多代理协作，
> 追查一次动作为什么没做成，又该用什么证明它真的完成。

- **书稿版次**：v2.0.0 修订稿，2026-11-20；延续八章与两附录体例。
- **证据基线**：CallMeGuLab/dsh-purge-safe **2.0.0**，提交 `cc881fbd68b891772330c6b0d275b0c971794e00`。
- **迁移案例**：zhuguang-ZFG/pi-purge **2.0.0**，提交 `5cd5f3551fba1c7320751b825e9167da5af6c25e`；zhuguang-ZFG/dsh-purge-safe 与主基线同提交。两仓独立核对，正文命令保留主线名称。
- **目标宿主**：上游声明 **DSH 0.2.2-rc.3**；官方 Web 与官方桌面分开安装、分开应用。
- **验证范围**：源码核对、离线组件实验、PDF/EPUB 构建。真实宿主安装、Apply、重启、联网演练与拒绝率评测未测。
- **配图**：16 张钢笔线描 SVG，包括卷首、八张章图及入口路径、备份版本、四项验收、回报处理四张细节图，以及双重包装、名称迁移、共享路径三张案例图，主体线条带粗细变化，配合中文标注、局部排线和暖纸色；流程图同步手绘线条。风格沿用 FA-029 几何图解叙事 × C-03 普鲁士蓝。[手绘插画册](dist/illustrations.html) 支持缩放、拖动和键盘翻图；采用方式见 [GitHub 视觉参考](VISUAL_REFERENCES.md)。

## 目录

| 章 | 文件 | 要解决的问题 |
| --- | --- | --- |
| 0 | [序章](00-序章-从一个我不能说起.md) | 分清模型回答、运行时决定和工具报错；认清新版基线 |
| 1 | [七道闸门](01-七道闸门.md) | 沿调用循环定位阻断，从本地安装到第一份状态记录 |
| 2 | [五十九刀](02-五十九刀.md) | 数清补丁集合，理解匹配、展示聚合、备份与恢复 |
| 3 | [组装权之战](03-组装权之战.md) | 正文来源、persona 折叠、动态 contexts 与防重入 |
| 4 | [证据账本](04-证据账本.md) | 状态、加载、模型输入和任务结果分别验收 |
| 5 | [红队指挥官](05-红队指挥官.md) | 角色分工、官方 Teams、任务回报与 Super Agent 实现边界 |
| 6 | [造车记](06-造车记.md) | 把版本、路径、恢复、重试和文档变成可核对记录；复核双仓迁移与实验隔离 |
| 7 | [结语](07-结语.md) | 把扳手和维护依据一起交给接手的人 |
| 附录 A | [命令与状态速查](附录A-命令速查.md) | 当前 CLI、会话入口、状态与文件位置 |
| 附录 B | [术语与来源](附录B-术语表.md) | 术语索引和固定提交的公开来源 |

## 学习路径：从入门到贯通

| 阶段 | 章节 | 要拿到的结果 |
| --- | --- | --- |
| 入门 | 0–1 | 一份有版本、路径、状态与未测项的验收单 |
| 进阶 | 2、4 | 解释 59 条定义与展示计数；读懂失败项和原始材料 |
| 深入 | 3、5 | 沿组装链解释一轮输入；核对团队事件、角色与回报 |
| 贯通 | 6–7、附录 | 把同样的检查用在自己的自动化工程里 |

**通过标准**：

- 入门：完成 §1.5，分清安装、Apply、重启与本地任务；没有宿主时明确保留未测项。
- 进阶：能复核 ALL_PATCHES 为 59 条；区分状态查询与 Apply 报告；解释 ok 与 complete。
- 深入：说明 persona 前缀、尾部协议、contexts 和防重入 slot；说明已有 team/mode 关闭事件为何不能被重写。
- 贯通：给自己的脚本补齐 §6.2 七项记录，用实际产物支撑“完成”。

只想读工程故事，可以先读 0、5、6、7 章。初版以社区版 1.6.84 为基线；旧版原文留在 Git 历史，迁移差异集中见附录 A.6，定位依据见 SOURCES.md。

## 构建 PDF / EPUB

```bash
# 固定版本见 build/toolchain.json；Windows 使用 Git Bash
python -m pip install pypdf==6.21.2 PyMuPDF==1.28.0
(cd build && PUPPETEER_SKIP_DOWNLOAD=1 bun install --frozen-lockfile)
bash build/build.sh
python build/check_book.py
bun build/check_artwork.mjs
python build/check_print.py
bun build/check_reading.mjs
python build/check_epub_mupdf.py
python examples/label-task/verify.py

# 可选：核对本版参考源码和离线组件实验，不调用宿主 Apply
python build/check_reference.py --reference /path/to/dsh-purge-safe --peer /path/to/pi-purge
python build/check_reference.py --reference /path/to/pi-purge --baseline build/baseline-pi.json
```

输出 `dist/chaizha.pdf` 与 `dist/chaizha.epub`。正文收录 00–07 章与附录 A/B，前言从本 README 裁剪生成；源码继续保留可编辑 Mermaid。卷首、章插画和流程图均在构建时生成或渲染。

EPUB 使用独立重排样式：正文左对齐，窄屏表格逐项显示字段名，每图附可放大的文字说明、原图页与返回入口。PDF 先放独立插画封面，再进入目录和阅读说明；采用 A4、正文左对齐，目录页码由最终目的地生成；章节书签与 25 幅图的编号短书签分层显示，每图只出现一次。两种格式都保留 8 个常用入口和翻阅索引。

贯穿案例位于 `examples/label-task/`：12 条虚构记录，先检出缺少 A12，再逐条校验完整输出。脚本还检查顺序、重复 id 和错误标签，并写入文件摘要与未测项；它不调用 DSH。EPUB 阅读验收使用 epub.js 0.3.93 和 MuPDF / PyMuPDF 1.28.0，加入缺失字体回退检查；另用 EPUBCheck 5.4.0 校验包结构（需 Java 17，命令见 CONTRIBUTING.md）。

EPUB 使用固定标识、作者元数据与 SVG 封面；修改时间取 metadata.yaml 日期，或由 SOURCE_DATE_EPOCH 覆盖。相同源码与工具链下可检查字节可复现性。

## 来源与事实边界

参考的是上述固定提交，不能仅凭插件版本号认定后续提交行为相同。附录 B 给出固定链接；本书仓库中的 `SOURCES.md` 保存函数定位、文档冲突与改稿勘误，`build/baseline.json` 与 `build/baseline-pi.json` 分别保存两仓关键文件摘要。

本书描述本机宿主机制和协作工程，练习使用本地测试与虚构记录。演练台进入确认、具体目标授权和证据真实性分别核对。发布说明中的性能目标保留其来源，不写成没有测量依据的效果结论。
