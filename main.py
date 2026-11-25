#!/usr/bin/env python3
"""World news poster for Wednesday 25 November 2026.

Draws a 1024x1024 newspaper-style infographic summarising the day's
top world stories and writes it to /output/entry.png.

Pure standard library: the PNG is encoded by hand (zlib + struct) and
the text is rendered with a small built-in 5x7 bitmap font, so the
program runs identically in the judge's no-network, stdlib-only
sandbox. Output is fully deterministic: same bytes on every run.

Run locally with:
    MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
PAPER = (247, 242, 231)
INK = (26, 26, 46)
NAVY = (20, 33, 61)
NAVY_LIGHT = (36, 54, 92)
RED = (193, 18, 31)
GOLD = (201, 162, 39)
TEAL = (14, 116, 109)
WHITE = (255, 255, 255)
CARD = (255, 255, 255)
RULE = (180, 172, 150)
MUTED = (90, 86, 76)
ORANGE = (214, 106, 24)
BLUE = (37, 99, 180)
GREEN = (34, 120, 60)
PURPLE = (110, 68, 160)

# ---------------------------------------------------------------------------
# 5x7 bitmap font. Each glyph is 7 rows; each row is a 5-bit mask,
# bit 4 is the leftmost pixel. Only the characters the poster needs.
# ---------------------------------------------------------------------------
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ",": (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    ":": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ";": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    "-": (0x00, 0x00, 0x00, 0x0E, 0x00, 0x00, 0x00),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x06, 0x04, 0x00, 0x04),
    "/": (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "%": (0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13),
    '"': (0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00),
    "+": (0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00),
    "=": (0x00, 0x00, 0x1F, 0x00, 0x1F, 0x00, 0x00),
    "*": (0x00, 0x04, 0x15, 0x0E, 0x15, 0x04, 0x00),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "_": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F),
    "<": (0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02),
    ">": (0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08),
}

BLANK_GLYPH = (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)


def text_width(text, scale):
    """Pixel width of text at the given font scale."""
    return len(text) * 6 * scale - scale


def wrap_text(text, max_width, scale):
    """Greedy word wrap; returns a list of lines fitting max_width."""
    max_chars = max(1, (max_width + scale) // (6 * scale))
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        current = ""
        for word in words:
            trial = word if not current else current + " " + word
            if len(trial) <= max_chars:
                current = trial
            else:
                if current:
                    lines.append(current)
                # A single over-long word is hard-split.
                while len(word) > max_chars:
                    lines.append(word[:max_chars])
                    word = word[max_chars:]
                current = word
        if current:
            lines.append(current)
    return lines


# ---------------------------------------------------------------------------
# Canvas: an RGB pixel buffer with simple drawing primitives.
# ---------------------------------------------------------------------------
class Canvas:
    def __init__(self, width, height, background):
        self.width = width
        self.height = height
        self.pixels = bytearray(background * (width * height))

    def set_pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.pixels[i] = color[0]
            self.pixels[i + 1] = color[1]
            self.pixels[i + 2] = color[2]

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        for yy in range(y0, y1):
            base = (yy * self.width + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.pixels[i] = color[0]
                self.pixels[i + 1] = color[1]
                self.pixels[i + 2] = color[2]

    def hline(self, x, y, w, color, thick=1):
        self.fill_rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.fill_rect(x, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        """Bresenham line with square brush of the given thickness."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        half = thick // 2
        while True:
            self.fill_rect(x0 - half, y0 - half, thick, thick, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color, thick=2, filled=False):
        x = 0
        y = r
        d = 3 - 2 * r
        while y >= x:
            if filled:
                self.hline(cx - x, cy + y, 2 * x + 1, color)
                self.hline(cx - x, cy - y, 2 * x + 1, color)
                self.hline(cx - y, cy + x, 2 * y + 1, color)
                self.hline(cx - y, cy - x, 2 * y + 1, color)
            else:
                for px, py in (
                    (cx + x, cy + y), (cx - x, cy + y),
                    (cx + x, cy - y), (cx - x, cy - y),
                    (cx + y, cy + x), (cx - y, cy + x),
                    (cx + y, cy - x), (cx - y, cy - x),
                ):
                    self.fill_rect(px - thick // 2, py - thick // 2,
                                   thick, thick, color)
            x += 1
            if d > 0:
                y -= 1
                d = d + 4 * (x - y) + 10
            else:
                d = d + 4 * x + 6

    def ellipse(self, cx, cy, rx, ry, color, thick=2):
        """Outline ellipse by sampling its parametric curve."""
        steps = max(48, int(2 * 3.14159 * max(rx, ry)))
        prev = None
        for i in range(steps + 1):
            t = 2 * 3.14159 * i / steps
            px = int(cx + rx * __import__("math").cos(t))
            py = int(cy + ry * __import__("math").sin(t))
            if prev is not None:
                self.line(prev[0], prev[1], px, py, color, thick)
            prev = (px, py)

    def draw_char(self, ch, x, y, scale, color):
        glyph = FONT.get(ch, BLANK_GLYPH)
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    self.fill_rect(x + col * scale, y + row * scale,
                                   scale, scale, color)

    def draw_text(self, text, x, y, scale, color):
        for ch in text:
            self.draw_char(ch, x, y, scale, color)
            x += 6 * scale
        return x

    def draw_text_centered(self, text, cx, y, scale, color):
        x = cx - text_width(text, scale) // 2
        self.draw_text(text, x, y, scale, color)
        return x

    def draw_wrapped(self, text, x, y, max_width, scale, color, leading=6):
        lines = wrap_text(text, max_width, scale)
        line_h = 7 * scale + leading
        for line in lines:
            self.draw_text(line, x, y, scale, color)
            y += line_h
        return y


