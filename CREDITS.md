# 致谢

## 作者

正文、插图、构建脚本与勘误维护：zhuguang-ZFG（<https://github.com/zhuguang-ZFG>）。

## 事实来源

书中的机制描述取自以下公开材料，事实边界以 `README.md`、`VERSIONS.md` 记录的证据基线为准：

- `YuJunZhiXue/dsh-purge` 社区分支的 `AGENTS.md`、`README.md`、`docs/`、`lib/`、`test/` 与 release notes。
- DSH Desktop 公开文档中关于启动流程、profile、沙箱与工具调用的说明。
- 上游各依赖仓库的许可证与文档；其权利归各自作者所有。

## 工具

- pandoc：EPUB 与单文件 HTML 生成。
- Mermaid CLI：流程图、状态图的 SVG 预渲染。
- Chrome / Edge headless：PDF 打印与插图预览。
- pypdf：`build/check_book.py` 的 PDF 文本断言。

## 风格参考

`配图方案.md` 中的风格库条目 FA-029（几何图解叙事，Chris Ware）与 C-03（普鲁士蓝）用于随书插画的视觉约定；插画为本项目重新绘制的几何示意图，不复制原作画面。
