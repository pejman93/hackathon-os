#!/usr/bin/env python3
"""TV cards, built from the share-card layout.

    python marketing/social/make-tv.py
"""
import pathlib, sys
import segno
from PIL import Image, ImageOps
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / 'screens'))
from layout import Layout

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parents[1] / 'output' / 'marketing' / 'social'
OUT.mkdir(parents=True, exist_ok=True)
PROJ = HERE.parents[1]
FONTS = PROJ / 'brand' / 'fonts'
CACHE = OUT / '_cache'
CACHE.mkdir(exist_ok=True)

INK    = (0x12/255, 0x13/255, 0x16/255)
PAPER  = (0xf2/255, 0xf1/255, 0xe9/255)
ACCENT = (0x7e/255, 0x98/255, 0xff/255)
MUTED  = (0xae/255, 0xb1/255, 0xb9/255)

URL = 'https://example.org/hackathon/#apply'
PROMISE_1 = 'Four days. Your team. A working AI product.'
PROMISE_2 = 'From 23 October at Example Campus.'
FOOTER = 'EXAMPLE.ORG/HACKATHON  •  ALL SKILL LEVELS WELCOME'

WARNINGS = []

for w in (600, 700, 800):
    pdfmetrics.registerFont(TTFont(f'BC{w}', FONTS / f'BarlowCondensed-{w}.ttf'))
for w in (400, 500, 700):
    pdfmetrics.registerFont(TTFont(f'DM{w}', FONTS / f'DMSans-{w}.ttf'))


def cic_mark():
    """Example Campus as supplied, cropped to the orange mark. See make-hero.py
    for why the grey "powered by" in the original file is re-typeset rather
    than recoloured."""
    return ImageReader(str(PROJ / 'brand' / 'logos' / 'partner-mark.png'))


def white_logo():
    dst = CACHE / 'logo-white.png'
    if not dst.exists():
        im = Image.open(PROJ / 'website/assets/logo.png').convert('RGBA')
        a = im.split()[3]
        w = Image.new('L', im.size, 255)
        Image.merge('RGBA', (w, w, w, a)).save(dst)
    return ImageReader(str(dst))


def photo(size, wash=0.80):
    """The same Demo Night crowd as the share cards, graded the same way:
    greyscale, then pushed most of the way to ink so the type sits on a calm
    ground. The people stay just readable — that is the point of using a
    photograph of a real room rather than a texture."""
    w, h = size
    dst = CACHE / f'bg-{w}x{h}-{wash}.jpg'
    if not dst.exists():
        src = next((PROJ / 'sample-data' / 'photos').glob('crowd*'))
        im = ImageOps.fit(Image.open(src).convert('RGB'), (w, h), Image.LANCZOS)
        im = ImageOps.grayscale(im).convert('RGB')
        tint = Image.new('RGB', im.size, tuple(int(v * 255) for v in INK))
        im = Image.blend(im, tint, wash)
        # A soft vertical scrim through the middle third, where all the type
        # sits. Baked into the JPEG rather than drawn per-element: a gradient
        # painted at render time bands visibly on cheap panels.
        veil = Image.new('L', (1, h))
        for yy in range(h):
            d = abs(yy - h * 0.46) / (h * 0.5)
            veil.putpixel((0, yy), int(150 * max(0.0, 1 - d ** 1.6)))
        im = Image.composite(tint, im, veil.resize(im.size, Image.BILINEAR))
        im.save(dst, quality=92)
    return ImageReader(str(dst))


def fit(c, text, font, target, start, floor=6):
    s = start
    while s > floor and c.stringWidth(text, font, s) > target:
        s -= 0.5
    return s


def lockup_width(c, logo_w, gap, wordmark_size):
    small = wordmark_size * 0.47
    return (logo_w + gap
            + max(c.stringWidth('AI ENTREPRENEURSHIP', 'DM700', small),
                  c.stringWidth('HACKATHON', 'BC800', wordmark_size)))