# ---------------------------------------------------------------------------
# Minimal PNG encoder (stdlib only): signature, IHDR, IDAT, IEND.
# ---------------------------------------------------------------------------
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(canvas):
    raw = bytearray()
    stride = canvas.width * 3
    for y in range(canvas.height):
        raw.append(0)  # filter: none
        start = y * stride
        raw += canvas.pixels[start:start + stride]
    ihdr = struct.pack(">IIBBBBB", canvas.width, canvas.height,
                       8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + _chunk(b"IEND", b""))


# ---------------------------------------------------------------------------
# Small pictograms, drawn with lines and rectangles.
# ---------------------------------------------------------------------------
def draw_globe(cv, cx, cy, r, color):
    cv.circle(cx, cy, r, color, thick=4)
    cv.ellipse(cx, cy, r, int(r * 0.38), color, thick=3)
    cv.ellipse(cx, cy, int(r * 0.38), r, color, thick=3)
    cv.hline(cx - r, cy, 2 * r, color, thick=3)
    cv.circle(cx - r // 3, cy - r // 3, 5, color, filled=True)
    cv.circle(cx + r // 2, cy + r // 4, 4, color, filled=True)


def draw_rocket(cv, x, y, s, color):
    # Nose cone, body, fins and flame, in a s x s box.
    cv.line(x + s // 2, y, x + s // 4, y + s // 3, color, thick=4)
    cv.line(x + s // 2, y, x + 3 * s // 4, y + s // 3, color, thick=4)
    cv.fill_rect(x + s // 4, y + s // 3, s // 2, s // 3, color)
    cv.circle(x + s // 2, y + s // 2, 5, (238, 234, 222), filled=True)
    cv.line(x + s // 4, y + s // 3, x + s // 8, y + 2 * s // 3, color, thick=4)
    cv.line(x + 3 * s // 4, y + s // 3, x + 7 * s // 8, y + 2 * s // 3,
            color, thick=4)
    cv.line(x + s // 2, y + 2 * s // 3, x + s // 2, y + s, ORANGE, thick=5)
    cv.line(x + s // 2 - 4, y + 2 * s // 3, x + s // 2, y + s - 4,
            ORANGE, thick=3)
    cv.line(x + s // 2 + 4, y + 2 * s // 3, x + s // 2, y + s - 4,
            ORANGE, thick=3)


def draw_tower(cv, x, y, s, color):
    cv.fill_rect(x + s // 3, y + s // 6, s // 3, 2 * s // 3, color)
    cv.vline(x + s // 2, y, s // 6, color, thick=3)
    cv.hline(x + s // 4, y + s // 3, s // 2, color, thick=3)
    cv.hline(x + s // 4, y + s // 2, s // 2, color, thick=3)
    cv.hline(x + s // 4, y + 2 * s // 3, s // 2, color, thick=3)
    cv.hline(x + s // 6, y + 5 * s // 6, 2 * s // 3, color, thick=4)


def draw_ship(cv, x, y, s, color):
    cv.line(x + s // 8, y + 2 * s // 3, x + 7 * s // 8, y + 2 * s // 3,
            color, thick=5)
    cv.line(x + s // 8, y + 2 * s // 3, x + s // 4, y + 5 * s // 6,
            color, thick=4)
    cv.line(x + 7 * s // 8, y + 2 * s // 3, x + 3 * s // 4, y + 5 * s // 6,
            color, thick=4)
    cv.hline(x + s // 4, y + 5 * s // 6, s // 2, color, thick=4)
    cv.vline(x + s // 2, y + s // 6, s // 2, color, thick=4)
    cv.line(x + s // 2, y + s // 6, x + 3 * s // 4, y + s // 3, color,
            thick=3)
    cv.line(x + s // 2, y + s // 6, x + 3 * s // 4, y + s // 3,
            color, thick=3)


def draw_cross(cv, x, y, s, color):
    cv.fill_rect(x + s // 3, y + s // 8, s // 3, 3 * s // 4, color)
    cv.fill_rect(x + s // 8, y + s // 3, 3 * s // 4, s // 3, color)


def draw_shield(cv, x, y, s, color):
    # Shield outline with a check mark.
    cv.line(x + s // 4, y + s // 8, x + 3 * s // 4, y + s // 8, color,
            thick=4)
    cv.line(x + 3 * s // 4, y + s // 8, x + 3 * s // 4, y + s // 2, color,
            thick=4)
    cv.line(x + 3 * s // 4, y + s // 2, x + s // 2, y + 7 * s // 8, color,
            thick=4)
    cv.line(x + s // 2, y + 7 * s // 8, x + s // 4, y + s // 2, color,
            thick=4)
    cv.line(x + s // 4, y + s // 2, x + s // 4, y + s // 8, color, thick=4)
    cv.line(x + 3 * s // 8, y + s // 2, x + s // 2, y + 5 * s // 8, color,
            thick=4)
    cv.line(x + s // 2, y + 5 * s // 8, x + 5 * s // 8, y + 3 * s // 8,
            color, thick=4)


def draw_star(cv, x, y, s, color):
    import math
    cx = x + s // 2
    cy = y + s // 2
    r_out = s // 2 - 2
    r_in = s // 5
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
    for i in range(10):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % 10]
        cv.line(x0, y0, x1, y1, color, thick=3)


ICONS = {
    "cyber": draw_rocket,
    "space": draw_rocket,
    "tower": draw_tower,
    "ship": draw_ship,
    "health": draw_cross,
    "shield": draw_shield,
    "star": draw_star,
}


# ---------------------------------------------------------------------------
# The day's news. Every story happened, or was first reported, on
# Wednesday 25 November 2026 (sources: Reuters, CNN, AP, AFP).
# ---------------------------------------------------------------------------
LEAD = {
    "tag": "TOP STORY - CYBERATTACK",
    "headline": "US SPY AGENCIES HIT BY CYBERATTACK",
    "body": ("CNN REPORTS THE CIA AND THE OFFICE OF THE DIRECTOR OF "
             "NATIONAL INTELLIGENCE WERE BREACHED, WITH UNCLASSIFIED "
             "INFORMATION COMPROMISED."),
    "color": RED,
}

STORIES = [
    {
        "tag": "SPACE",
        "headline": "FIRST PAKISTANI REACHES ORBIT",
        "body": ("MUHAMMAD ZEESHAN ALI FLEW ABOARD CHINA'S "
                 "SHENZHOU-24 TO TIANGONG."),
        "color": BLUE,
        "icon": "space",
    },
    {
        "tag": "MIDDLE EAST",
        "headline": "DRONE HITS RIYADH TOWER",
        "body": ("A HOUTHI DRONE HIT THE CAPITAL'S TALLEST TOWER, "
                 "WOUNDING 11 PEOPLE."),
        "color": ORANGE,
        "icon": "tower",
    },
    {
        "tag": "WAR IN UKRAINE",
        "headline": "UKRAINE HITS RUSSIAN SHIPS",
        "body": ("KYIV HIT A RUSSIAN CARGO SHIP AND SANK A WARSHIP "
                 "OFF LIBYA."),
        "color": NAVY_LIGHT,
        "icon": "ship",
    },
    {
        "tag": "HEALTH",
        "headline": "EBOLA TEAMS PULLED FROM FIGHTING",
        "body": ("HEALTH WORKERS LEFT A HOSPITAL IN ITURI AFTER "
                 "THREE DAYS OF FIGHTING."),
        "color": TEAL,
        "icon": "health",
    },
    {
        "tag": "SECURITY",
        "headline": "NATO SENDS WARNING JETS TO POLAND",
        "body": ("THE ALLIANCE PLANS SURVEILLANCE FLIGHTS AFTER "
                 "MISSILES HIT POLAND."),
        "color": PURPLE,
        "icon": "shield",
    },
    {
        "tag": "SCIENCE",
        "headline": "EARLIEST QUASAR EVER SEEN FOUND",
        "body": ("ASTRONOMERS FOUND A QUASAR FROM 630 MILLION "
                 "YEARS AFTER THE BIG BANG."),
        "color": GREEN,
        "icon": "star",
    },
]


# ---------------------------------------------------------------------------
# Poster layout.
# ---------------------------------------------------------------------------
def draw_poster():
    cv = Canvas(WIDTH, HEIGHT, PAPER)

    # --- Masthead ------------------------------------------------------
    cv.fill_rect(0, 0, WIDTH, 160, NAVY)
    cv.hline(0, 160, WIDTH, GOLD, thick=5)
    cv.draw_text_centered("THE WORLD IN ONE DAY", WIDTH // 2, 30, 6, WHITE)
    cv.draw_text_centered("WEDNESDAY 25 NOVEMBER 2026", WIDTH // 2, 100, 3,
                           GOLD)
    cv.draw_text_centered("SEVEN STORIES FROM AROUND THE GLOBE",
                          WIDTH // 2, 132, 2, (200, 205, 220))

    # --- Lead story ----------------------------------------------------
    lx, ly, lw, lh = 32, 180, 960, 204
    cv.fill_rect(lx, ly, lw, lh, CARD)
    cv.fill_rect(lx, ly, lw, 4, RED)
    cv.fill_rect(lx, ly + lh - 2, lw, 2, RULE)
    # Red tag chip.
    tag = LEAD["tag"]
    chip_w = text_width(tag, 2) + 24
    cv.fill_rect(lx + 20, ly + 18, chip_w, 30, RED)
    cv.draw_text(tag, lx + 32, ly + 26, 2, WHITE)
    # Headline, two lines max.
    y = cv.draw_wrapped(LEAD["headline"], lx + 20, ly + 60, 660, 4, INK,
                        leading=8)
    cv.draw_wrapped(LEAD["body"], lx + 20, y + 6, 660, 2, MUTED, leading=6)
    # Globe pictogram on the right of the lead box.
    draw_globe(cv, lx + lw - 100, ly + lh // 2, 56, NAVY_LIGHT)

    # --- Grid of six stories -------------------------------------------
    gx, gy = 32, 398
    cell_w, cell_h, gap = 472, 176, 14
    for idx, story in enumerate(STORIES):
        col = idx % 2
        row = idx // 2
        x = gx + col * (cell_w + gap)
        y = gy + row * (cell_h + gap)
        cv.fill_rect(x, y, cell_w, cell_h, CARD)
        cv.fill_rect(x, y, 6, cell_h, story["color"])
        cv.fill_rect(x, y + cell_h - 2, cell_w, 2, RULE)
        # Tag.
        cv.draw_text(story["tag"], x + 22, y + 14, 2, story["color"])
        # Headline (up to two lines) and body.
        hy = cv.draw_wrapped(story["headline"], x + 22, y + 40, 330, 3,
                             INK, leading=6)
        cv.draw_wrapped(story["body"], x + 22, hy + 4, 330, 2, MUTED,
                        leading=6)
        # Icon in a soft square at the right.
        ix, iy = x + cell_w - 92, y + 48
        cv.fill_rect(ix - 8, iy - 8, 84, 84, (238, 234, 222))
        ICONS[story["icon"]](cv, ix, iy, 68, story["color"])

    # --- Footer --------------------------------------------------------
    fy = 970
    cv.hline(32, fy, 960, RULE, thick=2)
    cv.draw_text_centered(
        "SOURCES: REUTERS - CNN - AP - AFP - 25 NOVEMBER 2026",
        WIDTH // 2, fy + 14, 2, MUTED)

    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    poster = draw_poster()
    with open(path, "wb") as f:
        f.write(encode_png(poster))
    print("wrote", path)


if __name__ == "__main__":
    main()
