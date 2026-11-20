# 本次改造的证据与勘误

核对日期：2026-11-20。参考仓库：`CallMeGuLab/dsh-purge-safe`；固定提交 `cc881fbd68b891772330c6b0d275b0c971794e00`，`package.json` 声明插件 2.0.0、目标 DSH 0.2.2-rc.3。全文中的路径均相对于该提交。机器可读的文件摘要见 `build/baseline.json`。

## 改稿前发现的问题

原书以 dsh-purge-community 1.6.84 为基线。新仓库的命令、补丁集合、组装算法和数据结构已有变化，不能按同一版本的增补处理。

| 原稿中的说法 | 本次核对结果 | 改稿范围 |
| --- | --- | --- |
| 86 条补丁，18/19 默认关闭，默认生效 84 条 | 导出的 `ALL_PATCHES.length` 为 59；四段分别为 5、3、8、43 条，最大 id 为 96 | 第 0–2、4、6–7 章、封面和章插画 |
| `purge-community selfcheck/diagnose/reanchor/probe/audit` | 当前 CLI 只解析 `--status/--apply/--revert/--uninstall/--edit/--help` | 安装教程、第 4 章、附录 A |
| `leadWithInject`、ChatML 信封、4096 长度的 loose 正则去重 | 当前 `rewritePromptAssembly` 把全文折入 persona 前缀，另处理 contexts 与尾段 | 第 3 章 |
| `Symbol.for("dsh-purge.assembleGuard")` | 当前键名为 `dsh-purge-safe.assembleGuard`；原 assemble 抛错时也会尝试改写空结构 | 第 3、6 章 |
| `evidence-ledger.mjs` 与 `redteam_evidence_upgrade` 提供四档置信度 | 当前树无该模块或工具；存在 SQLite `http_evidence`、`data_proof`、`agent_report` 等结构 | 第 4–5 章、附录 B |
| 统一左侧面板，应用后全部由用户手动重启 | 当前为标题旁右侧 dock；Web、官方桌面分开管理，面板成功应用会安排重启；CLI 打印重启提示 | 第 0–1、6 章、附录 A |
| 应用从不写 `prompt-inject.md` | 当前会播种或刷新默认稿，识别为用户自定义的稿件予以保留 | 第 2–3 章 |
| 上游 `AGENTS.md` 与 `npm run check:docs` 是当前事实来源 | 此提交无根 `AGENTS.md`，也无 `check:docs` 脚本 | 全书来源说明 |

原稿的马与车比喻、章节教学体例和几何墨线视觉继续使用。重写针对上述事实差异；不把旧版验收结论转记为新版实测。旧版原文可从本书 v1.0.0 对应的 Git 历史查阅。

## 源码定位

| 主题 | 文件与位置 | 可复核事实 |
| --- | --- | --- |
| 版本与运行时 | `package.json` | name、version、engines、dshTarget、bin、scripts |
| 本地安装与入口 | `README.zh-CN.md`；`bin/dsh-purge-safe.js` 的 `main` | Web/desktop profile 分开安装；六个长选项；CLI 无 `--json` 分支 |
| 默认配置 | `cordis.patch.yml`；`lib/index.js` 的 `DEFAULTS` | 自动应用默认关闭；自动重试开启，最大 3；自动续跑关闭 |
| 补丁集合 | `lib/core.js:5506` 的 `ALL_PATCHES` | 5 + 3 + 8 + 43 = 59 条；id 非连续 |
| 展示聚合 | `lib/core.js:5509` 的 `PATCH_DISPLAY_GROUPS` | disclaimer `[1]`；approval_sentence `[5,11,12]`；approval_policy `[8,9,10]` |
| 应用与判读 | `lib/core.js` 的 `applyPatches`、`patchStatus`、`patchStatusReady`、`summarizeApplyReport` | 状态查询与本次写盘报告的词汇不同；optional、strictFiles、hostCleanGate 影响判读 |
| 应用接口 | `lib/index.js` 的 `executePurgeApply` | `ok` 与 `complete` 分列；另有 host_written、failed_items、restart_after_apply |
| 状态接口 | `lib/index.js:2205` 的 `/dsh-purge-safe/status` | surface、process_surface、dsh_home、ai_base、patch_status；面板使用展示计数 |
| 备份与升级 | `lib/core.js` 的 `ensureOfficialSnapshot`、`refreshStaleBaksForUpgrade`、`restoreFromBak` | 旁置备份和 host-backups；识别旧备份；shim 符号链接不直接覆写目标 |
| 提示词来源 | `lib/rules.js:243` 的 `resolveInjectText`；`lib/core.js:8085` | 磁盘非空稿、进程已提交稿、随包默认依次取用；保护自定义稿、可刷新旧默认 |
| 工作区规则 | `lib/index.js:656` 的 `rewriteLiveAssembly`；`lib/rules.js` | 完整正文为空才读勾选规则；fallback 依据最终正文是否非空判断基线 |
| 最终组装 | `lib/identity.js:787` 的 `rewritePromptAssembly` | persona 前缀 -100000；能力协议 99999；锚点 100000；重写 contexts |
| 防重入 | `lib/identity.js:674` 的 `installAssembleGuard` | 全局 Symbol、共享 slot、setter 包装；两种异常分支分别处理 |
| 演练台确认记录 | `lib/drill-grant.js` | 当前 home 的 dsh-purge-safe/drill-grant.json；记录 granted 与时间，非目标授权清单 |
| 事实库 | `lib/redteam/schema.js`；`lib/redteam/store-core.js` | HTTP 原文、结构化数据证明、六态 agent_report 与 acknowledged_at |
| 并发名额 | `lib/redteam/tools.js:902` 的 `redteam_agent_slot` | used = max(实际运行子会话数, 预留数)；默认上限 3 |
| 官方团队接入 | `lib/redteam/team-mode.js` 的 `ensureRedteamTeamMode`、`installTeamMode` | 只为红队根会话补事件；尊重已有 enabled:false；覆盖中途切预设 |
| Super Agent 设计稿 | `docs/redteam-superagent-design.md`、`docs/redteam-superagent-dev.md` | 文件自述是设计/落地方案；其中 agent_task 等方案未见于当前 schema/tool 注册 |
| 重试与续跑 | `lib/continue-retry.js` | 请求错误重试、永久错误排除、用户取消处理；非旧版语义拒绝重试 |
| 固定版本 | `lib/update.js:26` | SEALED 为 true；更新入口短路返回固定版本结果 |

