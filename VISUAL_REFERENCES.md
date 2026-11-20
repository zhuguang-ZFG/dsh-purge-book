# 手绘与阅读体验参考

核对日期：2026-11-20。本轮参考项目用于插画制作与阅读体验；书中 DSH 机制仍以 build/baseline.json 的固定源码为准。

| 项目与固定提交 | 核对文件 | 本书采用方式 |
| --- | --- | --- |
| [Rough.js](https://github.com/rough-stuff/rough/tree/56a2762171b1294d643501e8d14f120db6b27bd7) | README.md、src/core.ts | 参考轮廓、排线、粗糙度、固定 seed 的分离思路。章插图继续由本书编排几何；Mermaid 的 handDrawn 渲染沿用其依赖链。未复制该仓库源码。 |
| [perfect-freehand](https://github.com/steveruizok/perfect-freehand/tree/176e00f2399f4969e1b0965c5921d96a3e50ce9f) | README.md、packages/perfect-freehand/package.json、LICENSE | 直接引入 npm 包 1.2.3，锁定依赖；使用 getStroke 把本书中心线和预设压力转换成粗细变化的闭合轮廓。 |
| [Excalidraw](https://github.com/excalidraw/excalidraw/tree/2c3dcc06ec807e81ab9437eceb1a8f7a3c590743) | README.md 的 Features 与 Excalidraw.com | 参考缩放、平移、SVG 导出和离线使用的体验；插画册用原生 HTML/JavaScript 独立实现，未嵌入其编辑器，也未复制其代码。 |

## 笔触实现

build/sketchbook.py 保留本书作者定义的马车、人物、票据和图解曲线。主体线条采样后附加确定性的压力值，交由 build/render_ink.mjs 调用 perfect-freehand。这里的压力是程序设定值，不是手写板采集数据。

主体轮廓与细节线分开：细辅助线、虚线、纸纹和排线继续保持轻量 SVG；文字保持原生 text，可搜索和提取。输出文件只包含标准矢量路径，不需要加载绘图库或运行脚本。笔画端部收细，闭合轮廓不收尖；同一输入与锁定工具链产生相同插画。

perfect-freehand 为 MIT 许可，版权归 Stephen Ruiz Ltd；许可文本随 npm 包保留在 build/node_modules/perfect-freehand/LICENSE。项目本身的书稿许可不替代依赖许可。其仓库 README 的默认选项与文档描述并非完全一致，因此这里显式设置 size、thinning、smoothing、streamline、simulatePressure、last 和端部参数。

## 阅读与验收

插画册支持适合窗口、原尺寸、最高 300% 缩放、鼠标拖动、触屏滚动、上一幅/下一幅和键盘操作；关闭后焦点返回原图。16 张图和说明全部内嵌，离线可用。

build/check_artwork.mjs 用断网浏览器检查 16 图文字边界和碰撞、59 格数量、缩放平移、键盘、焦点恢复、窄屏和翻图边界。build/check_print.py 测量实际 PDF 图中文字，build/check_reading.mjs 用实际 EPUB 引擎检查窄屏与跳转；视觉检查仍需抽查最终书页。

检索过程中 GitHub 连接器认证失败，公开 API 遇到限流；以上固定提交由 git ls-remote 读取，文件通过 raw.githubusercontent.com 获取。原始检索记录留在本地 build/tmp/artwork-v3/。
