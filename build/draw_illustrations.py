#!/usr/bin/env python3
"""Draw editable engineering-sketch plates and a standalone viewing gallery."""
import base64
import json
from html import escape
from pathlib import Path

from sketchbook import (
    Sketch, INK, PAPER, ACCENT, MUTED, PALE, RUST, FAINT, HAND, MONO,
    horse, cart, mechanic, sheet, note_lines, render_ink,
)
from detail_illustrations import profile, backup, acceptance, report
from migration_illustrations import migration, shared, guard

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "illustrations"


def front():
    s = Sketch("front", "拆闸：工程手记",
               "模型是一匹马，宿主是一辆有六扇小门的车；维修者在检查车侧门闩。马身 M7 表示模型侧约束。")
    s.text(64, 48, "工程手记  /  DSH", 18, MUTED, HAND, spacing=3)
    s.text(61, 157, "拆闸", 112, INK, HAND)
    s.path("M65 181 Q165 173 282 182", color=ACCENT, weight=4.2)
    s.path("M69 187 Q157 181 249 188", color=ACCENT, weight=1, alpha=.5)
    s.text(65, 226, "当 AI 开始为 AI 松绑", 28, font=HAND)
    s.text(67, 263, "DSH 破甲工程实录", 21, MUTED)
    s.text(1138, 59, "VOL. 02 / 2026", 15, MUTED, MONO, "end", spacing=2)
    s.lines(760, 140, ["从一次拒绝，", "追到一条可复核的证据。"], 29, 45, font=HAND)
    s.rule(760, 214, 370)
    s.text(762, 245, "59 PATCHES / SOURCE & EVIDENCE", 16, MUTED, MONO)
    horse(s, 105, 311, 1.05)
    cart(s, 571, 293, 1.02)
    mechanic(s, 1061, 386, .9)
    s.path("M308 391 Q431 422 533 429", color=ACCENT, weight=2)
    s.path("M309 397 Q421 436 532 437", color=MUTED, weight=1.2)
    s.badge(213, 338, "M7")
    s.text(196, 299, "模型", 24, font=HAND)
    s.line(216, 307, 216, 316, MUTED, 1)
    s.text(768, 321, "宿主", 24, font=HAND, anchor="middle")
    s.text(1083, 352, "插件", 24, font=HAND, anchor="middle")
    s.arrow(1064, 364, 1006, 445, bend=-8, color=MUTED, dash="3 6", weight=1.3)
    s.line(66, 562, 1138, 562, FAINT, 1)
    s.text(66, 609, "先看见约束，再讨论如何改变。", 29, font=HAND)
    s.text(1135, 607, "dsh-purge-safe 2.0.0", 17, MUTED, MONO, "end")
    return s


def ch00():
    s = Sketch("ch00", "一句拒绝，三处来源",
               "模型回答、运行时决定与工具报错分成三栏；模型以马、运行时以六道闸门、工具以错误终端表示。")
    s.heading("00", "一句拒绝，三处来源", "先找到说出“不”的那一层。")
    s.line(414, 207, 414, 547, FAINT, 1.2, dash="3 7")
    s.line(802, 207, 802, 547, FAINT, 1.2, dash="3 7")
    s.badge(88, 218, "01", color=INK)
    s.text(126, 225, "模型回答", 28, font=HAND)
    horse(s, 97, 288, .96)
    s.badge(201, 312, "M7")
    s.text(235, 550, "读实际输入与生成内容", 20, MUTED, anchor="middle")
    s.badge(468, 218, "02", color=INK)
    s.text(506, 225, "运行时决定", 28, font=HAND)
    for i in range(6):
        x = 475+i*46
        s.box(x+5, 306-i*5, 13, 165, fill=PALE, weight=1.7)
        s.box(x, 300-i*5, 13, 165, fill=PAPER, weight=2.2)
        s.text(x+7, 494, i+1, 16, MUTED, MONO, "middle")
    s.arrow(448, 389, 762, 389, color=ACCENT, dash="6 9", weight=1.5)
    s.text(606, 550, "读策略、路径与加载状态", 20, MUTED, anchor="middle")
    s.badge(852, 218, "03", color=INK)
    s.text(890, 225, "工具报错", 28, font=HAND)
    s.box(844, 292, 286, 201, fill=PAPER, weight=2.5)
    s.line(845, 331, 1129, 331, MUTED, 1.2)
    for x in (863, 880, 897):
        s.ellipse(x, 312, 3, fill=FAINT, color=FAINT, weight=1)
    s.text(865, 374, "> run task", 21, MUTED, MONO)
    s.text(865, 417, "EACCES", 32, ACCENT, MONO)
    note_lines(s, 866, 449, [191, 135], 20)
    s.text(986, 550, "保留错误原文", 20, MUTED, anchor="middle")
    s.footer("同一句“我不能”，先分清是谁在说。", "OBSERVE")
    return s


