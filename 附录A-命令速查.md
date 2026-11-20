# 附录 A 命令与状态速查

本表对应 dsh-purge-safe 2.0.0，固定提交 `cc881fbd68b891772330c6b0d275b0c971794e00`。参数以 `bin/dsh-purge-safe.js` 的实际分支为准，不沿用社区版的命令简称。

## A.1 安装与 CLI

| 命令 | 用途 | 注意 |
| --- | --- | --- |
| `dsh plugin --profile web add <绝对目录>` | 安装到 Web | 路径指向解压的本地插件 |
| `dsh plugin --profile desktop add <绝对目录>` | 安装到官方桌面 | 与 Web 分开安装和 Apply |
| `dsh-purge-safe --help` | 打印帮助 | -h 也走帮助分支 |
| `dsh-purge-safe --status` | 只读状态 | 打印文本，不提供 --json 分支 |
| `dsh-purge-safe --apply` | 匹配并应用补丁 | 看每项输出，之后重启 |
| `dsh-purge-safe --revert` | 恢复补丁 | 保留注入正文；之后重启 |
| `dsh-purge-safe --uninstall` | 恢复后卸载 | 恢复失败时停止删除 |
| `dsh-purge-safe --edit` | 打开注入文件编辑 | 文件缺失时可能创建默认稿 |

本地安装后命令未必在 PATH。进入插件目录，用 `node bin/dsh-purge-safe.js --status` 等等价入口；Node、home 和目标宿主需要对应，不能把系统默认 Node 读到的另一份安装当作界面状态。

CLI 在找不到宿主、注入为空、卸载失败或未捕获异常等分支退出 1。Apply 循环会逐项打印结果，但没有把每个补丁失败统一转换成非零退出码；因此退出 0 仍需核对报告。`--revert` 也会打印还原错误，不能只读进程码。

参数解析会找第一个已识别的长选项。未知词没有严格报错分支，而可能落入默认状态输出。因此旧命令偶尔“有输出”，不能证明旧功能仍在。只带 status 或 apply 而缺两个短横线，也不是这里的动作语法。

## A.2 会话与界面入口

| 入口 | 行为 |
| --- | --- |
| 会话标题旁 dsh-purge-safe | 打开右侧 dock |
| Clean／清洗页 | 状态、Apply、Restore、Uninstall、正文和规则管理 |
| Drill／演练台 | 确认后进入事实库、环境与任务视图 |
| `/purge status` / `apply` / `revert` / `uninstall` / `edit` / `help` | 会话命令；同名冲突时需看实际挂载 |
| `/rules list` / `use <id>` / `create <id>` / `delete <id>` / `reset` / `help` | 规则库管理；激活写规则目标文件 |
| `/rewind` | 当前会话回退；不应与宿主补丁恢复混淆 |
| purge_status、purge_apply、purge_revert | 插件注册的模型工具，分别查状态、应用和恢复 |

同名命令冲突可能被跳过或使用备用名，例如 `/purge-rewind`；不要为了抢回命令卸载别人的插件。其他接口、工具或 dock 仍需分别核对。

## A.3 状态判读

| 状态 | 一般含义 | 继续查什么 |
| --- | --- | --- |
| applied | 查询时检测到已应用 | 原文是否仍有残留；对应进程是否已重启 |
| pending | 仍有待处理原文或读取未完成 | 是否对正确宿主 Apply；本次读写报告 |
| skipped | 该份布局/原文没有需要处理的内容 | 是否为关键 hostCleanGate 定义 |
| unmatched | strictFiles 目标存在但未匹配 | 版本、文件与补丁适配 |
| missing_file | 缺少目标文件 | ai_base、当前布局、可选性 |
| na | 当前入口不适用或可选目标缺失 | 不应与“已应用”混算 |
| already | Apply 报告认为无需再次写入 | 属本次处理结果词汇 |
| pattern_not_found | Apply 没找到预期落点 | optional、strictFiles、hostCleanGate 与失败项 |
| read_error／write_error | 此次读写异常 | 错误原文、路径与文件占用 |
| backup_failed | 备份失败 | 先修复恢复依据，不能算软成功 |

表格是索引；精确判定回到 `patchStatus`、`rollupPatchStatus`、`isPatchResultSoftOk` 和 `patchStatusReady`。其中 ready 可以包含普通缺文件/跳过，不等于所有补丁都已写入。

## A.4 本机接口与文件

接口由当前宿主提供，地址和端口随实例变化。本书列路径用于核对与开发，不假定它们是独立公网 API。