## 文档与实现的冲突

| 文档表述 | 当前实现 | 本书采用的写法 |
| --- | --- | --- |
| README 流程图写规则集激活后写入 prompt-inject.md | `activateRule` 写入规则目标 AGENTS.md/CLAUDE.md；`resolveInjectText` 不直接选 active rule | 规则激活与注入正文分开解释，不照搬该流程图 |
| README 速度一节说补丁 #21 恢复 60 秒等待 | 当前 ALL_PATCHES 不含 #21 | 不把这项列为本基线已实现补丁，不提供据此推导的性能数字 |
| README 的工作区文件回退排在默认稿之前 | 实际调用链先 resolveInjectText，可在其中取得默认稿，最终全文仍空才读工作区勾选文件 | 以实际调用链说明可达条件 |
| 发布说明称降低拒绝率、提升稳定性 | 未附样本、基线、重复实验与统计结果 | 记为发布方目标，不写提升比例或实测结论 |
| 早期设计稿列出的能力缺口 | 当前 team-mode、agent_slot、agent_report 已有后续实现 | 用实现核对各项；保留尚未实现部分的设计身份 |

## 双仓迁移来源

主线仍固定在 CallMeGuLab/dsh-purge-safe 的 cc881fbd68b891772330c6b0d275b0c971794e00；zhuguang-ZFG/dsh-purge-safe 本次 HEAD 与它相同。迁移案例固定在 zhuguang-ZFG/pi-purge 的 5cd5f3551fba1c7320751b825e9167da5af6c25e，摘要另存 build/baseline-pi.json，不覆盖主线。两包都声明 2.0.0 / DSH 0.2.2-rc.3。

| 结论 | 固定提交定位 | 证据类型 |
| --- | --- | --- |
| 名称传播与不改项 | pi-purge/MIGRATION.md:5–25；package.json；bin/pi-purge.js | 源码与作者说明交叉核对 |
| 不应同时 Apply | MIGRATION.md:72；core.js 的 marker / BAK_SUFFIX | 作者警示与不同标记实现 |
| 独立状态、共享默认数据 | rules.js:34–55；redteam/store.js:25–33；redteam/index.js:39–58、115–116、186–187 | 实现路径；实际 root 配置仍需记录 |
| DSH_BASE 不是探测围栏 | core.js:2372–2410、2456–2464 | 实现读取 DSH_BASE 并追加候选，纠正文档“不读”的简述 |
| 改名后两包不共享 guard | identity.js:667、692–716；旧包对应段 | 两种安装顺序的假对象实验，两次 rewrite 均执行 |
| 作者机器误 Apply 与恢复 | MIGRATION.md:74–85 | 作者报告，未由本书重现或独立验证 |
| 固定版本仍关闭在线更新 | lib/update.js:12–26 | REPO 有值，SEALED 仍为 true |

逐文件比较会按六组名称规范化：92 个原样、52 个仅名称映射、9 个另有变化；pi 新增 MIGRATION.md。比较与两种 guard 顺序均由本书检查执行。跨包实验只解释包装链，不推断真实宿主递归、正文重复或模型效果。