def lockup(c, x, y, logo_w, wordmark_size, L=None):
    """logo · slanted divider · AI ENTREPRENEURSHIP / HACKATHON — the fixed
    lockup from the brief. y is the baseline of HACKATHON."""
    gap = logo_w * 0.30
    lh = logo_w * 146 / 375
    c.drawImage(white_logo(), x, y - lh * 0.30, width=logo_w, height=lh, mask='auto')

    dx = x + logo_w + gap * 0.42
    c.setStrokeColorRGB(*PAPER)
    c.setLineWidth(max(1.2, logo_w / 150))
    c.setStrokeAlpha(0.55)
    c.line(dx, y - lh * 0.24, dx + lh * 0.22, y + lh * 0.62)
    c.setStrokeAlpha(1)

    tx = dx + lh * 0.22 + gap * 0.50
    small = wordmark_size * 0.47
    c.setFillColorRGB(*PAPER)
    c.setFont('DM700', small)
    c.drawString(tx, y + wordmark_size * 0.82, 'AI ENTREPRENEURSHIP')
    c.setFont('BC800', wordmark_size)
    c.drawString(tx, y, 'HACKATHON')
    total = (tx - x) + max(c.stringWidth('AI ENTREPRENEURSHIP', 'DM700', small),
                           c.stringWidth('HACKATHON', 'BC800', wordmark_size))

    # ---- partner credit, same strip as our own lockup ----
    mid = y + lh * 0.20
    rule_x = x + total + lh * 0.52
    c.setStrokeColorRGB(*PAPER)
    c.setLineWidth(1)
    c.setStrokeAlpha(0.28)
    c.line(rule_x, mid - lh * 0.46, rule_x, mid + lh * 0.46)
    c.setStrokeAlpha(1)

    label_size = lh * 0.155
    lx = rule_x + lh * 0.36
    c.setFillColorRGB(*MUTED)
    c.setFont('DM700', label_size)
    c.drawString(lx, mid - label_size * 0.36, 'POWERED BY')
    lw = c.stringWidth('POWERED BY', 'DM700', label_size)

    mark_h = lh * 0.94
    mark_w = mark_h * 1.218
    mx = lx + lw + lh * 0.26
    c.drawImage(cic_mark(), mx, mid - mark_h / 2, width=mark_w, height=mark_h,
                mask='auto')
    total = (mx + mark_w) - x
    if L:
        L.place('lockup', x, y - lh * 0.30, total, lh * 1.2)
    return total


def qr_block(c, x, y, side, L=None):
    """Dark on white, full quiet zone, with APPLY NOW set beneath it as type —
    no coral circle on these, as asked."""
    qr = segno.make(URL, error='h')
    m = [list(r) for r in qr.matrix]
    n, border = len(m), 4
    mod = side / (n + border * 2)
    c.setFillColorRGB(1, 1, 1)
    c.roundRect(x, y, side, side, 8, stroke=0, fill=1)
    c.setFillColorRGB(*INK)
    for r, row in enumerate(m):
        run = None
        for col in range(n + 1):
            on = col < n and row[col]
            if on and run is None:
                run = col
            elif not on and run is not None:
                c.rect(x + (border + run) * mod, y + side - (border + r + 1) * mod,
                       (col - run) * mod, mod, stroke=0, fill=1)
                run = None
    label_size = side * 0.115
    c.setFont('BC800', label_size)
    c.setFillColorRGB(*ACCENT)
    c.drawCentredString(x + side / 2, y - label_size * 1.15, 'APPLY NOW')
    if L:
        L.place('qr', x, y - label_size * 1.5, side, side + label_size * 1.5)
    if mod < 5:
        WARNINGS.append(f'QR module {mod:.1f}px')
    return mod


