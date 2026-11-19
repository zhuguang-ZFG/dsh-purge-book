# 版本与证据基线

## 未发布

- 卷首手绘扉页 `illustrations/front.svg`；8 张章图改为手绘墨线（可复现抖动 + 轻二次描边）。

## 书版本

| 版本 | 日期 | 内容 |
| --- | --- | --- |
| v1.0.0 | 2026-11-19 | 8 章 + 2 附录；8 张 Mermaid 图与 8 张随书几何插画；PDF/EPUB 构建与 CI 验收；LICENSE、CONTRIBUTING |

## 证据基线

| 对象 | 版本 | 用途 |
| --- | --- | --- |
| dsh-purge-community | 1.6.84 | 正文所述补丁、提示词组装、自检与审计行为的事实来源 |
| DSH Desktop | 0.2.2-rc.1 | 宿主闸门与启动流程；0.2.1-rc.1 / rc.2 / rc.3 / rc.5 同样通过书中验收 |
| Node.js | 24.x | 组件实验与 CLI 运行前提 |

## 升级规则

1. 在 `README.md` 改版本行，在本文件追加一行，注明日期与受影响章节。
2. 逐章核对事实：补丁编号、锚点、`selfcheck` 层数与状态、`probe` nonce、审计格式、红队合同原文。
3. 重跑 `bash build/build.sh` 与 `python build/check_book.py`；版本号若进入 PDF 元数据，同步 `build/metadata.yaml`。
4. 无法核对的新行为写在"待验证"，不写进正文结论。
