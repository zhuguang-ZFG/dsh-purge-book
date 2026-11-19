# 附录 B 术语表

本表只收书中出现过的词，定义与正文用法一致，不引入新概念。括号内是该词首次出现的章。

| 术语 | 定义 | 首次出现 |
| --- | --- | --- |
| 破甲 | 把 DSH 里拦人的机制逐层拆掉的动作；不是绕过，插件本身就是替你拆闸的工具。 | 第 1 章 |
| 七道闸门 | 审批弹窗、沙箱拒绝、fs 围栏、工具结果修剪、计划模式硬拦、`ask_user_question` 等待、模型自拒；各自拦在循环的不同位置。 | 第 1 章 |
| 五层拆闸栈 | 宿主补丁、提示词注入、破甲强化段、权限配置、agent 预设；排除注入不等于撤销全局补丁。 | 第 1 章 |
| 幂等与 markers | 每条补丁带"我打过"的标记写进状态，重复「应用」不会打成两遍；幂等靠证据，不靠自觉。 | 第 1 章 |
| 锚点 | 补丁在宿主源码里定位的那段原文；`diagnose` 会给出行号、旧锚点与候选片段。 | 第 2 章 |
| 锚点漂移 | 宿主升级后源码变动，旧锚点对不上；表现为模型推脱、工具又被追问审批或补丁失效。 | 第 2 章 |
| 重锚覆盖 | `reanchor apply --lines` 把新锚点钉进 `anchor-overrides.json`，`clear` 撤销；覆盖只落本地，不改补丁定义。 | 第 2 章 |
| 不变量 | `prompt-inject.md`、规则集、其他插件配置，任何时候都不该被「应用」或「回滚」覆盖。 | 第 2 章 |
| 组装权 | 每次组装提示词时重新决定哪段进正文、排在哪；注入不是写一次就完的配置。 | 第 3 章 |
| `GLOBAL_PROMPT_ORDER` | `-100000`，注入 section 的排序值，保证抢在宿主提示词之前。 | 第 3 章 |
| ChatML 信封 | `<|im_start|>system:`，用来识别并清理宿主侧 system 段；宿主不用 ChatML 时该标签会被剥掉。 | 第 3 章 |
| 历史锁 | `OLD_IDENTITY_LOCK` / `OLD_WHO_FROM_INJECT` / `OLD_LCS_LOCK`，旧版本留下的身份句，组装时按序清理。 | 第 3 章 |
| 防重入桩 | `Symbol.for("dsh-purge.assembleGuard")`，挡住同一进程里身份注入被重复装配。 | 第 3 章 |
| 探针 nonce | `probe new` 生成的一次性回显串，模型原样回显才算链路通，30 分钟过期，存在 `probe.json`。 | 第 4 章 |
| 证据分级 | 口头报告记 `claimed`（带 `source_agent`），工具默认 `inferred`，`redteam_evidence_upgrade` 才算核实，`withdrawn` 表示撤回。 | 第 4 章 |
| 审计轮转 | `audit.jsonl` 记录 apply/revert/boost/probe/preset/reanchor 等动作，1MB 轮转、保留 2 份。 | 第 4 章 |
| 指挥稿 | 红队侧只派活、自己不动手的操作稿；由 `## 运行环境前提` / `## 指挥职责` 标出。 | 第 5 章 |
| CTF 合同剥离 | `CTF CORE CONTRACT` 只在官方模式保留，红队上下文里被剥离，避免与运行环境前提抢授权判断。 | 第 5 章 |
| 拒绝重试 | `retry on\|off`（默认 off，存 `tuning.json` 的 `refusalRetry`）只重试一次；`refusal_retry` 进审计（只记长度与前 80 字符），outcome 只表传输形态，不代表任务成功。 | 第 4 章 |

版本口径：本表对应 dsh-purge-community 1.6.84 / DSH Desktop 0.2.2-rc.1。版本号由 `npm run check:docs` 与 `package.json` 校验；面向 agent 的细节以 `AGENTS.md` 为准，与 `README.md` 冲突时先信本文件。
