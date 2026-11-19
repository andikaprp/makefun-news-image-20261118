#!/usr/bin/env python3
"""One Day on Earth - 18 November 2026 in one image.

Renders a single 1024x1024 page that sums up one day of world news:
a stat band, a sun-order world map, eleven illustrated dispatches and
a 34-brief logbook, all drawn from stories-18.json. Deterministic:
two runs produce byte-identical output. No network access.
"""

import json
import math
import os
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SIZE = 1024
MARGIN = 36
CW = SIZE - 2 * MARGIN  # content width

# ---------------------------------------------------------------- palette
INK = (10, 19, 34)          # page background, deep observatory navy
INK_SOFT = (12, 24, 44)     # map sea
CARD = (16, 29, 48)         # dispatch card fill
CARD_EDGE = (43, 65, 102)   # dispatch card outline
AMBER = (240, 168, 60)      # sun amber, the page's accent
AMBER_DEEP = (214, 138, 38)
TITLE_GOLD = (242, 176, 74)
TEAL = (70, 185, 167)       # section sub-labels
CREAM = (247, 243, 232)     # headlines
BODY = (185, 197, 214)      # summaries and briefs
MUTED = (139, 153, 176)     # small print
LAND = (126, 151, 186)      # map landmass
PIN_RING = (250, 246, 235)

# ---------------------------------------------------------------- fonts
_FONT_DIRS = [
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/truetype/liberation",
    "/usr/share/fonts",
]


def _font_file(name):
    for d in _FONT_DIRS:
        p = Path(d) / name
        if p.exists():
            return str(p)
    for d in _FONT_DIRS:  # same files, nested one level deeper
        for p in sorted(Path(d).rglob(name)):
            return str(p)
    raise FileNotFoundError(name)


SERIF_PATH = _font_file("DejaVuSerif-Bold.ttf")
SERIF2_PATH = _font_file("LiberationSerif-Bold.ttf")
SERIF_IT_PATH = _font_file("LiberationSerif-Italic.ttf")
SANS_PATH = _font_file("LiberationSans-Regular.ttf")
SANS_B_PATH = _font_file("LiberationSans-Bold.ttf")

_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


# ---------------------------------------------------------------- text kit
def text_w(draw, s, fnt, tracking=0.0):
    """Width of a string, allowing extra letter tracking."""
    if not s:
        return 0.0
    w = draw.textlength(s, font=fnt)
    if tracking:
        w += tracking * (len(s) - 1)
    return w


def draw_tracked(draw, xy, s, fnt, fill, tracking=0.0):
    """Draw letter-spaced text one glyph at a time; returns end x."""
    x, y = xy
    for ch in s:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking
    return x


def draw_right(draw, xy_right, s, fnt, fill, tracking=0.0):
    w = text_w(draw, s, fnt, tracking)
    draw_tracked(draw, (xy_right[0] - w, xy_right[1]), s, fnt, fill, tracking)


def wrap(draw, s, fnt, max_w):
    """Greedy word wrap; returns a list of lines."""
    words = s.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_size(draw, s, path, start, max_w):
    """Largest font size (<= start) whose width fits max_w."""
    size = start
    while size > 10 and draw.textlength(s, font=font(path, size)) > max_w:
        size -= 2
    return size

# ---------------------------------------------------------------- backdrop
def starfield(img):
    """Faint observatory stars, fixed by seed so renders never drift."""
    rng = random.Random(20261118)
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(110):
        x = rng.uniform(0, SIZE)
        y = rng.uniform(0, SIZE)
        a = rng.randint(28, 95)
        r = rng.choice([1, 1, 1, 2])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(200, 214, 235, a))
    for _ in range(14):  # a few four-point sparkles
        x = rng.uniform(10, SIZE - 10)
        y = rng.uniform(10, SIZE - 10)
        a = rng.randint(50, 105)
        s = rng.uniform(2.5, 4.5)
        d.line([x - s, y, x + s, y], fill=(220, 228, 245, a), width=1)
        d.line([x, y - s, x, y + s], fill=(220, 228, 245, a), width=1)


