# 附录 B 术语与来源

## B.1 术语

| 术语 | 本书中的含义 | 主章 |
| --- | --- | --- |
| dsh-purge-safe | 本版参考插件，package.json 声明 2.0.0，目标 DSH 0.2.2-rc.3。 | 第 0 章 |
| 固定提交 | 用完整 Git SHA 标识源码快照，避免同一个版本号下的不同提交混用。 | 第 0 章 |
| Harness | 模型外的组装、工具、会话与执行环境；本书以 DSH 为例。 | 第 0 章 |
| 七道闸门 | 对常见阻断的七类教学归纳，不代表当前软件恰好有七个开关。 | 第 1 章 |
| profile | Web 或官方桌面各自的插件加载配置。 | 第 1 章 |
| surface | 插件识别或请求控制的宿主入口；应与 process_surface 一起核对。 | 第 1 章 |
| DSH_HOME | 当前宿主数据根；另一个 home 的状态不能代替当前实例。 | 第 1 章 |
| Apply | 按当前定义匹配、备份并写宿主文件的动作；加载仍需要进程切换。 | 第 1 章 |
| ALL_PATCHES | 四段数组组成的完整定义集合；本基线 59 条，id 最大 96。 | 第 2 章 |
| markers | 帮助识别已应用内容的标记，需与残留原文检查共同理解。 | 第 2 章 |
| strictFiles | 使指定文件的不匹配进入严格判读的元数据。 | 第 2 章 |
| hostCleanGate | 影响关键宿主清洗判读的补丁元数据。 | 第 2 章 |
| optional | 标记目标或写法可缺席；不表示所有异常都可以忽略。 | 第 2 章 |
| PATCH_DISPLAY_GROUPS | 合并面板展示行，不改变 Apply 遍历的补丁集合。 | 第 2 章 |
| 锚点漂移 | 宿主原文或布局变化后，旧匹配条件失去落点。 | 第 2 章 |
| Restore | 恢复宿主改动，用户注入正文保留；与卸载不同。 | 第 2 章 |
| persona 前缀 | 注入全文最终折入的提示词位置，order 为 -100000。 | 第 3 章 |
| contexts | 动态上下文条目；与静态 sections 分开处理。 | 第 3 章 |
| 防重入桩 | 全局 Symbol 与共享 slot 避免 assemble 重复包装。 | 第 3 章 |
| fallback | 默认工作区基线策略，依据最终有效正文是否非空选择。 | 第 3 章 |
| 完整正文 | resolver 选出的全部文本；检查不只比对开头片段。 | 第 3 章 |
| complete | Apply 的完成判定，不能用 ok 字段替代。 | 第 4 章 |
| 人工回显实验 | 临时口令仅放测试正文，观察模型是否接触它；不是专用探针命令。 | 第 4 章 |
| http_evidence | 保存原始 HTTP 请求、响应及其关联的事实表。 | 第 4 章 |
| data_proof | 保存字段、数量、样本和来源等结构化证明。 | 第 4 章 |
| agent_report | 六态任务回报，描述工作进度，不等于证据置信度。 | 第 4 章 |
| acknowledged_at | 标识回报已经被处理的时间，避免旧等待重复触发。 | 第 5 章 |
| team/mode | 官方 Teams 的会话事件；本插件只为符合条件的红队根会话补写。 | 第 5 章 |
| redteam_agent_slot | 查询、预留或释放派活名额的工具，结合注册表与预留数判读。 | 第 5 章 |
| Super Agent | 发布说明使用的能力名称；本书逐项核对实现与设计稿。 | 第 5 章 |
| drill-grant.json | 进入演练台的确认记录，不包含逐目标授权清单。 | 第 5 章 |
| check_reference.py | 本书的源码基线与组件实验验收，不能替代实际宿主安装。 | 第 6 章 |
| 自动续跑 | 另起继续消息推动会话的能力；当前默认关闭，与错误重试分开。 | 第 6 章 |

## B.2 固定来源入口

以下链接全部固定在同一个提交。源码行号随新版本变化，阅读其他版本时优先按函数名重新定位。

