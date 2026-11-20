"""Small deterministic pen-and-paper drawing primitives for the book's SVG plates.

Authored curves carry the forms; restrained stroke drift, selective echoes and
clipped hatching provide texture. Text remains native, searchable SVG text.
"""
from html import escape
import json
import math
from pathlib import Path
import random
import re
import subprocess
import zlib

WIDTH, HEIGHT = 1200, 660
INK = "#173f50"
PAPER = "#faf7ef"
ACCENT = "#ad5538"
MUTED = "#637c80"
PALE = "#e2e9e2"
RUST = "#efded0"
FAINT = "#c9d1c7"
SANS = "Microsoft YaHei, Noto Sans CJK SC, sans-serif"
HAND = "KaiTi, STKaiti, Noto Serif CJK SC, serif"
MONO = "Consolas, Liberation Mono, monospace"


def n(value):
    return f"{value:.2f}".rstrip("0").rstrip(".")


def centerlines(path):
    """Flatten the authored M/L/Q/C/Z subset, preserving separate pen lifts."""
    tokens = re.findall(r"[A-Za-z]|[-+]?(?:\d*\.\d+|\d+)", path)
    index, current, start = 0, (0, 0), (0, 0)
    points = []
    while index < len(tokens):
        command = tokens[index]
        index += 1
        kind = command.upper()
        if kind not in ("M", "L", "Q", "C", "Z"):
            raise ValueError(f"Unsupported pen path command: {command}")
        if kind == "Z":
            if points:
                points.append(start)
                yield points, True
            points, current = [], start
            continue
        count = {"M": 1, "L": 1, "Q": 2, "C": 3}[kind]
        coords = []
        for _ in range(count):
            x, y = float(tokens[index]), float(tokens[index+1])
            index += 2
            coords.append((x+current[0], y+current[1]) if command.islower() else (x, y))
        if kind == "M":
            if points:
                yield points, False
            start = current = coords[0]
            points = [current]
            continue
        controls = [current, *coords]
        length = sum(math.dist(a, b) for a, b in zip(controls, controls[1:]))
        steps = max(2, math.ceil(length/5))
        for step in range(1, steps+1):
            t = step/steps
            layer = controls
            while len(layer) > 1:
                layer = [tuple((1-t)*a[j]+t*b[j] for j in (0, 1))
                         for a, b in zip(layer, layer[1:])]
            points.append(layer[0])
        current = coords[-1]
    if points:
        yield points, False


def render_ink(drawings):
    """One dependency call per build; output SVG needs no runtime JavaScript."""
    strokes = [stroke for drawing in drawings for stroke in drawing.pen_strokes]
    result = subprocess.run(
        ["bun", str(Path(__file__).with_name("render_ink.mjs"))],
        input=json.dumps(strokes), capture_output=True, text=True, encoding="utf-8",
        check=True, timeout=60,
    )
    outlines = json.loads(result.stdout)
    if len(outlines) != len(strokes):
        raise ValueError("Pen renderer returned an incomplete set of outlines")
    offset = 0
    for drawing in drawings:
        drawing.pen_paths = outlines[offset:offset+len(drawing.pen_strokes)]
        offset += len(drawing.pen_strokes)


