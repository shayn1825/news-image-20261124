#!/usr/bin/env python3
"""news-image-20261124 - "The Tuesday World": one image summing up the
world news of Tuesday 24 November 2026.

Draws a bold newspaper front page with Python 3.13 stdlib only:
  * a hand-built single-stroke vector font (glyphs are polylines on a
    5x7 grid, scaled and rasterised with Bresenham lines)
  * a flat RGB canvas with polygon / disc / ring primitives
  * a minimal PNG writer (zlib + CRC, deterministic bytes)

Layout: navy masthead naming the day, a red BREAKING band for the
lead story (Russian jet triggers a South Korean evacuation alert),
six stories in two columns, an IN BRIEF strip, and a footer.
Run:  MAKEFUN_OUTPUT_DIR=out python3 main.py   (default: /output)
"""

import binascii
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 234)
INK = (16, 24, 36)
NAVY = (14, 38, 63)
GOLD = (232, 179, 60)
RED = (163, 18, 38)
TEAL = (14, 110, 105)
BODYGRAY = (58, 62, 70)
LINECOL = (203, 196, 182)
WHITE = (255, 255, 255)
BLACK = (12, 12, 12)

# ------------------------------------------------- stroke font (5x7 grid)
# Each glyph: list of polylines; each polyline is "x,y x,y ..." with
# x in 0..4 (left to right) and y in 0..6 (top to bottom). A one-point
# polyline draws a dot. All copy is upper-case, so only caps + digits
# + punctuation are defined.
FONT = {
    "A": ["0,6 0,2 2,0 4,2 4,6", "0,4 4,4"],
    "B": ["0,0 0,6", "0,0 3,0 4,1 4,2 3,3 0,3",
          "0,3 3,3 4,4 4,5 3,6 0,6"],
    "C": ["4,1 3,0 1,0 0,1 0,5 1,6 3,6 4,5"],
    "D": ["0,0 0,6 3,6 4,5 4,1 3,0 0,0"],
    "E": ["4,0 0,0 0,6 4,6", "0,3 3,3"],
    "F": ["0,6 0,0 4,0", "0,3 3,3"],
    "G": ["4,2 4,1 3,0 1,0 0,1 0,5 1,6 3,6 4,5 4,3 2,3"],
    "H": ["0,0 0,6", "4,0 4,6", "0,3 4,3"],
    "I": ["2,0 2,6", "1,0 3,0", "1,6 3,6"],
    "J": ["3,0 4,0 4,5 3,6 1,6 0,5"],
    "K": ["0,0 0,6", "4,0 0,3 4,6"],
    "L": ["0,0 0,6 4,6"],
    "M": ["0,6 0,0 2,3 4,0 4,6"],
    "N": ["0,6 0,0 4,6 4,0"],
    "O": ["1,0 3,0 4,1 4,5 3,6 1,6 0,5 0,1 1,0"],
    "P": ["0,6 0,0 3,0 4,1 4,2 3,3 0,3"],
    "Q": ["1,0 3,0 4,1 4,5 3,6 1,6 0,5 0,1 1,0", "3,4 4,6"],
    "R": ["0,6 0,0 3,0 4,1 4,2 3,3 0,3", "2,3 4,6"],
    "S": ["4,1 3,0 1,0 0,1 0,2 1,3 3,3 4,4 4,5 3,6 1,6 0,5"],
    "T": ["0,0 4,0", "2,0 2,6"],
    "U": ["0,0 0,5 1,6 3,6 4,5 4,0"],
    "V": ["0,0 2,6 4,0"],
    "W": ["0,0 0,6 2,3 4,6 4,0"],
    "X": ["0,0 4,6", "4,0 0,6"],
    "Y": ["0,0 2,3 4,0", "2,3 2,6"],
    "Z": ["0,0 4,0 0,6 4,6"],
    "0": ["1,0 3,0 4,1 4,5 3,6 1,6 0,5 0,1 1,0", "3,1 1,5"],
    "1": ["1,1 2,0 2,6", "0,6 4,6"],
    "2": ["0,1 1,0 3,0 4,1 4,2 2,4 0,6 4,6"],
    "3": ["0,0 3,0 4,1 4,2 3,3 2,3", "2,3 3,3 4,4 4,5 3,6 1,6 0,5"],
    "4": ["0,0 0,3 4,3", "3,0 3,6"],
    "5": ["4,0 0,0 0,3 3,3 4,4 4,5 3,6 1,6 0,5"],
    "6": ["4,1 3,0 1,0 0,1 0,6 1,6 3,6 4,5 4,4 3,3 1,3 0,3"],
    "7": ["0,0 4,0 2,6", "1,3 3,3"],
    "8": ["1,0 3,0 4,1 4,2 3,3 1,3 0,2 0,1 1,0",
          "1,3 3,3 4,4 4,5 3,6 1,6 0,5 0,4 1,3"],
    "9": ["1,0 3,0 4,1 4,3 3,4 1,4 0,3 0,1 1,0", "4,3 4,6 3,6 1,6"],
    ".": ["2,6 2,6"],
    ",": ["2,5 1,6"],
    ":": ["2,1 2,1", "2,5 2,5"],
    ";": ["2,1 2,1", "2,4 2,6 1,6"],
    "'": ["2,0 1,2"],
    "-": ["0,3 4,3"],
    "/": ["4,6 0,0"],
    "(": ["3,0 2,1 1,3 2,5 3,6"],
    ")": ["1,0 2,1 3,3 2,5 1,6"],
    "%": ["0,1 0,1", "4,5 4,5", "4,0 0,6"],
    "!": ["2,0 2,4", "2,6 2,6"],
    "?": ["1,1 2,0 3,0 4,1 4,2 3,3 2,3 2,4", "2,6 2,6"],
    "+": ["2,1 2,5", "0,3 4,3"],
    "=": ["0,2 4,2", "0,4 4,4"],
    " ": [],
}

