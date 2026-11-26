#!/usr/bin/env python3
"""make.fun bounty draft v1: Sum up 26 November 2026 world news in one image.

Pure Python standard library only (os, struct, zlib): no Pillow, no font
files, no network. Text is drawn with an embedded 8x8 bitmap font (see
FONT below); the PNG is encoded by hand over an in-memory RGB buffer.

Deterministic: headlines are baked in below, no clocks, no randomness.
Writes /output/entry.png (or ./entry.png when /output is not writable).
1024x1024 PNG. Run twice -> identical bytes.

DRAFT ONLY - headlines are the morning of 26 Nov 2026 (checked ~10:50 CST).
Before submitting, refresh with the full day's news and re-run.
See README.md in this folder for the submission blockers (GitHub repo, wallet).
"""
import os
import struct
import zlib

W, H = 1024, 1024

STORIES = [
    ("TRADE", "US proposes new tariffs",
     "Tariffs aimed at 14 economies over factory overcapacity; up to 25% on Indian goods."),
    ("USA", "Thanksgiving parade postponed",
     "Macy's 100th parade in New York moved to Saturday as a major storm hits the coast."),
    ("EGYPT", "Cairo fuel-truck fire kills 30+",
     "A fuel vehicle caught fire on Cairo's ring road; dozens killed and injured."),
    ("TECH", "Huawei found guilty in US court",
     "A US jury found the Chinese tech giant guilty of conspiracy to steal trade secrets."),
    ("ISRAEL", "Judges: drop Netanyahu case",
     "Israeli judges recommended prosecutors drop the most serious bribery case."),
    ("SPACE", "China welcomes foreign astronaut",
     "China to host its first foreign astronaut aboard the Tiangong space station."),
    ("KOREA", "Kim: widen nuclear weapons use",
     "North Korea's Kim called for wider deployment of tactical nuclear weapons."),
    ("GULF", "Tankers hit in Strait of Hormuz",
     "Iran said two oil tankers were hit by naval mines and caught fire; Houthis hit Riyadh."),
]

COLORS = ["#b91c1c", "#1d4ed8", "#b45309", "#0f766e",
          "#6d28d9", "#be185d", "#334155", "#15803d"]