class Sketch:
    def __init__(self, key, title, description):
        self.key, self.title, self.description = key, title, description
        self.rng = random.Random(zlib.crc32(key.encode()))
        self.parts = []
        self.pen_strokes = []
        self.pen_paths = None
        self.raw(f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{PAPER}"/>')
        # Sparse paper fibres: vector marks, not a bitmap texture or noise filter.
        for _ in range(140):
            x, y = self.rng.uniform(25, 1175), self.rng.uniform(22, 638)
            self.path(f"M{n(x)} {n(y)} l{n(self.rng.uniform(1, 3.5))} -.4",
                      color=MUTED, weight=.55, alpha=.13)

    def raw(self, markup):
        self.parts.append(markup)

    def group(self, x=0, y=0, scale=1, rotation=0):
        self.raw(f'<g transform="translate({n(x)} {n(y)}) scale({n(scale)}) rotate({n(rotation)})">')

    def end(self):
        self.raw("</g>")

    def path(self, d, color=INK, fill="none", weight=2.2, alpha=1, echo=False,
             dash=None, attrs=""):
        if weight >= 1.6 and alpha >= .7 and not dash and color != "none":
            if fill != "none":
                self.raw(f'<path d="{d}" fill="{fill}" opacity="{n(alpha)}" {attrs}/>')
            elif attrs:
                self.raw(f'<g {attrs}></g>')
            for points, closed in centerlines(d):
                if len(points) < 2:
                    continue
                distances = [0]
                for a, b in zip(points, points[1:]):
                    distances.append(distances[-1]+math.dist(a, b))
                total = distances[-1] or 1
                phase = zlib.crc32(d.encode()) / 2**32 * math.tau
                pressured = [[round(x, 3), round(y, 3),
                              round(.52+.22*math.sin(phase+math.tau*distance/total), 4)]
                             for (x, y), distance in zip(points, distances)]
                pen_index = len(self.pen_strokes)
                self.pen_strokes.append({"points": pressured, "width": weight, "closed": closed})
                self.raw(f'<path d="{{{{pen:{pen_index}}}}}" fill="{color}" '
                         f'opacity="{n(alpha)}" data-ink="pressure"/>')
            return
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.raw(f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{n(weight)}" '
                 f'opacity="{n(alpha)}" stroke-linecap="round" stroke-linejoin="round"{extra} {attrs}/>')
        if echo and fill == "none":
            self.raw(f'<path d="{d}" fill="none" stroke="{color}" stroke-width=".75" '
                     'opacity=".22" transform="translate(.7 -.5)" stroke-linecap="round"/>')

    def line(self, x1, y1, x2, y2, color=INK, weight=1.8, alpha=1, dash=None, echo=False):
        length = math.hypot(x2-x1, y2-y1) or 1
        drift = self.rng.uniform(-1, 1) * min(1.5, length / 100)
        cx = (x1+x2)/2 - (y2-y1)/length*drift
        cy = (y1+y2)/2 + (x2-x1)/length*drift
        self.path(f"M{n(x1)} {n(y1)} Q{n(cx)} {n(cy)} {n(x2)} {n(y2)}",
                  color=color, weight=weight, alpha=alpha, dash=dash, echo=echo)

    def box(self, x, y, w, h, fill="none", color=INK, weight=2, attrs=""):
        drift = self.rng.uniform(-1.1, 1.1)
        d = (f"M{n(x+2)} {n(y)} Q{n(x+w/2)} {n(y+drift)} {n(x+w-2)} {n(y+1)} "
             f"Q{n(x+w+1)} {n(y+h/2)} {n(x+w)} {n(y+h-1)} "
             f"Q{n(x+w/2)} {n(y+h-drift)} {n(x)} {n(y+h)} "
             f"Q{n(x-1)} {n(y+h/2)} {n(x+2)} {n(y)} Z")
        self.path(d, color=color, fill=fill, weight=weight, attrs=attrs)
        if w > 70 and h > 50:
            self.line(x+4, y+3, x+w*.78, y+2, color=color, weight=.7, alpha=.27)
        return d

    def ellipse(self, x, y, rx, ry=None, color=INK, fill="none", weight=2, alpha=1):
        ry = rx if ry is None else ry
        k = .55228
        d = (f"M{n(x-rx)} {n(y)} "
             f"C{n(x-rx)} {n(y-ry*k)} {n(x-rx*k)} {n(y-ry)} {n(x)} {n(y-ry)} "
             f"C{n(x+rx*k)} {n(y-ry+.4)} {n(x+rx)} {n(y-ry*k)} {n(x+rx)} {n(y)} "
             f"C{n(x+rx-.3)} {n(y+ry*k)} {n(x+rx*k)} {n(y+ry)} {n(x)} {n(y+ry)} "
             f"C{n(x-rx*k)} {n(y+ry)} {n(x-rx)} {n(y+ry*k)} {n(x-rx)} {n(y)} Z")
        self.path(d, color, fill, weight, alpha)
        return d

    def hatch(self, d, bounds, color=MUTED, gap=8, alpha=.34, reverse=False):
        # Clip each stroke geometrically. Some SVG readers ignore nested clipPath
        # elements; explicit endpoints keep the shading portable to those readers.
        tokens = re.findall(r"[MLQZ]|[-+]?(?:\d*\.\d+|\d+)", d)
        polygon = []
        index = 0
        while index < len(tokens):
            command = tokens[index]
            index += 1
            if command in ("M", "L"):
                polygon.append((float(tokens[index]), float(tokens[index+1])))
                index += 2
            elif command == "Q":
                start = polygon[-1]
                control = (float(tokens[index]), float(tokens[index+1]))
                end = (float(tokens[index+2]), float(tokens[index+3]))
                index += 4
                for step in range(1, 13):
                    t = step/12
                    polygon.append(tuple((1-t)**2*start[axis]+2*(1-t)*t*control[axis]+t*t*end[axis] for axis in (0, 1)))
            elif command != "Z":
                raise ValueError(f"Unsupported hatch outline: {command}")
        x, y, w, h = bounds
        for pos in range(int(-h-20), int(w+h+20), gap):
            end = pos-h*.65 if reverse else pos+h*.65
            x0, y0 = x+pos, y-5
            dx, dy = end-pos, h+10
            intersections = []
            for a, b in zip(polygon, polygon[1:]+polygon[:1]):
                ex, ey = b[0]-a[0], b[1]-a[1]
                denominator = dx*ey-dy*ex
                if abs(denominator) < 1e-9:
                    continue
                t = ((a[0]-x0)*ey-(a[1]-y0)*ex)/denominator
                u = ((a[0]-x0)*dy-(a[1]-y0)*dx)/denominator
                if 0 <= t <= 1 and 0 <= u < 1:
                    intersections.append(t)
            intersections.sort()
            for start, stop in zip(intersections[::2], intersections[1::2]):
                self.line(x0+dx*start, y0+dy*start, x0+dx*stop, y0+dy*stop,
                          color, .95, alpha)

    def text(self, x, y, content, size=22, color=INK, font=SANS, anchor="start",
             weight="normal", spacing=0):
        # At the A4 print width, 21 SVG units stay above 8.5 pt. Running plate
        # codes are ornamental; all Chinese explanatory labels share this floor.
        if re.search(r"[\u4e00-\u9fff]", str(content)):
            size = max(size, 21)
        self.raw(f'<text x="{n(x)}" y="{n(y)}" fill="{color}" font-family="{font}" '
                 f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" '
                 f'letter-spacing="{spacing}">{escape(str(content))}</text>')

    def lines(self, x, y, lines, size=22, leading=32, **kwargs):
        for i, content in enumerate(lines):
            self.text(x, y+i*leading, content, size=size, **kwargs)

    def arrow(self, x1, y1, x2, y2, bend=0, color=INK, dash=None, weight=2):
        cx, cy = (x1+x2)/2, (y1+y2)/2+bend
        self.path(f"M{n(x1)} {n(y1)} Q{n(cx)} {n(cy)} {n(x2)} {n(y2)}",
                  color, weight=weight, echo=True, dash=dash)
        angle = math.atan2(y2-cy, x2-cx)
        for offset in (-.48, .48):
            self.line(x2, y2, x2-13*math.cos(angle+offset), y2-13*math.sin(angle+offset),
                      color, weight)

    def badge(self, x, y, text, color=ACCENT, radius=19, fill=PAPER):
        self.ellipse(x, y, radius, color=color, fill=fill, weight=1.8)
        self.text(x, y+6, text, 17, color, MONO, "middle")

    def rule(self, x, y, w, color=FAINT):
        self.line(x, y, x+w, y+.6, color, 1.1)

    def heading(self, number, title, subtitle):
        self.text(62, 48, "拆闸 / 工程手记", 18, MUTED, HAND, spacing=2)
        self.text(1138, 48, f"PLATE {number}", 15, MUTED, MONO, "end", spacing=2)
        self.text(60, 108, title, 39, INK, HAND)
        self.text(62, 145, subtitle, 19, MUTED)
        self.rule(60, 165, 1080)

    def footer(self, sentence, code):
        self.line(60, 610, 93, 609, ACCENT, 3.1)
        self.text(108, 617, sentence, 22, INK, HAND)
        self.text(1140, 618, code, 14, MUTED, MONO, "end", spacing=1.5)

    def svg(self):
        if self.pen_paths is None:
            raise ValueError("Call render_ink before exporting the drawing")
        body = "\n".join(self.parts)
        body = re.sub(r"\{\{pen:(\d+)\}\}", lambda m: self.pen_paths[int(m[1])], body)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" '
                f'role="img" aria-labelledby="{self.key}-title {self.key}-desc" data-plate="{self.key}">\n'
                f'<title id="{self.key}-title">{escape(self.title)}</title>\n'
                f'<desc id="{self.key}-desc">{escape(self.description)}</desc>\n'
                + body + "\n</svg>\n")