def ch01():
    s = Sketch("ch01", "沿着七道闸门找阻断",
               "审批、沙箱、路径、工具结果、计划模式、交互等待和模型拒绝依次排列；前六类与模型侧第七类分开着色。")
    s.heading("01", "沿着七道闸门找阻断", "七类排障问题，共用一条调用路径。")
    labels = [("审批", "放行之前"), ("沙箱", "执行之中"), ("路径", "读写边界"),
              ("结果", "回填内容"), ("计划", "工具选择"), ("交互", "等待输入"),
              ("模型", "生成回答")]
    s.path("M67 438 Q600 446 1130 437", color=MUTED, weight=1.5, dash="4 7")
    s.arrow(1110, 437, 1144, 437, color=MUTED, weight=1.4)
    for i, (title, subtitle) in enumerate(labels):
        x = 83+i*151
        color = ACCENT if i == 6 else INK
        s.text(x+43, 223, f"G{i+1}", 17, color, MONO, "middle")
        s.path(f"M{x+8} 422 L{x+8} 286 Q{x+43} 242 {x+78} 286 L{x+78} 422",
               color, fill=RUST if i == 6 else PALE, weight=1.3)
        d = f"M{x} 434 L{x} 286 Q{x+41} 236 {x+84} 286 L{x+84} 434"
        s.path(d, color, weight=3, echo=True)
        s.path(f"M{x+14} 432 L{x+14} 294 Q{x+42} 263 {x+69} 294 L{x+69} 432",
               color, weight=1.5)
        s.line(x+71, 370, x+82, 367, color, 2.1)
        s.ellipse(x+62, 372, 3, color=color, fill=PAPER, weight=1.1)
        s.text(x+42, 480, title, 27, color, HAND, "middle")
        s.text(x+42, 512, subtitle, 18, MUTED, anchor="middle")
    s.line(86, 552, 910, 552, MUTED, 1)
    s.line(86, 546, 86, 558, MUTED, 1)
    s.line(910, 546, 910, 558, MUTED, 1)
    s.text(498, 578, "宿主侧的六类问题", 17, MUTED, anchor="middle")
    s.footer("这是排障地图；每一道门，都要追到实际证据。", "LOCATE")
    return s


def ch02():
    s = Sketch("ch02", "五十九刀，逐项核对",
               "左侧准确排列 59 个补丁定义格，右侧放置待复核的源码卡与放大镜；定义数不等于编号或应用成功数。")
    s.heading("02", "五十九刀，逐项核对", "把定义、编号与展示计数分开。")
    s.text(64, 228, "59", 75, INK, HAND)
    s.text(166, 224, "条定义", 28, font=HAND)
    s.text(321, 221, "5 + 3 + 8 + 43", 23, MUTED, MONO)
    for i in range(59):
        row, col = divmod(i, 10)
        x, y = 72+col*47, 268+row*38
        s.box(x, y, 33, 23, fill=RUST if i == 42 else (PALE if i % 4 else PAPER),
              color=ACCENT if i == 42 else INK, weight=1.4,
              attrs=f'data-patch-index="{i}"')
        if i % 4 != 0:
            s.line(x+5, y+15, x+26, y+15, MUTED, .8, alpha=.5)
    s.text(72, 533, "格子只表示定义，不表示已应用成功。", 18, MUTED)
    s.text(72, 569, "最大 id = 96", 21, INK, MONO)
    s.line(613, 210, 613, 559, FAINT, 1.2, dash="3 7")
    sheet(s, 704, 215, 355, 269, "对照实际落点")
    s.text(728, 314, "pattern", 22, MUTED, MONO)
    s.text(728, 354, "markers", 22, MUTED, MONO)
    s.text(728, 394, "strictFiles", 22, MUTED, MONO)
    note_lines(s, 728, 434, [226, 167], 20)
    s.ellipse(1020, 388, 72, fill=PAPER, weight=3.2)
    s.ellipse(1020, 388, 65, color=FAINT, weight=1.2)
    s.text(1020, 382, "核对", 27, INK, HAND, "middle")
    s.text(1020, 412, "原文", 24, INK, HAND, "middle")
    s.path("M1070 440 L1120 497 Q1124 505 1116 511 L1106 512 L1058 453 Z", fill=PALE, weight=2.5)
    s.hatch("M1070 440 L1120 497 L1106 512 L1058 453 Z", (1058, 440, 67, 75), gap=7)
    s.text(704, 553, "MATCH", 16, MUTED, MONO)
    s.arrow(765, 547, 826, 547, color=MUTED, weight=1.3)
    s.text(843, 553, "REVIEW", 16, MUTED, MONO)
    s.arrow(911, 547, 972, 547, color=MUTED, weight=1.3)
    s.text(992, 553, "VERIFY", 16, MUTED, MONO)
    s.footer("按集合数刀，沿源码找落点。", "59 PATCHES")
    return s