# ---------------------------------------------------------------------------
# Embedded 8x8 bitmap font. Each glyph is 8 strings of 8 chars ('#' = ink).
# Covers every character used by the strings in this program (A-Z, a-z,
# 0-9, space and . , : ; ' - + % / | ! ? " ( ) = _). Unknown characters
# fall back to the '?' glyph.
# ---------------------------------------------------------------------------
_B = "........"
FONT = {
    " ": (_B, _B, _B, _B, _B, _B, _B, _B),
    "A": ("..####..", ".#....#.", ".#....#.", ".#....#.", ".######.", ".#....#.", ".#....#.", _B),
    "B": (".#####..", ".#....#.", ".#....#.", ".#####..", ".#....#.", ".#....#.", ".#####..", _B),
    "C": ("..####..", ".#....#.", ".#......", ".#......", ".#......", ".#....#.", "..####..", _B),
    "D": (".#####..", ".#....#.", ".#....#.", ".#....#.", ".#....#.", ".#....#.", ".#####..", _B),
    "E": (".######.", ".#......", ".#......", ".#####..", ".#......", ".#......", ".######.", _B),
    "F": (".######.", ".#......", ".#......", ".#####..", ".#......", ".#......", ".#......", _B),
    "G": ("..####..", ".#....#.", ".#......", ".#..###.", ".#....#.", ".#....#.", "..####..", _B),
    "H": (".#....#.", ".#....#.", ".#....#.", ".######.", ".#....#.", ".#....#.", ".#....#.", _B),
    "I": ("..####..", "...##...", "...##...", "...##...", "...##...", "...##...", "..####..", _B),
    "J": ("..#####.", "......#.", "......#.", "......#.", "......#.", ".#....#.", "..####..", _B),
    "K": (".#....#.", ".#...#..", ".#..#...", ".####...", ".#..#...", ".#...#..", ".#....#.", _B),
    "L": (".#......", ".#......", ".#......", ".#......", ".#......", ".#......", ".######.", _B),
    "M": (".#....#.", ".##..##.", ".#.##.#.", ".#....#.", ".#....#.", ".#....#.", ".#....#.", _B),
    "N": (".#....#.", ".##...#.", ".#.#..#.", ".#..#.#.", ".#...##.", ".#....#.", ".#....#.", _B),
    "O": ("..####..", ".#....#.", ".#....#.", ".#....#.", ".#....#.", ".#....#.", "..####..", _B),
    "P": (".#####..", ".#....#.", ".#....#.", ".#####..", ".#......", ".#......", ".#......", _B),
    "Q": ("..####..", ".#....#.", ".#....#.", ".#....#.", ".#..#.#.", ".#...#..", "..##..#.", _B),
    "R": (".#####..", ".#....#.", ".#....#.", ".#####..", ".#..#...", ".#...#..", ".#....#.", _B),
    "S": ("..####..", ".#....#.", ".#......", "..####..", "......#.", ".#....#.", "..####..", _B),
    "T": (".######.", "...##...", "...##...", "...##...", "...##...", "...##...", "...##...", _B),
    "U": (".#....#.", ".#....#.", ".#....#.", ".#....#.", ".#....#.", ".#....#.", "..####..", _B),
    "V": (".#....#.", ".#....#.", ".#....#.", ".#....#.", ".#....#.", "..#..#..", "...##...", _B),
    "W": (".#....#.", ".#....#.", ".#....#.", ".#....#.", ".#.##.#.", ".##..##.", ".#....#.", _B),
    "X": (".#....#.", "..#..#..", "...##...", "...##...", "...##...", "..#..#..", ".#....#.", _B),
    "Y": (".#....#.", ".#....#.", "..#..#..", "...##...", "...##...", "...##...", "...##...", _B),
    "Z": (".######.", "......#.", ".....#..", "....#...", "...#....", "..#.....", ".######.", _B),
    "a": (_B, _B, "..####..", ".#....#.", "..#####.", ".#....#.", "..####.#", _B),
    "b": (_B, ".#......", ".#......", ".#####..", ".#....#.", ".#....#.", ".#####..", _B),
    "c": (_B, _B, "..####..", ".#......", ".#......", ".#......", "..####..", _B),
    "d": (_B, "......#.", "......#.", "..#####.", ".#....#.", ".#....#.", "..#####.", _B),
    "e": (_B, _B, "..####..", ".#....#.", ".######.", ".#......", "..####..", _B),
    "f": (_B, "...###..", "...#....", "..####..", "...#....", "...#....", "...#....", _B),
    "g": (_B, _B, "..####..", ".#....#.", ".#....#.", "..#####.", "......#.", "..####.."),
    "h": (_B, ".#......", ".#......", ".#####..", ".#....#.", ".#....#.", ".#....#.", _B),
    "i": (_B, "...##...", _B, "...##...", "...##...", "...##...", "...##...", _B),
    "j": (_B, "....##..", _B, "....##..", "....##..", "....##..", "....##..", "..##...."),
    "k": (_B, ".#......", ".#......", ".#...#..", ".#..#...", ".####...", ".#...#..", _B),
    "l": (_B, "...##...", "...##...", "...##...", "...##...", "...##...", "...###..", _B),
    "m": (_B, _B, ".#....#.", ".##..##.", ".#.##.#.", ".#....#.", ".#....#.", _B),
    "n": (_B, _B, ".#####..", ".#....#.", ".#....#.", ".#....#.", ".#....#.", _B),
    "o": (_B, _B, "..####..", ".#....#.", ".#....#.", ".#....#.", "..####..", _B),
    "p": (_B, _B, ".#####..", ".#....#.", ".#....#.", ".#####..", ".#......", ".#......"),
    "q": (_B, _B, "..#####.", ".#....#.", ".#....#.", "..#####.", "......#.", "......#."),
    "r": (_B, _B, ".#####..", ".#....#.", ".#......", ".#......", ".#......", _B),
    "s": (_B, _B, "..#####.", ".#......", "..####..", "......#.", ".#####..", _B),
    "t": (_B, "...#....", "...#....", "..####..", "...#....", "...#....", "...##...", _B),
    "u": (_B, _B, ".#....#.", ".#....#.", ".#....#.", ".#...##.", "..###.#.", _B),
    "v": (_B, _B, ".#....#.", ".#....#.", ".#....#.", "..#..#..", "...##...", _B),
    "w": (_B, _B, ".#....#.", ".#....#.", ".#.##.#.", ".##..##.", ".#....#.", _B),
    "x": (_B, _B, ".#....#.", "..#..#..", "...##...", "..#..#..", ".#....#.", _B),
    "y": (_B, _B, ".#....#.", ".#....#.", "..#..#..", "...##...", "...#....", "..#....."),
    "z": (_B, _B, ".######.", ".....#..", "....#...", "...#....", ".######.", _B),
    "0": ("..####..", ".#....#.", ".#..#.#.", ".#.#..#.", ".##...#.", ".#....#.", "..####..", _B),
    "1": ("...##...", "..##....", "...#....", "...#....", "...#....", "...#....", "..#####.", _B),
    "2": ("..####..", ".#....#.", "......#.", "....##..", "...#....", "..#.....", ".######.", _B),
    "3": ("..####..", ".#....#.", "......#.", "...###..", "......#.", ".#....#.", "..####..", _B),
    "4": ("....#...", "...##...", "..#.#...", ".#..#...", ".######.", "....#...", "....#...", _B),
    "5": (".######.", ".#......", ".#####..", "......#.", "......#.", ".#....#.", "..####..", _B),
    "6": ("...###..", "..#.....", ".#......", ".#####..", ".#....#.", ".#....#.", "..####..", _B),
    "7": (".######.", "......#.", ".....#..", "....#...", "....#...", "....#...", "....#...", _B),
    "8": ("..####..", ".#....#.", ".#....#.", "..####..", ".#....#.", ".#....#.", "..####..", _B),
    "9": ("..####..", ".#....#.", ".#....#.", "..#####.", "......#.", ".....#..", "..###...", _B),
    ".": (_B, _B, _B, _B, _B, _B, "...##...", _B),
    ",": (_B, _B, _B, _B, _B, _B, "...##...", "...#...."),
    ":": (_B, _B, "...##...", _B, _B, "...##...", _B, _B),
    ";": (_B, _B, "...##...", _B, _B, "...##...", "...#....", _B),
    "'": (_B, "...##...", "...##...", _B, _B, _B, _B, _B),
    "-": (_B, _B, _B, _B, "..####..", _B, _B, _B),
    "+": (_B, "...##...", "...##...", ".######.", "...##...", "...##...", _B, _B),
    "%": (".##...#.", ".#.#.#..", ".##.#...", "...#....", "..#..##.", "..#.#..#", ".#...##.", _B),
    "/": ("......#.", ".....#..", "....#...", "....#...", "...#....", "..#.....", ".#......", _B),
    "|": ("...##...", "...##...", "...##...", "...##...", "...##...", "...##...", "...##...", _B),
    "!": ("...##...", "...##...", "...##...", "...##...", "...##...", _B, "...##...", _B),
    "?": ("..####..", ".#....#.", "......#.", "....##..", "....#...", _B, "....#...", _B),
    '"': (_B, ".#..#...", ".#..#...", _B, _B, _B, _B, _B),
    "(": ("....##..", "...#....", "..#.....", "..#.....", "..#.....", "...#....", "....##..", _B),
    ")": ("..##....", "....#...", ".....#..", ".....#..", ".....#..", "....#...", "..##....", _B),
    "=": (_B, _B, "..####..", _B, _B, "..####..", _B, _B),
    "_": (_B, _B, _B, _B, _B, _B, ".######.", _B),
}