源码实验不调用安装、Apply、revert 或宿主探测入口。Node 24.14.0 权限模型禁止写盘和子进程；测试通过实际拒绝的写入 / spawn 断言确认限制。DSH_HOME / DSH_BASE 只作夹具配置，不被描述成隔离措施。源码仍有读取权限，因此这不是执行任意不可信包的完整沙箱。

## 验证口径

本次完成源码核对、纯函数组件实验和书籍构建验收。没有在真实 DSH 上执行安装、Apply、重启、联网演练或模型拒绝率评测。组件实验记录在 `build/tmp/reference-check.json`，可用 `python build/check_reference.py --reference <仓库路径>` 重新核对固定提交、文件摘要、补丁集合与教学示例。此命令不调用宿主补丁写盘入口。

当前本地验收：主线 61 项、pi-purge 59 项源码与离线组件检查通过；66 项成书检查覆盖 9 张流程图、16 张手绘图、书签目标、103 个 PDF 内部链接、68 个目录页码、EPUB 链接、元数据与术语回指。本次 PDF 为 49 页、106 个书签；EPUB 含 11 个正文章节文档、25 个非线性原图页与 26 个 SVG 资源。CI 配置已接入两份固定源码和工具版本检查；远端 CI 未运行。

阅读质量验收：EPUBCheck 5.4.0 零错误、零警告。epub.js 0.3.93 / JSZip 3.10.1 在本机 Chrome 中通过 44 个章节布局、22 个缺失字体回退场景、33 个索引入口、25 个原图页往返和前后翻页，未请求外网资源。MuPDF / PyMuPDF 1.28.0 另在 320/390 像素与 16/24 磅下独立重排，四种布局均解码 51 个图片出现位置（正文、原图页和封面），中文与链接可读，未见横向溢出。MuPDF 的 unknown epub version: 3.0 诊断保留在报告中，其他警告会让检查失败。PDF 没有孤页或表格尾部单行，25 个图区中文实际字号均不少于 8.5 磅。阅读报告在 build/tmp/reading-check/，最终 PDF 抽查图在 build/tmp/editorial-v6/。未测试 Apple Books、微信读书或 Kindle 实机，不能据此保证所有设备显示一致。

贯穿案例为明确标注的教学设定。examples/label-task/verify.py 在本地生成 12 条虚构记录、缺项与完整输出及 SHA-256；校验能检出缺少 A12、顺序变化、重复 id 与错误标签。通过项只说明本地文件比较，不证明 DSH 安装、进程加载或模型输入。

前一轮手绘修订另行核对九图的可复现输出、标题与替代说明、59 个补丁示意格，以及插画册内嵌资源与 SVG 源文件的一致性。浏览器检查未发现插图文字重叠或越界，插画册放大、关闭和手机窄屏检查通过；实际 PDF 抽查覆盖卷首、正文折叠、协作、爆炸装配及流程图。记录保存在本地 build/tmp/artwork-v2/，不计入该轮 45 项自动成书检查。

后续 GitHub 视觉参考优化增加 perfect-freehand 笔触和缩放查看器。两次全新绘制与落盘九图逐字节一致；build/check_artwork.mjs 检查离线加载、图片文字、缩放、拖动、键盘、焦点和窄屏，报告保存在 build/tmp/artwork-check/。第 4 章排障树调整后，全部标签仍在同一页可提取，实际字号约 9.8 磅。此轮只调整视觉和阅读体验，未变更 DSH 事实基线。

此前一轮增加四张操作细节图并修订正文语气，未改变事实基线。八章代码块、行内代码和表格逐项比较均未改动；书签同时核对目标页内容与纵向位置，EPUB 插图链接核对跨章文件名和片段锚点。13 图的文字边界、离线画廊、缩放、拖动、键盘、焦点与窄屏检查通过。修订对照和实际 PDF 抽查图保存在本地 build/tmp/editorial-v4/。


本轮出版修订将独立手绘封面放到 PDF 第一页，目录、阅读说明与插图书签分别定位；正文改为左对齐，长标识不再迫使整页缩小。EPUB 封面直接引用 SVG，避免嵌套外部 SVG 在第二引擎中不显示；表格默认使用字段卡，不依赖引擎媒体查询。长标识和代码以 span 拆分视觉换行，逐文档断言全部可见字符不变，不插入零宽字符。图册旧“九张”文案同步为 16 张。

工具版本记录在 build/toolchain.json，构建时保存实际版本；CI 固定 Bun、Node、Python、Pandoc、Chrome 和 Python 依赖，并运行 strict 检查。Mermaid CLI 从范围约束改为精确 12.2.0，锁文件同步。操作系统和字体仍可能影响分页，不承诺跨机器 PDF 字节一致。