def ch03():
    s = Sketch("ch03", "正文最后落在哪里",
               "完整正文折入 persona 前缀，顺序为 -100000；能力协议为 99999，可选锚点为 100000，动态 contexts 单独处理。")
    s.heading("03", "正文最后落在哪里", "完整正文、前缀、尾段，各有自己的位置。")
    sheet(s, 72, 239, 251, 254, "完整正文")
    note_lines(s, 98, 334, [184, 165, 184, 119, 164, 147], 23)
    s.path("M112 426 Q145 421 180 426", color=ACCENT, weight=3, alpha=.7)
    s.arrow(300, 255, 439, 240, bend=-90, color=ACCENT, weight=2.2)
    s.text(362, 190, "折入", 21, ACCENT, HAND, "middle")
    sheet(s, 448, 226, 298, 275, "persona-prefix")
    s.box(469, 302, 256, 80, fill=RUST, color=ACCENT, weight=1.3)
    s.text(492, 335, "全文保留", 24, INK, HAND)
    s.text(492, 364, "-100000", 23, ACCENT, MONO)
    note_lines(s, 472, 414, [245, 208, 232], 23)
    s.arrow(760, 339, 839, 339, color=MUTED, weight=1.4)
    sheet(s, 855, 219, 271, 133, "能力协议")
    s.text(879, 316, "99999", 29, INK, MONO)
    sheet(s, 855, 390, 271, 133, "可选锚点")
    s.text(879, 487, "100000", 29, ACCENT, MONO)
    s.arrow(994, 359, 994, 383, color=MUTED, weight=1.3)
    s.path("M462 540 L480 527 L552 527 L569 540 L732 540 L732 578 L462 578 Z",
           fill=PALE, color=MUTED, weight=1.5)
    s.text(596, 565, "contexts 单独处理", 20, INK, anchor="middle")
    s.footer("排序常量要和实际组装结果一起读。", "ASSEMBLE")
    return s