ADV = 5.6  # glyph advance, in font units (5 wide + 0.6 gap)


def _pts(spec):
    out = []
    for tok in spec.split():
        a, b = tok.split(",")
        out.append((int(a), int(b)))
    return out


def glyph_points(ch):
    return [_pts(s) for s in FONT.get(ch, [])]


def text_w(text, scale):
    if not text:
        return 0
    return int(round(len(text) * ADV * scale - 0.6 * scale))


def stroke_w(scale):
    if scale < 4:
        return 1
    if scale < 7:
        return 2
    return 3


# ------------------------------------------------------------------ canvas
def new_canvas():
    return bytearray(PAPER * W * H)


def _clip(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def fill_rect(cv, x, y, w, h, col):
    x0 = _clip(x, 0, W)
    y0 = _clip(y, 0, H)
    x1 = _clip(x + w, 0, W)
    y1 = _clip(y + h, 0, H)
    r, g, b = col
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            cv[i] = r
            cv[i + 1] = g
            cv[i + 2] = b


def hline(cv, x0, x1, y, col):
    if y < 0 or y >= H:
        return
    a = _clip(min(x0, x1), 0, W - 1)
    b = _clip(max(x0, x1), 0, W - 1)
    r, g, bb = col
    for xx in range(a, b + 1):
        i = (y * W + xx) * 3
        cv[i] = r
        cv[i + 1] = g
        cv[i + 2] = bb


def dot(cv, cx, cy, t, col):
    fill_rect(cv, cx - t // 2, cy - t // 2, t, t, col)


def line(cv, x0, y0, x1, y1, t, col):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
        dot(cv, x, y, t, col)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


def fill_poly(cv, pts, col):
    # even-odd scanline fill of a polygon given as [(x, y), ...]
    ys = [p[1] for p in pts]
    y0, y1 = max(0, min(ys)), min(H - 1, max(ys))
    n = len(pts)
    for y in range(y0, y1 + 1):
        xs = []
        for i in range(n):
            x1, yy1 = pts[i]
            x2, yy2 = pts[(i + 1) % n]
            if yy1 == yy2:
                continue
            lo, hi = (yy1, yy2) if yy1 < yy2 else (yy2, yy1)
            if lo <= y < hi:
                xs.append(x1 + (y - yy1) * (x2 - x1) / (yy2 - yy1))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            hline(cv, int(round(xs[k])), int(round(xs[k + 1])), y, col)


def disc(cv, cx, cy, r, col):
    for dy in range(-r, r + 1):
        dx = int((r * r - dy * dy) ** 0.5)
        hline(cv, cx - dx, cx + dx, cy + dy, col)


def ring(cv, cx, cy, r, t, col):
    import math
    steps = 72
    prev = None
    for k in range(steps + 1):
        a = 2 * math.pi * k / steps
        p = (cx + int(round(r * math.cos(a))),
             cy + int(round(r * math.sin(a))))
        if prev is not None:
            line(cv, prev[0], prev[1], p[0], p[1], t, col)
        prev = p


def draw_text(cv, x, y, scale, col, text, align="left"):
    """Draw text with its top-left at (x, y); y is the glyph top."""
    text = text.upper()  # the stroke font holds capitals only
    if align == "center":
        x -= text_w(text, scale) // 2
    elif align == "right":
        x -= text_w(text, scale)
    t = stroke_w(scale)
    cx = x
    for ch in text:
        for stroke in glyph_points(ch):
            if len(stroke) == 1:
                px = cx + int(round(stroke[0][0] * scale))
                py = y + int(round(stroke[0][1] * scale))
                dot(cv, px, py, t, col)
                continue
            prev = None
            for gx, gy in stroke:
                p = (cx + int(round(gx * scale)),
                     y + int(round(gy * scale)))
                if prev is not None:
                    line(cv, prev[0], prev[1], p[0], p[1], t, col)
                prev = p
        cx += int(round(ADV * scale))
    return cx


def wrap(text, scale, max_w):
    """Greedy word wrap; returns list of lines fitting max_w."""
    words = text.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# --------------------------------------------------------------------- PNG
def _chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data +
            struct.pack(">I", binascii.crc32(tag + data) & 0xFFFFFFFF))


def write_png(path, cv):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += cv[y * W * 3:(y + 1) * W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) +
           _chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
           _chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)
    return len(png)


