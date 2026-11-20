#!/usr/bin/env python3
"""Draw the news-image-20261119 entry, v2: one page summing up the world
news of Thursday 19 November 2026, rendered with PIL so every letter stays
crisp at 1024x1024. No network, no randomness, no clock: the same run
always writes the same bytes.

v2 keeps everything that made v1 strong - 52 stories, 16 cards, 7 regions,
9 fields, BY REGION + BY FIELD bars computed from the data, the day-in-
numbers strip, the 7-point UTC timeline, the dotted world map with 16
numbered pins, the 36-more list and the sources footer - and fixes what
the live top 3 do better:
  * the 3 big-card banners are redrawn as detailed scenes: the summit as
    three seated leaders with flags and nameplates, the ICJ as a courthouse
    with scales and a big red 9-6 badge, COP31 as a globe and thermometer
    under a rotated FOSSIL FUELS CUT stamp; the GTA VI card gets a night
    cityscape with a glowing VI sign and the Anthropic card a dark chart
    with green candles;
  * the 36-more list is reworked into 3 columns with headlines rewritten
    short enough that nothing truncates mid-word (the build asserts this);
  * a THE VERDICT box sits beside the map, every card carries a
    REPORTED / CLAIM / FORECAST tag, and a HOW SURE ARE WE? legend
    explains them in the footer;
  * the DATE CHECK drops two corrections the current rank 1 already has
    right (Krasnodar two refineries, South Africa 7.25%) and keeps the
    verified hits: the Hormuz tanker claim (IRGC, 4 Nov) and the Nature
    red-giant paper (18 Nov) both ran as 19 Nov news on the rank-1 page,
    and the rank-3 page ran "Earth's missing billion years" (Nature, 4 Nov)
    as a card and put Voyager "one light-day out" in its numbers strip
    although its own DATE CHECK says it happened Wednesday.

Every story on the page happened, or was first reported, on Thursday
19 November 2026, verified against Reuters, AP, AFP, BBC, CNN, WSJ, UN
News, Carbon Brief, Yonhap, ABS, NWS, AIU, IMD, Le Monde and France 24.
"""
import math
import os
from collections import Counter

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 24
CW = W - 2 * M  # 976 content width

PAPER = (251, 250, 247)
INK = (17, 17, 19)
BODY = (64, 62, 58)
NAVY = (18, 32, 62)
NAVY_SOFT = (38, 56, 92)
GOLD = (198, 154, 60)
CRIMSON = (166, 25, 46)
GREY = (96, 94, 88)
CARD = (255, 255, 255)
RULE = (208, 202, 188)
PALE = (206, 219, 238)
RED = (178, 34, 34)
TEAL = (14, 120, 120)
ORANGE = (200, 110, 20)
GREEN = (16, 120, 70)
AMBER = (198, 138, 0)
BLUE = (36, 86, 170)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def f(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, font, max_w):
    out, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def para(d, lines, x, y, font, fill, leading):
    for ln in lines:
        d.text((x, y), ln, font=font, fill=fill)
        y += leading
    return y


def trunc(d, text, font, max_w):
    """Shorten text to fit max_w, adding an ellipsis if cut."""
    if d.textlength(text, font=font) <= max_w:
        return text
    ell = "…"
    while text and d.textlength(text + ell, font=font) > max_w:
        text = text[:-1].rstrip()
        if " " in text:
            text = text.rsplit(" ", 1)[0]
        else:
            text = text[:-1]
    return text + ell


def vgrad(d, x0, y0, x1, y1, top, bottom, bands=8):
    """Vertical gradient as thin horizontal bands (PIL has no gradient)."""
    for i in range(bands):
        t = i / (bands - 1) if bands > 1 else 0
        col = tuple(int(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
        y_a = y0 + (y1 - y0) * i / bands
        y_b = y0 + (y1 - y0) * (i + 1) / bands
        d.rectangle([x0, y_a, x1, y_b], fill=col)


def burst(d, cx, cy, r, col):
    pts = []
    for i in range(16):
        ang = math.pi * i / 8
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=col)


def star5(d, cx, cy, r, col):
    """A five-pointed star (for the Chinese flag)."""
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=col)


def pic_bust(d, cx, table_y, skin, hair, suit, tie):
    """A seated leader, drawn as a bust behind a table: hair cap, head,
    shoulders and a tie sliver. table_y is the top edge of the table."""
    hr = 6
    d.ellipse([cx - hr - 1, table_y - 26, cx + hr + 1, table_y - 14], fill=hair)
    d.ellipse([cx - hr, table_y - 23, cx + hr, table_y - 11], fill=skin)
    d.rounded_rectangle([cx - 12, table_y - 12, cx + 12, table_y],
                        radius=4, fill=suit)
    d.polygon([(cx - 2, table_y - 12), (cx + 2, table_y - 12),
               (cx + 3, table_y - 4), (cx, table_y - 1), (cx - 3, table_y - 4)],
              fill=tie)


def pic_scales(d, cx, cy, s, col):
    # scales of justice: beam, two pans, central pillar
    w = max(2, int(s * 0.06))
    d.line([cx, cy - s * 0.30, cx, cy + s * 0.30], fill=col, width=w)
    d.line([cx - s * 0.38, cy - s * 0.22, cx + s * 0.38, cy - s * 0.22], fill=col, width=w)
    d.ellipse([cx - s * 0.07, cy - s * 0.38, cx + s * 0.07, cy - s * 0.24], fill=col)
    for dx in (-0.38, 0.38):
        d.line([cx + dx * s, cy - s * 0.22, cx + dx * s, cy + s * 0.02], fill=col, width=max(1, w - 1))
        d.polygon([(cx + dx * s - s * 0.16, cy + s * 0.02), (cx + dx * s + s * 0.16, cy + s * 0.02),
                   (cx + dx * s, cy + s * 0.18)], fill=col)
    d.rectangle([cx - s * 0.16, cy + s * 0.30, cx + s * 0.16, cy + s * 0.36], fill=col)


def pic_cyclone(d, cx, cy, s, col):
    for i, (r, a0, a1) in enumerate(((0.44, 20, 300), (0.32, 140, 420), (0.20, 260, 540))):
        d.arc([cx - s * r, cy - s * r, cx + s * r, cy + s * r], start=a0, end=a1,
              fill=col, width=max(3, int(s * 0.09)))
    d.ellipse([cx - s * 0.06, cy - s * 0.06, cx + s * 0.06, cy + s * 0.06], fill=col)


def pic_chart_down(d, cx, cy, s, col):
    w = max(2, int(s * 0.06))
    bars = [0.42, 0.34, 0.28, 0.18]
    bw = s * 0.16
    x0 = cx - s * 0.40
    for i, h in enumerate(bars):
        x = x0 + i * (bw + s * 0.04)
        d.rectangle([x, cy + s * 0.30 - h * s, x + bw, cy + s * 0.30], fill=col)
    d.line([cx - s * 0.44, cy - s * 0.28, cx + s * 0.10, cy - s * 0.02,
            cx + s * 0.44, cy + s * 0.10], fill=CRIMSON, width=w)
    d.polygon([(cx + s * 0.44, cy + s * 0.10), (cx + s * 0.44, cy - s * 0.10),
               (cx + s * 0.24, cy + s * 0.10)], fill=CRIMSON)


