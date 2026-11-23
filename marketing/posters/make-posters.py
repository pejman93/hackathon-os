#!/usr/bin/env python3
"""Three A4 QR posters, built as vector PDF so they print sharp at any size.

    python marketing/posters/make-posters.py
"""
import math, os, pathlib
import segno
from PIL import Image
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

HERE = pathlib.Path(__file__).resolve().parent
FONTS = HERE.parents[1] / 'brand' / 'fonts'
PROJ = HERE.parents[1]   # repo root, from marketing/07-qr/_src/
OUT = HERE.parents[1] / 'output' / 'marketing' / 'posters'
OUT.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

W, H = A4                                  # 595.28 x 841.89 pt

INK    = (0x12/255, 0x13/255, 0x16/255)
PAPER  = (0xf2/255, 0xf1/255, 0xe9/255)
ACCENT = (0x7e/255, 0x98/255, 0xff/255)
CORAL  = (0xff/255, 0x70/255, 0x4b/255)
MUTED  = (0xae/255, 0xb1/255, 0xb9/255)
GLOW   = (0x1b/255, 0x1d/255, 0x42/255)

URL = 'https://example.org/hackathon/#apply'

for w in (600, 700, 800):
    pdfmetrics.registerFont(TTFont(f'BC{w}', FONTS / f'BarlowCondensed-{w}.ttf'))
for w in (400, 500, 700):
    pdfmetrics.registerFont(TTFont(f'DM{w}', FONTS / f'DMSans-{w}.ttf'))

WARNINGS = []


# ---------------------------------------------------------------- the logo
def white_logo():
    """The supplied logo is brand indigo with alpha. The site renders it white
    with a CSS filter; print has no such luxury, so recolour the pixels and
    keep the alpha exactly as it is."""
    dst = PROJ / 'brand' / 'logos' / 'logo-white.png'
    if not dst.exists():
        im = Image.open(PROJ / 'website/assets/logo.png').convert('RGBA')
        r, g, b, a = im.split()
        white = Image.new('L', im.size, 255)
        Image.merge('RGBA', (white, white, white, a)).save(dst)
    return ImageReader(str(dst))


# ------------------------------------------------------------ text helpers
def fit(c, text, font, target_w, start, floor=8):
    """Largest size at or below `start` that keeps `text` inside target_w."""
    size = start
    while size > floor and c.stringWidth(text, font, size) > target_w:
        size -= 0.5
    return size


def centred(c, text, font, size, y, colour):
    c.setFont(font, size)
    c.setFillColorRGB(*colour)
    c.drawCentredString(W / 2, y, text)


# ------------------------------------------------------------- the QR code
def draw_qr(c, x, y, side, label='SCAN TO APPLY'):
    """QR as vector rects on a paper panel.

    Dark-on-light, because a minority of scanners still refuse inverted codes,
    and a poster is not something you can fix after printing. The quiet zone is
    the panel itself — 4 modules minimum, which the spec requires and which
    cheap generators routinely omit.
    """
    qr = segno.make(URL, error='h')
    matrix = [list(row) for row in qr.matrix]
    n = len(matrix)
    border = 4
    total = n + border * 2
    mod = side / total

    c.setFillColorRGB(*PAPER)
    c.roundRect(x, y, side, side, 10, stroke=0, fill=1)

    c.setFillColorRGB(*INK)
    for r, row in enumerate(matrix):
        run = None
        for col in range(n + 1):                      # +1 flushes the last run
            on = col < n and row[col]
            if on and run is None:
                run = col
            elif not on and run is not None:
                # one rect per horizontal run: fewer ops, no hairline seams
                c.rect(x + (border + run) * mod,
                       y + side - (border + r + 1) * mod,
                       (col - run) * mod, mod, stroke=0, fill=1)
                run = None

    module_mm = mod / 72 * 25.4
    if module_mm < 0.6:
        WARNINGS.append(f'QR module {module_mm:.2f}mm — below the 0.6mm phone-camera floor')

    size = fit(c, label, 'DM700', side, 11)
    c.setFont('DM700', size)
    c.setFillColorRGB(*MUTED)
    c.drawCentredString(x + side / 2, y - 19, label)
    return module_mm


# ------------------------------------------------- the coral deadline stamp
def draw_stamp(c, cx, cy, r, lines):
    """One coral circle carrying the date, per the identity rules.

    Text in a circle has to clear the ARC, not the
    bounding box — a line near the top or bottom has far less width than the
    diameter suggests. Every line's corners are checked against the radius
    here, and a violation is reported rather than silently printed.
    """
    c.setFillColorRGB(*CORAL)
    c.circle(cx, cy, r, stroke=0, fill=1)
    c.setFillColorRGB(*INK)

    total = sum(h for _, _, _, h in lines)
    cursor = total / 2
    for text, font, size, lh in lines:
        cursor -= lh
        baseline = cy + cursor + lh * 0.30
        c.setFont(font, size)
        c.drawCentredString(cx, baseline, text)

        half_w = c.stringWidth(text, font, size) / 2
        for corner_y in (baseline - size * 0.22, baseline + size * 0.72):
            dy = corner_y - cy
            if math.hypot(half_w, dy) > r * 0.90:
                WARNINGS.append(
                    f'stamp line {text!r} breaks the arc '
                    f'({math.hypot(half_w, dy):.1f}pt vs r={r:.1f}pt)')


