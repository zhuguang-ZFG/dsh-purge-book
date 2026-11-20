# 致谢

## 作者

正文、插图、构建脚本与勘误维护：zhuguang-ZFG（<https://github.com/zhuguang-ZFG>）。

## 事实来源

本版机制描述以 CallMeGuLab/dsh-purge-safe 2.0.0 的固定提交 `cc881fbd68b891772330c6b0d275b0c971794e00` 为准；来源索引见附录 B，函数定位与文档冲突见 `SOURCES.md`：

- `CallMeGuLab/dsh-purge-safe` 的源码、README、设计文档、release notes、NOTICE 与 LICENSE；代码和随包资料的权利与许可遵循各自声明。
- `zhuguang-ZFG/dsh-purge-safe`（与主基线同提交）及 `zhuguang-ZFG/pi-purge` 的固定源码和 MIGRATION.md，用于双仓迁移案例；作者事故记录保留归因，不冒充本书实测。
- 初版参考过 `YuJunZhiXue/dsh-purge` 社区分支 1.6.84。保留这份历史归属，不将初版的机制和验证结果直接沿用到新基线。
- 上游各依赖仓库的许可证与文档；其权利归各自作者所有。

## 工具

- pandoc：EPUB 与单文件 HTML 生成。
- Mermaid CLI：流程图、状态图的 SVG 预渲染。
- Chrome / Edge headless：PDF 打印与插图预览。
- pypdf：PDF 书签整理、实际跳转位置与链接核对，以及 `build/check_book.py` 的文本断言。
- PyMuPDF 1.28.0：最终 PDF 分析、字号测量，以及基于 MuPDF 的第二引擎 EPUB 阅读验收；仅作构建工具，不嵌入书籍。
- epub.js 0.3.93（Free BSD）与 JSZip 3.10.1（MIT/GPLv3 双许可）：本地验收中读取归档 EPUB、重排、翻页和导航；不嵌入书籍内容。
- EPUBCheck 5.4.0（BSD-3-Clause）：EPUB 包结构与资源关系校验。
- perfect-freehand 1.2.3（MIT，Stephen Ruiz Ltd）：插图主体线条的压力轮廓生成；由锁文件记录依赖。
- Rough.js、Excalidraw：笔触控制与离线缩放查看体验的参考；固定提交和采用范围见 `VISUAL_REFERENCES.md`。

## 风格参考

`配图方案.md` 中的风格库条目 FA-029（几何图解叙事，Chris Ware）与 C-03（普鲁士蓝）用于随书插画的视觉约定。手绘质量修订核对了本地索引和参考图；图中马车、人物、票据与证据关系由本项目编写曲线和构图重新绘制，不复制参考图的主体或画面，也未调用图像生成模型。