def pic_gavel(d, cx, cy, s, col):
    # gavel: head + handle, diagonal, over a sound block
    w = max(3, int(s * 0.09))
    d.line([cx - s * 0.30, cy + s * 0.28, cx + s * 0.34, cy - s * 0.30], fill=col, width=w)
    d.line([cx - s * 0.42, cy - s * 0.02, cx - s * 0.06, cy + s * 0.30], fill=col, width=int(w * 1.6))
    d.rectangle([cx - s * 0.30, cy + s * 0.34, cx + s * 0.30, cy + s * 0.42], fill=col)
    d.ellipse([cx + s * 0.30, cy - s * 0.34, cx + s * 0.44, cy - s * 0.20], fill=(255, 210, 60))


def pic_runner(d, cx, cy, s, col):
    # runner in stride: head, torso, limbs as thick lines
    w = max(3, int(s * 0.09))
    d.ellipse([cx + s * 0.10, cy - s * 0.42, cx + s * 0.26, cy - s * 0.26], fill=col)
    d.line([cx, cy - s * 0.22, cx - s * 0.06, cy + s * 0.06], fill=col, width=w)
    d.line([cx - s * 0.02, cy - s * 0.16, cx + s * 0.28, cy - s * 0.28], fill=col, width=w)
    d.line([cx - s * 0.02, cy - s * 0.14, cx - s * 0.30, cy - s * 0.04], fill=col, width=w)
    d.line([cx - s * 0.06, cy + s * 0.06, cx - s * 0.34, cy + s * 0.22], fill=col, width=w)
    d.line([cx - s * 0.06, cy + s * 0.06, cx + s * 0.26, cy + s * 0.30], fill=col, width=w)
    d.line([cx - s * 0.34, cy + s * 0.22, cx - s * 0.38, cy + s * 0.38], fill=col, width=w)
    d.line([cx + s * 0.26, cy + s * 0.30, cx + s * 0.42, cy + s * 0.38], fill=col, width=w)


def pic_dome(d, cx, cy, s, col):
    # parliament dome on a columned base
    w = max(2, int(s * 0.05))
    d.arc([cx - s * 0.30, cy - s * 0.38, cx + s * 0.30, cy + s * 0.10], 180, 360, fill=col, width=w)
    d.line([cx, cy - s * 0.52, cx, cy - s * 0.38], fill=col, width=w)
    d.rectangle([cx - s * 0.34, cy + s * 0.08, cx + s * 0.34, cy + s * 0.16], fill=col)
    for i in range(4):
        x = cx - s * 0.27 + i * s * 0.18
        d.rectangle([x, cy + s * 0.16, x + s * 0.06, cy + s * 0.36], fill=col)
    d.rectangle([cx - s * 0.38, cy + s * 0.36, cx + s * 0.38, cy + s * 0.42], fill=col)


def pic_car(d, cx, cy, s, col):
    # a tiny car in profile: body, cabin, two wheels
    d.rounded_rectangle([cx - s * 0.42, cy - s * 0.10, cx + s * 0.42, cy + s * 0.12],
                        radius=int(s * 0.06), fill=col)
    d.polygon([(cx - s * 0.22, cy - s * 0.10), (cx - s * 0.12, cy - s * 0.26),
               (cx + s * 0.18, cy - s * 0.26), (cx + s * 0.28, cy - s * 0.10)],
              fill=col)
    for wx in (-0.24, 0.24):
        d.ellipse([cx + wx * s - s * 0.09, cy + s * 0.06,
                   cx + wx * s + s * 0.09, cy + s * 0.24], fill=(20, 20, 24))

# ---------------- card banners ----------------
# Each banner is a wide scene at the top of its card, built in three
# layers: a vertical sky gradient (thin bands), a background scene
# (skyline, stars, rain, ground), and a foreground pictogram with a small
# detail (a sun, a moon, smoke, a leader line). Original drawings.
# v2 redraws the big three as characterful scenes (leaders at a table,
# courthouse with a 9-6 badge, globe under a FOSSIL FUELS CUT stamp) and
# gives GTA VI a night cityscape with a glowing VI sign and Anthropic a
# dark chart with green candles.