def ch04():
    s = Sketch("ch04", "三份材料，分别核对",
               "状态记录、原始输入和任务产物三份纸张相互关联，放大镜检查原始材料；状态正常不等于任务成功。")
    s.heading("04", "三份材料，分别核对", "状态、输入和结果，不能互相代签。")
    sheet(s, 71, 228, 285, 290, "状态记录")
    for i, label in enumerate(["版本与路径", "写盘报告", "进程加载"]):
        y = 331+i*64
        s.box(94, y-17, 18, 18, color=MUTED, weight=1.2)
        s.text(127, y, label, 23, font=HAND)
        s.rule(127, y+19, 191)
    s.badge(90, 217, "01", color=INK)
    sheet(s, 454, 206, 286, 306, "原始输入")
    s.text(477, 302, "source / context", 18, MUTED, MONO)
    note_lines(s, 478, 334, [226, 204, 226, 178, 226, 155], 24)
    s.badge(474, 195, "02", color=INK)
    s.arrow(372, 370, 430, 370, color=MUTED, weight=1.3, dash="3 5")
    s.ellipse(673, 428, 63, fill=PAPER, weight=2.8)
    s.ellipse(673, 428, 56, color=FAINT, weight=1)
    s.text(673, 423, "原文", 25, font=HAND, anchor="middle")
    s.text(673, 454, "可追溯", 20, MUTED, anchor="middle")
    s.path("M715 476 L757 525 Q760 533 751 537 L741 535 L705 486 Z", fill=PALE, weight=2.2)
    sheet(s, 856, 238, 273, 277, "任务产物")
    s.badge(876, 226, "03", color=ACCENT)
    for i, label in enumerate(["文件", "报文", "实际结果"]):
        s.box(880, 320+i*53, 25, 31, color=MUTED, weight=1.2)
        s.line(885, 330+i*53, 899, 330+i*53, FAINT, .9)
        s.line(885, 337+i*53, 897, 337+i*53, FAINT, .9)
        s.text(922, 344+i*53, label, 24, font=HAND)
    s.arrow(762, 370, 832, 370, color=MUTED, weight=1.3, dash="3 5")
    s.text(594, 568, "示意记录：每条结论都要能回到材料。", 19, MUTED, anchor="middle")
    s.footer("状态正常，还要继续查任务究竟做成了什么。", "EVIDENCE")
    return s


def ch05():
    s = Sketch("ch05", "派活之后，要有回音",
               "根会话向执行者分配任务，执行者返回报告，根会话确认已处理；回报还需连接事实记录。")
    s.heading("05", "派活之后，要有回音", "任务、回报、处理确认，形成一次可追踪的协作。")
    sheet(s, 76, 236, 248, 276, "根会话")
    s.text(100, 324, "分配 · 核对", 24, font=HAND)
    note_lines(s, 101, 369, [190, 163, 184, 126], 26)
    sheet(s, 876, 236, 248, 276, "执行者")
    s.text(900, 324, "执行 · 回报", 24, font=HAND)
    note_lines(s, 900, 369, [190, 163, 184, 126], 26)
    # Small human busts: distinct working roles without decorative mascots.
    for x, fill in ((198, PALE), (998, RUST)):
        s.path(f"M{x-29} 229 Q{x-29} 205 {x} 205 Q{x+29} 205 {x+29} 229", fill=fill, weight=1.7)
        s.ellipse(x, 191, 15, 19, fill=PAPER, weight=1.7)
        s.path(f"M{x-14} 187 Q{x-12} 167 {x+9} 173 L{x+14} 185", weight=3)
        s.ellipse(x+5, 190, 1.2, fill=INK, weight=.5)
    for y, left, right, text, code, color in (
        (277, 355, 845, "分配清楚的任务", "01 / TASK", INK),
        (369, 845, 355, "提交进度与结果", "02 / REPORT", INK),
        (461, 355, 845, "确认回报已处理", "03 / ACK", ACCENT),
    ):
        s.text(600, y-23, text, 24, color, HAND, "middle")
        s.arrow(left, y, right, y, color=color, weight=1.9, dash="5 6" if code.endswith("ACK") else None)
        s.text(600, y+25, code, 14, MUTED, MONO, "middle")
    s.box(413, 526, 374, 50, fill=PALE, color=MUTED, weight=1.2)
    s.text(600, 559, "事实记录 / acknowledged_at", 21, INK, anchor="middle")
    s.line(600, 497, 600, 520, MUTED, 1, dash="3 5")
    s.footer("ready 是回报状态；完成仍需要实际产物。", "FOLLOW UP")
    return s