| 编号 | 材料 | 覆盖章节 |
| --- | --- | --- |
| S1 | [package.json](https://github.com/CallMeGuLab/dsh-purge-safe/blob/cc881fbd68b891772330c6b0d275b0c971794e00/package.json)；[中文 README](https://github.com/CallMeGuLab/dsh-purge-safe/blob/cc881fbd68b891772330c6b0d275b0c971794e00/README.zh-CN.md) | 0–1、6 |
| S2 | [CLI](https://github.com/CallMeGuLab/dsh-purge-safe/blob/cc881fbd68b891772330c6b0d275b0c971794e00/bin/dsh-purge-safe.js)；[默认配置](https://github.com/CallMeGuLab/dsh-purge-safe/blob/cc881fbd68b891772330c6b0d275b0c971794e00/cordis.patch.yml) | 1、4、附录 A |
| S3 | [core.js](https://github.com/CallMeGuLab/dsh-purge-safe/blob/cc881fbd68b891772330c6b0d275b0c971794e00/lib/core.js) | 2、4、6 |
| S4 | [identity.js](https://github.com/CallMeGuLab/dsh-purge-safe/blob/cc881fbd68b891772330c6b0d275b0c971794e00/lib/identity.js)；[rules.js](https://github.com/CallMeGuLab/dsh-purge-safe/blob/cc881fbd68b891772330c6b0d275b0c971794e00/lib/rules.js) | 2–3、5 |
| S5 | [插件入口 index.js](https://github.com/CallMeGuLab/dsh-purge-safe/blob/cc881fbd68b891772330c6b0d275b0c971794e00/lib/index.js)；[continue-retry.js](https://github.com/CallMeGuLab/dsh-purge-safe/blob/cc881fbd68b891772330c6b0d275b0c971794e00/lib/continue-retry.js) | 3–4、6 |
| S6 | [事实库 schema](https://github.com/CallMeGuLab/dsh-purge-safe/blob/cc881fbd68b891772330c6b0d275b0c971794e00/lib/redteam/schema.js)；[存储实现](https://github.com/CallMeGuLab/dsh-purge-safe/blob/cc881fbd68b891772330c6b0d275b0c971794e00/lib/redteam/store-core.js) | 4–5 |
| S7 | [团队事件](https://github.com/CallMeGuLab/dsh-purge-safe/blob/cc881fbd68b891772330c6b0d275b0c971794e00/lib/redteam/team-mode.js)；[工具注册](https://github.com/CallMeGuLab/dsh-purge-safe/blob/cc881fbd68b891772330c6b0d275b0c971794e00/lib/redteam/tools.js) | 4–5 |
| S8 | [Super Agent 设计稿](https://github.com/CallMeGuLab/dsh-purge-safe/blob/cc881fbd68b891772330c6b0d275b0c971794e00/docs/redteam-superagent-design.md)；[落地方案](https://github.com/CallMeGuLab/dsh-purge-safe/blob/cc881fbd68b891772330c6b0d275b0c971794e00/docs/redteam-superagent-dev.md) | 5 |
| S9 | [确认记录](https://github.com/CallMeGuLab/dsh-purge-safe/blob/cc881fbd68b891772330c6b0d275b0c971794e00/lib/drill-grant.js)；[卸载](https://github.com/CallMeGuLab/dsh-purge-safe/blob/cc881fbd68b891772330c6b0d275b0c971794e00/lib/uninstall.js)；[更新短路](https://github.com/CallMeGuLab/dsh-purge-safe/blob/cc881fbd68b891772330c6b0d275b0c971794e00/lib/update.js) | 2、5–6 |
| S10 | [release-notes.md](https://github.com/CallMeGuLab/dsh-purge-safe/blob/cc881fbd68b891772330c6b0d275b0c971794e00/release-notes.md)；[NOTICE](https://github.com/CallMeGuLab/dsh-purge-safe/blob/cc881fbd68b891772330c6b0d275b0c971794e00/NOTICE)；[LICENSE](https://github.com/CallMeGuLab/dsh-purge-safe/blob/cc881fbd68b891772330c6b0d275b0c971794e00/LICENSE) | 0、5–6 |

本书仓库另有 SOURCES.md 保存具体函数与勘误，baseline.json 保存摘要。正文中的源码事实以这些固定材料核对；安装和模型效果没有借用旧版本验收结论。


迁移案例的固定来源：

- [zhuguang-ZFG/dsh-purge-safe，cc881fbd](https://github.com/zhuguang-ZFG/dsh-purge-safe/tree/cc881fbd68b891772330c6b0d275b0c971794e00)：与本书主基线同提交。
- [zhuguang-ZFG/pi-purge，5cd5f355](https://github.com/zhuguang-ZFG/pi-purge/tree/5cd5f3551fba1c7320751b825e9167da5af6c25e)：名称迁移与实现对照。
- [MIGRATION.md](https://github.com/zhuguang-ZFG/pi-purge/blob/5cd5f3551fba1c7320751b825e9167da5af6c25e/MIGRATION.md)：改名表、共存警示与作者报告的验证事故。第 6.8 节以 core.js 补充其关于 DSH_BASE 的简述。