# ------------------------------------------------------------------ layouts
def centred(c, size, L):
    W, H = size
    k = H / 1080.0                       # everything scales off the 1080 design
    c.drawImage(photo(size), 0, 0, W, H, mask=None)

    logo_w, wm = 300 * k, 62 * k
    total = lockup_width(c, logo_w, logo_w * 0.30, wm)
    lockup(c, (W - total) / 2, H - 300 * k, logo_w, wm, L)

    s1 = fit(c, PROMISE_1, 'DM500', W - 200 * k, 46 * k)
    c.setFont('DM500', s1)
    c.setFillColorRGB(*PAPER)
    c.drawCentredString(W / 2, H - 420 * k, PROMISE_1)
    L.place('p1', (W - c.stringWidth(PROMISE_1, 'DM500', s1)) / 2, H - 432 * k,
            c.stringWidth(PROMISE_1, 'DM500', s1), s1 * 1.2)

    s2 = fit(c, PROMISE_2, 'DM400', W - 200 * k, 34 * k)
    c.setFont('DM400', s2)
    c.setFillColorRGB(*MUTED)
    c.drawCentredString(W / 2, H - 478 * k, PROMISE_2)
    L.place('p2', (W - c.stringWidth(PROMISE_2, 'DM400', s2)) / 2, H - 490 * k,
            c.stringWidth(PROMISE_2, 'DM400', s2), s2 * 1.2)

    side = 292 * k
    qr_block(c, (W - side) / 2, 172 * k, side, L)

    sf = fit(c, FOOTER, 'DM700', W - 160 * k, 21 * k)
    c.setFont('DM700', sf)
    c.setFillColorRGB(*PAPER)
    c.drawCentredString(W / 2, 86 * k, FOOTER)
    L.place('footer', (W - c.stringWidth(FOOTER, 'DM700', sf)) / 2, 78 * k,
            c.stringWidth(FOOTER, 'DM700', sf), sf * 1.3)


def left(c, size, L):
    W, H = size
    k = H / 1080.0
    c.drawImage(photo(size), 0, 0, W, H, mask=None)

    x = 96 * k
    side = 316 * k
    qx = W - 96 * k - side

    logo_w, wm = 286 * k, 58 * k
    lockup(c, x, H - 300 * k, logo_w, wm, L)

    col = qx - x - 90 * k               # text column stops clear of the QR
    s1 = fit(c, PROMISE_1, 'DM500', col, 46 * k)
    c.setFont('DM500', s1)
    c.setFillColorRGB(*PAPER)
    c.drawString(x, H - 430 * k, PROMISE_1)
    L.place('p1', x, H - 442 * k, c.stringWidth(PROMISE_1, 'DM500', s1), s1 * 1.2)

    s2 = fit(c, PROMISE_2, 'DM400', col, 34 * k)
    c.setFont('DM400', s2)
    c.setFillColorRGB(*MUTED)
    c.drawString(x, H - 490 * k, PROMISE_2)
    L.place('p2', x, H - 502 * k, c.stringWidth(PROMISE_2, 'DM400', s2), s2 * 1.2)

    qr_block(c, qx, 292 * k, side, L)

    c.setStrokeColorRGB(*PAPER)
    c.setLineWidth(1)
    c.setStrokeAlpha(0.18)
    c.line(x, 150 * k, W - 96 * k, 150 * k)
    c.setStrokeAlpha(1)
    sf = fit(c, FOOTER, 'DM700', W - 200 * k, 22 * k)
    c.setFont('DM700', sf)
    c.setFillColorRGB(*PAPER)
    c.drawString(x, 96 * k, FOOTER)
    L.place('footer', x, 88 * k, c.stringWidth(FOOTER, 'DM700', sf), sf * 1.3)


LAYOUTS = [('centred', centred), ('left', left)]
# 1200x630 was tried and dropped. A 45-module QR needs ~250px to stay above
# 5px per module, which is 40% of a 630px-tall card — there is no room left
# for the lockup, the promise and the footer. Share cards are clicked anyway;
# the four originals in this folder still do that job.
SIZES = [('tv-1920x1080', (1920, 1080))]


def main():
    for lname, fn in LAYOUTS:
        for sname, size in SIZES:
            path = OUT / f'{sname}-{lname}-qr.pdf'
            c = rl_canvas.Canvas(str(path), pagesize=size)
            c.setTitle(f'Example College AI Entrepreneurship Hackathon — {sname} {lname}')
            L = Layout(path.stem)
            fn(c, size, L)
            c.showPage()
            c.save()
            WARNINGS.extend(L.problems)
            print(f'  {path.name:34} {len(L.boxes)} elements, {len(L.problems)} overlap(s)')
    print()
    if WARNINGS:
        print('WARNINGS:')
        for w in dict.fromkeys(WARNINGS):
            print('  !', w)
    else:
        print('no warnings — overlap and QR checks pass')


if __name__ == '__main__':
    main()
