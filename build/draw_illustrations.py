#!/usr/bin/env python3
"""生成每章一张 FA-029 几何图解插画（普鲁士蓝配色）。

输出 illustrations/ch00.svg … ch07.svg；源文件随仓库维护，构建时复制到 figures 目录。
图中只用编号与拉丁字母，中文释义写在 Markdown 图注里，避免阅读器字体差异。
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "illustrations"
INK = "#003153"
PAPER = "#f6f1e6"
MUTED = "#7d8b93"
ACCENT = "#b3541e"


def frame(inner: str, title: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 420" role="img" aria-label="{title}">
<title>{title}</title>
<rect width="800" height="420" fill="{PAPER}"/>
<rect x="16" y="16" width="768" height="388" fill="none" stroke="{INK}" stroke-width="2"/>
<g fill="none" stroke="{INK}" stroke-width="2" stroke-linejoin="round">{inner}</g>
</svg>
'''


def label(x: int, y: int, text: str, size: int = 16, color: str = INK) -> str:
    return (f'<text x="{x}" y="{y}" fill="{color}" stroke="none" '
            f'font-family="sans-serif" font-size="{size}">{text}</text>')


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
              '<path d="M444 250 L500 306"/>', label(340, 390, "EVIDENCE LEDGER", 20)]
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


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, build in [("ch00", ch00), ("ch01", ch01), ("ch02", ch02), ("ch03", ch03),
                        ("ch04", ch04), ("ch05", ch05), ("ch06", ch06), ("ch07", ch07)]:
        path = OUT / f"{name}.svg"
        path.write_text(build(), encoding="utf-8")
        print(f"{path.name}: {path.stat().st_size} bytes")


if __name__ == "__main__":
    main()
