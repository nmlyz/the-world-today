#!/usr/bin/env python3
"""Draw a one-image newspaper front page summing up the world news of
Tuesday 24 November 2026, and write it to /output/entry.png.

Standard library only, no network, fully deterministic: every run writes
the same bytes. All text uses a hand-made 5x7 bitmap font; every picture
is drawn with code. Eight stories: the Ukrainian sea drone sinking a
Russian corvette at Benghazi, three more ships hit in the Strait of
Hormuz, EU sanctions aimed at 60 Russian banks, the Democrats taking
258 House seats, aid workers killed in Gaza, drones striking Khartoum
again, students flooding Europe's streets, and Seoul naming new top
diplomats.
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (247, 243, 232)
INK = (20, 22, 26)
RED = (179, 32, 42)
BLUE = (29, 78, 137)
DARKBLUE = (16, 42, 84)
NIGHT = (13, 20, 44)
YELLOW = (240, 192, 32)
GOLD = (212, 160, 32)
GRAY = (110, 110, 110)
LIGHT = (226, 219, 198)
WHITE = (255, 255, 255)
SKY = (188, 214, 235)
DUSK = (232, 140, 80)
SEA = (64, 120, 178)
DEEPSEA = (24, 68, 120)
SAND = (214, 188, 140)
GREEN = (46, 125, 50)
PITCH = (52, 138, 72)
ORANGE = (232, 119, 34)
BROWN = (120, 84, 50)
SKIN = (232, 190, 160)
TEAL = (18, 92, 96)
SMOKE = (150, 150, 150)
DARKGREEN = (24, 90, 48)
PALE = (232, 228, 200)
STEEL = (60, 64, 74)
HULL = (40, 44, 54)

# ---------------------------------------------------------------- font
# Hand-made 5x7 bitmap glyphs: 7 rows of 5 pixels, '#' is ink.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": (".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    "'": ("..#..", "..#..", "..#..", ".....", ".....", ".....", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "%": ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
}


def text_width(s, scale):
    if not s:
        return 0
    return len(s) * 6 * scale - scale


def wrap_lines(s, scale, max_w):
    words = s.upper().split()
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def frame(self, x, y, w, h, c, t=2):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=2):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        r = t // 2
        while True:
            self.rect(x0 - r, y0 - r, t, t, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def polyline(self, pts, c, t=2):
        for i in range(len(pts) - 1):
            self.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], c, t)

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if fill:
                    if d2 <= r * r:
                        self.set(xx, yy, c)
                else:
                    if r * r - 2 * r <= d2 <= r * r + 2 * r:
                        self.set(xx, yy, c)

    def polygon(self, pts, c):
        ys = [p[1] for p in pts]
        for yy in range(min(ys), max(ys) + 1):
            nodes = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    nodes.append(x0 + (yy - y0) * (x1 - x0) // (y1 - y0))
            nodes.sort()
            for i in range(0, len(nodes) - 1, 2):
                self.rect(nodes[i], yy, nodes[i + 1] - nodes[i] + 1, 1, c)

    def star(self, cx, cy, r, c):
        pts = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            rr = r if i % 2 == 0 else r // 2
            pts.append((cx + int(rr * math.cos(ang)),
                        cy + int(rr * math.sin(ang))))
        self.polygon(pts, c)

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s.upper():
            glyph = FONT.get(ch, FONT[" "])
            for ry in range(7):
                row = glyph[ry]
                for rx in range(5):
                    if row[rx] == "#":
                        self.rect(cx + rx * scale, y + ry * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_centered(self, cx, y, s, scale, c):
        return self.text(cx - text_width(s, scale) // 2, y, s, scale, c)

    def text_wrapped(self, x, y, s, scale, c, max_w, line_gap=1):
        lines = wrap_lines(s, scale, max_w)
        for i, ln in enumerate(lines):
            self.text(x, y + i * (7 * scale + line_gap), ln, scale, c)
        return len(lines)


# ---------------------------------------------------------------- png
def write_png(canvas, path):
    raw = bytearray()
    stride = canvas.w * 3
    for yy in range(canvas.h):
        raw.append(0)
        raw += canvas.px[yy * stride:(yy + 1) * stride]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    png = bytearray(b"\x89PNG\r\n\x1a\n")
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    os.chmod(path, 0o644)


def panel(cv, x, y, w, h):
    cv.rect(x, y, w, h, WHITE)
    cv.frame(x, y, w, h, INK, 2)


def kicker(cv, x, y, s):
    cv.rect(x, y, text_width(s, 2) + 12, 16, RED)
    cv.text(x + 6, y + 1, s, 2, WHITE)


# ---------------------------------------------------------------- pictures
def pic_benghazi(cv, x, y, w, h):
    """Night port at Benghazi: a Russian corvette listing and burning
    at its berth, a small drone boat slipping away. Drawn for 400x196."""
    cv.rect(x, y, w, h, NIGHT)
    for sx, sy, r in ((24, 16, 2), (84, 10, 1), (150, 22, 2), (210, 12, 1),
                      (300, 14, 2), (360, 24, 1), (60, 44, 1), (250, 40, 1),
                      (330, 52, 1), (120, 60, 1)):
        cv.circle(x + sx, y + sy, r, WHITE)
    # moon
    cv.circle(x + w - 52, y + 30, 17, (200, 196, 170))
    cv.circle(x + w - 52, y + 30, 13, PALE)
    # city silhouette along the far shore
    shore = y + 108
    cv.rect(x, y + 78, w, shore - (y + 78), (8, 12, 28))
    for bx, bw, bh in ((8, 34, 30), (46, 26, 44), (76, 40, 24),
                       (250, 30, 38), (284, 36, 26), (324, 28, 48)):
        cv.rect(x + bx, shore - bh, bw, bh, (5, 8, 20))
    # one minaret
    cv.rect(x + 200, shore - 58, 8, 58, (5, 8, 20))
    cv.polygon([(x + 198, shore - 58), (x + 210, shore - 58),
                (x + 204, shore - 72)], (5, 8, 20))
    # lit windows
    for wx, wy in ((16, 92), (30, 100), (54, 76), (66, 88), (88, 98),
                   (258, 84), (292, 96), (306, 88), (332, 72)):
        cv.rect(x + wx, y + wy, 3, 3, YELLOW)
    # searchlight beam from the shore
    cv.polygon([(x + 210, shore), (x + 236, y + 18), (x + 252, y + 22),
                (x + 216, shore)], (150, 165, 200))
    # sea
    cv.rect(x, shore, w, y + h - shore, DEEPSEA)
    for wx in range(12, w - 20, 46):
        cv.rect(x + wx, shore + 62, 26, 2, SEA)
        cv.rect(x + wx + 18, shore + 74, 18, 2, (40, 90, 150))
    # the corvette, listing by the stern
    sx, sy = x + 66, shore + 6
    cv.polygon([(sx, sy - 34), (sx + 150, sy - 26), (sx + 214, sy - 12),
                (sx + 208, sy + 4), (sx + 8, sy + 8)], HULL)
    cv.rect(sx + 8, sy - 34, 206, 4, STEEL)
    # superstructure and funnel, leaning with the ship
    cv.polygon([(sx + 66, sy - 30), (sx + 128, sy - 28), (sx + 130, sy - 52),
                (sx + 68, sy - 54)], (120, 124, 132))
    cv.polygon([(sx + 136, sy - 30), (sx + 150, sy - 30), (sx + 152, sy - 56),
                (sx + 138, sy - 56)], (90, 92, 100))
    # mast
    cv.line(sx + 96, sy - 52, sx + 92, sy - 80, STEEL, 3)
    cv.line(sx + 80, sy - 74, sx + 106, sy - 76, STEEL, 2)
    cv.circle(sx + 92, sy - 82, 2, RED)
    # explosion bursting from the hull
    ex, ey = sx + 118, sy - 44
    cv.star(ex, ey, 26, ORANGE)
    cv.star(ex, ey, 16, YELLOW)
    cv.circle(ex, ey, 7, WHITE)
    # smoke column
    for dx, dy, r in ((-6, -38, 8), (2, -48, 10), (-2, -56, 9), (6, -64, 7)):
        cv.circle(ex + dx, ey + dy, r, (90, 92, 100))
    # the drone boat, small and low, slipping away to the right
    dx, dy = x + w - 96, shore + 30
    cv.polygon([(dx, dy), (dx + 38, dy), (dx + 32, dy + 8),
                (dx + 4, dy + 8)], (10, 12, 16))
    cv.line(dx + 12, dy, dx + 12, dy - 14, (10, 12, 16), 2)
    cv.circle(dx + 12, dy - 16, 2, RED)
    cv.line(dx - 2, dy + 10, dx - 22, dy + 14, WHITE, 2)
    cv.line(dx - 2, dy + 12, dx - 20, dy + 18, WHITE, 2)


def pic_hormuz(cv, x, y, w, h):
    """A tanker in the narrow Strait of Hormuz, hit at the bow, cliffs
    closing in on both sides. Drawn for 452x66."""
    cv.rect(x, y, w, h, (210, 225, 235))
    # headlands
    cv.polygon([(x, y + h), (x, y + 26), (x + 52, y + 8), (x + 78, y + 30),
                (x + 66, y + h)], (150, 120, 85))
    cv.polygon([(x + w, y + h), (x + w, y + 22), (x + w - 48, y + 6),
                (x + w - 74, y + 28), (x + w - 62, y + h)], (140, 110, 78))
    # strait water
    cv.rect(x, y + 30, w, h - 30, SEA)
    for wx in range(8, w - 16, 34):
        cv.rect(x + wx, y + 58, 20, 2, (140, 190, 225))
    # the tanker
    tx, ty = x + 150, y + 34
    cv.polygon([(tx, ty), (tx + 148, ty), (tx + 148, ty + 16),
                (tx + 132, ty + 16), (tx, ty + 16)], (30, 34, 40))
    cv.rect(tx + 4, ty - 4, 140, 4, RED)
    cv.rect(tx + 108, ty - 18, 30, 14, WHITE)
    cv.rect(tx + 112, ty - 14, 8, 6, BLUE)
    cv.rect(tx + 96, ty - 12, 8, 12, (90, 92, 100))
    # explosion and spray at the bow
    ex, ey = tx + 6, ty - 4
    cv.star(ex, ey, 16, ORANGE)
    cv.star(ex, ey, 10, YELLOW)
    for sx, sy in ((-14, -12), (10, -16), (-4, -20), (16, -8)):
        cv.circle(ex + sx, ey + sy, 2, WHITE)
    # a small patrol boat
    bx, by = x + 336, y + 48
    cv.polygon([(bx, by), (bx + 30, by), (bx + 26, by + 6), (bx + 4, by + 6)],
               (20, 24, 30))
    cv.line(bx + 10, by, bx + 10, by - 10, (20, 24, 30), 2)


def pic_eu(cv, x, y, w, h):
    """A bank, a globe with payment arcs, and a shadow-fleet tanker
    under a ban. Drawn for 452x66."""
    cv.rect(x, y, w, h, (235, 232, 220))
    # the bank, left
    bx, by = x + 18, y + 14
    cv.polygon([(bx, by), (bx + 96, by), (bx + 48, by - 12)], LIGHT)
    cv.rect(bx, by + 2, 96, 6, WHITE)
    for i in range(4):
        cv.rect(bx + 10 + i * 24, by + 10, 8, 30, WHITE)
        cv.rect(bx + 10 + i * 24, by + 10, 8, 2, GRAY)
    cv.rect(bx, by + 40, 96, 4, WHITE)
    cv.rect(bx - 4, by + 44, 104, 4, (200, 196, 184))
    # the globe, centre, with payment arcs
    gx, gy, gr = x + 216, y + 34, 24
    cv.circle(gx, gy, gr, SEA)
    cv.circle(gx - 8, gy - 6, 7, GREEN)
    cv.circle(gx + 9, gy + 7, 6, GREEN)
    cv.circle(gx + 6, gy - 12, 4, DARKGREEN)
    cv.circle(gx, gy, gr, INK, fill=False)
    cv.polyline([(gx - 34, gy - 16), (gx - 18, gy - 34), (gx, gy - 38),
                 (gx + 18, gy - 34), (gx + 34, gy - 16)], GOLD, 3)
    cv.polyline([(gx - 40, gy + 8), (gx - 20, gy - 6), (gx, gy - 10),
                 (gx + 20, gy - 6), (gx + 40, gy + 8)], GOLD, 2)
    # the shadow tanker under a ban, right
    tx, ty = x + 330, y + 40
    cv.polygon([(tx, ty), (tx + 76, ty), (tx + 76, ty + 12),
                (tx + 64, ty + 12), (tx, ty + 12)], (50, 54, 62))
    cv.rect(tx + 52, ty - 10, 16, 10, (90, 92, 100))
    cv.circle(tx + 38, ty - 2, 26, RED, fill=False)
    cv.line(tx + 38 - 18, ty - 2 + 18, tx + 38 + 18, ty - 2 - 18, RED, 4)


def pic_washington(cv, x, y, w, h):
    """The Capitol dome beside a seat bar chart, 258 against 173.
    Drawn for 452x66."""
    cv.rect(x, y, w, h, SKY)
    # capitol
    cx, base = x + 96, y + h - 4
    cv.rect(cx - 78, base - 22, 156, 22, WHITE)
    for i in range(6):
        cv.rect(cx - 66 + i * 24, base - 22, 5, 22, (200, 205, 212))
    cv.rect(cx - 30, base - 34, 60, 12, WHITE)
    cv.circle(cx, base - 34, 26, WHITE)
    cv.circle(cx, base - 34, 26, (200, 205, 212), fill=False)
    cv.rect(cx - 26, base - 36, 52, 4, WHITE)
    cv.line(cx, base - 60, cx, base - 76, INK, 2)
    cv.rect(cx + 2, base - 76, 12, 8, RED)
    cv.rect(cx + 2, base - 72, 12, 4, WHITE)
    # seat bars
    bx = x + 224
    cv.text(bx, y + 6, "258", 2, BLUE)
    cv.rect(bx + 40, y + 8, 168, 12, BLUE)
    cv.text(bx, y + 32, "173", 2, RED)
    cv.rect(bx + 40, y + 34, 113, 12, RED)
    cv.text(bx + 40, y + 52, "HOUSE SEATS", 2, INK)


def pic_gaza(cv, x, y, w, h):
    """A dusk street in Gaza: an aid truck loaded with food parcels,
    a broken wall, smoke. Drawn for 452x66."""
    cv.rect(x, y, w, h, DUSK)
    cv.rect(x, y + 26, w, 12, (240, 190, 120))
    cv.rect(x, y + 38, w, h - 38, (120, 110, 100))
    # smoke column
    for dx, dy, r in ((0, 6, 7), (6, 16, 9), (-2, 26, 8)):
        cv.circle(x + w - 40 + dx, y + dy, r, (110, 108, 104))
    # broken wall, left
    cv.polygon([(x + 8, y + h), (x + 8, y + 40), (x + 30, y + 34),
                (x + 44, y + 44), (x + 60, y + 38), (x + 72, y + 46),
                (x + 72, y + h)], (90, 86, 80))
    # rubble blocks
    for rx, ry, rw, rh in ((84, 58, 16, 8), (104, 60, 12, 6),
                           (330, 58, 18, 8), (352, 61, 12, 5)):
        cv.rect(x + rx, y + ry, rw, rh, (80, 76, 70))
    # the aid truck
    tx, ty = x + 150, y + 30
    cv.rect(tx, ty, 118, 28, WHITE)
    cv.rect(tx, ty, 118, 4, BLUE)
    cv.rect(tx + 118, ty + 6, 34, 22, WHITE)
    cv.rect(tx + 126, ty + 10, 12, 8, BLUE)
    cv.circle(tx + 18, ty + 28, 6, INK)
    cv.circle(tx + 104, ty + 28, 6, INK)
    cv.circle(tx + 140, ty + 28, 6, INK)
    # food parcels in the load bed
    for px, pc in ((6, RED), (26, GREEN), (46, ORANGE), (66, TEAL),
                   (86, (150, 100, 40))):
        cv.rect(tx + px, ty + 8, 16, 14, pc)
        cv.line(tx + px, ty + 8, tx + px + 16, ty + 22, WHITE, 1)
    # a small flag on a pole
    fx = x + 400
    cv.line(fx, y + h, fx, y + 16, BROWN, 2)
    cv.rect(fx, y + 16, 26, 16, WHITE)
    cv.circle(fx + 13, y + 24, 5, GREEN)
    cv.circle(fx + 15, y + 24, 4, WHITE)


def pic_khartoum(cv, x, y, w, h):
    """Khartoum skyline with a minaret, a drone overhead, smoke
    columns. Drawn for 294x50."""
    cv.rect(x, y, w, h, (240, 200, 150))
    cv.rect(x, y + 34, w, h - 34, (150, 130, 105))
    # skyline
    for bx, bw, bh in ((6, 34, 16), (44, 26, 22), (74, 40, 12),
                       (150, 30, 20), (184, 36, 14), (224, 30, 24)):
        cv.rect(x + bx, y + 34 - bh + 12, bw, bh, (60, 60, 70))
    # minaret
    cv.rect(x + 122, y + 2, 7, 44, (60, 60, 70))
    cv.polygon([(x + 120, y + 2), (x + 131, y + 2), (x + 125, y - 6)],
               (60, 60, 70))
    # drone silhouette
    dx, dy = x + 210, y + 10
    cv.rect(dx, dy, 16, 5, INK)
    cv.rect(dx - 8, dy - 2, 32, 2, INK)
    cv.rect(dx + 2, dy + 5, 3, 5, INK)
    cv.rect(dx + 11, dy + 5, 3, 5, INK)
    # smoke columns
    for sx, sy, r in ((52, 14, 5), (56, 22, 6), (244, 12, 5), (248, 20, 6)):
        cv.circle(x + sx, y + sy, r, (110, 108, 104))


def pic_students(cv, x, y, w, h):
    """A student march: crowd heads and placards, a colosseum arch
    and the Eiffel tower at the edges. Drawn for 294x50."""
    cv.rect(x, y, w, h, SKY)
    cv.rect(x, y + h - 12, w, 12, (150, 150, 150))
    # colosseum arch, left
    cv.rect(x + 4, y + 18, 34, 28, (170, 130, 95))
    cv.circle(x + 14, y + 34, 6, SKY)
    cv.circle(x + 28, y + 34, 6, SKY)
    cv.rect(x + 4, y + 18, 34, 5, (140, 105, 70))
    # eiffel tower, right
    ex = x + w - 26
    cv.polygon([(ex - 12, y + h - 12), (ex, y + 2), (ex + 12, y + h - 12)],
               (60, 64, 74))
    cv.rect(ex - 8, y + 30, 16, 3, SKY)
    cv.rect(ex - 5, y + 20, 10, 3, SKY)
    # the crowd
    for i, cx in enumerate(range(x + 52, x + w - 40, 26)):
        col = (RED, BLUE, GREEN, ORANGE, TEAL)[i % 5]
        cv.circle(cx, y + 28, 7, SKIN)
        cv.rect(cx - 9, y + 34, 18, 12, col)
        if i % 2 == 0:
            cv.line(cx, y + 34, cx, y + 14, BROWN, 2)
            cv.rect(cx - 11, y + 4, 22, 10, WHITE)
            cv.rect(cx - 11, y + 4, 22, 2, RED)
    for i, cx in enumerate(range(x + 64, x + w - 40, 26)):
        col = (TEAL, ORANGE, BLUE, RED, GREEN)[i % 5]
        cv.circle(cx, y + 38, 6, (210, 170, 140))
        cv.rect(cx - 8, y + 43, 16, 7, col)


def pic_seoul(cv, x, y, w, h):
    """A government building in Seoul with the South Korean flag and
    the unification flag, a podium in front. Drawn for 294x50."""
    cv.rect(x, y, w, h, SKY)
    cv.rect(x, y + h - 10, w, 10, (150, 150, 150))
    # government building
    bx, by = x + 78, y + 12
    cv.polygon([(bx, by), (bx + 130, by), (bx + 118, by - 8),
                (bx + 12, by - 8)], DARKBLUE)
    cv.rect(bx, by, 130, 26, WHITE)
    for i in range(6):
        cv.rect(bx + 12 + i * 20, by + 4, 5, 22, (200, 205, 212))
    cv.rect(bx - 6, by + 26, 142, 4, (200, 196, 184))
    # podium
    cv.polygon([(x + 138, y + h - 10), (x + 148, y + h - 10),
                (x + 152, y + 28), (x + 134, y + 28)], (90, 84, 76))
    cv.rect(x + 132, y + 28, 22, 4, (70, 66, 60))
    # South Korean flag, left pole
    fx = x + 40
    cv.line(fx, y + h - 10, fx, y + 4, BROWN, 2)
    cv.rect(fx, y + 4, 26, 16, WHITE)
    cv.circle(fx + 13, y + 12, 5, RED)
    cv.circle(fx + 13, y + 14, 5, BLUE)
    # unification flag, right pole
    fx = x + w - 66
    cv.line(fx, y + h - 10, fx, y + 4, BROWN, 2)
    cv.rect(fx, y + 4, 26, 16, WHITE)
    cv.polygon([(fx + 8, y + 8), (fx + 18, y + 8), (fx + 16, y + 16),
                (fx + 9, y + 15)], (90, 150, 200))


# ---------------------------------------------------------------- layout
def build():
    cv = Canvas(W, H, PAPER)

    # masthead
    cv.text_centered(W // 2, 8, "TUESDAY - THE WORLD IN ONE PICTURE", 3, INK)
    cv.rect(24, 36, W - 48, 5, INK)
    cv.text_centered(W // 2, 44, "24 NOVEMBER 2026", 7, RED)
    cv.rect(24, 100, W - 48, 3, INK)
    cv.rect(24, 107, W - 48, 7, INK)

    # numbers strip under the masthead
    sx, sy, sh = 24, 122, 54
    cv.rect(sx, sy, W - 48, sh, WHITE)
    cv.frame(sx, sy, W - 48, sh, INK, 2)
    cells = [("258", "SEATS"), ("60", "BANKS"), ("330", "VOTES"),
             ("3", "SHIPS"), ("100+", "CITIES")]
    cw = (W - 48) // 5
    for i, (num, lab) in enumerate(cells):
        cx0 = sx + i * cw
        if i:
            cv.rect(cx0, sy, 2, sh, INK)
        ccx = cx0 + cw // 2
        cv.text_centered(ccx, sy + 5, num, 4, RED)
        cv.text_centered(ccx, sy + 36, lab, 2, INK)

    # ---- lead story: Benghazi, double-size panel
    ax, ay, aw, ah = 24, 184, W - 48, 218
    panel(cv, ax, ay, aw, ah)
    pic_benghazi(cv, ax + 14, ay + 12, 400, ah - 24)
    tx = ax + 428
    kicker(cv, tx, ay + 12, "LIBYA")
    cv.text(tx, ay + 38, "UKRAINE SINKS", 5, INK)
    cv.text(tx, ay + 76, "RUSSIAN WARSHIP", 5, RED)
    cv.rect(tx, ay + 118, aw - 442, 3, INK)
    cv.text_wrapped(tx, ay + 126, "A UKRAINIAN SEA DRONE SANK A RUSSIAN "
                    "CORVETTE AT ITS BERTH IN BENGHAZI AND DESTROYED "
                    "A HELICOPTER.", 2, INK, aw - 442, line_gap=1)
    cv.text_wrapped(tx, ay + 126 + 3 * 15,
                    "ZELENSKY CLAIMED THE STRIKE. LIBYA'S EASTERN "
                    "GOVERNMENT FILED A FORMAL COMPLAINT AT THE UN.",
                    2, INK, aw - 442, line_gap=1)

    # ---- rows of two, then three
    bw = (W - 48 - 16) // 2
    qx = 24 + bw + 16

    def story2(x, y, pic, kick, head1, head2, facts):
        panel(cv, x, y, bw, 204)
        pic(cv, x + 14, y + 8, bw - 28, 66)
        kicker(cv, x + 14, y + 80, kick)
        cv.text(x + 14, y + 102, head1, 3, INK)
        cv.text(x + 14, y + 125, head2, 3, RED)
        cv.rect(x + 14, y + 152, bw - 28, 3, INK)
        cv.text_wrapped(x + 14, y + 158, facts, 2, INK, bw - 28, line_gap=1)

    def story3(x, w, y, pic, kick, head1, head2, facts):
        panel(cv, x, y, w, 176)
        pic(cv, x + 10, y + 6, w - 20, 50)
        kicker(cv, x + 10, y + 60, kick)
        cv.text(x + 10, y + 82, head1, 2, INK)
        cv.text(x + 10, y + 100, head2, 2, RED)
        cv.rect(x + 10, y + 118, w - 20, 3, INK)
        cv.text_wrapped(x + 10, y + 124, facts, 2, INK, w - 20, line_gap=1)

    story2(24, 412, pic_hormuz, "GULF", "THREE MORE SHIPS", "HIT IN HORMUZ",
           "WEEKEND STRIKES BRING ATTACKS TO THE HIGHEST PACE SINCE "
           "FEBRUARY. TRUMP MAY RESUME STRIKES ON IRAN.")
    story2(qx, 412, pic_eu, "EUROPE", "EU AIMS SANCTIONS", "AT 60 RUSSIAN BANKS",
           "BRUSSELS PROPOSES CUTTING 60 BANKS FROM SWIFT, A CRYPTO "
           "CRACKDOWN AND A PORT BAN ON 70 SHADOW TANKERS.")
    story2(24, 626, pic_washington, "AMERICA", "DEMOCRATS TAKE", "258 HOUSE SEATS",
           "LARGEST HOUSE MAJORITY SINCE 1992. CHUCK HUBBARD BEAT "
           "VIRGINIA FOXX BY 330 VOTES OF 287,000 AFTER A RECOUNT.")
    story2(qx, 626, pic_gaza, "MIDDLE EAST", "AID WORKERS", "KILLED IN GAZA",
           "AN ISRAELI STRIKE HIT A CAR OF FOOD FOR DISPLACED PEOPLE. "
           "SIX DIED SATURDAY, SIX MORE SUNDAY.")

    cw3 = (W - 48 - 32) // 3
    rx = 24 + cw3 + 16
    rx2 = rx + cw3 + 16
    w3 = W - 48 - 2 * cw3 - 32
    story3(24, cw3, 840, pic_khartoum, "AFRICA", "DRONES STRIKE", "KHARTOUM AGAIN",
           "DRONE STRIKES KILL FOUR IN GREATER KHARTOUM. A UN BUILDING "
           "IS DAMAGED.")
    story3(rx, cw3, 840, pic_students, "EUROPE", "STUDENTS FLOOD", "EUROPE'S STREETS",
           "STRIKE IN 100+ ITALIAN CITIES. TENS OF THOUSANDS MARCH "
           "IN PARIS.")
    story3(rx2, w3, 840, pic_seoul, "ASIA", "SEOUL NAMES NEW", "TOP DIPLOMATS",
           "LEE JAE MYUNG NAMES NEW FOREIGN AND UNIFICATION MINISTERS.")

    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    try:
        os.umask(0o022)
    except OSError:
        pass
    write_png(build(), os.path.join(outdir, "entry.png"))


if __name__ == "__main__":
    main()
