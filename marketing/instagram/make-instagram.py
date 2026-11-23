#!/usr/bin/env python3
"""The Instagram set: two carousels and three stories.

Each carousel is drawn once on a canvas as wide as all its slides and then sliced, so swiping
continues the picture instead of cutting to a new one.

    python marketing/instagram/make-instagram.py
"""
import math, pathlib, sys
import segno
from PIL import Image, ImageOps
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / 'screens'))
from layout import Layout

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parents[1] / 'output' / 'marketing' / 'instagram'
OUT.mkdir(parents=True, exist_ok=True)
PROJ = HERE.parents[1]
FONTS = PROJ / 'brand' / 'fonts'
CACHE = OUT / '_cache'
CACHE.mkdir(exist_ok=True)

POST = (1080, 1350)
STORY = (1080, 1920)
STORY_SAFE = 260

INK    = (0x12/255, 0x13/255, 0x16/255)
PAPER  = (0xf2/255, 0xf1/255, 0xe9/255)
ACCENT = (0x7e/255, 0x98/255, 0xff/255)
BRAND  = (0x14/255, 0x1a/255, 0x9d/255)
CORAL  = (0xff/255, 0x70/255, 0x4b/255)
MUTED  = (0xae/255, 0xb1/255, 0xb9/255)
SLATE  = (0x4a/255, 0x4d/255, 0x55/255)
DEEP   = (0x1b/255, 0x1d/255, 0x42/255)

URL = 'https://example.org/hackathon/#apply'
WARNINGS = []

for w in (600, 700, 800):
    pdfmetrics.registerFont(TTFont(f'BC{w}', FONTS / f'BarlowCondensed-{w}.ttf'))
for w in (400, 500, 700):
    pdfmetrics.registerFont(TTFont(f'DM{w}', FONTS / f'DMSans-{w}.ttf'))


def logo(white=True):
    src = PROJ / 'website/assets/logo.png'
    if not white:
        return ImageReader(str(src))
    dst = CACHE / 'logo-white.png'
    if not dst.exists():
        im = Image.open(src).convert('RGBA')
        a = im.split()[3]
        w = Image.new('L', im.size, 255)
        Image.merge('RGBA', (w, w, w, a)).save(dst)
    return ImageReader(str(dst))


def wide_photo(name, slides, size, wash):
    """One picture as wide as the whole carousel, graded and washed BEFORE it
    is sliced, so no seam can appear at a slide boundary."""
    w, h = size[0] * slides, size[1]
    dst = CACHE / f'wide-{name}-{slides}-{h}-{wash}.jpg'
    if not dst.exists():
        src = next((PROJ / 'sample-data' / 'photos').glob(f'{name}*'))
        im = ImageOps.fit(Image.open(src).convert('RGB'), (w, h), Image.LANCZOS)
        im = ImageOps.grayscale(im).convert('RGB')
        tint = Image.new('RGB', im.size, tuple(int(v * 255) for v in DEEP))
        Image.blend(im, tint, wash).save(dst, quality=90)
    return ImageReader(str(dst)), w, h


def fit(c, text, font, target, start, floor=6):
    s = start
    while s > floor and c.stringWidth(text, font, s) > target:
        s -= 0.5
    return s


def wrap(c, text, font, size, width):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if c.stringWidth(t, font, size) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(c, text, font, size, x, y, width, leading, colour):
    lines = wrap(c, text, font, size, width)
    c.setFont(font, size)
    c.setFillColorRGB(*colour)
    for i, line in enumerate(lines):
        c.drawString(x, y - i * leading, line)
    return lines


def qr_block(c, x, y, side, label_colour, L=None, label='SCAN TO APPLY'):
    qr = segno.make(URL, error='h')
    m = [list(r) for r in qr.matrix]
    n, border = len(m), 4
    mod = side / (n + border * 2)
    c.setFillColorRGB(1, 1, 1)
    c.roundRect(x, y, side, side, 10, stroke=0, fill=1)
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
    c.setFont('DM700', 17)
    c.setFillColorRGB(*label_colour)
    c.drawCentredString(x + side / 2, y - 32, label)
    if mod < 7:
        WARNINGS.append(f'QR module {mod:.1f}px — small for a phone screenshot')
    if L:
        L.place('qr', x, y - 46, side, side + 46)