def hex2rgb(hx):
    hx = hx.lstrip("#")
    return (int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16))


CREAM = hex2rgb("#fdf6e9")
DARK = hex2rgb("#111827")
WHITE = (255, 255, 255)
SUB = hex2rgb("#d1d5db")
BODY = hex2rgb("#374151")
FOOT = hex2rgb("#6b7280")


class Canvas:
    """In-memory RGB pixel buffer with tiny drawing primitives."""

    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(bg) * (w * h)

    def fill_rect(self, x, y, rw, rh, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + rw), min(self.h, y + rh)
        if x0 >= x1 or y0 >= y1:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            off = (yy * self.w + x0) * 3
            self.buf[off:off + len(row)] = row

    def rounded_panel(self, x, y, rw, rh, radius, fill, border, bw):
        """Filled rect with rounded corners and a border of width bw."""
        def inside(px, py, inset):
            # point in the rounded rect shrunk by `inset` on every side
            if px < inset or py < inset or px >= rw - inset or py >= rh - inset:
                return False
            cx = min(max(px, inset + radius), rw - inset - radius - 1)
            cy = min(max(py, inset + radius), rh - inset - radius - 1)
            dx, dy = px - cx, py - cy
            return dx * dx + dy * dy <= (radius - inset) * (radius - inset) \
                if (px != cx or py != cy) else True
        for py in range(rh):
            base = (y + py) * self.w + x
            for px in range(rw):
                if inside(px, py, 0):
                    col = fill if inside(px, py, bw) else border
                    off = (base + px) * 3
                    self.buf[off:off + 3] = bytes(col)

    def text(self, x, y, s, scale, color):
        """Draw string s with the 8x8 font scaled by integer `scale`."""
        for i, ch in enumerate(s):
            glyph = FONT.get(ch, FONT["?"])
            gx = x + i * 8 * scale
            for row in range(8):
                bits = glyph[row]
                for col in range(8):
                    if bits[col] == "#":
                        self.fill_rect(gx + col * scale, y + row * scale,
                                       scale, scale, color)

    def text_width(self, s, scale):
        return len(s) * 8 * scale


