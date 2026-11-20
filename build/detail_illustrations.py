"""Focused reading plates: paths, backup identity, acceptance and report handling."""
from sketchbook import Sketch, INK, PAPER, ACCENT, MUTED, PALE, RUST, FAINT, HAND, MONO, sheet


def profile():
    s = Sketch("profile", "先认入口，再核对路径",
               "Web 与官方桌面各有自己的安装记录；终端查询须核对 dsh_home 和 ai_base，与正在使用的界面对应。")
    s.heading("1·2", "先认入口，再核对路径", "两种入口分别安装、分别 Apply；状态不能互相代替。")
    for x, label, code, color in [(75, "Web 入口", "--profile web", INK),
                                  (680, "官方桌面", "--profile desktop", ACCENT)]:
        # An uneven display rim and separate stand keep the object legible at print size.
        s.path(f"M{x} 224 Q{x+122} 217 {x+247} 224 L{x+249} 390 Q{x+124} 398 {x} 391 Z",
               fill=PAPER, weight=2.8)
        s.box(x+12, 238, 222, 133, fill=PALE, weight=1.1, color=MUTED)
        s.line(x+110, 398, x+107, 424, INK, 2.3)
        s.line(x+144, 398, x+150, 424, INK, 2.3)
        s.path(f"M{x+70} 432 Q{x+125} 416 {x+185} 432", weight=2.5)
        s.text(x+124, 292, label, 29, color, HAND, "middle")
        s.text(x+124, 335, code, 17, MUTED, MONO, "middle")
        s.arrow(x+260, 304, x+292, 304, color=color, weight=1.8)
        s.path(f"M{x+302} 233 L{x+370} 233 L{x+389} 253 L{x+389} 387 L{x+302} 387 Z",
               fill=PAPER, color=color, weight=2)
        s.path(f"M{x+369} 234 L{x+368} 256 L{x+388} 254", color=color, weight=1.3)
        for y in (282, 301, 320): s.line(x+316, y, x+374, y, MUTED, 1)
        s.text(x+346, 363, "状态", 22, color, HAND, "middle")
    s.line(600, 207, 600, 444, FAINT, 1, dash="4 7")
    s.box(74, 475, 1052, 89, fill=PALE, weight=1.6, color=MUTED)
    s.text(98, 508, "终端查询时，对照正在使用的界面", 23, INK, HAND)
    s.text(98, 542, "surface / dsh_home / ai_base", 21, MUTED, MONO)
    s.text(1097, 542, "核对实际返回值", 22, ACCENT, HAND, "end")
    s.footer("路径相同、入口对应，才在查同一份安装。", "PROFILE")
    return s


def backup():
    s = Sketch("backup", "备份要能认出自己的版本",
               "上排示意官方文件由旧版换成新版，下排显示旧备份可能仍在；符合源码条件时刷新备份，恢复前还须识别符号链接。")
    s.heading("2·2", "备份要能认出自己的版本", "文件名相同，不代表内容仍属于同一版。")
    for x, title, tint in [(102, "升级前", PALE), (484, "官方升级后", RUST), (870, "核对后", PALE)]:
        s.text(x+98, 211, title, 25, INK, HAND, "middle")
        s.path(f"M{x} 239 L{x+155} 239 L{x+191} 273 L{x+191} 352 L{x} 352 Z",
               fill=tint, weight=2.2)
        s.path(f"M{x+154} 240 L{x+153} 275 L{x+189} 273", color=MUTED, weight=1.2)
    s.text(197, 307, "旧版原文", 27, INK, HAND, "middle")
    s.text(579, 307, "新版原文", 27, ACCENT, HAND, "middle")
    s.text(965, 307, "新版原文", 27, INK, HAND, "middle")
    s.arrow(312, 293, 455, 293, weight=1.8)
    s.arrow(699, 293, 839, 293, weight=1.8)
    s.text(769, 252, "检查条件", 21, MUTED, HAND, "middle")
    for x, label, color in [(102, "旧版 .bak", INK), (484, "仍是旧版 .bak", ACCENT), (870, "刷新后的 .bak", INK)]:
        s.box(x, 406, 191, 69, fill=PAPER, color=color, weight=2)
        s.text(x+95, 448, label, 21, color, HAND, "middle")
    s.line(197, 360, 197, 396, MUTED, 1.1, dash="3 5")
    s.line(579, 360, 579, 396, ACCENT, 1.1, dash="3 5")
    s.path("M568 370 L590 389 M590 370 L568 389", color=ACCENT, weight=2.5)
    s.arrow(696, 440, 839, 440, color=ACCENT, weight=1.7, dash="4 5")
    s.text(769, 485, "满足条件才刷新", 19, ACCENT, HAND, "middle")
    s.path("M96 531 L96 563 L1110 563 L1110 531", color=MUTED, weight=1.2)
    s.text(600, 545, "Restore 前还要识别文件类型：符号链接不能按普通文件处理。", 23, INK, HAND, "middle")
    s.footer("版本关系示意；实际刷新取决于当前内容的检查结果。", "RESTORE")
    return s


