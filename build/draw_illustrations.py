#!/usr/bin/env python3
"""生成卷首手绘扉页与每章一张 FA-029 几何图解插画（普鲁士蓝配色）。

输出 illustrations/front.svg 与 ch00.svg … ch07.svg；源文件随仓库维护，构建时复制到 figures 目录。
线条在生成时做可复现的墨线抖动与轻二次描边，得到手绘感；随机种子由图题决定。
图中只用编号与拉丁字母，中文释义写在 Markdown 图注里，避免阅读器字体差异。
"""
import math
import random
import re
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "illustrations"
INK = "#003153"
PAPER = "#f6f1e6"
MUTED = "#7d8b93"
ACCENT = "#b3541e"

TOKEN = re.compile(r"[MmLlHhVvQqTtCcSsAaZz]|[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?")
COMMANDS = set("MmLlHhVvQqTtCcSsAaZz")
SHAPE = re.compile(r"<(path|rect|circle)\b([^>]*)/>")
ATTR = re.compile(r'([\w:-]+)\s*=\s*"([^"]*)"')


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def parse_path(d: str):
    """Parse the subset used by this file: M/L/H/V/Q/Z, absolute or relative."""
    tokens = TOKEN.findall(d)
    i = 0
    pos = (0.0, 0.0)
    start = pos
    command = None
    subpaths = []
    current = None

    def number():
        nonlocal i
        value = float(tokens[i])
        i += 1
        return value

    while i < len(tokens):
        token = tokens[i]
        if token in COMMANDS:
            command = token
            i += 1
            if command in "Zz":
                if current is not None:
                    if math.dist(pos, start) > 1e-6:
                        current.append(("line", pos, start))
                    subpaths[-1][1] = True
                current = None
                pos = start
            continue
        if command is None:
            raise ValueError(f"path data starts with a number: {d!r}")
        relative = command.islower()
        kind = command.upper()
        if kind == "M":
            x, y = number(), number()
            if relative:
                x += pos[0]
                y += pos[1]
            pos = (x, y)
            start = pos
            current = []
            subpaths.append([current, False])
            command = "l" if relative else "L"
        elif kind == "L":
            x, y = number(), number()
            if relative:
                x += pos[0]
                y += pos[1]
            if current is None:
                current = []
                subpaths.append([current, False])
            current.append(("line", pos, (x, y)))
            pos = (x, y)
        elif kind == "H":
            x = number()
            if relative:
                x += pos[0]
            if current is None:
                current = []
                subpaths.append([current, False])
            current.append(("line", pos, (x, pos[1])))
            pos = (x, pos[1])
        elif kind == "V":
            y = number()
            if relative:
                y += pos[1]
            if current is None:
                current = []
                subpaths.append([current, False])
            current.append(("line", pos, (pos[0], y)))
            pos = (pos[0], y)
        elif kind == "Q":
            cx, cy = number(), number()
            x, y = number(), number()
            if relative:
                cx += pos[0]
                cy += pos[1]
                x += pos[0]
                y += pos[1]
            if current is None:
                current = []
                subpaths.append([current, False])
            current.append(("quad", pos, (cx, cy), (x, y)))
            pos = (x, y)
        else:
            raise ValueError(f"unsupported path command {kind}")
    return subpaths


def rough_line(p0, p1, rng, amp):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    length = math.hypot(dx, dy)
    if length < 1e-6:
        return [p0, p1]
    nx, ny = -dy / length, dx / length
    steps = max(2, min(28, int(length / 18) + 1))
    phase = rng.uniform(0, 2 * math.pi)
    frequency = rng.uniform(1.0, 2.2)
    points = []
    for step in range(steps):
        t = step / steps
        base = (p0[0] + dx * t, p0[1] + dy * t)
        wobble = amp * math.sin(math.pi * t) * (
            0.78 * math.sin(2 * math.pi * frequency * t + phase)
            + 0.22 * rng.uniform(-1.0, 1.0)
        )
        points.append((base[0] + nx * wobble, base[1] + ny * wobble))
    points.append(p1)
    return points


