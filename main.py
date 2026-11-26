#!/usr/bin/env python3
"""make.fun bounty draft v1: Sum up 26 November 2026 world news in one image.

Deterministic, no network: headlines are baked in below.
Writes /output/entry.png (or ./entry.png when /output is not writable).
1024x1024 PNG. Run twice -> identical bytes.

DRAFT ONLY — headlines are the morning of 26 Nov 2026 (checked ~10:50 CST).
Before submitting, refresh with the full day's news and re-run.
See README.md in this folder for the submission blockers (GitHub repo, wallet).
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

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


def wrap(draw, text, font, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def main():
    img = Image.new("RGB", (W, H), "#fdf6e9")
    d = ImageDraw.Draw(img)
    f_title = ImageFont.truetype(BOLD, 44)
    f_sub = ImageFont.truetype(REG, 22)
    f_tag = ImageFont.truetype(BOLD, 20)
    f_head = ImageFont.truetype(BOLD, 26)
    f_body = ImageFont.truetype(REG, 20)

    d.rectangle([0, 0, W, 118], fill="#111827")
    d.text((32, 22), "THE WORLD IN ONE DAY", font=f_title, fill="white")
    d.text((32, 76), "Thursday, 26 November 2026  •  8 stories, one picture",
           font=f_sub, fill="#d1d5db")

    # 2 columns x 4 rows of panels
    x0, y0, pw, ph, gap = 24, 138, 476, 192, 20
    for i, (tag, head, body) in enumerate(STORIES):
        x = x0 + (i % 2) * (pw + gap)
        y = y0 + (i // 2) * (ph + gap)
        d.rounded_rectangle([x, y, x + pw, y + ph], radius=10,
                            fill="white", outline=COLORS[i], width=4)
        d.text((x + 18, y + 14), f"{i+1:02d}  •  {tag}", font=f_tag, fill=COLORS[i])
        for j, line in enumerate(wrap(d, head, f_head, pw - 36)):
            d.text((x + 18, y + 46 + j * 32), line, font=f_head, fill="#111827")
        n_head_lines = len(wrap(d, head, f_head, pw - 36))
        for j, line in enumerate(wrap(d, body, f_body, pw - 36)):
            d.text((x + 18, y + 46 + n_head_lines * 32 + 8 + j * 26),
                   line, font=f_body, fill="#374151")

    d.text((32, 988), "Sources: Reuters, AP/AFP, SCMP, Economic Times — morning of 26 Nov 2026.",
           font=ImageFont.truetype(REG, 16), fill="#6b7280")

    outdir = "/output" if os.path.isdir("/output") and os.access("/output", os.W_OK) else "."
    path = os.path.join(outdir, "entry.png")
    img.save(path, format="PNG", optimize=True)
    print(path)


if __name__ == "__main__":
    main()