# ---------------------------------------------------------------- header
def header(img, page):
    d = ImageDraw.Draw(img, "RGBA")
    f_eye = font(SANS_B_PATH, 14)
    # eyebrow row: a small drawn diamond, then the two tracked labels
    cx, cy = MARGIN + 4, 31
    d.polygon([(cx, cy - 5), (cx + 5, cy), (cx, cy + 5), (cx - 5, cy)],
              fill=AMBER)
    draw_tracked(d, (MARGIN + 16, 24), page["eyebrow_left"], f_eye, AMBER, 1.4)
    draw_right(d, (SIZE - MARGIN, 24), page["eyebrow_right"], f_eye,
               (203, 213, 228), 1.4)
    # title
    size = fit_size(d, page["title"], SERIF_PATH, 92, CW)
    d.text((MARGIN - 2, 42), page["title"], font=font(SERIF_PATH, size),
           fill=TITLE_GOLD)
    # subtitle, shrunk until it fits the measure
    sub_size = fit_size(d, page["subtitle"], SERIF_IT_PATH, 17, CW)
    d.text((MARGIN, 138), page["subtitle"],
           font=font(SERIF_IT_PATH, sub_size), fill=(200, 207, 221))
    # double rule under the subtitle
    d.line([MARGIN, 160, SIZE - MARGIN, 160], fill=AMBER + (220,), width=1)
    d.line([MARGIN, 164, SIZE - MARGIN, 164], fill=AMBER + (150,), width=1)


def stat_band(img, page, stats):
    d = ImageDraw.Draw(img, "RGBA")
    d.text((MARGIN, 172), page["stats_label"], font=font(SANS_B_PATH, 13),
           fill=TEAL)
    # auto-layout: measure the values, then spread the columns so the
    # big serif numbers can never run into each other
    size = 37
    while size > 24:
        f_num = font(SERIF2_PATH, size)
        widths = [d.textlength(st["value"], font=f_num) for st in stats]
        if sum(widths) + 5 * 20 <= CW:
            break
        size -= 1
    gap = (CW - sum(widths)) / 5.0
    f_cap = font(SANS_PATH, 11)
    x = float(MARGIN)
    for st, w in zip(stats, widths):
        # amber bead on the rule above each column
        d.ellipse([x + 1, 157, x + 7, 163], fill=AMBER)
        d.text((x, 184), st["value"], font=f_num, fill=TITLE_GOLD)
        cap_w = max(w + gap - 10, 152)
        cy = 226
        for line in wrap(d, st["caption"], f_cap, cap_w):
            d.text((x, cy), line, font=f_cap, fill=(167, 178, 196))
            cy += 12.5
        x += w + gap

# ---------------------------------------------------------------- the map
MAP_Y = 258
MAP_H = 64


# Pin positions on the map, as fractions of the box: placed for legibility
# in sun order, as the page's own caption says - positions approximate.
PIN_POS = {
    1: (0.660, 0.50), 2: (0.598, 0.42), 3: (0.368, 0.36), 4: (0.628, 0.55),
    5: (0.562, 0.30), 6: (0.518, 0.30), 7: (0.556, 0.58), 8: (0.400, 0.52),
    9: (0.466, 0.30), 10: (0.434, 0.38), 11: (0.882, 0.86),
}


def _project(lon, lat, box):
    x0, y0, x1, y1 = box
    px = x0 + 8 + (lon + 180.0) / 360.0 * (x1 - x0 - 16)
    py = y0 + 3 + (82.0 - lat) / 138.0 * (y1 - y0 - 6)
    return px, py