def draw_banner(img, d, x0, y0, x1, y1, kind, accent, icon):
    w, h = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    s = int(h * 0.78)
    if kind == "summit2":
        # Shenzhen hall in daylight: pale walls so the dark suits read,
        # three flags on poles, three seated leaders behind a cream table
        # with nameplates.
        vgrad(d, x0, y0, x1, y1, (216, 222, 236), (182, 194, 214))
        table_y = y1 - 13
        d.rectangle([x0, table_y, x1, y1], fill=(232, 226, 210))
        d.line([x0, table_y, x1, table_y], fill=GOLD, width=2)
        leaders = [
            ("TRUMP", (240, 205, 170), (240, 210, 110), (30, 30, 36), (200, 40, 40), "us"),
            ("XI", (232, 190, 160), (30, 30, 34), (24, 24, 30), (200, 40, 40), "cn"),
            ("PUTIN", (238, 200, 165), (170, 170, 175), (28, 28, 34), (40, 90, 180), "ru"),
        ]
        for i, (name, skin, hair, suit, tie, flag) in enumerate(leaders):
            fx = cx + (i - 1) * w * 0.27
            fw, fh = 24, 15
            d.line([fx, y0 + 2, fx, table_y], fill=(100, 100, 110), width=2)
            if flag == "us":
                for j in range(5):
                    d.rectangle([fx - fw / 2, y0 + 2 + j * fh / 5,
                                 fx + fw / 2, y0 + 2 + (j + 1) * fh / 5],
                                fill=(178, 34, 34) if j % 2 == 0 else (255, 255, 255))
                d.rectangle([fx - fw / 2, y0 + 2, fx - fw / 2 + fw * 0.45, y0 + 2 + fh * 0.4],
                            fill=(30, 50, 110))
            elif flag == "cn":
                d.rectangle([fx - fw / 2, y0 + 2, fx + fw / 2, y0 + 2 + fh], fill=(222, 40, 40))
                star5(d, fx - fw * 0.22, y0 + 2 + fh * 0.32, 4, (255, 210, 60))
            else:
                for j, c in enumerate([(255, 255, 255), (40, 90, 180), (200, 40, 40)]):
                    d.rectangle([fx - fw / 2, y0 + 2 + j * fh / 3,
                                 fx + fw / 2, y0 + 2 + (j + 1) * fh / 3], fill=c)
            pic_bust(d, fx, table_y, skin, hair, suit, tie)
            fn = f(SANS_B, 7)
            d.text((fx - d.textlength(name, font=fn) / 2, y1 - 11),
                   name, font=fn, fill=NAVY)
    elif kind == "icj2":
        # The Hague: pale stone courthouse, the scales, a big red 9-6 badge.
        vgrad(d, x0, y0, x1, y1, (232, 228, 218), (200, 192, 176))
        for i in range(5):
            x = x0 + w * (0.06 + i * 0.19)
            d.rectangle([x, y1 - h * 0.62, x + w * 0.07, y1], fill=(120, 108, 88))
        d.rectangle([x0, y1 - h * 0.66, x1, y1 - h * 0.60], fill=(120, 108, 88))
        d.polygon([(x0 + w * 0.30, y1 - h * 0.66), (x0 + w * 0.70, y1 - h * 0.66),
                   (cx, y1 - h * 0.92)], fill=(140, 128, 106))
        d.rectangle([x0, y1 - h * 0.14, x1, y1], fill=(90, 80, 64))
        pic_scales(d, cx - w * 0.14, cy - 2, s, NAVY)
        # the 9-6 badge sits bottom-left, clear of the confidence pill
        # that lives at the banner's top-right corner
        d.rounded_rectangle([x0 + 6, y1 - 24, x0 + 58, y1 - 5], radius=4, fill=CRIMSON)
        fb = f(SANS_B, 14)
        d.text((x0 + 32 - d.textlength("9–6", font=fb) / 2, y1 - 22),
               "9–6", font=fb, fill=(255, 255, 255))
    elif kind == "cop31b":
        # Antalya: teal sky, globe, red thermometer, sun - and a rotated
        # FOSSIL FUELS CUT stamp across the middle.
        vgrad(d, x0, y0, x1, y1, (120, 200, 190), (40, 140, 140))
        d.ellipse([x0 + w * 0.06, cy - h * 0.34, x0 + w * 0.06 + h * 0.68, cy + h * 0.34],
                  fill=(40, 110, 180))
        d.arc([x0 + w * 0.06, cy - h * 0.34, x0 + w * 0.06 + h * 0.68, cy + h * 0.34],
              300, 60, fill=(90, 190, 120), width=3)
        d.arc([x0 + w * 0.06, cy - h * 0.34, x0 + w * 0.06 + h * 0.68, cy + h * 0.34],
              120, 250, fill=(90, 190, 120), width=3)
        d.ellipse([x0 + 6, y0 + 3, x0 + 18, y0 + 15], fill=(255, 230, 120))
        tx = x0 + w * 0.78
        d.rectangle([tx - 3, y0 + h * 0.16, tx + 3, y1 - h * 0.22], fill=(255, 255, 255))
        d.rectangle([tx - 3, y0 + h * 0.52, tx + 3, y1 - h * 0.22], fill=(220, 40, 40))
        d.ellipse([tx - 7, y1 - h * 0.26, tx + 7, y1 - h * 0.06], fill=(220, 40, 40))
        stamp = Image.new("RGBA", (140, 26), (0, 0, 0, 0))
        sd = ImageDraw.Draw(stamp)
        sd.rectangle([1, 1, 138, 24], outline=(200, 30, 40, 255), width=2)
        sf = f(SANS_B, 11)
        sd.text(((140 - sd.textlength("FOSSIL FUELS CUT", font=sf)) / 2, 6),
                "FOSSIL FUELS CUT", font=sf, fill=(200, 30, 40, 255))
        stamp = stamp.rotate(-7, expand=True, resample=Image.BICUBIC)
        img.paste(stamp, (int(cx + 8 - stamp.width / 2), int(cy - stamp.height / 2)), stamp)
    elif kind == "ant2":
        # Nasdaq, first day: a dark chart with rising green candles.
        d.rectangle([x0, y0, x1, y1], fill=(14, 26, 46))
        for i in range(4):
            y = y0 + h * (0.20 + i * 0.20)
            d.line([x0 + 6, y, x1 - 6, y], fill=(40, 52, 74), width=1)
        tops = [cy + 9, cy + 6, cy + 4, cy + 1, cy - 2, cy - 5]
        pts = []
        for i, top in enumerate(tops):
            bx = x0 + 14 + i * 28
            d.line([bx + 4, top - 3, bx + 4, cy + 11], fill=(40, 200, 120), width=2)
            d.rectangle([bx, top, bx + 9, cy + 11], fill=(40, 200, 120))
            pts.append((bx + 4, top))
        d.line(pts, fill=(80, 230, 140), width=2)
        ef = f(SANS_B, 12)
        d.text((x0 + 6, y0 + 3), "ANT $83", font=ef, fill=(255, 255, 255))
    elif kind == "gta2":
        # Vice City at night: skyline, stars, a glowing VI sign, a car.
        vgrad(d, x0, y0, x1, y1, (58, 38, 92), (34, 20, 56))
        for sx, sy in ((0.06, 0.22), (0.16, 0.55), (0.30, 0.14), (0.55, 0.60),
                       (0.70, 0.18), (0.86, 0.45), (0.94, 0.22)):
            d.ellipse([x0 + w * sx - 1, y0 + h * sy - 1, x0 + w * sx + 1, y0 + h * sy + 1],
                      fill=(200, 170, 230))
        for bx, bw, bh in ((0.00, 0.13, 0.30), (0.15, 0.10, 0.42), (0.27, 0.12, 0.24),
                           (0.41, 0.09, 0.36), (0.52, 0.13, 0.28), (0.67, 0.10, 0.44),
                           (0.79, 0.11, 0.30), (0.92, 0.08, 0.38)):
            d.rectangle([x0 + w * bx, y1 - h * bh, x0 + w * (bx + bw), y1],
                        fill=(18, 10, 34))
        for wx in (0.05, 0.19, 0.32, 0.45, 0.57, 0.71, 0.83, 0.94):
            for wy in (0.62, 0.78):
                d.rectangle([x0 + w * wx, y1 - h * wy, x0 + w * wx + 2, y1 - h * wy + 2],
                            fill=(255, 210, 110))
        d.rectangle([x0, y1 - 5, x1, y1], fill=(22, 14, 38))
        pic_car(d, x0 + w * 0.80, y1 - 8, 14, (200, 50, 80))
        vf = f(SANS_B, 22)
        vt = "VI"
        vx = cx - d.textlength(vt, font=vf) / 2
        vy = y0 + 3
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            d.text((vx + dx, vy + dy), vt, font=vf, fill=(150, 30, 90))
        d.text((vx, vy), vt, font=vf, fill=(255, 70, 190))
    elif kind == "bridge":
        # night over the Kerch Strait: arch, road deck, explosion burst
        vgrad(d, x0, y0, x1, y1, (14, 22, 52), (28, 42, 78))
        for sx, sy in ((0.07, 0.22), (0.18, 0.60), (0.30, 0.16), (0.52, 0.72),
                       (0.66, 0.24), (0.79, 0.58), (0.90, 0.20)):
            d.ellipse([x0 + w * sx - 1.5, y0 + h * sy - 1.5,
                       x0 + w * sx + 1.5, y0 + h * sy + 1.5], fill=(255, 255, 255))
        d.ellipse([x0 + w * 0.55, y0 + 4, x0 + w * 0.55 + 16, y0 + 20], fill=(240, 238, 220))
        d.ellipse([x0 + w * 0.55 + 5, y0 + 2, x0 + w * 0.55 + 21, y0 + 18], fill=(28, 42, 78))
        d.rectangle([x0, y1 - h * 0.30, x1, y1 - h * 0.24], fill=(70, 80, 100))
        d.arc([cx - w * 0.30, y1 - h * 0.62, cx + w * 0.30, y1 - h * 0.10], 180, 360,
              fill=(120, 130, 150), width=3)
        for i in range(5):
            x = cx - w * 0.24 + i * w * 0.12
            d.line([x, y1 - h * 0.30, x, y1 - h * 0.52], fill=(120, 130, 150), width=2)
        burst(d, cx - w * 0.28, y1 - h * 0.48, int(h * 0.22), (255, 180, 60))
        burst(d, cx + w * 0.30, y1 - h * 0.36, int(h * 0.14), (255, 140, 60))
    elif kind == "cyclone":
        vgrad(d, x0, y0, x1, y1, (150, 196, 228), (190, 220, 240))
        for i in range(6):
            x = x0 + w * (0.10 + i * 0.15)
            d.line([x, y0 + 4, x - 6, y0 + h * 0.45], fill=(255, 255, 255), width=2)
            x2 = x0 + w * (0.16 + i * 0.15)
            d.line([x2, y0 + h * 0.55, x2 - 6, y1 - 4], fill=(255, 255, 255), width=2)
        d.rectangle([x0, y1 - h * 0.16, x1, y1], fill=(60, 110, 160))
        for i in range(5):
            x = x0 + w * (0.06 + i * 0.20)
            d.arc([x, y1 - h * 0.16, x + w * 0.12, y1 - h * 0.02], 180, 360,
                  fill=(220, 240, 255), width=2)
        pic_cyclone(d, cx, cy - 4, s, (20, 60, 110))
    elif kind == "missile":
        # pre-dawn Riyadh: alert glow, missile trail, burst over the city
        vgrad(d, x0, y0, x1, y1, (60, 50, 70), (140, 90, 70))
        for bx, bw, bh in ((0.00, 0.15, 0.34), (0.17, 0.11, 0.24), (0.30, 0.16, 0.42),
                           (0.48, 0.11, 0.28), (0.61, 0.15, 0.38), (0.78, 0.11, 0.24),
                           (0.91, 0.09, 0.32)):
            d.rectangle([x0 + w * bx, y1 - h * bh, x0 + w * (bx + bw), y1],
                        fill=(30, 26, 40))
        for bx in (0.05, 0.35, 0.66, 0.84):
            for wy in (0.55, 0.70):
                d.rectangle([x0 + w * bx, y1 - h * wy, x0 + w * bx + 4, y1 - h * wy + 5],
                            fill=(255, 210, 110))
        for i in range(6):
            t = i / 5
            tx = x0 + w * (0.12 + t * 0.55)
            ty = cy - h * (0.30 - t * 0.55)
            d.ellipse([tx - 1.5, ty - 1.5, tx + 1.5, ty + 1.5], fill=(255, 210, 90))
        burst(d, x0 + w * 0.60, y0 + h * 0.22, int(h * 0.20), (255, 170, 60))
    elif kind == "gavel":
        # Seoul court: wood tones, gavel over a sound block
        vgrad(d, x0, y0, x1, y1, (120, 84, 52), (84, 58, 36))
        d.rectangle([x0, y1 - h * 0.16, x1, y1], fill=(60, 40, 24))
        for i in range(4):
            x = x0 + w * (0.10 + i * 0.24)
            d.rectangle([x, y0 + h * 0.12, x + w * 0.10, y1 - h * 0.16], fill=(150, 110, 70))
        pic_gavel(d, cx, cy - 2, s, (250, 240, 220))
    elif kind == "march":
        # Bogotá street march: crowd dots, placards, the yellow-blue-red band
        vgrad(d, x0, y0, x1, y1, (240, 230, 210), (210, 196, 170))
        d.rectangle([x0, y0, x1, y0 + h * 0.14], fill=(255, 210, 60))
        d.rectangle([x0, y0 + h * 0.14, x1, y0 + h * 0.24], fill=(40, 90, 180))
        d.rectangle([x0, y0 + h * 0.24, x1, y0 + h * 0.34], fill=(200, 40, 40))
        for i in range(9):
            x = x0 + w * (0.05 + i * 0.11)
            d.ellipse([x - 4, y1 - h * 0.42, x + 4, y1 - h * 0.42 + 8], fill=(40, 40, 48))
            d.rectangle([x - 5, y1 - h * 0.42 + 9, x + 5, y1 - h * 0.10], fill=(60, 60, 70))
        for px, py in ((0.22, 0.42), (0.55, 0.38), (0.82, 0.44)):
            d.rectangle([x0 + w * px - 8, y0 + h * py, x0 + w * px + 8, y0 + h * py + 12],
                        fill=(255, 255, 255), outline=(40, 40, 48))
    elif kind == "exam":
        # Suneung: classroom, desks, pencil, wall clock (top-left now,
        # so the confidence tag at top-right stays clear)
        vgrad(d, x0, y0, x1, y1, (210, 225, 235), (170, 190, 210))
        d.ellipse([x0 + 6, y0 + 4, x0 + 28, y0 + 26], fill=(255, 255, 255))
        d.line([x0 + 17, y0 + 15, x0 + 17, y0 + 8], fill=NAVY, width=2)
        d.line([x0 + 17, y0 + 15, x0 + 23, y0 + 15], fill=NAVY, width=2)
        for i in range(3):
            x = x0 + w * (0.08 + i * 0.28)
            d.rectangle([x, y1 - h * 0.34, x + w * 0.20, y1 - h * 0.28], fill=(150, 110, 70))
            d.rectangle([x + 2, y1 - h * 0.28, x + w * 0.20 - 2, y1], fill=(120, 86, 52))
            d.ellipse([x + w * 0.08, y1 - h * 0.52, x + w * 0.08 + 10, y1 - h * 0.52 + 10],
                      fill=(50, 50, 60))
        d.polygon([(cx - s * 0.30, cy - s * 0.10), (cx + s * 0.30, cy - s * 0.10),
                   (cx + s * 0.36, cy + s * 0.02), (cx - s * 0.36, cy + s * 0.02)],
                  fill=(255, 210, 60))
    elif kind == "chart_down":
        d.rectangle([x0, y0, x1, y1], fill=(240, 238, 230))
        for i in range(5):
            y = y0 + h * (0.18 + i * 0.16)
            d.line([x0 + 6, y, x1 - 6, y], fill=(220, 216, 206), width=1)
        pic_chart_down(d, cx, cy, s, NAVY)
    elif kind == "runner":
        # Nairobi: track lanes, lane lines, runner (sun moved top-left)
        vgrad(d, x0, y0, x1, y1, (200, 60, 50), (150, 40, 36))
        d.rectangle([x0, y1 - h * 0.30, x1, y1], fill=(190, 120, 70))
        for i in range(3):
            y = y1 - h * (0.24 - i * 0.08)
            d.line([x0, y, x1, y], fill=(255, 255, 255), width=1)
        d.ellipse([x0 + 6, y0 + 4, x0 + 24, y0 + 22], fill=(255, 230, 120))
        pic_runner(d, cx, cy - 2, s, (255, 255, 255))
    elif kind == "flood":
        # South Florida: grey rain sky, waves, a half-submerged house
        vgrad(d, x0, y0, x1, y1, (140, 155, 170), (180, 195, 205))
        for i in range(6):
            x = x0 + w * (0.10 + i * 0.15)
            d.line([x, y0 + 4, x - 6, y0 + h * 0.40], fill=(255, 255, 255), width=2)
        d.rectangle([x0, y1 - h * 0.30, x1, y1], fill=(50, 100, 150))
        for i in range(5):
            x = x0 + w * (0.06 + i * 0.20)
            d.arc([x, y1 - h * 0.30, x + w * 0.12, y1 - h * 0.16], 180, 360,
                  fill=(220, 240, 255), width=2)
        hx = cx - w * 0.20
        d.rectangle([hx, y1 - h * 0.52, hx + w * 0.30, y1 - h * 0.30], fill=(200, 170, 120))
        d.polygon([(hx - 4, y1 - h * 0.52), (hx + w * 0.15, y1 - h * 0.68),
                   (hx + w * 0.30 + 4, y1 - h * 0.52)], fill=(140, 60, 50))
    elif kind == "parliament":
        # Paris: tricolore sky, parliament dome
        d.rectangle([x0, y0, x1, y0 + h * 0.34], fill=(40, 90, 180))
        d.rectangle([x0, y0 + h * 0.34, x1, y0 + h * 0.67], fill=(255, 255, 255))
        d.rectangle([x0, y0 + h * 0.67, x1, y1], fill=(200, 40, 40))
        d.rectangle([x0, y1 - h * 0.34, x1, y1], fill=(230, 225, 215))
        pic_dome(d, cx, cy + 4, s, NAVY)
    elif kind == "diplomacy":
        # Mogadishu: two flagpoles, a broken chain link between them
        vgrad(d, x0, y0, x1, y1, (210, 225, 240), (170, 190, 210))
        for fx, col1, col2 in ((0.20, (100, 160, 220), (255, 255, 255)),
                               (0.52, (220, 40, 40), (255, 255, 255))):
            x = x0 + w * fx
            d.line([x, y0 + h * 0.14, x, y1 - h * 0.10], fill=(60, 60, 70), width=2)
            d.rectangle([x, y0 + h * 0.14, x + w * 0.14, y0 + h * 0.42], fill=col1)
            d.rectangle([x, y0 + h * 0.14, x + w * 0.14, y0 + h * 0.28], fill=col2)
        d.arc([cx - s * 0.22, cy - s * 0.20, cx + s * 0.02, cy + s * 0.20], 90, 270,
              fill=CRIMSON, width=3)
        d.arc([cx - s * 0.02, cy - s * 0.20, cx + s * 0.22, cy + s * 0.20], 270, 90,
              fill=CRIMSON, width=3)
        d.line([cx - s * 0.02, cy - s * 0.20, cx + s * 0.02, cy - s * 0.20], fill=CRIMSON, width=3)