def rough_quad(p0, control, p1, rng, amp):
    approximate = math.dist(p0, control) + math.dist(control, p1)
    steps = max(6, min(32, int(approximate / 16) + 1))
    phase = rng.uniform(0, 2 * math.pi)
    frequency = rng.uniform(1.0, 2.0)
    points = []
    for step in range(steps):
        t = step / steps
        base = (
            (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * control[0] + t ** 2 * p1[0],
            (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * control[1] + t ** 2 * p1[1],
        )
        dx = 2 * (1 - t) * (control[0] - p0[0]) + 2 * t * (p1[0] - control[0])
        dy = 2 * (1 - t) * (control[1] - p0[1]) + 2 * t * (p1[1] - control[1])
        norm = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / norm, dx / norm
        wobble = amp * math.sin(math.pi * t) * (
            0.75 * math.sin(2 * math.pi * frequency * t + phase)
            + 0.25 * rng.uniform(-1.0, 1.0)
        )
        points.append((base[0] + nx * wobble, base[1] + ny * wobble))
    points.append(p1)
    return points


def rough_rect(x, y, width, height, rng, amp):
    points = [(x, y)]
    for corner in ((x + width, y), (x + width, y + height), (x, y + height), (x, y)):
        points.extend(rough_line(points[-1], corner, rng, amp)[1:])
    return points


def rough_circle(cx, cy, radius, rng, amp):
    steps = 30
    phase = rng.uniform(0, 2 * math.pi)
    points = []
    for step in range(steps):
        angle = 2 * math.pi * step / steps
        r = radius + amp * (
            0.72 * math.sin(3 * angle + phase) + 0.28 * math.sin(7 * angle + phase * 2)
        )
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    points.append(points[0])
    return points


def points_to_d(points, closed):
    out = []
    last = None
    for point in points:
        if last is not None and math.dist(point, last) < 0.01:
            continue
        out.append(("M" if last is None else "L") + f" {fmt(point[0])} {fmt(point[1])}")
        last = point
    if closed:
        out.append("Z")
    return " ".join(out)


def rough_element(tag, raw_attrs, rng, amp):
    attrs = dict(ATTR.findall(raw_attrs))
    if tag == "path":
        subpaths = parse_path(attrs.pop("d"))
        coords = [point for segments, _ in subpaths for segment in segments for point in segment[1:]]
        if coords:
            xs = [point[0] for point in coords]
            ys = [point[1] for point in coords]
            diagonal = math.hypot(max(xs) - min(xs), max(ys) - min(ys))
            if diagonal < 30:
                amp = min(amp, max(0.35, diagonal * 0.055))
        parts = []
        for segments, closed in subpaths:
            points = []
            for segment in segments:
                if segment[0] == "line":
                    chunk = rough_line(segment[1], segment[2], rng, amp)
                else:
                    chunk = rough_quad(segment[1], segment[2], segment[3], rng, amp)
                points.extend(chunk if not points else chunk[1:])
            if points:
                parts.append(points_to_d(points, closed))
        d = " ".join(parts)
    elif tag == "rect":
        x, y = float(attrs.pop("x")), float(attrs.pop("y"))
        width, height = float(attrs.pop("width")), float(attrs.pop("height"))
        amp = min(amp, max(0.35, min(width, height) * 0.08))
        d = points_to_d(rough_rect(x, y, width, height, rng, amp), True)
    elif tag == "circle":
        cx, cy = float(attrs.pop("cx")), float(attrs.pop("cy"))
        radius = float(attrs.pop("r"))
        amp = min(amp, max(0.35, radius * 0.08))
        d = points_to_d(rough_circle(cx, cy, radius, rng, amp), True)
    else:
        return None
    attrs.setdefault("stroke-linecap", "round")
    attrs.setdefault("stroke-linejoin", "round")
    rendered = " ".join(f'{key}="{value}"' for key, value in attrs.items())
    return f'<path d="{d}" {rendered}/>'


def roughen_fragment(fragment, rng, default_stroke=INK):
    """Turn geometric primitives into hand-drawn ink strokes.

    The first pass wobbles every line; plain ink outlines get a lighter second pass,
    like a pen going over the same contour twice. Text elements are left untouched.
    """
    def replace(match):
        tag, raw_attrs = match.group(1), match.group(2)
        info = dict(ATTR.findall(raw_attrs))
        stroke = info.get("stroke", default_stroke)
        primary = rough_element(tag, raw_attrs, rng, 1.15)
        if primary is None:
            return match.group(0)
        second = ""
        if (
            stroke in (INK, "currentColor")
            and "stroke-dasharray" not in info
            and info.get("fill", "none") == "none"
        ):
            child = rough_element(
                tag, raw_attrs, random.Random(rng.randrange(1 << 30)), 1.15 * 1.25
            )
            if child:
                second = child.replace("/>", ' opacity="0.5"/>')
        return primary + second

    return SHAPE.sub(replace, fragment)


def frame(inner: str, title: str) -> str:
    rng = random.Random(zlib.crc32(title.encode("utf-8")))
    border = rough_element(
        "rect",
        f'x="16" y="16" width="768" height="388" fill="none" stroke="{INK}" stroke-width="2"',
        random.Random(zlib.crc32((title + ":border").encode("utf-8"))),
        1.0,
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 420" role="img" aria-label="{title}">
<title>{title}</title>
<rect width="800" height="420" fill="{PAPER}"/>
{border}
<g fill="none" stroke="{INK}" stroke-width="2" stroke-linejoin="round">{roughen_fragment(inner, rng)}</g>
</svg>
'''


def label(x: int, y: int, text: str, size: int = 16, color: str = INK) -> str:
    return (f'<text x="{x}" y="{y}" fill="{color}" stroke="none" '
            f'font-family="sans-serif" font-size="{size}">{text}</text>')


def text_center(x: int, y: int, text: str, size: int = 16, color: str = INK,
                weight: str = "normal", spacing: int = 0) -> str:
    extra = f' font-weight="{weight}"' if weight != "normal" else ""
    if spacing:
        extra += f' letter-spacing="{spacing}"'
    return (f'<text x="{x}" y="{y}" text-anchor="middle" fill="{color}" stroke="none" '
            f'font-family="sans-serif" font-size="{size}"{extra}>{text}</text>')


def ch00() -> str:
    parts = []
    # 马代表模型；第七道模型自拒标在马身上
    parts += ['<rect x="70" y="185" width="120" height="62"/>',
              '<path d="M190 185 L225 155 L248 166 L232 205 L190 220 Z"/>',
              '<path d="M70 247 L58 320 M110 247 L104 320 M165 247 L178 320 M190 240 L215 315"/>',
              '<path d="M70 200 L40 185 L52 168"/>',
              f'<circle cx="150" cy="150" r="22" stroke="{ACCENT}" stroke-width="2"/>',
              label(140, 155, "M7", 12, ACCENT),
              f'<path d="M160 170 L178 190" stroke="{ACCENT}"/>',
              label(96, 360, "MODEL", 18)]
    # 六道宿主闸门
    for i in range(6):
        x = 300 + i * 42
        parts += [f'<rect x="{x}" y="120" width="10" height="180" fill="{INK if i % 2 else "none"}"/>',
                  label(x - 2, 110, str(i + 1), 14)]
    parts.append('<path d="M250 300 L560 300" stroke-dasharray="6 6"/>')
    # 车：焊死的门
    parts += ['<path d="M620 250 L645 200 L720 200 L750 250 Z"/>',
              '<rect x="600" y="250" width="160" height="52"/>',
              '<circle cx="635" cy="306" r="16"/><circle cx="725" cy="306" r="16"/>',
              label(640, 360, "HARNESS", 18)]
    return frame("".join(parts), "chap00 six host gates and model refusal")
 


def ch01() -> str:
    parts = []
    for i in range(7):
        x = 78 + i * 96
        parts += [f'<path d="M{x} 300 L{x} 150 Q{x+28} 118 {x+56} 150 L{x+56} 300"/>',
                  f'<path d="M{x+10} 300 L{x+10} 172 Q{x+28} 152 {x+46} 172 L{x+46} 300" stroke="{MUTED}"/>',
                  label(x + 16, 340, f"G{i+1}", 18)]
    parts += ['<path d="M60 372 L740 372"/>',
              '<path d="M60 372 L740 372" stroke-dasharray="4 10" stroke="white"/>',
              '<path d="M700 372 l-18 -12 v24 Z" fill="currentColor"/>',
              label(60, 70, "SEVEN GATES / ONE PATH", 20)]
    return frame("".join(parts), "chap01 seven gates")


def ch02() -> str:
    parts = []
    # 左栏：86 条补丁的定位网格，其中一格标为漂移锚点
    for i in range(86):
        row, col = divmod(i, 8)
        x, y = 54 + col * 44, 78 + row * 24
        fill = ACCENT if i == 42 else (INK if i % 7 else "none")
        parts.append(f'<rect x="{x}" y="{y}" width="30" height="14" fill="{fill}"/>')
    # 右栏：漂移 -> 诊断候选 -> 重锚 -> 验证
    parts += ['<path d="M440 60 L440 360" stroke-dasharray="6 8"/>',
              label(470, 92, "DRIFT", 18, ACCENT),
              '<path d="M470 108 L556 108" stroke-dasharray="4 6"/>',
              '<path d="M548 102 l10 6 -10 6 Z"/>',
              '<circle cx="620" cy="180" r="52"/>',
              '<path d="M656 216 L700 260"/>',
              label(588, 186, "ANCHOR", 14),
              '<rect x="470" y="270" width="230" height="50"/>',
              label(486, 300, "REANCHOR", 18),
              '<path d="M585 232 L585 270" stroke-dasharray="4 6"/>',
              label(470, 352, "VERIFY", 18),
              '<path d="M540 340 l14 14 30 -34"/>',
              label(54, 390, "86 PATCHES / DIAGNOSE -> REANCHOR", 18)]
    return frame("".join(parts), "chap02 drift diagnosis and reanchor")


def ch03() -> str:
    parts = []
    for i in range(8):
        x = 150 + i * 72
        fill = ACCENT if i == 4 else INK
        parts += [f'<rect x="{x}" y="180" width="54" height="86" fill="none" stroke="{fill}" stroke-width="2"/>',
                  label(x + 9, 232, f"0{i+1}", 18, fill)]
    parts += ['<path d="M422 170 Q380 80 140 130" stroke-dasharray="7 7"/>',
              '<path d="M140 130 l20 -12 v24 Z"/>',
              label(150, 118, "-100000", 16, ACCENT),
              '<path d="M110 300 L700 300"/>', label(96, 356, "PROMPT ORDER", 20)]
    return frame("".join(parts), "chap03 prompt queue")


def ch04() -> str:
    parts = []
    for r in range(4):
        y = 96 + r * 56
        parts.append(f'<path d="M70 {y} L700 {y}"/>')
        for c in range(6):
            x = 70 + c * 105
            parts.append(f'<path d="M{x} {y} L{x} {y+56}"/>')
    parts += [label(84, 132, "OK", 16), label(294, 244, "PENDING", 16, ACCENT),
              label(510, 300, "OK", 16), '<circle cx="400" cy="205" r="62"/>',
              label(366, 212, "NONCE", 16), '<path d="M444 250 L500 306"/>',
              label(300, 390, "SELFCHECK / PROBE / EVIDENCE LEDGER", 18)]
    return frame("".join(parts), "chap04 evidence ledger")


def ch05() -> str:
    parts = []
    parts += ['<rect x="70" y="90" width="240" height="210"/>',
              '<rect x="490" y="90" width="240" height="210"/>',
              label(110, 130, "DISPATCH", 20), label(530, 130, "EXECUTOR", 20)]
    for i in range(3):
        parts.append(f'<path d="M110 {170+i*36} L270 {170+i*36}" stroke="{MUTED}"/>')
        parts.append(f'<path d="M530 {170+i*36} L690 {170+i*36}" stroke="{MUTED}"/>')
    parts += ['<path d="M320 175 L480 175"/>', '<path d="M462 165 l18 10 -18 10 Z"/>',
              label(330, 158, "TASK", 16),
              '<path d="M320 255 L480 255" stroke-dasharray="8 8"/>',
              '<path d="M350 238 L450 272 M450 238 L350 272" stroke="currentColor" stroke-width="3"/>',
              label(330, 292, "TRIGGER", 16, ACCENT),
              '<path d="M70 340 L730 340"/>', label(70, 372, "EVIDENCE LEDGER", 18)]
    return frame("".join(parts), "chap05 commander")


def ch06() -> str:
    parts = []
    parts += ['<path d="M250 250 L300 195 L520 195 L580 250 Z"/>',
              '<rect x="220" y="250" width="390" height="58"/>',
              '<circle cx="300" cy="312" r="26"/><circle cx="530" cy="312" r="26"/>']
    for i in range(7):
        x = 240 + i * 54
        y = 120 if i % 2 == 0 else 370
        parts += [f'<circle cx="{x}" cy="{y}" r="14"/>', label(x - 5, y + 6, str(i + 1), 14)]
        parts.append(f'<path d="M{x} {y+14 if i%2==0 else y-14} L{x} {185 if i%2==0 else 340}" stroke="{MUTED}" stroke-dasharray="4 6"/>')
    parts += [label(70, 80, "DISASSEMBLY / REASSEMBLY", 20),
              '<path d="M70 90 L730 90"/>']
    return frame("".join(parts), "chap06 assembly")


def ch07() -> str:
    parts = []
    parts += ['<path d="M120 250 L160 200 L200 215 L185 255 L120 270 Z"/>',
              '<path d="M120 250 L100 320 M150 265 L145 325 M180 260 L195 320"/>',
              '<path d="M560 220 L590 180 L680 180 L720 225 Z"/>',
              '<rect x="540" y="225" width="190" height="55"/>',
              '<circle cx="575" cy="285" r="17"/><circle cx="695" cy="285" r="17"/>',
              '<path d="M200 215 Q380 100 590 180" stroke-dasharray="7 7"/>',
              '<path d="M570 172 l22 6 -16 16 Z"/>',
              '<path d="M700 320 Q400 390 190 320" stroke-dasharray="7 7"/>',
              '<path d="M210 312 l-22 6 16 16 Z"/>',
              label(330, 70, "WHO DRIVES WHOM", 20)]
    return frame("".join(parts), "chap07 loop")


def front() -> str:
    """卷首扉页：马（模型）拉车（宿主），车上七道小门，扳手（插件）卸下最后一枚门闩。"""
    parts = []
    parts.append(text_center(400, 86, "CHAIZHA", 52, INK, "bold", 8))
    parts.append(text_center(400, 114, "SEVEN GATES / ONE PATH", 15, MUTED, "normal", 4))
    parts.append(f'<path d="M312 98 L488 98" stroke="{ACCENT}" stroke-width="2"/>')

    # 地平线
    parts.append('<path d="M70 330 L730 330" stroke-dasharray="5 7"/>')

    # 马：躯干、颈头、耳朵、四条腿、尾与鬃；M7 是模型自身的第七道闸
    parts.append('<path d="M78 245 L78 210 Q80 192 108 190 L168 190 Q190 192 194 212 L194 245 Z"/>')
    parts.append('<path d="M168 200 L204 160 L236 170 L220 205 L194 220"/>')
    parts.append('<path d="M204 160 L198 145 L214 154"/>')
    parts.append('<path d="M90 245 L82 320 M118 245 L116 320 M160 245 L168 320 M188 244 L198 320"/>')
    parts.append('<path d="M78 210 Q50 200 42 170"/>')
    parts.append('<path d="M200 165 Q185 150 170 160"/>')
    parts.append(f'<circle cx="222" cy="181" r="3" fill="{INK}"/>')
    parts.append(f'<circle cx="130" cy="176" r="18" stroke="{ACCENT}"/>')
    parts.append(text_center(130, 181, "M7", 11, ACCENT))

    # 缰绳/挽具线接到车上
    parts.append('<path d="M194 226 L350 240" stroke-dasharray="5 7"/>')

    # 车：顶棚、车身、两只轮
    parts.append('<path d="M380 220 L410 190 L570 190 L600 220 Z"/>')
    parts.append('<rect x="350" y="220" width="250" height="70"/>')
    parts.append('<circle cx="400" cy="305" r="26"/><circle cx="560" cy="305" r="26"/>')
    parts.append('<circle cx="400" cy="305" r="9"/><circle cx="560" cy="305" r="9"/>')

    # 车侧七道小门
    for i in range(7):
        x = 362 + i * 34
        parts.append(f'<path d="M{x} 285 L{x} 247 Q{x+11} 230 {x+22} 247 L{x+22} 285"/>')

    # 扳手（插件）正在卸下第七道门闩
    parts.append('<circle cx="690" cy="230" r="14"/>')
    parts.append('<path d="M690 244 L690 292 M690 258 L650 270 M690 258 L710 278 '
                 'M690 292 L675 325 M690 292 L706 325"/>')
    parts.append('<path d="M650 270 L615 262"/>')
    parts.append('<path d="M615 262 Q606 254 600 262 Q606 270 615 266"/>')
    parts.append(f'<circle cx="592" cy="262" r="6" stroke="{ACCENT}"/>')
    parts.append(f'<path d="M584 250 L578 244 M600 250 L606 244 M584 274 L578 280" stroke="{ACCENT}"/>')

    # 三层关系与底部署名
    parts.append(text_center(120, 355, "MODEL", 18, INK))
    parts.append(text_center(475, 355, "HARNESS", 18, INK))
    parts.append(text_center(690, 355, "PLUGIN", 18, INK))
    parts.append(text_center(400, 392, "86 PATCHES / 25 LAYERS / ONE ECHO", 13, MUTED, "normal", 3))
    return frame("".join(parts), "frontispiece: horse, cart, seven gates")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, build in [("front", front), ("ch00", ch00), ("ch01", ch01), ("ch02", ch02),
                        ("ch03", ch03), ("ch04", ch04), ("ch05", ch05), ("ch06", ch06),
                        ("ch07", ch07)]:
        path = OUT / f"{name}.svg"
        path.write_text(build(), encoding="utf-8")
        print(f"{path.name}: {path.stat().st_size} bytes")


if __name__ == "__main__":
    main()
