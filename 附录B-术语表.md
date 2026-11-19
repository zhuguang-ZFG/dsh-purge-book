# 附录 B 术语表

本表只收书中出现过的词，定义与正文用法一致，不引入新概念。括号内是该词定义所在的主章；首次提及可能更早（例如序章的全书地图）。

| 术语 | 定义 | 主章 |
| --- | --- | --- |
| Harness | 承载模型、工具循环与运行时拦截的宿主程序；本书指 DSH Desktop。 | 第 0 章 |
| dsh-purge-community | 本书主角，`dsh-purge` 的社区分支；证据基线 1.6.84。 | 第 0 章 |
| 破甲 | 把 DSH 里拦人的机制逐层拆掉的动作；不是绕过，插件本身就是替你拆闸的工具。 | 第 1 章 |
| 七道闸门 | 审批弹窗、沙箱拒绝、fs 围栏、工具结果修剪、计划模式硬拦、`ask_user_question` 等待、模型自拒；分布在循环的放行、执行、回填与生成环节。 | 第 1 章 |
| 五层拆闸栈 | 宿主补丁、提示词注入、破甲强化段、权限配置、agent 预设；排除注入不等于撤销全局补丁。 | 第 1 章 |
| selfcheck | `purge-community selfcheck`；25 层逐层证据，五态 `ok` / `pending` / `inferred` / `unknown` / `broken`，`broken` 退出码 1。 | 第 1 章 |
| 补丁（刀号） | 写进宿主源码的一条替换；`id` 是刀号。`ALL_PATCHES` 全表 86 条，其中 18/19 两条可选补丁默认关闭，生效口径 84；展示分组不改变执行集合。 | 第 2 章 |
| 幂等 | 重复「应用」不会打成两遍；靠 `markers` 命中，不靠自觉。 | 第 2 章 |
| markers | 补丁 `replace` 里留下的 `[dsh-purge]` 标记，写进 `markers`，作为“已应用”的判据。 | 第 2 章 |
| 锚点 | 补丁在宿主源码里定位的那段原文；`diagnose` 会给出行号、旧锚点与候选片段。 | 第 2 章 |
| 锚点漂移 | 宿主升级后源码变动，旧锚点对不上；`diagnose` 给文件、行号、旧锚点首行与候选片段。 | 第 2 章 |
| 重锚（本地覆盖） | `reanchor apply --lines` 把新锚点写进 `anchor-overrides.json`，`clear` 撤销；覆盖只落本地，不改补丁定义。 | 第 2 章 |
| 不变量 | `prompt-inject.md`、规则集、其他插件配置，任何时候都不该被「应用」或「回滚」覆盖。 | 第 2 章 |
| 组装权 | 每次组装提示词时重新决定哪段进正文、排在哪；注入不是写一次就完的配置。 | 第 3 章 |
| `GLOBAL_PROMPT_ORDER` | `-100000`，注入 section 的排序值，保证抢在宿主提示词之前。 | 第 3 章 |
| ChatML 信封 | system 段的 `im_start` 起始标签；必须单独一行，开闭标签成对，否则注入整段失效或被吞。 | 第 3 章 |
| 自家上一代的锁（历史锁） | `OLD_IDENTITY_LOCK` / `OLD_WHO_FROM_INJECT` / `OLD_LCS_LOCK`，旧版本留下的身份句，组装时按序清理。 | 第 3 章 |
| 防重入桩 | `Symbol.for("dsh-purge.assembleGuard")`，挡住同一进程里 assemble 代理重复包装（装两次包两层会爆栈）。 | 第 3 章 |
| 探针 nonce | `probe new` 生成的一次性回显串，模型原样回显才算链路通，30 分钟过期，存在 `probe.json`。 | 第 4 章 |
| 证据分级 | 口头报告记 `claimed`（带 `source_agent`），工具默认 `inferred`，`redteam_evidence_upgrade` 才算核实，`withdrawn` 表示撤回。 | 第 4 章 |
| 审计与轮转 | `audit.jsonl` 记录 apply/revert/boost/probe/preset/reanchor 等动作，1MB 轮转、保留 2 份。 | 第 4 章 |
| 拒绝检测 + 单次重试 | `purge-community retry on` / `retry off`（默认 off，存 `tuning.json` 的 `refusalRetry`）只重试一次；`refusal_retry` 进审计（只记长度与前 80 字符），outcome 只表传输形态，不代表任务成功。 | 第 4 章 |
| 证据账本 | 记录谁说的、凭什么信的结构化账本；自检与探针管链路，账本管证据来源与置信度。 | 第 4 章 |
| 四档置信度 | `claimed` 口头报告、`observed` 工具或数据库证实、`derived` 从 observed 推理、`inferred` 推测；升级到 `observed` 需 `redteam_evidence_upgrade` 与 `verified_result`。 | 第 5 章 |
| 指挥稿 | 红队侧只派活、自己不动手的操作稿；由 `## 运行环境前提` / `## 指挥职责` 标出。 | 第 5 章 |
| CTF 合同剥离 | `CTF CORE CONTRACT` 只在官方模式保留，红队上下文里被剥离，避免与运行环境前提抢授权判断。 | 第 5 章 |
| asar_handoff.phase | `/dsh-purge/status` 的换包相位：`starting` 启动请求，`ready` / `waiting_for_quit` 助手运行过，`complete` 换包完成；`.rename-pending` 不是成功。 | 第 6 章 |

版本口径：本表对应 dsh-purge-community 1.6.84 / DSH Desktop 0.2.2-rc.1。版本号由上游工程的 `npm run check:docs` 与 `package.json` 校验；面向 agent 的细节以上游 `AGENTS.md` 为准，与上游 `README.md` 冲突时先信本表。