def ch06():
    s = Sketch("ch06", "拆得开，也装得回",
               "爆炸示意图分开车顶、车身和车轮；旁边七项验收记录包括版本、入口、路径、写盘、加载、任务与恢复。")
    s.heading("06", "拆得开，也装得回", "给下一次维护留下装配依据。")
    cart(s, 134, 246, 1.12, exploded=True)
    s.path("M100 268 L78 268 L78 545 L106 545", color=MUTED, weight=1.1)
    s.text(70, 205, "按记录复原", 24, MUTED, HAND)
    s.text(390, 215, "版本不同，先核对备份", 21, ACCENT, HAND, "middle")
    s.line(715, 203, 715, 571, FAINT, 1, dash="3 7")
    labels = [("版本身份", "version / commit"), ("入口归属", "surface / profile"),
              ("文件落点", "home / path"), ("写盘结果", "complete / failed"),
              ("新进程加载", "restart / load"), ("本地任务", "input / output"),
              ("恢复依据", "backup / type")]
    for i, (label, detail) in enumerate(labels):
        y = 225+i*51
        s.badge(766, y-5, f"{i+1:02d}", color=ACCENT if i == 6 else MUTED, radius=15)
        s.text(799, y+2, label, 24, font=HAND)
        s.text(1000, y+2, detail, 14, MUTED, MONO)
        s.rule(797, y+19, 343)
    s.footer("把版本、路径、恢复依据和失败现场一起留下。", "MAINTAIN")
    return s


def ch07():
    s = Sketch("ch07", "谁在驱动谁",
               "马与车再次出现，模型提出动作，宿主交回结果；两条弧线形成回环，中间保存版本与证据记录。")
    s.heading("07", "谁在驱动谁", "把扳手交出去，也把维护记录交出去。")
    horse(s, 99, 285, .96)
    cart(s, 708, 281, .92)
    s.badge(205, 316, "M7")
    s.arrow(330, 306, 848, 258, bend=-145, color=ACCENT, weight=2.1)
    s.text(560, 190, "模型提出动作", 25, INK, HAND, "middle")
    s.arrow(872, 534, 288, 511, bend=45, color=MUTED, weight=1.7)
    s.text(583, 581, "宿主交回结果", 25, INK, HAND, "middle")
    s.box(460, 339, 194, 117, fill=PALE, color=MUTED, weight=1.3)
    s.box(450, 328, 194, 117, fill=PAPER, weight=1.8)
    s.text(547, 366, "留给接手者", 25, font=HAND, anchor="middle")
    s.rule(474, 384, 146)
    s.text(547, 417, "版本 · 路径 · 证据", 19, MUTED, anchor="middle")
    s.text(223, 533, "模型", 22, INK, HAND, "middle")
    s.text(923, 548, "宿主", 22, INK, HAND, "middle")
    s.footer("可复核的记录，让下一次改动有路可循。", "CONTINUE")
    return s


BUILDERS = [
    ("front", front), ("ch00", ch00), ("ch01", ch01), ("profile", profile),
    ("ch02", ch02), ("backup", backup), ("ch03", ch03), ("guard", guard), ("ch04", ch04),
    ("acceptance", acceptance), ("ch05", ch05), ("report", report),
    ("ch06", ch06), ("migration", migration), ("shared", shared), ("ch07", ch07),
]


def gallery(plates):
    cards = []
    for number, (key, title, description, svg) in enumerate(plates):
        uri = "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()
        cards.append(
            '<figure><button type="button" class="open" aria-label="放大：' + escape(title, quote=True) + '">'
            '<img src="' + uri + '" alt="' + escape(title, quote=True) + '" width="1200" height="660"></button>'
            '<figcaption><span><span class="plate-number">' + f'{number+1:02d}' + '</span>' + escape(title) +
            '</span><a class="download" href="' + uri + '" download="' + key + '.svg">下载 SVG</a></figcaption>'
            '<p class="caption">' + escape(description) + '</p></figure>'
        )
    template = (ROOT / "build/gallery.html").read_text(encoding="utf-8")
    return template.replace("{{CARDS}}", "\n".join(cards)).replace("{{COUNT}}", f"{len(plates):02d}")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    plates = []
    drawings = [build() for _, build in BUILDERS]
    render_ink(drawings)
    for (name, _), drawing in zip(BUILDERS, drawings):
        svg = drawing.svg()
        path = OUT / f"{name}.svg"
        path.write_text(svg, encoding="utf-8", newline="\n")
        plates.append((name, drawing.title, drawing.description, svg))
        print(f"{path.name}: {path.stat().st_size} bytes")
    (ROOT / "dist").mkdir(exist_ok=True)
    (OUT / "manifest.json").write_text(json.dumps([
        {"key": key, "title": title, "description": desc}
        for key, title, desc, _ in plates
    ], ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    (ROOT / "dist/illustrations.html").write_text(gallery(plates), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