def circle(c, cx, cy, r, lines, L=None, name='circle'):
    c.setFillColorRGB(*CORAL)
    c.circle(cx, cy, r, stroke=0, fill=1)
    c.setFillColorRGB(*INK)
    total = sum(h for _, _, _, h in lines)
    cur = total / 2
    for text, font, size, lh in lines:
        cur -= lh
        base = cy + cur + lh * 0.30
        c.setFont(font, size)
        c.drawCentredString(cx, base, text)
        half = c.stringWidth(text, font, size) / 2
        for corner in (base - size * 0.22, base + size * 0.72):
            if math.hypot(half, corner - cy) > r * 0.90:
                WARNINGS.append(f'{name}: {text!r} breaks the arc')
    if L:
        L.place(name, cx - r, cy - r, 2 * r, 2 * r)


def dots(c, i, n, y, colour):
    """Carousel position indicator. Instagram draws its own, but its dots sit
    below the image and are easy to miss; this one is inside the artwork."""
    gap, rr = 22, 5
    total = (n - 1) * gap
    for k in range(n):
        c.setFillColorRGB(*colour)
        c.setFillAlpha(1 if k == i else 0.3)
        c.circle(1080 / 2 - total / 2 + k * gap, y, rr, stroke=0, fill=1)
    c.setFillAlpha(1)


def lockup(c, x, y, colour, white=True, w=150):
    c.drawImage(logo(white), x, y, width=w, height=w * 146 / 375, mask='auto')


# =================================================================== A
CAR_A = [
    dict(kind='hook',  big=['AI TAKES', 'THE JOBS?'], accent_from=1),
    dict(kind='facts', big=['YOU TAKE', 'THE BUSINESS.'], accent_from=0,
         facts=['Four days building an AI product a business would pay to use',
                'Teams are built for you — builders, business minds, designers',
                'No experience needed. Free to apply, no CV']),
    dict(kind='cta',   big=['BRING YOUR', 'WHAT IF.'], accent_from=1),
]

# =================================================================== B
CAR_B = [
    dict(kind='deny', top='YOU DON’T NEED', big='A TEAM.',
         body='We build them. Mixed on purpose, so everyone has something to contribute.'),
    dict(kind='deny', top='YOU DON’T NEED', big='AN IDEA.',
         body='You can arrive with nothing but curiosity. The idea comes on day one, with your team.'),
    dict(kind='deny', top='YOU DON’T NEED', big='TO CODE.',
         body='Teams need people who work out the customer, the price and the pitch just as much.'),
    dict(kind='cta',  top='YOU DO NEED', big='FOUR DAYS.',
         body='23–26 October 2026, Example Campus. Apply by 4 October.'),
]


def draw_carousel_a(slides_dir):
    n = len(CAR_A)
    bg, bw, bh = wide_photo('crowd', n, POST, 0.58)
    for i, s in enumerate(CAR_A):
        path = slides_dir / f'A-{i+1}-of-{n}.pdf'
        c = rl_canvas.Canvas(str(path), pagesize=POST)
        L = Layout(path.stem)
        c.drawImage(bg, -i * POST[0], 0, bw, bh, mask=None)

        # continuous horizon rule, drawn in canvas coordinates
        c.setStrokeColorRGB(*ACCENT)
        c.setLineWidth(2)
        c.setStrokeAlpha(0.5)
        c.line(-i * POST[0], 392, -i * POST[0] + bw, 392)
        c.setStrokeAlpha(1)

        lockup(c, 72, 1216, PAPER)
        c.setFont('DM700', 15)
        c.setFillColorRGB(*ACCENT)
        c.drawRightString(1008, 1240, f'{i+1} / {n}')

        big = s['big']
        size = min(fit(c, t, 'BC800', 936, 132) for t in big)
        lh = size * 0.84
        first = 1020
        for k, t in enumerate(big):
            c.setFont('BC800', size)
            c.setFillColorRGB(*(ACCENT if k >= s['accent_from'] else PAPER))
            c.drawString(72, first - k * lh, t)
        L.place('big', 72, first - (len(big) - 1) * lh - 30, 936,
                (len(big) - 1) * lh + size)

        if s['kind'] == 'facts':
            fy = 330
            for f in s['facts']:
                c.setFillColorRGB(*ACCENT)
                c.circle(80, fy + 7, 5, stroke=0, fill=1)
                ln = para(c, f, 'DM400', 25, 104, fy, 880, 33, PAPER)
                fy -= 33 * len(ln) + 26
        elif s['kind'] == 'cta':
            qr_block(c, 72, 150, 320, PAPER, L)
            c.setFont('DM700', 27)
            c.setFillColorRGB(*PAPER)
            c.drawString(436, 340, '23–26 OCTOBER 2026')
            c.setFont('DM400', 23)
            c.setFillColorRGB(*MUTED)
            c.drawString(436, 302, 'Example Campus · Free · All skill levels')
            c.drawString(436, 268, 'Apply by 4 October')
            c.setFont('DM700', 25)
            c.setFillColorRGB(*ACCENT)
            c.drawString(436, 198, 'example.org/hackathon')
            circle(c, 900, 470, 92, [('APPLY', 'BC800', 37, 35), ('NOW', 'BC800', 37, 35)],
                   L, 'applynow')
        else:
            c.setFont('DM400', 26)
            c.setFillColorRGB(*MUTED)
            c.drawString(72, 330, 'Example College’s first AI Entrepreneurship Hackathon')

        if i == 0:
            c.setFont('DM700', 22)
            c.setFillColorRGB(*ACCENT)
            c.drawRightString(1008, 150, 'SWIPE →')

        dots(c, i, n, 96, PAPER)
        c.showPage()
        c.save()
        WARNINGS.extend(L.problems)
        print(f'  {path.name}')