def acceptance():
    s = Sketch("acceptance", "四项验收，逐项留材料",
               "文件、进程、模型输入和任务产物各有一张验收签；用标记与写盘报告、进程与入口、请求或回显、真实产物分别核对。")
    s.heading("4·2", "四项验收，逐项留材料", "检查顺序可以连起来，证据不能互相代签。")
    labels = [("文件已改", "路径与标记", "写盘结果"), ("代码已加载", "新进程", "有效版本与入口"),
              ("模型收到", "最终请求", "或设计过的回显"), ("任务完成", "真实产物", "原始结果与复查")]
    for i, (title, a, b) in enumerate(labels):
        x = 76+i*282
        # Hanging paper inspection tags with a hand-looped string.
        s.path(f"M{x+101} 247 Q{x+85} 202 {x+113} 201 Q{x+145} 210 {x+124} 252",
               color=MUTED, weight=1.7)
        d = f"M{x} 287 L{x+40} 244 L{x+181} 244 L{x+221} 287 L{x+221} 509 L{x} 509 Z"
        s.path(d, fill=RUST if i==3 else PAPER, weight=2.5)
        s.ellipse(x+111, 267, 7, color=MUTED, weight=1)
        s.badge(x+36, 315, str(i+1), color=ACCENT if i==3 else MUTED, radius=16)
        s.text(x+111, 365, title, 27, INK, HAND, "middle")
        s.rule(x+23, 389, 174)
        s.text(x+111, 429, a, 23, INK, anchor="middle")
        s.text(x+111, 464, b, 21, MUTED, anchor="middle")
        if i<3:s.arrow(x+233, 361, x+265, 361, color=MUTED, weight=1.3, dash="3 4")
    s.text(600, 555, "前一项通过，只说明可以继续查下一项。", 24, ACCENT, HAND, "middle")
    s.footer("没有观察到的步骤，留作未测。", "ACCEPTANCE")
    return s


def report():
    s = Sketch("report", "处理等待，不替成果盖章",
               "一份 waiting 回报写明 needs 和 blocked_reason；主会话核对并处理后记录 acknowledged_at，最终成果仍须复查。")
    s.heading("5·2", "处理等待，不替成果盖章", "示意：任务回报的处理记录，与成果验收分别保存。")
    sheet(s, 75, 217, 350, 291, "待处理回报")
    s.text(101, 313, "status: waiting", 24, ACCENT, MONO)
    s.text(101, 361, "needs", 23, INK, MONO)
    s.text(101, 392, "写清所缺资源", 22, MUTED, HAND)
    s.text(101, 437, "blocked_reason", 23, INK, MONO)
    s.text(101, 468, "保留具体阻断", 22, MUTED, HAND)
    s.arrow(451, 350, 713, 350, weight=2.1)
    s.text(583, 303, "主会话核对并处理", 24, INK, HAND, "middle")
    s.text(583, 397, "记录已处理的回报", 21, MUTED, "sans-serif", "middle")
    # Ledger with ruled entry and a pen-shaped time marker, not a success seal.
    s.box(745, 218, 375, 290, fill=PAPER, weight=2.3)
    s.line(787, 220, 787, 507, FAINT, 1.2)
    for y in (290, 351, 411, 471): s.rule(760, y, 344)
    s.text(812, 266, "处理记录", 29, INK, HAND)
    s.text(811, 330, "acknowledged_at", 23, INK, MONO)
    s.text(811, 389, "回报已处理的时间", 22, MUTED, HAND)
    s.text(811, 451, "成果另行验收", 25, ACCENT, HAND)
    s.path("M1063 509 L1090 465 L1098 470 L1072 514 L1060 523 Z", fill=PALE, weight=2)
    s.path("M1060 523 L1064 513 L1072 514 Z", fill=INK, weight=1)
    s.text(600, 560, "waiting、ready 等描述工作状态；原始材料支持结果判断。", 23, INK, HAND, "middle")
    s.footer("避免同一条旧等待，在后续轮次反复触发处理。", "REPORT")
    return s