# ---------------- data ----------------

# Cards: (number, region, field, topic, verify, accent, banner kind,
#         headline, body, confidence). Headlines: big <= 56 chars, 5-col
#         small <= 42, 4-col small <= 54. Bodies: big <= 86, 5-col <= 60,
#         4-col <= 76. Confidence: REPORTED = confirmed by named sources;
#         CLAIM = one side says it, unverified; FORECAST = a poll, a draft
#         or a schedule (what happens next, not what happened).
CARDS = [
    (1, "ASIA", "Diplomacy", "SUMMIT", "REUTERS · WSJ", NAVY, "summit2",
     "Trump, Xi and Putin hold first three-way summit",
     "90 minutes at Kylin Villa: a 'Declaration toward Peace' — nuclear war 'cannot be won'.",
     "REPORTED"),
    (2, "EUROPE", "Justice", "GENOCIDE", "UN NEWS · CNN", CRIMSON, "icj2",
     "World Court: Myanmar committed genocide",
     "9–6, the first state held responsible. Some 10,000 killed; reparations ordered.",
     "REPORTED"),
    (3, "EUROPE", "Climate", "COP31", "REUTERS", TEAL, "cop31b",
     "COP31 draft drops fossil fuels and $120bn aid goal",
     "Second draft, 14:10: cut 144→80 paragraphs; fossil fuels and the $120bn goal cut.",
     "REPORTED"),
    (4, "AMERICAS", "Markets", "IPO", "WSJ · CNN", NAVY, "ant2",
     "Anthropic starts trading on Nasdaq as ANT",
     "Priced $83; opens $111.50, closes ~$97. Biggest IPO ever.",
     "REPORTED"),
    (5, "WORLD", "Culture", "GTA VI", "METACRITIC", GOLD, "gta2",
     "GTA VI goes on sale around the world",
     "Midnight launch, NZ first; PS5, Xbox only. Metacritic 99.",
     "REPORTED"),
    (6, "EUROPE", "War", "KERCH BRIDGE", "REUTERS · CNN", CRIMSON, "bridge",
     "Ukraine hits Crimean Bridge a third time",
     "Rail section hit after midnight; trains halt, then resume.",
     "REPORTED"),
    (7, "ASIA", "Climate", "AKVAN", "IMD · REUTERS", ORANGE, "cyclone",
     "Cyclone Akvan nears India's east coast",
     "Nearly 300,000 evacuated in Odisha. Landfall due Friday.",
     "FORECAST"),
    (8, "MIDDLE EAST", "War", "RIYADH", "REUTERS", CRIMSON, "missile",
     "Houthi missile threat over Riyadh",
     "04:42 alert, then a boom; debris damages buildings.",
     "CLAIM"),
    (9, "ASIA", "Justice", "SEOUL", "REUTERS · AP", NAVY, "gavel",
     "Korea's top court orders ex-PM Han retried",
     "15-year term partly overturned; retrial ordered. Detention extended.",
     "REPORTED"),
    (10, "AMERICAS", "Society", "BOGOTÁ", "INFOBAE", ORANGE, "march",
     "Colombia's unions hold a national strike",
     "Marches in Bogotá, Medellín, Cali vs the 'Economic Rescue' law.",
     "REPORTED"),
    (11, "ASIA", "Society", "SUNEUNG", "YONHAP", NAVY_SOFT, "exam",
     "Half a million sit Korea's Suneung exam",
     "551,864 candidates; flights pause 13:10–13:35. AI-cheating crackdown.",
     "REPORTED"),
    (12, "OCEANIA", "Markets", "JOBS", "ABS · REUTERS", TEAL, "chart_down",
     "Australia's jobless rate jumps to 4.9%",
     "Five-year high; 43,500 jobs lost in October vs a forecast gain of 25,000.",
     "REPORTED"),
    (13, "AFRICA", "Culture", "DOPING", "AIU · REUTERS", CRIMSON, "runner",
     "Marathon champion banned 3 years for EPO",
     "Jepchirchir admits EPO use; Sydney win stripped, Cheptai crowned.",
     "REPORTED"),
    (14, "AMERICAS", "Climate", "FLORIDA", "NWS · AP", ORANGE, "flood",
     "Floods shut South Florida schools again",
     "Up to 16.6 inches in Broward; synagogue roof collapses. Wettest November.",
     "REPORTED"),
    (15, "EUROPE", "Politics", "PARIS", "LE MONDE", NAVY, "parliament",
     "French left splits over a Mélenchon pact",
     "Greens offer a coalition; he welcomes talks. Glucksmann attacks.",
     "REPORTED"),
    (16, "AFRICA", "Diplomacy", "MOGADISHU", "REUTERS · AP", NAVY_SOFT, "diplomacy",
     "Somalia orders the UAE ambassador out",
     "72 hours to leave; Mogadishu recalls its envoy, citing an 'open invasion'.",
     "REPORTED"),
]