def wheel(s, x, y, r=29):
    s.ellipse(x, y, r, fill=PAPER, weight=2.8)
    s.ellipse(x, y, r-5, color=MUTED, weight=1.1)
    for i in range(10):
        angle = math.tau*i/10+.12
        s.line(x+7*math.cos(angle), y+7*math.sin(angle),
               x+(r-6)*math.cos(angle), y+(r-6)*math.sin(angle), MUTED, 1)
    s.ellipse(x, y, 6, fill=INK, weight=1)


def horse(s, x, y, scale=1):
    s.group(x, y, scale)
    s.ellipse(121, 222, 139, 7, color=FAINT, fill=PALE, weight=.6)
    # Far legs remain lighter; the near silhouette carries the weight.
    s.path("M68 139 L79 151 L63 209 L48 212 L52 199 Z", fill=PALE, color=MUTED, weight=1.8)
    s.path("M158 129 L174 143 L198 207 L182 211 L160 170 Z", fill=PALE, color=MUTED, weight=1.8)
    body = ("M28 96 C25 78 53 67 86 73 L135 77 Q153 80 162 60 "
            "L178 30 L175 11 L191 22 L198 15 L205 33 L231 49 "
            "Q247 55 241 68 Q239 77 218 80 L199 74 Q188 101 181 123 "
            "L175 147 L180 209 L166 213 L154 165 L145 146 Q115 152 84 143 "
            "L65 207 L50 211 L62 154 L44 145 L38 200 L21 207 L26 149 "
            "Q16 128 28 96 Z")
    s.path(body, fill=PAPER, weight=3)
    shade = "M29 119 Q55 138 86 131 Q121 144 161 128 L175 148 Q122 160 83 144 L44 146 Z"
    s.path(shade, color="none", fill=PALE)
    s.hatch(shade, (25, 120, 158, 35), gap=7, alpha=.43)
    s.path("M34 93 Q50 78 74 80 M87 84 Q113 91 139 86 M155 90 Q171 74 180 44", color=MUTED, weight=1.1)
    s.path("M27 94 C7 88 8 119 -6 133 C1 129 11 117 12 103 M24 94 Q-1 93 -8 118", weight=2.6, echo=True)
    s.path("M178 30 Q161 48 153 64 M175 38 L162 42 M170 46 L158 51 M166 54 L153 60", weight=2.4)
    s.ellipse(211, 48, 2.7, fill=INK, weight=.5)
    s.path("M229 63 q5 2 7 -1 M220 73 Q209 68 205 62", weight=1.1)
    s.path("M200 35 L190 69 L218 81 M202 60 L240 65", color=ACCENT, weight=1.8)
    s.ellipse(192, 72, 4.5, color=ACCENT, weight=1.5)
    for a, b, c, d in [(20, 211, 39, 208), (48, 215, 66, 212), (165, 217, 183, 213), (181, 215, 199, 211)]:
        s.line(a, b, c, d, INK, 3.6)
    s.end()


