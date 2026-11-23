#!/usr/bin/env python3
"""Generate every sample image in the repository from code.

No real photo, logo or signature is stored here. This script draws a made-up
college logo, partner marks, signatures, portraits and illustrated "event
photos", so all tools can run end to end on fictional data.

    python tools/make_demo_assets.py
"""
import json
import math
import pathlib
import random
import shutil

import numpy as np
import segno
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOGOS = ROOT / "brand" / "logos"
FONTS = ROOT / "brand" / "fonts"
PHOTOS = ROOT / "sample-data" / "photos"
SIGS = ROOT / "print-kit" / "src"
SITE = ROOT / "website" / "assets"

INK, PAPER, ACCENT = (0x12, 0x13, 0x16), (0xf2, 0xf1, 0xe9), (0x7e, 0x98, 0xff)
BRAND, CORAL = (0x14, 0x1a, 0x9d), (0xff, 0x70, 0x4b)

# ----------------------------------------------------------------- the logo
# A shield and the word EXAMPLE, drawn from straight lines on a 2896 x 848 grid.
W, H = 2896, 848
STROKE = 118


def box(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def letters():
    """Each letter is a list of closed polygons; overlaps are avoided so even-odd fill is safe."""
    top, bottom, s = 130, 718, STROKE
    mid = (top + bottom) / 2
    out, x, gap = [], 700, 62

    def E(x):
        w = 250
        return [[(x, top), (x + w, top), (x + w, top + s), (x + s, top + s), (x + s, mid - s / 2 + 2), (x + w - 28, mid - s / 2 + 2),
                 (x + w - 28, mid + s / 2 - 2), (x + s, mid + s / 2 - 2), (x + s, bottom - s), (x + w, bottom - s), (x + w, bottom), (x, bottom)]], w

    def X(x):
        w = 330
        c = x + w / 2
        return [[(x, top), (x + 136, top), (c, mid - 92), (x + w - 136, top), (x + w, top), (c + 94, mid), (x + w, bottom), (x + w - 136, bottom),
                 (c, mid + 92), (x + 136, bottom), (x, bottom), (c - 94, mid)]], w

    def A(x):
        w = 360
        c = x + w / 2
        return [[(c - 66, top), (c + 66, top), (x + w, bottom), (x + w - 126, bottom), (x + w - 156, bottom - 118), (x + 156, bottom - 118),
                 (x + 126, bottom), (x, bottom)], [(c, top + 170), (c + 62, bottom - 226), (c - 62, bottom - 226)]], w

    def M(x):
        w = 430
        c = x + w / 2
        return [[(x, top), (x + 136, top), (c, top + 300), (x + w - 136, top), (x + w, top), (x + w, bottom), (x + w - s, bottom), (x + w - s, top + 214),
                 (c + 40, bottom - 110), (c - 40, bottom - 110), (x + s, top + 214), (x + s, bottom), (x, bottom)]], w

    def P(x):
        w = 290
        return [[(x, top), (x + w - 44, top), (x + w, top + 44), (x + w, mid + 76), (x + w - 44, mid + 120), (x + s, mid + 120), (x + s, bottom), (x, bottom)],
                [(x + s, top + s - 12), (x + w - s, top + s - 12), (x + w - s, mid + 14), (x + s, mid + 14)]], w

    def L(x):
        w = 236
        return [[(x, top), (x + s, top), (x + s, bottom - s), (x + w, bottom - s), (x + w, bottom), (x, bottom)]], w

    for fn in (E, X, A, M, P, L, E):
        polys, w = fn(x)
        out.extend(polys)
        x += w + gap
    return out, x - gap


def shield():
    """The shield fills the left 20.5 % of the logo and 73.5 % of its height."""
    w, h = 0.205 * W, 0.735 * H
    x, y = 0.0, (H - h) / 2
    outer, inner = [], []
    for k in range(0, 41):
        t = k / 40
        outer.append((x + w * t, y + h * 0.62 + h * 0.38 * math.sin(math.pi * t)))
    outer = [(x, y), (x + w, y)] + list(reversed(outer))
    pad = 46
    for k in range(0, 41):
        t = k / 40
        inner.append((x + pad + (w - 2 * pad) * t, y + h * 0.60 + (h * 0.38 - pad) * math.sin(math.pi * t)))
    inner = [(x + pad, y + pad), (x + w - pad, y + pad)] + list(reversed(inner))
    bars = [box(x + w * f - 21, y + 170, x + w * f + 21, y + h * .82 - abs(f - .5) * 150) for f in (.32, .5, .68)]
    return [outer, inner] + bars


def logo_polygons():
    word, end = letters()
    sx = (W - 640) / (end - 700)                  # fit the word to the space after the shield
    word = [[(640 + (px - 700) * sx, py) for px, py in poly] for poly in word]
    return shield() + word


def write_logo_vector():
    curves = []
    for poly in logo_polygons():
        segs = [["L", list(p), list(p)] for p in poly[1:]]
        curves.append({"start": list(poly[0]), "segs": segs})
    (LOGOS / "logo_vec.json").write_text(json.dumps({"w": W, "h": H, "curves": curves}, separators=(",", ":")))


def render_logo(colour, out_w=375, out_h=146, ss=4):
    """Logo on a transparent canvas with a small tagline, the shape the layouts expect."""
    cw, ch = out_w * ss, out_h * ss
    mask = Image.new("L", (cw, ch), 0)
    scale = cw / W
    yoff = 0
    d = Image.new("1", (cw, ch), 0)
    draw = ImageDraw.Draw(d)
    target = Image.new("L", (cw, ch), 0)
    for poly in logo_polygons():
        layer = Image.new("1", (cw, ch), 0)
        ImageDraw.Draw(layer).polygon([(px * scale, py * scale + yoff) for px, py in poly], fill=1)
        target = Image.fromarray(np.bitwise_xor(np.array(target) > 0, np.array(layer)).astype("uint8") * 255)
    tag = ImageFont.truetype(str(FONTS / "DMSans-500.ttf"), int(15.5 * ss))
    ImageDraw.Draw(target).text((0, int(ch * .80)), "Example College of Business and Technology", font=tag, fill=255)
    im = Image.new("RGBA", (cw, ch), colour + (0,))
    im.putalpha(target)
    return im.resize((out_w, out_h), Image.LANCZOS)


def partner_mark(label, colour, size=(1522, 1250)):
    w, h = size
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = int(h * .30)
    cx = w // 2
    d.ellipse([cx - r, h * .06, cx + r, h * .06 + 2 * r], outline=colour + (255,), width=int(r * .28))
    d.ellipse([cx - r * .3, h * .06 + r * .7, cx + r * .3, h * .06 + r * 1.3], fill=colour + (255,))
    f = ImageFont.truetype(str(FONTS / "BarlowCondensed-800.ttf"), int(h * .24))
    tw = d.textlength(label, font=f)
    d.text(((w - tw) / 2, h * .70), label, font=f, fill=colour + (255,))
    return im


# ----------------------------------------------------------------- signatures
def signature(seed, w=900, h=320):
    rng = random.Random(seed)
    ss = 3
    im = Image.new("L", (w * ss, h * ss), 0)
    d = ImageDraw.Draw(im)
    pts = []
    x, phase = 40.0, rng.random() * 6
    loops = rng.randint(6, 8)
    for k in range(900):
        t = k / 899
        env = .55 + .45 * math.sin(math.pi * t) ** .6
        y = h * .52 - h * .34 * env * math.sin(t * loops * 2 * math.pi + phase) * (1 if k % 180 > 30 else .7)
        x = 40 + (w - 120) * t + 26 * math.cos(t * loops * 2 * math.pi + phase)
        pts.append((x * ss, y * ss))
    d.line(pts, fill=255, width=4 * ss, joint="curve")
    d.line([(60 * ss, h * .82 * ss), (w * .55 * ss, h * .68 * ss), (w * .92 * ss, h * .76 * ss)], fill=255, width=3 * ss, joint="curve")
    a = im.resize((w, h), Image.LANCZOS)
    out = Image.new("RGBA", (w, h), INK + (0,))
    out.putalpha(a)
    return out.crop(a.getbbox())


# ----------------------------------------------------------------- illustrated "photos"
def gradient(w, h, top, bottom):
    t = np.linspace(0, 1, h)[:, None, None]
    arr = np.array(top, float)[None, None] * (1 - t) + np.array(bottom, float)[None, None] * t
    return Image.fromarray(np.repeat(arr, w, axis=1).astype("uint8"), "RGB")


def finish(im, seed):
    rng = np.random.default_rng(seed)
    arr = np.asarray(im, float)
    h, w = arr.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    v = 1 - .22 * (((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) / 2
    arr = arr * v[..., None] + rng.normal(0, 3.2, arr.shape)
    return Image.fromarray(np.clip(arr, 0, 255).astype("uint8"), "RGB")


def person(d, x, base, s, colour):
    head = s * .21
    d.ellipse([x - head, base - s - head, x + head, base - s + head], fill=colour)
    d.rounded_rectangle([x - s * .36, base - s + head * 1.25, x + s * .36, base + s * .6], radius=int(s * .24), fill=colour)


def crowd_layer(im, rows, seed, c0, c1):
    rng = random.Random(seed)
    w, h = im.size
    for r in range(rows):
        t = r / max(rows - 1, 1)
        layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        s = h * (.13 + .17 * t)
        base = h * (.60 + .36 * t)
        col = tuple(int(c0[i] * (1 - t) + c1[i] * t) for i in range(3)) + (255,)
        x = -rng.random() * s
        while x < w + s:
            person(d, x, base + rng.uniform(-s * .08, s * .08), s * rng.uniform(.92, 1.08), col)
            x += s * rng.uniform(.72, 1.05)
        im.paste(layer.filter(ImageFilter.GaussianBlur((1 - t) * 2.2)), (0, 0), layer.filter(ImageFilter.GaussianBlur((1 - t) * 2.2)))


def scene_crowd(w, h, seed=1):
    im = gradient(w, h, (20, 22, 52), (10, 11, 20))
    glow = Image.new("RGB", (w, h), (0, 0, 0))
    d = ImageDraw.Draw(glow)
    for k, x in enumerate((.18, .38, .62, .82)):
        d.polygon([(w * x - 8, 0), (w * x + 8, 0), (w * (x + (.5 - x) * .5) + w * .10, h * .8), (w * (x + (.5 - x) * .5) - w * .10, h * .8)],
                  fill=(58, 70, 170) if k % 2 else (92, 104, 226))
    glow = glow.filter(ImageFilter.GaussianBlur(w * .018))
    im = Image.fromarray(np.clip(np.asarray(im, int) + np.asarray(glow, int) // 2, 0, 255).astype("uint8"))
    d = ImageDraw.Draw(im)
    d.rectangle([w * .30, h * .14, w * .70, h * .46], fill=(126, 152, 255))
    d.rectangle([w * .31, h * .155, w * .69, h * .445], fill=(232, 236, 255))
    crowd_layer(im, 4, seed, (64, 70, 120), (14, 15, 26))
    return finish(im, seed)


def scene_campus(w, h, seed=2):
    im = gradient(w, h, (118, 164, 228), (233, 236, 244))
    d = ImageDraw.Draw(im)
    rng = random.Random(seed)
    for _ in range(9):
        cx, cy, r = rng.uniform(0, w), rng.uniform(0, h * .3), rng.uniform(w * .05, w * .13)
        d.ellipse([cx - r, cy - r * .32, cx + r, cy + r * .32], fill=(245, 247, 252))
    im = im.filter(ImageFilter.GaussianBlur(w * .008))
    d = ImageDraw.Draw(im)
    x0, x1, y0, y1 = w * .14, w * .92, h * .16, h * .80
    d.polygon([(x0, y0 + h * .10), (x1, y0), (x1, y1), (x0, y1)], fill=(170, 84, 56))
    cols, rows = 13, 5
    for r in range(rows):
        for c in range(cols):
            u = (c + .22) / cols
            uu = (c + .78) / cols
            top = lambda f: (y0 + h * .10 * (1 - f))
            ya = top(u) + (y1 - top(u)) * ((r + .22) / rows)
            yb = top(u) + (y1 - top(u)) * ((r + .78) / rows)
            d.rounded_rectangle([x0 + (x1 - x0) * u, ya, x0 + (x1 - x0) * uu, yb], radius=3, fill=(46, 66, 112) if (r + c) % 3 else (232, 214, 150))
    d.rectangle([0, y1, w, h], fill=(120, 120, 126))
    for k in range(0, int(w), max(14, w // 60)):
        d.line([(k, y1), (k - w * .12, h)], fill=(104, 104, 110), width=1)
    d.ellipse([-w * .08, h * .34, w * .20, h * .88], fill=(52, 96, 66))
    return finish(im, seed)


def scene_workspace(w, h, seed=3):
    im = gradient(w, h, (236, 238, 246), (196, 200, 216))
    d = ImageDraw.Draw(im)
    for k in range(5):
        x = w * (.06 + k * .19)
        d.rectangle([x, h * .08, x + w * .13, h * .42], fill=(170, 196, 240))
        d.line([(x + w * .065, h * .08), (x + w * .065, h * .42)], fill=(240, 242, 248), width=max(2, w // 300))
    d.rectangle([0, h * .68, w, h], fill=(70, 74, 92))
    for k in range(4):
        x = w * (.05 + k * .24)
        d.rounded_rectangle([x, h * .60, x + w * .20, h * .68], radius=6, fill=(214, 186, 150))
        d.rounded_rectangle([x + w * .04, h * .40, x + w * .15, h * .58], radius=5, fill=INK)
        d.rectangle([x + w * .05, h * .415, x + w * .14, h * .565], fill=(126, 152, 255) if k % 2 else (20, 26, 157))
        person(d, x + w * .10, h * .95, h * .32, (34, 37, 58) if k % 2 else (24, 28, 90))
    return finish(im, seed)


def scene_stage(w, h, seed=4):
    im = gradient(w, h, (28, 32, 92), (12, 13, 22))
    d = ImageDraw.Draw(im)
    d.rectangle([w * .16, h * .10, w * .84, h * .58], fill=(240, 241, 250))
    d.rectangle([w * .16, h * .10, w * .84, h * .20], fill=BRAND)
    for k in range(4):
        d.rounded_rectangle([w * .22, h * (.27 + k * .07), w * (.72 - k * .08), h * (.30 + k * .07)], radius=4, fill=(126, 152, 255))
    d.rectangle([0, h * .74, w, h], fill=(26, 28, 44))
    person(d, w * .28, h * .82, h * .36, (14, 15, 26))
    person(d, w * .74, h * .84, h * .34, (20, 22, 40))
    return finish(im, seed)


def scene_team(w, h, seed=5):
    im = gradient(w, h, (243, 244, 250), (206, 212, 232))
    d = ImageDraw.Draw(im)
    d.rectangle([0, h * .80, w, h], fill=(150, 154, 174))
    d.rectangle([w * .06, h * .10, w * .24, h * .74], fill=BRAND)
    d.rectangle([w * .76, h * .10, w * .94, h * .74], fill=(126, 152, 255))
    rng = random.Random(seed)
    palette = [(26, 30, 72), (56, 62, 120), (20, 26, 157), (42, 46, 70), (92, 104, 196)]
    for row, (y, s) in enumerate(((.66, .30), (.86, .36))):
        n = 9 - row * 2
        for k in range(n):
            x = w * (.14 + .72 * (k + .5) / n)
            person(d, x + rng.uniform(-8, 8), h * y, h * s, palette[(k + row) % len(palette)])
    return finish(im, seed)


def scene_hero(w, h, seed=6):
    """A lit stage on the right, so the headline on the left stays readable."""
    im = gradient(w, h, (34, 42, 120), (16, 18, 44))
    glow = Image.new("RGB", (w, h), (0, 0, 0))
    d = ImageDraw.Draw(glow)
    for x in (.56, .70, .84, .98):
        d.polygon([(w * x - 10, 0), (w * x + 10, 0), (w * (x - .06) + w * .12, h * .86), (w * (x - .06) - w * .12, h * .86)], fill=(120, 136, 255))
    glow = glow.filter(ImageFilter.GaussianBlur(w * .02))
    im = Image.fromarray(np.clip(np.asarray(im, int) + np.asarray(glow, int) * 2 // 3, 0, 255).astype("uint8"))
    d = ImageDraw.Draw(im)
    d.rectangle([w * .56, h * .12, w * .95, h * .50], fill=(150, 170, 255))
    d.rectangle([w * .57, h * .135, w * .94, h * .485], fill=(240, 242, 255))
    d.rectangle([w * .57, h * .135, w * .94, h * .20], fill=BRAND)
    for k in range(4):
        d.rounded_rectangle([w * .60, h * (.25 + k * .055), w * (.88 - k * .05), h * (.27 + k * .055)], radius=4, fill=(126, 152, 255))
    crowd_layer(im, 3, seed, (58, 66, 130), (16, 17, 34))
    return finish(im, seed)


SCENES = {"hero": scene_hero, "crowd": scene_crowd, "campus": scene_campus, "workspace": scene_workspace, "stage": scene_stage, "team": scene_team}


def portrait(seed, initials, size=500):
    """A monogram tile: the card crops portraits differently, so nothing important sits near an edge."""
    rng = random.Random(seed)
    bg = rng.choice([BRAND, (40, 50, 130), (70, 88, 200), (30, 32, 60)])
    im = gradient(size, size, bg, tuple(int(c * .6) for c in bg))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(str(FONTS / "BarlowCondensed-800.ttf"), int(size * .42))
    box = d.textbbox((0, 0), initials, font=f)
    d.text(((size - box[2] - box[0]) / 2, size * .40 - (box[1] + box[3]) / 2), initials, font=f, fill=(242, 241, 233))
    return finish(im, seed)


# file, width, height, scene: the event site's picture wall, drawn at web size
SITE_SCENES = [("hero", 1600, 1000, "hero"), ("hero-tall", 900, 1600, "hero"), ("bg-group", 1400, 957, "crowd"), ("winner", 1200, 800, "stage"), ("audience", 1200, 800, "crowd"),
               ("gallery-01", 840, 560, "campus"), ("gallery-02", 840, 560, "workspace"), ("gallery-03", 560, 840, "stage"), ("gallery-04", 840, 560, "team"),
               ("gallery-05", 840, 560, "crowd"), ("gallery-06", 840, 560, "workspace"), ("gallery-07", 560, 840, "campus"), ("gallery-08", 840, 560, "stage"),
               ("gallery-09", 560, 840, "workspace"), ("gallery-10", 840, 560, "team"), ("gallery-11", 560, 840, "crowd"), ("gallery-12", 840, 560, "campus"),
               ("gallery-13", 560, 840, "team"), ("gallery-14", 630, 840, "stage"), ("gallery-15", 578, 840, "workspace"), ("gallery-16", 840, 560, "crowd")]
SITE_PEOPLE = {"grace": "GH", "alan": "AT", "konrad": "KZ", "katherine": "KJ", "dorothy": "DV", "charles": "CB", "emmy": "EN", "john": "JM", "ada": "AL"}


def site_assets():
    (SITE / "recap").mkdir(parents=True, exist_ok=True)
    (SITE / "people").mkdir(parents=True, exist_ok=True)
    shutil.copy(LOGOS / "logo.png", SITE / "logo.png")
    shutil.copy(LOGOS / "partner-mark.png", SITE / "recap" / "partner-mark.png")
    shutil.copy(LOGOS / "partner-mark-2.png", SITE / "recap" / "partner-mark-2.png")
    for i, (name, w, h, scene) in enumerate(SITE_SCENES):
        SCENES[scene](w, h, 40 + i).convert("RGB").save(SITE / "recap" / f"{name}.jpg", quality=72, optimize=True, progressive=True)
    for i, (name, initials) in enumerate(SITE_PEOPLE.items()):
        portrait(70 + i, initials, 420).save(SITE / "people" / f"{name}.jpg", quality=78, optimize=True)


# ----------------------------------------------------------------- documents
DOCS = ROOT / "documents" / "assets"
# the slide decks show a small animated "reaction" card where a meme could go
REACTIONS = {"meme-take-my-money": "SHOW ME\nTHE MODEL", "meme-lets-ride": "LET'S\nBUILD", "meme-this-is-fine": "IT'S\nFINE", "meme-cat-typing": "TYPING\nFURIOUSLY",
             "meme-its-alive": "IT'S\nALIVE!", "meme-sleepy": "SLEEP\nLATER", "meme-ship-it": "SHIP\nIT", "meme-let-it-go": "CUT\nSCOPE", "meme-showtime": "SHOW\nTIME",
             "meme-drumroll": "DRUM\nROLL"}


def reaction(text, seed, w=400, h=300, frames=6):
    """A small looping card: the word on a blue tile with a travelling row of dots."""
    f = ImageFont.truetype(str(FONTS / "BarlowCondensed-800.ttf"), 84)
    out = []
    for k in range(frames):
        im = Image.new("RGB", (w, h), BRAND if seed % 2 else (40, 50, 130))
        d = ImageDraw.Draw(im)
        d.multiline_text((w / 2, h * .44), text, font=f, fill=(242, 241, 233), anchor="mm", align="center", spacing=2)
        for i in range(frames):
            x = w * (.5 + (i - (frames - 1) / 2) * .075)
            r = 8 if i == k else 4
            d.ellipse([x - r, h * .88 - r, x + r, h * .88 + r], fill=(126, 152, 255) if i == k else (90, 100, 190))
        out.append(im.convert("P", palette=Image.ADAPTIVE, colors=16))
    return out


def fireworks(w=400, h=267, frames=8, seed=9):
    rng = random.Random(seed)
    bursts = [(rng.uniform(.1, .9) * w, rng.uniform(.15, .7) * h, rng.choice([(255, 217, 131), (126, 152, 255), (255, 112, 75), (242, 241, 233)]), rng.randrange(frames)) for _ in range(7)]
    out = []
    for k in range(frames):
        im = Image.new("RGB", (w, h), (10, 11, 22))
        d = ImageDraw.Draw(im)
        for cx, cy, col, start in bursts:
            t = ((k - start) % frames) / frames
            r = 8 + t * 58
            fade = 1 - t
            c = tuple(int(10 + (v - 10) * fade) for v in col)
            for a in range(0, 360, 24):
                x, y = cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))
                d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=c)
        out.append(im.convert("P", palette=Image.ADAPTIVE, colors=32))
    return out


def save_gif(frames, path, ms=140):
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=ms, loop=0, optimize=True)


def brush_background(w, h, seed=21):
    rng = random.Random(seed)
    im = gradient(w, h, (20, 26, 157), (10, 14, 92))
    layer = Image.new("RGB", (w, h), (0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(70):
        y = rng.uniform(-.1, 1.1) * h
        x0, x1 = rng.uniform(-.2, .5) * w, rng.uniform(.5, 1.2) * w
        c = rng.randint(10, 34)
        d.line([(x0, y), ((x0 + x1) / 2, y + rng.uniform(-60, 60)), (x1, y + rng.uniform(-90, 90))], fill=(c // 2, c // 2, c * 2), width=rng.randint(8, 46), joint="curve")
    layer = layer.filter(ImageFilter.GaussianBlur(w * .006))
    return finish(Image.fromarray(np.clip(np.asarray(im, int) + np.asarray(layer, int), 0, 255).astype("uint8")), seed)


def stairs_art(w, h, seed=22):
    """Steps rising to an open door: the "you build here" picture."""
    im = gradient(w, h, (20, 26, 157), (8, 12, 70))
    d = ImageDraw.Draw(im)
    steps, sx, sy = 6, w * .05, h * .075
    x0, base = w * .04, h * .92
    for k in range(steps):
        d.rectangle([x0 + k * sx, base - (k + 1) * sy, x0 + (k + 1) * sx, base], fill=(126 - k * 6, 152 - k * 6, 255))
    dx, top = x0 + steps * sx + w * .005, base - steps * sy - h * .34
    d.rectangle([dx, top, dx + w * .08, base - steps * sy], fill=(255, 236, 170))
    d.polygon([(dx + w * .08, top), (dx + w * .115, top + h * .04), (dx + w * .115, base - steps * sy + h * .04), (dx + w * .08, base - steps * sy)], fill=(242, 241, 233))
    person(d, x0 + sx * 2.5, base - sy * 3, h * .16, (16, 18, 44))
    return finish(im, seed)


def document_assets():
    DOCS.mkdir(parents=True, exist_ok=True)
    brush_background(1920, 1080).save(DOCS / "background.jpg", quality=80, optimize=True)
    stairs_art(1600, 900).save(DOCS / "you-build-here-art.jpg", quality=80, optimize=True)
    for name, scene, w, h, seed in (("photo-team", "team", 900, 1140, 31), ("photo-brainstorm", "workspace", 1000, 938, 32), ("photo-polaroids", "stage", 900, 1308, 33)):
        SCENES[scene](w, h, seed).save(DOCS / f"{name}.jpg", quality=78, optimize=True)
    strip = scene_crowd(1654, 380, 34)
    strip = Image.blend(strip, Image.new("RGB", strip.size, (14, 18, 90)), .45)
    strip.save(DOCS / "overview-banner-bg.jpg", quality=84, optimize=True)
    for i, (name, text) in enumerate(REACTIONS.items()):
        save_gif(reaction(text, i), DOCS / f"{name}.gif")
    save_gif(fireworks(), DOCS / "fireworks-wide.gif", 110)
    render_logo_plain((255, 255, 255)).save(DOCS / "logo-white-plain.png", optimize=True)


def render_logo_plain(colour, out_w=1640, ss=2):
    """The logo alone, on the exact logo grid, for slides."""
    cw, ch = out_w * ss, round(out_w * ss * H / W)
    scale = cw / W
    target = np.zeros((ch, cw), dtype=bool)
    for poly in logo_polygons():
        layer = Image.new("1", (cw, ch), 0)
        ImageDraw.Draw(layer).polygon([(px * scale, py * scale) for px, py in poly], fill=1)
        target ^= np.array(layer, dtype=bool)
    im = Image.new("RGBA", (cw, ch), colour + (0,))
    im.putalpha(Image.fromarray(target.astype("uint8") * 255))
    return im.resize((out_w, round(out_w * H / W)), Image.LANCZOS)


def main():
    for folder in (LOGOS, PHOTOS, SIGS, SITE / "recap"):
        folder.mkdir(parents=True, exist_ok=True)
    write_logo_vector()
    render_logo(BRAND).save(LOGOS / "logo.png")
    render_logo((255, 255, 255)).save(LOGOS / "logo-white.png")
    partner_mark("PARTNER", CORAL).save(LOGOS / "partner-mark.png")
    partner_mark("VENUE", (0x2f, 0x7d, 0x5b), (715, 728)).save(LOGOS / "partner-mark-2.png")
    signature(11).save(SIGS / "sig_president.png")
    signature(29).save(SIGS / "sig_lead.png")
    qr = segno.make("https://example.org/hackathon/", error="h")
    (SIGS / "qr_hackathon.json").write_text(json.dumps({"url": "https://example.org/hackathon/", "error": "H", "modules": [[int(bool(v)) for v in row] for row in qr.matrix]}, separators=(",", ":")))
    for name in ("crowd", "campus", "workspace", "stage", "team"):
        SCENES[name](2000, 1336).convert("RGB").save(PHOTOS / f"{name}.jpg", quality=82, optimize=True)
    site_assets()
    document_assets()
    print("demo assets written")


if __name__ == "__main__":
    main()