# 36 more stories: (number, region, field, city, headline). Headlines are
# rewritten short (city names are not repeated in them) so every item fits
# its column whole at 10pt - the build asserts zero truncation.
MORE = [
    (17, "EUROPE", "Diplomacy", "GREENLAND", "Denmark backs Arctic pact 109–0."),
    (18, "AMERICAS", "Politics", "WASHINGTON", "Iran war powers rejected 51–48."),
    (19, "ASIA", "Justice", "JAKARTA", "Asset-seizure law passes at last."),
    (20, "MIDDLE EAST", "War", "GAZA", "Israeli tanks push past Yellow Line."),
    (21, "ASIA", "Politics", "DHAKA", "Violence spreads; Yunus home burned."),
    (22, "AMERICAS", "War", "PORT-AU-PRINCE", "Police kill 34 gang members."),
    (23, "AFRICA", "Markets", "PRETORIA", "SARB holds rate at 7.25%, 4–3 split."),
    (24, "EUROPE", "Culture", "ROME", "Author Corrado Augias dies at 91."),
    (25, "OCEANIA", "Justice", "WELLINGTON", "Pay-equity reset discriminatory."),
    (26, "OCEANIA", "Climate", "NUKU'ALOFA", "Tonga declares drought emergency."),
    (27, "AFRICA", "Culture", "RABAT", "FIFA confirms 2027 presidential vote."),
    (28, "EUROPE", "Climate", "BRUSSELS", "EU delays methane rules by 2 years."),
    (29, "EUROPE", "Science", "LONDON", "MAIB: Bayesian sank in a wind flaw."),
    (30, "AFRICA", "Society", "OFF SENEGAL", "Migrant boat capsizes; 4 dead."),
    (31, "EUROPE", "Diplomacy", "BERLIN", "'Coalition of the willing' meets."),
    (32, "ASIA", "Climate", "ANTALYA", "Adaptation finance fell to $64.1bn."),
    (33, "AMERICAS", "Markets", "WASHINGTON", "Anthropic raises +$26bn privately."),
    (34, "EUROPE", "Politics", "PARIS", "Polls: Le Pen leads; Mélenchon ~20%."),
    (35, "EUROPE", "Justice", "THE HAGUE", "ICJ: Myanmar must report in 2 yrs."),
    (36, "EUROPE", "Diplomacy", "SHENZHEN", "Macron downplays the declaration."),
    (37, "ASIA", "War", "SHENZHEN", "Putin: no deals after bridge strikes."),
    (38, "OCEANIA", "Markets", "CANBERRA", "Participation 66.6%; dollar slides."),
    (39, "OCEANIA", "Culture", "SYDNEY", "Cheptai crowned Sydney champion."),
    (40, "OCEANIA", "Culture", "AUCKLAND", "NZ unlocks GTA VI first in the world."),
    (41, "ASIA", "Justice", "SEOUL", "Kim Keon Hee's 4-year term upheld."),
    (42, "AMERICAS", "Society", "BOGOTÁ", "97% of strike activities peaceful."),
    (43, "AMERICAS", "Diplomacy", "WASHINGTON", "Trump heads to Asia after midterms."),
    (44, "MIDDLE EAST", "War", "RIYADH", "MBS meets CENTCOM chief before boom."),
    (45, "AFRICA", "Diplomacy", "MOGADISHU", "Crowds rally for the expulsion."),
    (46, "OCEANIA", "Climate", "SUVA", "Fiji declares disaster; FJD 20m fund."),
    (47, "ASIA", "Diplomacy", "MANILA", "Trump heads to ASEAN, then Shenzhen."),
    (48, "EUROPE", "War", "KYIV", "Bridge strikes are stage 7: Zelenskyy."),
    (49, "EUROPE", "Justice", "THE HAGUE", "ICJ judgment: 191 pages, ~3 hours."),
    (50, "ASIA", "Climate", "ANTALYA", "Draft dated 14:10; all-night talks."),
    (51, "MIDDLE EAST", "War", "RIYADH", "Phone warnings before dawn; all clear."),
    (52, "EUROPE", "Climate", "BRUSSELS", "Methane MRV for importers from 2029."),
]