# ----------------------------------------------------------- the page shell
def shell(c):
    c.setFillColorRGB(*INK)
    c.rect(0, 0, W, H, stroke=0, fill=1)

    # Indigo glow behind the headline, built from concentric discs because a
    # gradient mesh would not survive every RIP the print shop might use.
    for i in range(60, 0, -1):
        t = i / 60
        c.setFillColorRGB(*[INK[k] + (GLOW[k] - INK[k]) * (1 - t) ** 2 for k in range(3)])
        c.circle(W / 2, H * 0.60, 330 * t, stroke=0, fill=1)

    c.setStrokeColorRGB(1, 1, 1)
    c.setLineWidth(0.4)
    c.setStrokeAlpha(0.035)
    for i in range(1, 7):
        c.line(W * i / 7, 0, W * i / 7, H)
    for i in range(1, 10):
        c.line(0, H * i / 10, W, H * i / 10)
    c.setStrokeAlpha(1)

    # Logo lockup, left
    lw = 118
    c.drawImage(white_logo(), 48, H - 96, width=lw, height=lw * 146 / 375,
                mask='auto')
    c.setStrokeColorRGB(*MUTED)
    c.setLineWidth(0.9)
    c.setStrokeAlpha(0.55)
    c.line(48 + lw + 17, H - 94, 48 + lw + 27, H - 62)
    c.setStrokeAlpha(1)
    c.setFillColorRGB(*PAPER)
    c.setFont('DM700', 7.6)
    c.drawString(48 + lw + 36, H - 71, 'AI ENTREPRENEURSHIP')
    c.setFont('BC800', 15)
    c.drawString(48 + lw + 36, H - 88, 'HACKATHON')

    draw_stamp(c, W - 96, H - 78, 42, [
        ('APPLY BY', 'DM700', 7.2, 11),
        ('4 OCT',    'BC800', 25,   24),
        ('2026',     'DM500', 7.2,  11),
    ])


def footer(c):
    c.setFont('DM500', 10.5)
    c.setFillColorRGB(*MUTED)
    c.drawCentredString(W / 2, 96, '23–26 OCT 2026  ·  EXAMPLE CAMPUS  ·  ALL SKILL LEVELS')

    bar_w, bar_h = 330, 40
    c.setFillColorRGB(*ACCENT)
    c.roundRect((W - bar_w) / 2, 40, bar_w, bar_h, 4, stroke=0, fill=1)
    c.setFillColorRGB(*INK)
    c.setFont('DM700', 15)
    c.drawCentredString(W / 2, 53, 'example.org/hackathon')


# ------------------------------------------------------------- the posters
POSTERS = [
    {
        'slug': 'poster-a-takes-jobs',
        'head': [('AI TAKES JOBS?', PAPER), ('THEN TAKE', ACCENT), ('THE BUSINESS.', ACCENT)],
        'sub':  'Four days building an AI product a business would actually pay for.',
    },
    {
        'slug': 'poster-b-what-if',
        'head': [('WHAT IF', PAPER), ('YOU', PAPER), ('BUILT IT?', ACCENT)],
        'sub':  'That idea you keep coming back to. Give it four days.',
    },
    {
        'slug': 'poster-c-you-take',
        'head': [('AI TAKES', PAPER), ('THE JOBS.', PAPER), ('YOU TAKE', ACCENT), ('THE BUSINESS.', ACCENT)],
        'sub':  'Example College’s first hackathon. No experience required.',
    },
]

for p in POSTERS:
    path = OUT / (p['slug'] + '.pdf')
    c = rl_canvas.Canvas(str(path), pagesize=A4)
    c.setTitle(f"Example College AI Entrepreneurship Hackathon — {p['slug']}")
    shell(c)

    lines = p['head']
    avail = W - 96
    qr_side, qr_y = 230, 150
    n = len(lines)

    # The headline is constrained twice over: by the page width, and by the
    # space left between the coral stamp above and the QR panel below. Solving
    # only for width let a four-line headline sit on top of the QR, so both
    # limits are computed and the smaller one wins.
    CAP_TOP  = 700                      # glyph tops stay clear of the stamp
    SUB_DROP = 30                       # headline baseline -> subhead baseline
    MIN_GAP  = 34                       # subhead baseline -> QR panel
    sub_floor = qr_y + qr_side + MIN_GAP
    band = CAP_TOP - sub_floor
    by_width  = min(fit(c, t, 'BC800', avail, 120) for t, _ in lines)
    by_height = (band - SUB_DROP) / (0.72 + 0.83 * (n - 1))
    size = min(by_width, by_height)

    lh = size * 0.83
    # Centre the headline+subhead block in the band. Hanging it from the top
    # left a dead strip above the QR on the shorter headlines.
    block = 0.72 * size + (n - 1) * lh + SUB_DROP
    first = CAP_TOP - (band - block) / 2 - 0.72 * size
    for i, (text, colour) in enumerate(lines):
        centred(c, text, 'BC800', size, first - i * lh, colour)

    sub_y = first - (n - 1) * lh - SUB_DROP
    s_size = fit(c, p['sub'], 'DM400', avail - 60, 15)
    centred(c, p['sub'], 'DM400', s_size, sub_y, MUTED)

    module_mm = draw_qr(c, (W - qr_side) / 2, qr_y, qr_side)

    gap = sub_y - (qr_y + qr_side)
    if gap < MIN_GAP - 0.6:
        WARNINGS.append(f"{p['slug']}: only {gap:.0f}pt between subhead and QR")
    if first + 0.72 * size > 716:
        WARNINGS.append(f"{p['slug']}: headline reaches the logo/stamp band")

    footer(c)
    c.showPage()
    c.save()
    print(f"{p['slug']:24} QR {qr_side/72*25.4:.0f}mm  module {module_mm:.2f}mm  head {size:.0f}pt")

print()
if WARNINGS:
    print('WARNINGS:')
    for w in dict.fromkeys(WARNINGS):
        print('  !', w)
else:
    print('no layout warnings — every stamp line clears the arc, QR modules above the floor')
