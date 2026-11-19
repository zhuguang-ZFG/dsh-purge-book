# 附录 A 命令速查

本附录只整理 `AGENTS.md` §3、§6、§16、§26 中书中用到的条目，供动手时照抄。`purge-community` 是命令简称，不保证装进 profile 后已在系统 PATH——先按 `docs/INSTALLATION.md#cli-rollback` 使用当前 profile 的 `bin/community.js` 与正确运行时，不要为了找命令再安装另一份 npm 包。安装验证看版本、bundle 和配置合成；**不能把模型是否拒绝当作安装成功判据**。

## A.1 CLI 常用表（§3、§26）

| 命令 | 作用 | 退出码 |
| --- | --- | --- |
| `purge-community status` | 兼容级别、宿主选择与备份列表（补丁计数看 `selfcheck`） | 0 |
| `purge-community selfcheck [--json / --text]` | 25 层逐层证据 | **broken → 1**；其余 → 0（含 pending / inferred / unknown） |
| `purge-community host-status` | 只读磁盘布局与当前服务入口证据，不退出/换包/重启 | 0，须检查 state |
| `purge-community diagnose [--json]` | 锚点漂移诊断（含行号 + 片段） | 0 |
| `purge-community reanchor list` / `show <id>` | 查看已有覆盖与单条详情 | 0 |
| `purge-community reanchor apply <id> [--index n] [--lines a-b] [--yes]` | 半自动重锚：先 dry-run 看候选，确认后写入 | 0 |
| `purge-community reanchor clear <id>` | 撤销覆盖，恢复出厂锚点 | 0 |
| `purge-community probe [new]` | 生成/查看运行时探针 | 0 |
| `purge-community audit [--limit n]` | 最近动作记录（apply/revert/boost/probe/preset/reanchor/refusal_retry 等） | 0 |
| `purge-community boost [on / off]` | 尾部强化段开关 | 0 |
| `purge-community preset [status / install [--force]]` | `unrestricted` 预设落盘 | 0 |
| `purge-community retry [on / off]` | 拒绝检测后的单次重试开关（默认 off，存 `tuning.json` 的 `refusalRetry`） | 0 |
| `purge-community usage` / `prune` | 备份占用 / 清理+GC | 0 |
| `purge-community backup` / `rollback <id>` | 快照 / 回滚插件 | 0 |
| `purge-community apply` / `revert` / `uninstall` / `edit` | 原版能力（转发 `dsh-purge`） | 透传 |

`reanchor` 的用法顺序：`list` 看有哪些覆盖，`show <id>` 看某一条，`apply <id> --index n` 或 `--lines a-b` 先看 dry-run 候选片段，确认后加 `--yes` 写入，`clear <id>` 撤销覆盖、恢复出厂锚点。覆盖存在 `anchor-overrides.json`，引擎把它当该条的 `pattern`。完整命令集合以上游 `bin/community.js` 的用法串为准；本表只覆盖书中出现的命令。

`retry` 只重试一次，避免死循环；每次重试写 `audit.jsonl` 的 `refusal_retry`（只记长度与前 80 字符）。排查拒绝率先看 `audit --limit 20` 有没有 `refusal_retry`，再决定是否调整 `tuning.injectPosition`。

## A.2 selfcheck 五状态

| 状态 | 含义 |
| --- | --- |
| `ok` | 已确认 |
| `pending` | 待应用 |
| `inferred` | 宿主推导（黄） |
| `unknown` | 证据不足（黄） |
| `broken` | 已确认故障或权限不匹配（退出码 1） |

**pending 不是故障**——别去改补丁表，点一次「应用」即可。`inferred` 与 `unknown` 同样标黄，表示证据不足以确认；`broken` 才需要按 §5 决策树跑 `diagnose`。

退出码只区分 `broken`：其余状态（含 `pending` / `inferred` / `unknown`）都是 0。自动化不能把 0 当成全绿，仍要读 `state`。

口径提醒：补丁总数的**全表 86** 与症状表的**全量 84** 不矛盾——18/19 两条可选补丁默认关闭，生效口径即 86 − 2 = 84。

## A.3 状态与文件（§6）

路径中的 `$DSH_HOME` 指 DSH 的数据目录；这些文件可以安全读，不要乱写。

| 路径 | 内容 |
| --- | --- |
| `$DSH_HOME/dsh-purge/tuning.json` | 书中涉及的开关：`boost`、`injectPosition`、`askNoBlock`、`refusalRetry`、`extraPatches` |
| `$DSH_HOME/dsh-purge/probe.json` | 探针 nonce（30 分钟 TTL） |
| `$DSH_HOME/dsh-purge/anchor-overrides.json` | 本地重锚覆盖（不改插件源码；删掉即恢复出厂锚点） |
| `$DSH_HOME/dsh-purge-community/audit.jsonl` | 动作审计（1MB 轮转，保留 2 份）；面板「维护 → 最近动作」 |
| `$DSH_HOME/dsh-purge/applied.json` · `installed-rev` | 上次应用的插件版本 |
| `$DSH_HOME/dsh-purge-community/backups/<id>/` | 快照（`manifest.json` + 小文件；大文件在 `objects/`） |
| `$DSH_HOME/.agent-presets/unrestricted/` | 无限制模式预设（升级保留原文；首行模板标记不代表用户授权覆盖） |
| `$DSH_HOME/prompt-inject.md` | **用户的注入正文**，插件只读不改（除非用户点保存） |

**不变量**：`prompt-inject.md`、规则集、其他插件配置，任何时候都不该被「应用」或「回滚」覆盖。

## A.4 备用命令名（§16）

同名命令由原插件保留。Purge 备用命令依次为 `/purge-community`、`/purge-rules`、`/purge-skills`、`/purge-rewind`；面板 `/dsh-purge/status` 返回的 `commands` 可查看实际注册名称。备用名称也占用时**只跳过该命令并报警，不覆盖他人命令**，不影响其他命令、工具、提示词与 HTTP 接口。不要为恢复面板卸载用户的回退插件。