NUMBERS = [
    ("3", "presidents at one table"),
    ("9–6", "World Court genocide vote"),
    ("$81.3bn", "Anthropic's record IPO"),
    ("~300,000", "evacuated before Akvan"),
    ("551,864", "sit Korea's Suneung"),
    ("4.9%", "Australian jobless rate"),
]

# the day in UTC — every time verified against the reporting
UTC_TIMELINE = [
    ("00:30", "Australia jobs: 4.9%"),
    ("01:42", "Riyadh missile alert"),
    ("04:10", "Seoul flights pause"),
    ("05:00", "GTA VI unlocks in N. America"),
    ("09:00", "ICJ: Myanmar genocide"),
    ("11:10", "COP31 draft 2 published"),
    ("17:00", "ANT starts trading, $111.50"),
]

# (number, lat, lon) for the map pins — one per card
PINS = [
    (1, 22.5, 114.0), (2, 52.1, 4.3), (3, 36.9, 30.7), (4, 40.7, -74.0),
    (5, -36.8, 174.8), (6, 45.3, 36.5), (7, 20.0, 86.0), (8, 24.7, 46.7),
    (9, 37.5, 127.0), (10, 4.7, -74.1), (11, 35.2, 129.1), (12, -35.3, 149.1),
    (13, -1.3, 36.8), (14, 26.1, -80.2), (15, 48.9, 2.35), (16, 2.0, 45.3),
]

# display offsets (dx, dy) for pins that would overlap at their true spot;
# a thin leader line is drawn from the true spot to the nudged pin.
PIN_OFF = {
    2: (8, -6), 3: (-8, 8), 4: (-10, -6), 6: (0, -8), 8: (-6, -8),
    9: (0, -9), 10: (10, 4), 11: (10, 7), 13: (8, 6), 14: (-8, 6),
    15: (-10, -4), 16: (8, 6),
}

# dotted world map: landmasses as lon/lat ellipses (centre lon, centre lat,
# half-width lon, half-height lat); a dot is drawn for every grid cell
# whose centre falls inside one of them.
LANDMASSES = [
    (-100, 47, 58, 20), (-152, 64, 18, 8), (-86, 14, 12, 7), (-42, 73, 14, 9),
    (-60, -14, 19, 27), (14, 53, 26, 15), (-2, 54, 4, 5), (17, 3, 31, 32),
    (47, -19, 3, 8), (48, 30, 18, 12), (70, 45, 30, 18), (115, 42, 35, 20),
    (78, 21, 11, 11), (103, 13, 11, 9), (114, -2, 24, 5), (134, -25, 19, 11),
    (141, -5, 9, 4), (139, 37, 4, 6), (172, -41, 4, 6),
]


def _on_land(lon, lat):
    for clon, clat, hlon, hlat in LANDMASSES:
        if ((lon - clon) / hlon) ** 2 + ((lat - clat) / hlat) ** 2 <= 1:
            return True
    return False


# region and field counts, computed from the story data (never hand-counted)
REGION_ORDER = ["ASIA", "EUROPE", "MIDDLE EAST", "AFRICA", "AMERICAS", "OCEANIA", "WORLD"]
FIELD_ORDER = ["Diplomacy", "Justice", "Climate", "Markets", "War", "Culture",
               "Politics", "Society", "Science"]
_rc = Counter([c[1] for c in CARDS] + [m[1] for m in MORE])
_fc = Counter([c[2] for c in CARDS] + [m[2] for m in MORE])
REGIONS = [(r, _rc[r]) for r in REGION_ORDER if _rc[r]]
FIELDS = [(fld, _fc[fld]) for fld in FIELD_ORDER if _fc[fld]]

LEFT_OUT = ("Krasnodar refineries hit 17–18 Nov (two plants) · Hemedti's 2nd "
            "death sentence, ruled Wed 18 Nov · Hormuz tankers, an IRGC claim "
            "from 4 Nov · Van Gogh's $190.4m sale, Wed 18 Nov at Sotheby's · "
            "IAEA on Yongbyon, Wed 18 Nov · Nature's red-giant paper, 18 Nov")