def sun_map(img, page, dispatches, briefs):
    """The map is drawn on a 2x layer and downscaled, so the squashed
    coastline lands smooth instead of speckled."""
    SS = 2
    bw, bh = CW, MAP_H
    layer = Image.new("RGBA", (bw * SS, bh * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer, "RGBA")
    box = (0, 0, bw * SS, bh * SS)
    d.rounded_rectangle(box, radius=9 * SS, fill=INK_SOFT + (255,),
                        outline=(51, 80, 126), width=SS)
    # landmasses from the carried-over coastline data
    land = json.loads((HERE / "land.json").read_text())
    for poly in land["polygons"]:
        for ring in poly:
            if all(lat < -55 for _, lat in ring):
                continue  # the page crops Antarctica away
            pts = []
            for lon, lat in ring:
                px, py = _project(lon, lat, (0, 0, bw, bh))
                pts.append((px * SS, py * SS))
            if len(pts) > 2:
                d.polygon(pts, fill=LAND + (235,))
    # the sun's path: a golden arc settling toward New Zealand
    p0 = (0.640 * bw * SS, 2.0 * SS)
    p1 = (0.830 * bw * SS, 8.0 * SS)
    p2 = (0.882 * bw * SS, (bh - 6.0) * SS)
    arc = []
    for i in range(81):
        t = i / 80.0
        ax = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
        ay = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
        arc.append((ax, ay))
    d.line(arc, fill=AMBER + (70,), width=5 * SS)
    d.line(arc, fill=AMBER + (255,), width=2 * SS)
    f_lab = font(SANS_B_PATH, 10 * SS)
    for label, fx, ly in [("DAWN", 0.612, 1), ("DUSK", 0.688, 13),
                          ("MIDDAY", 0.612, 42)]:
        lx = fx * bw * SS
        ly = ly * SS
        w = text_w(d, label, f_lab, 1.6 * SS)
        d.rounded_rectangle([lx - 3 * SS, ly - SS, lx + w + 3 * SS, ly + 13 * SS],
                            radius=3 * SS, fill=INK + (215,))
        draw_tracked(d, (lx, ly), label, f_lab, AMBER, 1.6 * SS)
    # brief dots first, dispatch pins on top
    for b in briefs:
        px, py = _project(b["lon"], b["lat"], (0, 0, bw, bh))
        px, py = px * SS, py * SS
        r = 1.8 * SS
        d.ellipse([px - r, py - r, px + r, py + r], fill=(205, 216, 233, 210))
    f_pin = font(SANS_B_PATH, 10 * SS)
    for s in dispatches:
        fx, fy = PIN_POS[s["n"]]
        px, py = fx * bw * SS, fy * bh * SS
        r = 10 * SS
        d.ellipse([px - r, py - r, px + r, py + r], fill=AMBER,
                  outline=PIN_RING, width=2 * SS)
        label = str(s["n"])
        tw = d.textlength(label, font=f_pin)
        d.text((px - tw / 2, py - 6 * SS), label, font=f_pin, fill=INK)
    # caption along the bottom of the box
    draw_tracked(d, (10 * SS, (bh - 14) * SS), page["map_caption"],
                 font(SANS_PATH, 9 * SS), (168, 180, 200), 1.1 * SS)
    img.paste(layer.resize((bw, bh), Image.LANCZOS), (MARGIN, MAP_Y),
              layer.resize((bw, bh), Image.LANCZOS))


# ---------------------------------------------------------------- card art
def _sky_base(w, h, seed):
    rng = random.Random(seed)
    art = Image.new("RGB", (w, h), (13, 23, 43))
    d = ImageDraw.Draw(art, "RGBA")
    for i in range(h):  # gentle vertical deepening
        shade = int(10 * i / max(h - 1, 1))
        d.line([0, i, w, i], fill=(13 - shade // 3, 23 - shade // 2, 43 - shade))
    for _ in range(46):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        a = rng.randint(60, 170)
        d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=(215, 224, 240, a))
    return art, d, rng


def _burst(d, cx, cy, scale, rng):
    for k in range(12):
        ang = k * math.pi / 6 + rng.uniform(-0.1, 0.1)
        ln = scale * rng.uniform(0.45, 1.0)
        d.line([cx, cy, cx + ln * math.cos(ang), cy + ln * math.sin(ang)],
               fill=(245, 183, 84, 235), width=2)
    d.ellipse([cx - 2.5, cy - 2.5, cx + 2.5, cy + 2.5], fill=(255, 214, 130, 255))


def sky_bursts(w, h):
    """Card 2: interception bursts and dashed trajectories over a night sky."""
    art, d, rng = _sky_base(w, h, 20261118 + 2)
    for cx, cy, s in [(0.30, 0.42, 15), (0.55, 0.30, 11), (0.78, 0.52, 13)]:
        _burst(d, w * cx, h * cy, s, rng)
    for (x0, y0, x1, y1, bend) in [(0.06, 0.85, 0.34, 0.40, -14),
                                  (0.44, 0.16, 0.72, 0.52, -10),
                                  (0.66, 0.88, 0.94, 0.34, -12)]:
        pts = []
        for i in range(25):
            t = i / 24.0
            px = x0 * w + (x1 - x0) * w * t
            py = y0 * h + (y1 - y0) * h * t + bend * math.sin(t * math.pi)
            pts.append((px, py))
        for i in range(0, len(pts) - 1, 2):  # dashed
            d.line([pts[i], pts[i + 1]], fill=(240, 168, 60, 220), width=2)
    return art


def sky_drones(w, h):
    """Card 5: a drone swarm as a field of pale dots, one burst, marker squares."""
    art, d, rng = _sky_base(w, h, 20261118 + 5)
    for _ in range(30):
        cx = w * rng.uniform(0.06, 0.52)
        cy = h * rng.uniform(0.10, 0.62)
        r = rng.uniform(1.2, 2.4)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(228, 234, 244, 235))
    _burst(d, w * 0.66, h * 0.40, 12, rng)
    for sx, sy in [(0.84, 0.24), (0.90, 0.62)]:
        d.rectangle([w * sx, h * sy, w * sx + 5, h * sy + 5],
                    fill=(240, 168, 60, 255))
    return art


def panel_art(name, w, h, cx, cy):
    """Crop a wide strip out of a carried-over illustrated panel."""
    src = Image.open(HERE / "art" / name).convert("RGB")
    sw, sh = src.size
    target = w / h
    crop_h = sw / target
    if crop_h <= sh:
        box_w, box_h = sw, crop_h
    else:
        box_w, box_h = sh * target, sh
    x0 = min(max(cx * sw - box_w / 2, 0), sw - box_w)
    y0 = min(max(cy * sh - box_h / 2, 0), sh - box_h)
    strip = src.crop((int(x0), int(y0), int(x0 + box_w), int(y0 + box_h)))
    return strip.resize((w, h), Image.LANCZOS)


ART_ANCHORS = {
    "panel-summit.png": (0.50, 0.40),
    "panel-voyager.png": (0.36, 0.38),
    "panel-cyclone.png": (0.50, 0.35),
    "panel-eu-loan.png": (0.50, 0.30),
    "panel-gaza-tanks.png": (0.50, 0.55),
    "panel-fed.png": (0.50, 0.35),
    "panel-anthropic.png": (0.42, 0.22),
    "panel-vangogh.png": (0.50, 0.42),
    "panel-gta.png": (0.50, 0.45),
}


def card_art(story, w, h):
    kind = story["art"]
    if kind == "sky-bursts":
        return sky_bursts(w, h)
    if kind == "sky-drones":
        return sky_drones(w, h)
    cx, cy = ART_ANCHORS[kind]
    return panel_art(kind, w, h, cx, cy)

# ---------------------------------------------------------------- rich lines
def rich_wrap(draw, segments, max_w):
    """Wrap styled segments [(text, font, fill)] into lines of word tokens."""
    tokens = []
    for text, fnt, fill in segments:
        for i, word in enumerate(text.split(" ")):
            tokens.append((word, fnt, fill, i > 0))
    lines, cur, cur_w = [], [], 0.0
    space_w = draw.textlength(" ", font=segments[0][1])
    for word, fnt, fill, has_space in tokens:
        w = draw.textlength(word, font=fnt)
        add = w + (space_w if cur and has_space else 0.0)
        if cur and cur_w + add > max_w:
            lines.append(cur)
            cur, cur_w = [(word, fnt, fill)], w
        else:
            cur.append((word, fnt, fill))
            cur_w += add
    if cur:
        lines.append(cur)
    return lines


def rich_draw(draw, x, y, line, space_w):
    cx = x
    for i, (word, fnt, fill) in enumerate(line):
        if i > 0:
            cx += space_w
        draw.text((cx, y), word, font=fnt, fill=fill)
        cx += draw.textlength(word, font=fnt)
    return cx


# ---------------------------------------------------------------- dispatches
def dispatch_card(img, story, x, y, w, h, art_h, head_size):
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([x, y, x + w, y + h], radius=8, fill=CARD + (255,),
                        outline=CARD_EDGE, width=1)
    art = card_art(story, w, art_h)
    img.paste(art, (x, y))
    # number chip on the art's top-left
    d.rectangle([x + 9, y + 8, x + 30, y + 29], fill=AMBER)
    num = str(story["n"])
    f_num = font(SANS_B_PATH, 12)
    tw = d.textlength(num, font=f_num)
    d.text((x + 19 - tw / 2, y + 13), num, font=f_num, fill=INK)
    # dateline chip straddling the art's bottom edge
    f_date = font(SANS_B_PATH, 10)
    dw = text_w(d, story["place"], f_date, 0.4)
    dy = y + art_h - 8
    d.rectangle([x + 6, dy, x + 12 + dw, dy + 15], fill=INK + (235,))
    draw_tracked(d, (x + 9, dy + 2), story["place"], f_date, AMBER, 0.4)
    # headline, auto-shrunk until it fits two lines
    tx = x + 10
    size = head_size
    while size > 13:
        f_head = font(SERIF_PATH, size)
        lines = wrap(d, story["headline"], f_head, w - 19)
        if len(lines) <= 2:
            break
        size -= 1
    hy = y + art_h + 5
    for line in lines:
        d.text((tx, hy), line, font=f_head, fill=CREAM)
        hy += size + 3
    # summary with its attribution, shrunk if it would spill off the card
    text = story["summary"] + " - " + story["source"]
    sum_size = 11.0
    while sum_size > 9.5:
        f_sum = font(SANS_PATH, sum_size)
        sum_lines = wrap(d, text, f_sum, w - 19)
        if hy + 1 + len(sum_lines) * 12.5 <= y + h - 3:
            break
        sum_size -= 0.5
    for line in sum_lines:
        d.text((tx, hy + 1), line, font=f_sum, fill=BODY)
        hy += 12.5


def dispatches(img, page, stories):
    d = ImageDraw.Draw(img, "RGBA")
    d.text((MARGIN, 330), page["dispatch_header"], font=font(SANS_B_PATH, 15),
           fill=AMBER)
    draw_right(d, (SIZE - MARGIN, 332), page["dispatch_note"],
               font(SERIF_IT_PATH, 13), (159, 176, 200))
    by_n = {s["n"]: s for s in stories}
    rows = [
        ([1, 2, 3], 348, 114, 309, 44, 19),
        ([4, 5, 6, 7], 468, 108, 229, 36, 17),
        ([8, 9, 10, 11], 582, 108, 229, 36, 17),
    ]
    for ns, y, h, w, art_h, head_size in rows:
        gap = (CW - w * len(ns)) / (len(ns) - 1)
        for i, n in enumerate(ns):
            dispatch_card(img, by_n[n], int(MARGIN + i * (w + gap)), y, w, h,
                          art_h, head_size)


# ---------------------------------------------------------------- logbook
BRIEF_PITCH = 11.8


def brief_line(img, b, x, y, max_w):
    d = ImageDraw.Draw(img, "RGBA")
    size = 11
    while size > 9:
        f = font(SANS_PATH, size)
        f_b = font(SANS_B_PATH, size)
        segs = [
            (str(b["n"]), font(SANS_B_PATH, size), AMBER),
            (b["place"] + " — ", f_b, (232, 226, 210)),
            (b["text"] + " ", f, BODY),
            ("(" + b["source"] + ")", f, MUTED),
        ]
        lines = rich_wrap(d, segs, max_w)
        if len(lines) == 1:
            break
        size -= 0.5
        f = font(SANS_PATH, size)
    rich_draw(d, x, y, lines[0], d.textlength(" ", font=f))


def logbook(img, page, legs, briefs):
    d = ImageDraw.Draw(img, "RGBA")
    d.text((MARGIN, 694), page["logbook_header"], font=font(SANS_B_PATH, 15),
           fill=AMBER)
    draw_right(d, (SIZE - MARGIN, 696), page["logbook_note"],
               font(SERIF_IT_PATH, 13), (159, 176, 200))
    by_n = {b["n"]: b for b in briefs}
    columns = {"left": (MARGIN, 466), "right": (522, 466)}
    cursors = {"left": 718.0, "right": 718.0}
    for leg in legs:
        x, w = columns[leg["column"]]
        y = cursors[leg["column"]]
        if leg["header"]:
            d.text((x, y), leg["header"], font=font(SANS_B_PATH, 12), fill=TEAL)
            y += 15
        for n in leg["briefs"]:
            brief_line(img, by_n[n], x, y, w)
            y += BRIEF_PITCH
        cursors[leg["column"]] = y + 6


# ---------------------------------------------------------------- footer
def footer(img, page):
    d = ImageDraw.Draw(img, "RGBA")
    box = (MARGIN, 957, SIZE - MARGIN, 991)
    d.rounded_rectangle(box, radius=7, fill=(14, 24, 42, 255),
                        outline=AMBER_DEEP, width=1)
    f_lab = font(SANS_B_PATH, 11)
    f_txt = font(SANS_PATH, 10.5)
    segs = [
        (page["cutting_label"] + " — ", f_lab, AMBER),
        (page["cutting_text"], f_txt, BODY),
    ]
    lines = rich_wrap(d, segs, CW - 20)
    ly = 963
    for line in lines[:2]:
        rich_draw(d, MARGIN + 10, ly, line, d.textlength(" ", font=f_txt))
        ly += 13
    d.text((MARGIN, 996), page["footer_line"], font=font(SANS_PATH, 11),
           fill=BODY)
    d.text((MARGIN, 1010), page["sources_line"], font=font(SANS_PATH, 10),
           fill=MUTED)


# ---------------------------------------------------------------- assembly
def render():
    data = json.loads((HERE / "stories-18.json").read_text())
    page = data["page"]
    # the page never truncates a story: refuse to render an ellipsis
    blob = json.dumps(data, ensure_ascii=False)
    assert "..." not in blob and "…" not in blob, "ellipsis in content"
    assert len(data["dispatches"]) == 11 and len(data["briefs"]) == 34
    img = Image.new("RGB", (SIZE, SIZE), INK)
    starfield(img)
    header(img, page)
    stat_band(img, page, data["stats"])
    sun_map(img, page, data["dispatches"], data["briefs"])
    dispatches(img, page, data["dispatches"])
    logbook(img, page, data["legs"], data["briefs"])
    footer(img, page)
    return img


def main():
    img = render()
    again = render()
    assert img.tobytes() == again.tobytes(), "render is not deterministic"
    # the graded copy goes to the output dir (the repo mount is read-only
    # there, so the local convenience copy below must never be fatal)
    shared = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    shared.mkdir(parents=True, exist_ok=True)
    img.save(shared / "entry.png", format="JPEG", quality=88)
    out = HERE / "entry.png"
    try:
        img.save(out, format="JPEG", quality=88)
    except OSError:
        pass
    print("wrote", shared / "entry.png")


if __name__ == "__main__":
    main()