# ------------------------------------------------------------------ layout
def jet(cv, ox, oy, s, col):
    """White jet silhouette, side view, nose to the right."""
    def sc(pts):
        return [(ox + int(round(a * s)), oy + int(round(b * s)))
                for a, b in pts]
    fill_poly(cv, sc([(6, 26), (40, 16), (86, 14), (104, 22), (108, 26),
                      (86, 32), (40, 32), (6, 28)]), col)
    fill_poly(cv, sc([(26, 24), (34, 6), (42, 8), (36, 24)]), col)
    fill_poly(cv, sc([(62, 30), (82, 44), (94, 44), (72, 28)]), col)
    fill_poly(cv, sc([(34, 26), (52, 12), (62, 14), (46, 26)]), col)
    for yy in (176, 198, 220):
        fill_rect(cv, 736, yy, 30, 4, col)


def masthead(cv):
    fill_rect(cv, 0, 0, W, 116, NAVY)
    draw_text(cv, 40, 20, 2.5, GOLD, "THE WORLD IN ONE IMAGE")
    draw_text(cv, 40, 44, 8, WHITE, "24 NOVEMBER 2026")
    draw_text(cv, 984, 20, 4, GOLD, "TUESDAY", align="right")
    ring(cv, 905, 82, 26, 2, GOLD)
    line(cv, 879, 82, 931, 82, 2, GOLD)
    line(cv, 905, 56, 905, 108, 2, GOLD)
    # two meridian ellipses across the globe
    import math
    for rx in (12, 5):
        prev = None
        for k in range(37):
            a = 2 * math.pi * k / 36
            p = (905 + int(round(rx * math.sin(a))),
                 82 + int(round(26 * math.cos(a))))
            if prev is not None:
                line(cv, prev[0], prev[1], p[0], p[1], 1, GOLD)
            prev = p