def draw_carousel_b(slides_dir):
    """Cream palette. The continuity device is type, not photography: one
    enormous WHAT IF runs the full width of the canvas behind everything, so
    each slide shows a different fragment of the same letters."""
    n = len(CAR_B)
    cw = POST[0] * n
    for i, s in enumerate(CAR_B):
        path = slides_dir / f'B-{i+1}-of-{n}.pdf'
        c = rl_canvas.Canvas(str(path), pagesize=POST)
        L = Layout(path.stem)
        c.setFillColorRGB(*PAPER)
        c.rect(0, 0, *POST, stroke=0, fill=1)

        ghost = 'WHAT IF YOU BUILT IT?'
        gsize = fit(c, ghost, 'BC800', cw - 120, 900)
        c.setFillColorRGB(*BRAND)
        c.setFillAlpha(0.07)
        c.setFont('BC800', gsize)
        c.drawString(60 - i * POST[0], 470, ghost)
        c.setFillAlpha(1)

        c.setStrokeColorRGB(*BRAND)
        c.setLineWidth(2)
        c.setStrokeAlpha(0.35)
        c.line(-i * POST[0], 392, -i * POST[0] + cw, 392)
        c.setStrokeAlpha(1)

        lockup(c, 72, 1216, BRAND, white=False)
        c.setFont('DM700', 15)
        c.setFillColorRGB(*BRAND)
        c.drawRightString(1008, 1240, f'{i+1} / {n}')

        c.setFont('DM700', 30)
        c.setFillColorRGB(*SLATE)
        c.drawString(72, 1010, s['top'])
        L.place('top', 72, 1002, c.stringWidth(s['top'], 'DM700', 30), 38)

        size = fit(c, s['big'], 'BC800', 936, 168)
        c.setFont('BC800', size)
        c.setFillColorRGB(*BRAND)
        c.drawString(72, 1010 - size * 0.92, s['big'])
        L.place('big', 72, 1010 - size * 0.92 - size * 0.26, 936, size)

        ln = para(c, s['body'], 'DM400', 27, 72, 640, 880, 37, SLATE)
        L.place('body', 72, 640 - (len(ln) - 1) * 37 - 8, 880, (len(ln) - 1) * 37 + 30)

        if s['kind'] == 'cta':
            qr_block(c, 72, 150, 320, SLATE, L)
            c.setFont('DM700', 25)
            c.setFillColorRGB(*BRAND)
            c.drawString(436, 250, 'example.org/hackathon')
            c.setFont('DM400', 22)
            c.setFillColorRGB(*SLATE)
            c.drawString(436, 212, 'Free · No CV · All skill levels')
            circle(c, 900, 470, 92, [('APPLY', 'BC800', 37, 35), ('NOW', 'BC800', 37, 35)],
                   L, 'applynow')
        if i == 0:
            c.setFont('DM700', 22)
            c.setFillColorRGB(*BRAND)
            c.drawRightString(1008, 150, 'SWIPE →')

        dots(c, i, n, 96, BRAND)
        c.showPage()
        c.save()
        WARNINGS.extend(L.problems)
        print(f'  {path.name}')