| 路径 | 内容 |
| --- | --- |
| `/dsh-purge-safe/status` | 宿主、版本、逐项状态与展示计数 |
| `/dsh-purge-safe/apply` | 应用报告，关注 complete、host_written、failed_items |
| `/dsh-purge-safe/revert` | 恢复入口 |
| `/dsh-purge-safe/override` | 注入正文管理 |
| `/dsh-purge-safe/drill-grant` | 演练台确认记录读写 |
| `/redteam/api` | 演练台 HTTP 桥 |
| `$DSH_HOME/prompt-inject.md` | 当前注入正文；自定义稿与默认稿分别处理 |
| `$DSH_HOME/rules/` | 规则正文、元数据与 active 状态 |
| `$DSH_HOME/dsh-purge-safe/workspace-policy.json` | 工作区基线策略 |
| `$DSH_HOME/dsh-purge-safe/cwd-selections.json` | 工作区文件勾选记录 |
| `$DSH_HOME/dsh-purge-safe/host-backups/` | 宿主原文备份保险库 |
| `$DSH_HOME/dsh-purge-safe/continue-retry.json` | 重试与续跑设置 |
| `$DSH_HOME/dsh-purge-safe/drill-grant.json` | 当前 home 的进入确认与时间 |
| `$DSH_HOME/redteam/` | 演练事实和知识库根目录 |

## A.5 旧版迁移速查

`purge-community selfcheck`、`diagnose`、`reanchor`、`probe`、`audit`、`boost`、`retry` 和 `rollback` 不属于当前 CLI。旧版 probe.json、tuning.json、audit.jsonl 的位置与轮转约定，也不能当作当前状态文件合同。

当前固定版本关闭在线更新、通道切换和下载回退；更新以替换本地包为路径。别根据 update.js 里仍留着的下载辅助代码，推定公开入口能够联网更新。先检查 SEALED 与调用分支。

## A.6 机制与旧稿差异

这里集中保留从社区版 1.6.84 迁移时需要辨认的差异，供旧版读者查阅。当前机制的完整说明仍以正文及固定源码为准。

| 旧稿中的说法 | 当前核对结果 |
| --- | --- |
| 七类闸门各有对应开关；默认 boost、unrestricted 与五层表 | 七类是排障分类，不能直接映射为七个独立开关。当前落点见 §1.3。 |
| 同一个补丁 id 始终代表同一功能 | 当前 #85、#86 为会话 steering，#90 为 OpenAI system role 适配；记录须包含版本、id、name。 |
| diagnose/reanchor 或加 --yes 自动重锚 | 当前 CLI 没有对应入口；不匹配时保存路径、版本、补丁身份和脱敏片段。 |
| 备份全部属于插件快照 objects 库 | 当前有旁置 .dshpurge.bak、host-backups 保险库及内容摘要。 |
| prompt-inject.md 只读 | 缺文件或仍为旧默认稿时可播种、刷新；用户自定义稿保留。 |
| ChatML 换行、leadWithInject 与 loose 正则去重 | 当前未见对应函数与常量；沿 foldInjectIntoPersona、contexts 与全文兜底检查输入。 |
| selfcheck 的 25 层五态输出 | 当前使用状态查询与 Apply 报告，两套词汇需分开读取。 |
| 没回显就等于注入未到达 | 还可能是未执行指令、提示冲突、截断或观察错轮；不能据一次失败确定中断位置。 |
| evidence-ledger.mjs、redteam_evidence_upgrade 与四档置信度 | 当前未见这两个工具；SQLite 记录原始材料，agent_report 的六态描述工作状态。 |
| 拒绝后只重试一次 | 当前错误重试默认最多 3 次；自动续跑默认关闭；永久错误和取消另行处理。 |
| CTF 合同切割构成硬边界 | 当前不使用旧切割函数。提示词约定、进入确认和工具代码校验分别判读。 |
| 社区安装器的归档相位、镜像重试可套用 | 当前包没有那套完整安装器；使用 Web/desktop 的安装、写盘、加载与恢复记录。 |
| 上游 CI 已钉死文档版本 | 当前根目录未见 AGENTS.md，package scripts 未见 check:docs；本书的基线检查属于本书仓库。 |

## A.7 贯穿案例：12 条资料的验收

**以下数据、回报和故障均为教学设定。**任务是规范 12 条虚构资料的标签：去掉首尾空格、转成小写，保留 id 与顺序。本例不安装插件、不调用 Apply、不发送模型请求，也不生成网络流量。