def breaking(cv):
    fill_rect(cv, 0, 116, W, 196, RED)
    fill_rect(cv, 40, 134, 170, 36, BLACK)
    draw_text(cv, 125, 141, 3, WHITE, "BREAKING", align="center")
    draw_text(cv, 40, 180, 6, WHITE, "RUSSIAN JET SPARKS")
    draw_text(cv, 40, 228, 6, WHITE, "KOREA ALERT")
    draw_text(cv, 40, 282, 2.5, WHITE,
              "SEOUL ORDERS ULLEUNG ISLANDERS TO SHELTER")
    jet(cv, 770, 150, 1.9, WHITE)


STORIES = [
    # (column, kicker, kicker colour, headline, body)
    (0, "TECH", TEAL, "HUANG BACK AT NVIDIA",
     "Trump brokers the CEO return; shares jump 31% in a day."),
    (0, "CHINA", RED, "DEATH FOR LEAKS",
     "Official sentenced for passing 100 intelligence reports abroad."),
    (0, "UKRAINE", NAVY, "BLAST BESIDE PALACE",
     "Russian blast hits a building beside the president's offices."),
    (1, "NORTH KOREA", RED, "PYONGYANG MULLS EXIT",
     "Pyongyang may shut the Swiss office after sanctions on a camp."),
    (1, "POLAND", TEAL, "DRONE OVER POLAND",
     "Russian UAV briefly violates Polish airspace in night strikes."),
    (1, "USA", NAVY, "O'HARE GROUND STOP",
     "Brief halt over staffing as 81.5m Americans start Thanksgiving trips."),
]


def story(cv, x, top, w, kicker, kcol, headline, body):
    fill_rect(cv, x, top + 2, 10, 10, kcol)
    draw_text(cv, x + 20, top, 2.5, kcol, kicker)
    draw_text(cv, x, top + 26, 4, INK, headline)
    lines = wrap(body, 3, w)
    yy = top + 62
    for ln in lines[:3]:
        draw_text(cv, x, yy, 3, BODYGRAY, ln)
        yy += 26


def body(cv):
    fill_rect(cv, 512, 336, 2, 476, LINECOL)
    tops = [336, 496, 656]
    for col_idx in (0, 1):
        x = 40 if col_idx == 0 else 524
        w = 460
        rows = [s for s in STORIES if s[0] == col_idx]
        for row, (_, kicker, kcol, headline, body_text) in zip(tops, rows):
            story(cv, x, row, w, kicker, kcol, headline, body_text)


def in_brief(cv):
    fill_rect(cv, 0, 836, W, 116, NAVY)
    draw_text(cv, 40, 852, 3, GOLD, "IN BRIEF")
    items = [
        ("UN: AI SAFETY RULES IN A YEAR", 40, 890),
        ("SEOUL MINISTER QUITS ON AI", 524, 890),
        ("LAHORE AIR WORST ON EARTH", 40, 920),
        ("GAZA CHILDREN FLOWN TO UK", 524, 920),
    ]
    for text, x, y in items:
        fill_rect(cv, x, y + 4, 8, 8, GOLD)
        draw_text(cv, x + 18, y, 2.5, WHITE, text)


def footer(cv):
    draw_text(cv, 512, 972, 2.5, INK,
              "ALL STORIES FIRST REPORTED ON TUESDAY 24 NOVEMBER 2026",
              align="center")
    draw_text(cv, 512, 1000, 2, BODYGRAY,
              "SOURCES: REUTERS - TIMES OF INDIA", align="center")


def build():
    cv = new_canvas()
    masthead(cv)
    breaking(cv)
    body(cv)
    in_brief(cv)
    footer(cv)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    size = write_png(path, build())
    print("wrote %s (%d bytes)" % (path, size))


if __name__ == "__main__":
    main()