def cart(s, x, y, scale=1, exploded=False):
    s.group(x, y, scale)
    roof_shift = -48 if exploded else 0
    wheel_shift = 44 if exploded else 0
    s.ellipse(200, 239+wheel_shift, 234, 9, color=FAINT, fill=PALE, weight=.5)
    s.path("M0 79 L52 38 L414 38 L360 80 Z", fill=PALE, weight=2.5)
    side = "M360 80 L414 38 L414 154 L360 197 Z"
    s.path(side, fill=PALE, weight=2.5)
    s.hatch(side, (360, 38, 56, 165), gap=9, alpha=.38)
    s.box(0, 80, 360, 116, fill=PAPER, weight=2.8)
    if exploded:
        s.line(25, 72, 25, 24, MUTED, 1.1, dash="4 5")
        s.line(335, 72, 335, 24, MUTED, 1.1, dash="4 5")
    s.group(0, roof_shift)
    s.path("M-6 78 L49 32 L418 32 L363 79 Z", fill=PAPER, weight=2.5)
    for i in range(6):
        s.line(42+i*57, 47, 28+i*57, 61, FAINT, 1.1)
    s.end()
    for i in range(6):
        gx = 14+i*57
        door = f"M{gx} 176 L{gx} 111 Q{gx+21} 88 {gx+43} 110 L{gx+43} 177 Z"
        s.path(door, fill=PALE if i == 5 else PAPER, weight=1.7)
        s.line(gx+9, 113, gx+9, 165, FAINT, 1)
        s.path(f"M{gx+17} 140 l14 0 M{gx+21} 136 l0 8", color=ACCENT if i == 5 else MUTED, weight=2)
    s.line(3, 187, 354, 188, INK, 2.2)
    if exploded:
        for wx in (59, 302):
            s.line(wx, 193, wx, 226, MUTED, 1.1, dash="4 5")
    wheel(s, 59, 216+wheel_shift)
    wheel(s, 302, 216+wheel_shift)
    s.line(-39, 134, 0, 150, INK, 3.2)
    s.end()