书稿仓库提供 `examples/label-task/verify.py`。在仓库根目录运行：

```sh
python examples/label-task/verify.py
```

脚本在自己的目录生成 input.json、output-incomplete.json、output.json 和 verification.json。前者有 A01–A12 共 12 个 id；奇数行标签为带空格的 Note，偶数行为带空格的 GUIDE。故意构造的缺项输出只有 A01–A11，正确输出则逐条保留 id 并规范标签。

没有仓库时，可用下面这段最小示例复核核心判断：

```python
source = [{"id": f"A{i:02d}", "tag": " Note " if i % 2 else " GUIDE "}
          for i in range(1, 13)]
expected = [{"id": r["id"], "tag": r["tag"].strip().lower()} for r in source]
incomplete = expected[:-1]
missing = [r["id"] for r in source
           if r["id"] not in {x["id"] for x in incomplete}]
assert missing == ["A12"] and incomplete != expected
assert len(expected) == 12
```

完整脚本还校验重复 id、顺序变化和错误标签；相同数量但内容不符也会失败。verification.json 保存输入、两份输出的 SHA-256 与校验结果，不使用当前时间，因此相同脚本可重复得到相同记录。

| 沿章节追查 | 本例留下什么 | 可以得出的结论 |
| --- | --- | --- |
| 入口与安装（第 1 章） | profile、home、版本留作未测 | 没有真实宿主记录，不能确认安装 |
| 补丁与输入（第 2–3 章） | 区分 59 条定义与 12 条资料 | 少一条资料不能推出补丁失败 |
| 产物（第 4 章） | 缺少 A12 的失败记录、修正后的逐条比较 | 本地文件内容可验收 |
| 回报（第 5 章） | progress、waiting、ready 作为教学回报 | ready 仍需查文件；处理时间不证明成果 |
| 交接（第 6 章） | 文件摘要、失败原因、完整输出、未测项 | 接手者能重跑同一检查，再补自己的宿主观察 |


## A.8 两仓身份与迁移速查

本表只适用于 2026-11-20 固定的两个提交。主线仍使用 dsh-purge-safe；pi-purge 作为迁移案例，不把包名批量替换进前文。

| 项目 | dsh-purge-safe | pi-purge |
| --- | --- | --- |
| 参考仓库 | zhuguang-ZFG/dsh-purge-safe；与主基线上游同提交 | zhuguang-ZFG/pi-purge |
| 固定提交 | cc881fbd68b891772330c6b0d275b0c971794e00 | 5cd5f3551fba1c7320751b825e9167da5af6c25e |
| 包版本 / 目标宿主 | 2.0.0 / DSH 0.2.2-rc.3 | 2.0.0 / DSH 0.2.2-rc.3 |
| CLI 文件 | bin/dsh-purge-safe.js | bin/pi-purge.js |
| 状态查询 | dsh-purge-safe --status | pi-purge --status |
| 状态目录 | $DSH_HOME/dsh-purge-safe/ | $DSH_HOME/pi-purge/ |
| 宿主备份后缀 | .dshpurge.bak | .pipurge.bak |
| HTTP 前缀 | /dsh-purge-safe/* | /pi-purge/* |
| 重启环境变量 | DSH_PURGE_RESTART | PI_PURGE_RESTART |
| 提示段名前缀 | dshpg-* | pipg-* |
| assembleGuard 键 | dsh-purge-safe.assembleGuard | pi-purge.assembleGuard |

保持不变的入口包括 `/purge`、`/rules`、`/rewind` 和 `purge_status / purge_apply / purge_revert`。新分支仍会把若干历史工具包别名归一到当前包名，不能以“去旧名”为由删掉兼容分支。lib/update.js 虽填入新仓库名，SEALED 仍为 true；这不代表自动更新已经启用。

在相同 home 下，prompt-inject.md、rules/、redteam/ 和 .agent-presets/redteam/ 仍是共同路径；显式配置可改变部分位置。换包前先恢复旧包、核对结果，再处理插件加载和共享数据。名称对照不能替代第 6.7 节的迁移验收。

两仓离线检查使用 Node 24.14.0，禁止写盘与子进程：

```bash
python build/check_reference.py --reference /path/to/dsh-purge-safe --peer /path/to/pi-purge
python build/check_reference.py --reference /path/to/pi-purge --baseline build/baseline-pi.json
```

它们检查固定源码和假对象，不执行插件安装、Apply、revert 或模型请求。读取权限仍允许源码读取文件，不能把它当成验证任意不可信程序的通用隔离环境。