def wrap(text, scale, width):
    """Greedy word wrap; a character cell is 8*scale px wide."""
    max_chars = max(1, width // (8 * scale))
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if len(t) <= max_chars:
            cur = t
        else:
            if cur:
                lines.append(cur)
            while len(w) > max_chars:  # hard-split overlong words
                lines.append(w[:max_chars])
                w = w[max_chars:]
            cur = w
    if cur:
        lines.append(cur)
    return lines


def write_png(canvas, path):
    """Minimal deterministic PNG writer (filter 0 rows, zlib level 9)."""
    raw = bytearray()
    stride = canvas.w * 3
    for yy in range(canvas.h):
        raw.append(0)
        raw += canvas.buf[yy * stride:(yy + 1) * stride]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


def main():
    img = Canvas(W, H, CREAM)

    # Dark header band
    img.fill_rect(0, 0, W, 118, DARK)
    img.text(32, 20, "THE WORLD IN ONE DAY", 6, WHITE)
    img.text(32, 80, "Thursday, 26 November 2026  |  8 stories, one picture",
             2, SUB)

    # 2 columns x 4 rows of panels
    x0, y0, pw, ph, gap = 24, 138, 476, 192, 20
    for i, (tag, head, body) in enumerate(STORIES):
        x = x0 + (i % 2) * (pw + gap)
        y = y0 + (i // 2) * (ph + gap)
        color = hex2rgb(COLORS[i])
        img.rounded_panel(x, y, pw, ph, 10, WHITE, color, 4)
        img.text(x + 18, y + 12, "%02d | %s" % (i + 1, tag), 3, color)
        head_lines = wrap(head, 3, pw - 36)
        for j, line in enumerate(head_lines):
            img.text(x + 18, y + 42 + j * 30, line, 3, DARK)
        body_y = y + 42 + len(head_lines) * 30 + 6
        for j, line in enumerate(wrap(body, 2, pw - 36)):
            img.text(x + 18, body_y + j * 20, line, 2, BODY)

    # Footer (wraps to two lines at this scale)
    foot = "Sources: Reuters, AP/AFP, SCMP, Economic Times - morning of 26 Nov 2026."
    for j, line in enumerate(wrap(foot, 2, W - 64)):
        img.text(32, 972 + j * 22, line, 2, FOOT)

    outdir = "/output" if os.path.isdir("/output") and os.access("/output", os.W_OK) else "."
    path = os.path.join(outdir, "entry.png")
    write_png(img, path)
    print(path)


if __name__ == "__main__":
    main()