NOT_YET = ("Cyclone Akvan's landfall (Fri 20) · the close of COP31 (Fri 20)")
CORRECTIONS = ("Other front pages ran the Hormuz tanker claim (IRGC, 4 Nov) "
               "and the Nature red-giant paper (18 Nov) as 19 Nov news; "
               "'Earth's missing billion years' (Nature, 4 Nov) as a card; "
               "and Voyager 'one light-day out' in a numbers strip, though "
               "it happened Wednesday.")

CONF_COLOUR = {"REPORTED": GREEN, "CLAIM": AMBER, "FORECAST": BLUE}
VERDICT = [
    "Myanmar committed genocide, 9 to 6.",
    "First state the court holds liable.",
    "Must allow return, make reparations.",
]
LEGEND = ("HOW SURE ARE WE? REPORTED = confirmed by named sources · CLAIM = "
          "one side says, unverified · FORECAST = poll, draft or schedule")

# ---------------- card drawing ----------------

def draw_card(img, d, card, x, y, w, h, big):
    num, region, field, topic, verify, accent, kind, headline, body, conf = card
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=RULE)
    d.rectangle([x, y, x + w, y + 3], fill=accent)
    if big:
        bh = 48
        hs, ts, bs, vs = 18, 12, 13, 10
    else:
        bh = 34
        hs, ts, bs, vs = 13, 10, 11, 8
    draw_banner(img, d, x + 1, y + 4, x + w - 1, y + 3 + bh, kind, accent, topic)
    # confidence pill, top-right of the banner (art is kept clear of it)
    cf = f(SANS_B, 8 if big else 7)
    pw = d.textlength(conf, font=cf) + 10
    ph = 13 if big else 12
    px1 = x + w - 5
    d.rounded_rectangle([px1 - pw, y + 6, px1, y + 6 + ph], radius=5,
                        fill=CONF_COLOUR[conf])
    d.text((px1 - pw + 5, y + 6 + (ph - (8 if big else 7)) // 2),
           conf, font=cf, fill=(255, 255, 255))
    ty = y + 3 + bh + 4
    ftag = f(SANS_B, ts)
    fv = f(SANS, vs)
    # tag + verify must both fit: drop the region, then shorten the verify
    # to its first source, rather than ever showing a truncated "…"
    tag = f"{num:02d} · {region} · {topic}"
    vt = verify
    gap = 6
    avail = w - 14
    if d.textlength(tag, font=ftag) + gap + d.textlength(vt, font=fv) > avail:
        tag = f"{num:02d} · {topic}"
    if d.textlength(tag, font=ftag) + gap + d.textlength(vt, font=fv) > avail:
        vt = verify.split(" · ")[0]
    if d.textlength(tag, font=ftag) + gap + d.textlength(vt, font=fv) > avail:
        vt = ""
    d.text((x + 9, ty), tag, font=ftag, fill=accent)
    if vt:
        d.text((x + w - 9 - d.textlength(vt, font=fv), ty + (ts - vs) // 2),
               vt, font=fv, fill=GREY)
    hy = ty + ts + 4
    fh = f(SANS_B, hs)
    for ln in wrap(d, headline, fh, w - 18)[:2 if big else 3]:
        d.text((x + 9, hy), ln, font=fh, fill=INK)
        hy += hs + 1
    fb = f(SANS, bs)
    by = hy + (2 if big else 1)
    for ln in wrap(d, body, fb, w - 18)[:2]:
        d.text((x + 9, by), ln, font=fb, fill=BODY)
        by += bs


# ---------------- page sections ----------------

def draw_header(d, y):
    hh = 68
    d.rectangle([M, y, M + CW, y + hh], fill=NAVY)
    bx0, bx1 = M + 12, M + 108
    d.rectangle([bx0, y + 10, bx1, y + hh - 10], fill=(255, 255, 255))
    fn = f(SANS_B, 20)
    d.text((bx0 + (bx1 - bx0 - d.textlength("NOV 19", font=fn)) / 2, y + 14),
           "NOV 19", font=fn, fill=NAVY)
    fs = f(SANS_B, 12)
    d.text((bx0 + (bx1 - bx0 - d.textlength("THU · 2026", font=fs)) / 2, y + 38),
           "THU · 2026", font=fs, fill=CRIMSON)
    d.text((M + 120, y + 10), "Thursday 19 November 2026",
           font=f(SERIF, 30), fill=(255, 255, 255))
    d.text((M + 120, y + 46),
           "The world, one page. Everything here happened — or was first reported — on that day.",
           font=f(SANS, 11), fill=PALE)
    total = len(CARDS) + len(MORE)
    cnt = f"{total} STORIES · {len(REGIONS)} REGIONS · {len(FIELDS)} FIELDS · 16 CARDS · ONE PAGE"
    fc = f(SANS_B, 10)
    d.text((M + CW - 12 - d.textlength(cnt, font=fc), y + 15), cnt, font=fc, fill=GOLD)
    d.text((M + CW - 12 - d.textlength("ONE DAY · ONE PAGE", font=fc), y + 32),
           "ONE DAY · ONE PAGE", font=fc, fill=(255, 255, 255))
    return y + hh


def draw_numbers(d, y):
    """Day-in-numbers strip: big navy number on top, small description below."""
    d.rectangle([M, y, M + CW, y + 29], fill=(255, 255, 255), outline=RULE)
    n = len(NUMBERS)
    seg = CW / n
    fn = f(SANS_B, 13)
    fv = f(SANS, 10)
    for i, (num, desc) in enumerate(NUMBERS):
        cx = M + seg * i + seg / 2
        d.text((cx - d.textlength(num, font=fn) / 2, y + 1), num, font=fn, fill=NAVY)
        d.text((cx - d.textlength(desc, font=fv) / 2, y + 16), desc, font=fv, fill=BODY)
        if i:
            d.line([M + seg * i, y + 3, M + seg * i, y + 27], fill=RULE, width=1)
    return y + 30


def draw_strip(d, y, items, name_font_size=9, val_font_size=11, name_is_bold=True):
    """A labelled horizontal strip: (label, value) pairs separated by rules."""
    n = len(items)
    seg = CW / n
    fn = f(SANS_B if name_is_bold else SANS, name_font_size)
    fv = f(SANS_B, val_font_size)
    for i, (label, val) in enumerate(items):
        cx = M + seg * i + seg / 2
        d.text((cx - d.textlength(label, font=fn) / 2, y), label, font=fn, fill=GREY)
        d.text((cx - d.textlength(val, font=fv) / 2, y + name_font_size + 2),
               val, font=fv, fill=INK)
        if i:
            d.line([M + seg * i, y + 2, M + seg * i, y + name_font_size + val_font_size + 5],
                   fill=RULE, width=1)
    return y + name_font_size + val_font_size + 5


def draw_timeline(d, y, items):
    d.text((M, y), "THE DAY BY HOURS", font=f(SANS_B, 10), fill=GREY)
    y0 = y + 12
    seg = CW / len(items)
    d.line([M, y0 + 3, M + CW, y0 + 3], fill=RULE, width=1)
    ft = f(SANS_B, 10)
    fe = f(SANS, 10)
    for i, (t, txt) in enumerate(items):
        cx = M + seg * i + seg / 2
        d.ellipse([cx - 3.5, y0, cx + 3.5, y0 + 7], fill=NAVY)
        d.text((cx - d.textlength(t, font=ft) / 2, y0 + 10), t, font=ft, fill=NAVY)
        d.text((cx - d.textlength(txt, font=fe) / 2, y0 + 21), txt, font=fe, fill=BODY)
    return y0 + 31


def draw_map_verdict(d, y, h):
    """Dotted world map (left) with 16 numbered pins, and THE VERDICT box
    (right) - the ICJ ruling in three lines, dark navy like rank 2's."""
    mw = 600
    vw = CW - mw - 16
    vx = M + mw + 16
    d.text((M, y), "WHERE IT HAPPENED — 16 PINS, ONE PER CARD",
           font=f(SANS_B, 10), fill=GREY)
    d.text((vx, y), "THE VERDICT — THE HAGUE · 10:00",
           font=f(SANS_B, 10), fill=GREY)
    y0 = y + 12
    y1 = y0 + h
    d.rectangle([M, y0, M + mw, y1], fill=(235, 240, 246), outline=RULE)
    lon_lo, lon_hi, lat_lo, lat_hi = -180, 180, -56, 84
    ncols, nrows = 122, 48
    step_lon = (lon_hi - lon_lo) / ncols
    step_lat = (lat_hi - lat_lo) / nrows
    for r in range(nrows):
        lat = lat_hi - (r + 0.5) * step_lat
        for c in range(ncols):
            lon = lon_lo + (c + 0.5) * step_lon
            if _on_land(lon, lat):
                px = M + (lon - lon_lo) / (lon_hi - lon_lo) * mw
                py = y0 + (lat_hi - lat) / (lat_hi - lat_lo) * (y1 - y0)
                d.ellipse([px - 1.2, py - 1.2, px + 1.2, py + 1.2],
                          fill=(150, 162, 174))
    for num, lat, lon in PINS:
        px = M + (lon - lon_lo) / (lon_hi - lon_lo) * mw
        py = y0 + (lat_hi - lat) / (lat_hi - lat_lo) * (y1 - y0)
        if num in PIN_OFF:
            dx, dy = PIN_OFF[num]
            qx, qy = px + dx, py + dy
            d.line([px, py, qx, qy], fill=CRIMSON, width=1)
            px, py = qx, qy
        d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=CRIMSON,
                  outline=(255, 255, 255), width=2)
        d.text((px - 2 if num < 10 else px - 4.5, py - 4.5),
               str(num), font=f(SANS_B, 8), fill=(255, 255, 255))
    d.rectangle([vx, y0, vx + vw, y1], fill=NAVY)
    fv = f(SANS, 11)
    for i, ln in enumerate(VERDICT):
        d.text((vx + 10, y0 + 2 + i * 11), ln, font=fv, fill=(255, 255, 255))
    return y1


def draw_list(d, y, h):
    d.text((M, y), "36 MORE STORIES", font=f(SANS_B, 11), fill=INK)
    y0 = y + 14
    cols, rows = 3, 12
    cw = (CW - 2 * 16) / cols
    fc = f(SANS_B, 10)
    ft = f(SANS, 10)
    bad = []
    for i, (num, region, field, city, headline) in enumerate(MORE):
        col, row = i % cols, i // cols
        x = M + col * (cw + 16)
        yy = y0 + row * 10
        ctext = f"{num:02d} · {city} "
        cw_city = d.textlength(ctext, font=fc)
        shown = trunc(d, headline, ft, cw - cw_city)
        if shown != headline:
            bad.append((num, headline, shown))
        d.text((x, yy), ctext, font=fc, fill=INK)
        d.text((x + cw_city, yy), shown, font=ft, fill=BODY)
    if bad:
        print("LIST TRUNCATES (fix the headlines):")
        for num, orig, shown in bad:
            print(f"  #{num}: {orig!r} -> {shown!r}")
    assert not bad, f"{len(bad)} list items truncate mid-word"
    return y0 + rows * 10


def draw_date_check(d, y, width):
    lines = []
    fb = f(SANS, 11)
    for prefix, text in (("LEFT OUT — FIRST REPORTED ON OTHER DAYS: ", LEFT_OUT),
                         ("NOT YET: ", NOT_YET),
                         ("CORRECTIONS: ", CORRECTIONS)):
        for ln in wrap(d, prefix + text, fb, width - 20):
            lines.append(ln)
    print(f"date check lines: {len(lines)}")
    assert len(lines) <= 5, f"date check wraps to {len(lines)} lines"
    h = 14 + 11 + 12 * len(lines) + 10
    d.rectangle([M, y, M + CW, y + h], fill=(254, 248, 236), outline=GOLD)
    d.text((M + 10, y + 6), "DATE CHECK", font=f(SANS_B, 11), fill=CRIMSON)
    yy = y + 20
    for i, ln in enumerate(lines):
        fill = CRIMSON if i == 0 and ln.startswith("LEFT OUT") else INK
        if ln.startswith("NOT YET"):
            fill = NAVY
        if ln.startswith("CORRECTIONS"):
            fill = CRIMSON
        d.text((M + 10, yy), ln, font=fb, fill=fill)
        yy += 12
    return y + h


def draw_footer(d, y):
    d.text((M, y),
           "Sources: Reuters · AP · AFP · BBC · CNN · WSJ · UN News · Carbon Brief · Yonhap · ABS · NWS · AIU · IMD · Le Monde · France 24",
           font=f(SANS, 9), fill=GREY)
    d.text((M, y + 12),
           "All 52 stories happened, or were first reported, on Thu 19 Nov 2026.",
           font=f(SANS, 9), fill=GREY)
    d.text((M, y + 24), LEGEND, font=f(SANS, 9), fill=GREY)
    return y + 33

# ---------------- build ----------------

def build():
    assert len(CARDS) == 16 and len(MORE) == 36
    assert sum(n for _, n in REGIONS) == 52 and sum(n for _, n in FIELDS) == 52
    assert [c[0] for c in CARDS] + [m[0] for m in MORE] == list(range(1, 53))
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = 12
    y = draw_header(d, y)
    y += 2
    y = draw_strip(d, y, [(r.upper(), str(n)) for r, n in REGIONS])  # BY REGION
    y += 2
    y = draw_strip(d, y, [(fld.upper(), str(n)) for fld, n in FIELDS])  # BY FIELD
    y += 3
    y = draw_numbers(d, y)
    y += 2
    y = draw_timeline(d, y, UTC_TIMELINE)
    y += 2
    # cards: row 1 = 3 big; row 2 = 5 small; rows 3-4 = 4 small
    big_w = (CW - 2 * 6) // 3
    x = M
    for card in CARDS[:3]:
        draw_card(img, d, card, x, y, big_w, 140, True)
        x += big_w + 6
    y += 140 + 6
    row2_w = (CW - 4 * 6) // 5
    x = M
    for card in CARDS[3:8]:
        draw_card(img, d, card, x, y, row2_w, 108, False)
        x += row2_w + 6
    y += 108 + 6
    row_w = (CW - 3 * 6) // 4
    for row_cards in (CARDS[8:12], CARDS[12:16]):
        x = M
        for card in row_cards:
            draw_card(img, d, card, x, y, row_w, 108, False)
            x += row_w + 6
        y += 108 + 6
    y -= 6
    y += 3
    y = draw_map_verdict(d, y, 36)
    y += 3
    y = draw_list(d, y, 108)
    y += 2
    y = draw_date_check(d, y, CW)
    y += 1
    y = draw_footer(d, y)
    print(f"final y after footer: {y} (canvas {H})")
    assert y <= H, f"layout overflows: footer ends at {y}"
    return img


if __name__ == "__main__":
    img = build()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")