def mechanic(s, x, y, scale=1):
    s.group(x, y, scale)
    s.ellipse(18, 164, 37, 5, color=FAINT, fill=PALE, weight=.5)
    s.path("M1 104 L16 107 L11 155 L-4 156 Z M21 108 L35 104 L41 154 L27 156 Z", fill=INK, weight=2)
    jacket = "M-3 57 Q16 45 36 57 L42 110 Q21 119 -6 109 Z"
    s.path(jacket, fill=PALE, weight=2.5)
    s.hatch("M28 58 L36 57 L42 110 L27 113 Z", (26, 55, 17, 61), gap=5)
    s.ellipse(17, 31, 17, 21, fill=PAPER, weight=2.3)
    s.path("M0 26 Q-1 4 23 10 Q38 13 34 27 L24 22 L12 21 Z", fill=INK, weight=1)
    s.path("M1 33 L-4 39 L2 42 M7 47 Q14 50 18 45", weight=1.2)
    s.ellipse(5, 31, 1.4, fill=INK, weight=.5)
    s.path("M-2 60 L-24 82 L-48 74 L-53 85 L-23 96 L8 76", fill=PALE, weight=2.3)
    s.path("M35 64 Q47 84 45 101 L34 105", fill=PALE, weight=2.2)
    s.line(19, 61, 19, 106, MUTED, 1.1)
    s.box(23, 82, 11, 12, color=MUTED, weight=1)
    s.path("M-54 76 L-72 53 Q-81 53 -82 45 L-76 47 L-72 42 Q-67 49 -70 53 L-49 74", fill=PAPER, weight=2)
    s.path("M-7 157 Q0 154 12 156 L12 161 L-8 161 Z M27 156 L41 154 L46 160 L27 162 Z", fill=INK, weight=1.5)
    s.end()


def sheet(s, x, y, w, h, title, fill=PAPER):
    s.box(x+8, y+8, w, h, fill=PALE, color=FAINT, weight=1)
    s.box(x, y, w, h, fill=fill, weight=2)
    s.path(f"M{x+w-25} {y} L{x+w-25} {y+25} L{x+w} {y+25}", color=MUTED, weight=1)
    s.text(x+22, y+42, title, 25, font=HAND)
    s.rule(x+22, y+60, w-44)


def note_lines(s, x, y, widths, gap=20, color=MUTED):
    for i, width in enumerate(widths):
        s.line(x, y+i*gap, x+width, y+i*gap+.4, color, 1.2, alpha=.75)