# =============================================================== stories
STORIES = [
    dict(name='01-hook', photo='crowd', big=['AI TAKES', 'THE JOBS?'],
         accent_from=1, kicker='Example College’S FIRST', sub='Then take the business.', cta=False),
    dict(name='02-what', photo='workspace', big=['FOUR DAYS.', 'ONE WORKING', 'AI PRODUCT.'],
         accent_from=2, kicker='23–26 OCTOBER 2026 · EXAMPLE CAMPUS',
         sub='Teams built for you. No code needed. Free to apply.', cta=False),
    dict(name='03-apply', photo='stage', big=['BRING YOUR', 'WHAT IF.'],
         accent_from=1, kicker='APPLY BY 4 OCTOBER', sub='', cta=True),
]


def draw_stories(out):
    for s in STORIES:
        path = out / f'story-{s["name"]}.pdf'
        c = rl_canvas.Canvas(str(path), pagesize=STORY)
        L = Layout(path.stem)
        bg, bw, bh = wide_photo(s['photo'], 1, STORY, 0.62)
        c.drawImage(bg, 0, 0, bw, bh, mask=None)

        lockup(c, 72, STORY[1] - STORY_SAFE - 40, PAPER, w=168)
        c.setFont('DM700', 19)
        c.setFillColorRGB(*ACCENT)
        c.drawString(72, STORY[1] - STORY_SAFE - 96, s['kicker'])

        big = s['big']
        size = min(fit(c, t, 'BC800', 936, 150) for t in big)
        lh = size * 0.84
        first = 1180
        for k, t in enumerate(big):
            c.setFont('BC800', size)
            c.setFillColorRGB(*(ACCENT if k >= s['accent_from'] else PAPER))
            c.drawString(72, first - k * lh, t)
        L.place('big', 72, first - (len(big) - 1) * lh - 34, 936,
                (len(big) - 1) * lh + size)

        if s['sub']:
            ln = para(c, s['sub'], 'DM400', 30, 72, first - len(big) * lh - 18, 900, 40, PAPER)
            L.place('sub', 72, first - len(big) * lh - 18 - (len(ln) - 1) * 40 - 10, 900,
                    (len(ln) - 1) * 40 + 34)

        if s['cta']:
            qr_block(c, 72, STORY_SAFE + 150, 360, PAPER, L)
            c.setFont('DM700', 30)
            c.setFillColorRGB(*PAPER)
            c.drawString(478, STORY_SAFE + 360, '23–26 OCT 2026')
            c.setFont('DM400', 25)
            c.setFillColorRGB(*MUTED)
            c.drawString(478, STORY_SAFE + 320, 'Example Campus · Free')
            c.setFont('DM700', 26)
            c.setFillColorRGB(*ACCENT)
            c.drawString(478, STORY_SAFE + 250, 'example.org/')
            c.drawString(478, STORY_SAFE + 216, 'hackathon')
            circle(c, 880, STORY_SAFE + 600, 96,
                   [('APPLY', 'BC800', 39, 37), ('NOW', 'BC800', 39, 37)], L, 'applynow')
        else:
            circle(c, 880, STORY_SAFE + 300, 96,
                   [('APPLY', 'BC800', 39, 37), ('NOW', 'BC800', 39, 37)], L, 'applynow')
            c.setFont('DM700', 26)
            c.setFillColorRGB(*ACCENT)
            c.drawString(72, STORY_SAFE + 268, 'example.org/hackathon')

        # the zones Instagram covers with its own controls
        for y0 in (0, STORY[1] - STORY_SAFE):
            for _, (bx0, by0, bx1, by1) in L.boxes:
                if by0 < y0 + STORY_SAFE and by1 > y0:
                    WARNINGS.append(f'{path.stem}: content inside the {STORY_SAFE}px story safe zone')
                    break
        c.showPage()
        c.save()
        WARNINGS.extend(L.problems)
        print(f'  {path.name}')


def main():
    a = OUT / 'carousel-A-ai-takes-the-jobs'
    b = OUT / 'carousel-B-you-dont-need'
    st = OUT / 'stories'
    for d in (a, b, st):
        d.mkdir(parents=True, exist_ok=True)
    print('carousel A (dark, photographic, continuous background):')
    draw_carousel_a(a)
    print('carousel B (cream, continuous oversized type):')
    draw_carousel_b(b)
    print('stories:')
    draw_stories(st)
    print()
    if WARNINGS:
        print('WARNINGS:')
        for w in dict.fromkeys(WARNINGS):
            print('  !', w)
    else:
        print('no warnings — overlap, arc, QR and story-safe-zone checks all pass')


if __name__ == '__main__':
    main()
