#!/usr/bin/env python3
"""An Instagram carousel cut from one wide picture, so the background runs across the slides.

    python marketing/instagram/make-carousel-a.py
"""
import pathlib, sys
from PIL import Image, ImageOps
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / 'screens'))
from layout import Layout

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parents[1] / 'output' / 'marketing' / 'instagram' / 'carousel-A-industry-connected'
OUT.mkdir(parents=True, exist_ok=True)
PROJ = HERE.parents[1]
FONTS = PROJ / 'brand' / 'fonts'
CACHE = OUT / '_cache'
CACHE.mkdir(exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1350
N = 3
MARGIN = 72
COL = W - MARGIN * 2
# The content band. Every slide centres its stack in the SAME band, so three
# slides carrying different amounts of copy still sit on a common axis when
# you swipe between them. Top-anchoring them left the lower third empty and
# made the set look unfinished.
BAND_TOP, BAND_BOTTOM = 1122, 330
MIN_TEXT = 30              # nothing readable is smaller than this

INK    = (0x12/255, 0x13/255, 0x16/255)
PAPER  = (0xf2/255, 0xf1/255, 0xe9/255)
ACCENT = (0x7e/255, 0x98/255, 0xff/255)
MUTED  = (0xc4/255, 0xc7/255, 0xd2/255)   # lifted from the old muted: too dim to read
DEEP   = (0x1b/255, 0x1d/255, 0x42/255)

CAP, DESC = 0.72, 0.22
WARNINGS = []

for w in (600, 700, 800):
    pdfmetrics.registerFont(TTFont(f'BC{w}', FONTS / f'BarlowCondensed-{w}.ttf'))
for w in (400, 500, 700):
    pdfmetrics.registerFont(TTFont(f'DM{w}', FONTS / f'DMSans-{w}.ttf'))


def white_logo():
    dst = CACHE / 'logo-white.png'
    if not dst.exists():
        im = Image.open(PROJ / 'website/assets/logo.png').convert('RGBA')
        a = im.split()[3]
        w = Image.new('L', im.size, 255)
        Image.merge('RGBA', (w, w, w, a)).save(dst)
    return ImageReader(str(dst))


def wide_photo(wash=0.62):
    w, h = W * N, H
    dst = CACHE / f'carA-{w}x{h}-{wash}.jpg'
    if not dst.exists():
        src = next((PROJ / 'sample-data' / 'photos').glob('crowd*'))
        im = ImageOps.fit(Image.open(src).convert('RGB'), (w, h), Image.LANCZOS)
        im = ImageOps.grayscale(im).convert('RGB')
        tint = Image.new('RGB', im.size, tuple(int(v * 255) for v in DEEP))
        Image.blend(im, tint, wash).save(dst, quality=90)
    return ImageReader(str(dst)), w, h


def fit(c, text, font, target, start, floor=8):
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


class Stack:
    """Each block states its ink height and the gap after it; the whole column
    is then centred in the band. No block knows its absolute position, so a
    size change re-flows the column instead of pushing one block through
    another."""

    def __init__(self):
        self.items = []

    def add(self, name, height, gap, draw):
        self.items.append((name, height, gap, draw))

    def render(self, c, L):
        total = (sum(i[1] for i in self.items)
                 + sum(i[2] for i in self.items[:-1]))
        band = BAND_TOP - BAND_BOTTOM
        if total > band:
            WARNINGS.append(f'{L.name}: stack is {total:.0f}pt, band is {band:.0f}pt')
        y = BAND_BOTTOM + (band + total) / 2
        for name, h, gap, draw in self.items:
            draw(c, y)
            L.place(name, MARGIN, y - h, COL, h)
            y -= h + gap
        return y


def display(c, L, s, lines, max_size, gap_after):
    """A condensed display block. Colour flips to accent on the final line."""
    size = min(fit(c, t, 'BC800', COL, max_size) for t in lines)
    lead = size * 0.84
    h = (len(lines) - 1) * lead + CAP * size

    def draw(c, top, size=size, lead=lead):
        for i, t in enumerate(lines):
            c.setFont('BC800', size)
            c.setFillColorRGB(*(ACCENT if i == len(lines) - 1 else PAPER))
            c.drawString(MARGIN, top - CAP * size - i * lead, t)
    s.add('title', h, gap_after, draw)
    return size


def body(c, s, name, text, size, colour, gap, font='DM400', width=None):
    if size < MIN_TEXT:
        WARNINGS.append(f'{name} at {size}pt is below the {MIN_TEXT}pt floor')
    width = width or COL
    lines = wrap(c, text, font, size, width)
    lead = size * 1.36
    h = (len(lines) - 1) * lead + CAP * size + DESC * size

    def draw(c, top, z=size, ls=lines, ld=lead):
        c.setFont(font, z)
        c.setFillColorRGB(*colour)
        for i, ln in enumerate(ls):
            c.drawString(MARGIN, top - CAP * z - i * ld, ln)
    s.add(name, h, gap, draw)


def bullets(c, s, name, items, size, gap):
    if size < MIN_TEXT:
        WARNINGS.append(f'{name} at {size}pt is below the {MIN_TEXT}pt floor')
    lead = size * 1.34
    wrapped = [wrap(c, t, 'DM400', size, COL - 46) for t in items]
    block = sum((len(w) - 1) * lead + CAP * size + DESC * size for w in wrapped)
    spacing = 30
    h = block + spacing * (len(items) - 1)

    def draw(c, top, z=size, ws=wrapped, ld=lead, sp=spacing):
        y = top
        for w in ws:
            c.setFillColorRGB(*ACCENT)
            c.circle(MARGIN + 9, y - CAP * z * 0.62, 8, stroke=0, fill=1)
            c.setFont('DM400', z)
            c.setFillColorRGB(*PAPER)
            for i, ln in enumerate(w):
                c.drawString(MARGIN + 46, y - CAP * z - i * ld, ln)
            y -= (len(w) - 1) * ld + CAP * z + DESC * z + sp
    s.add(name, h, gap, draw)


def chrome(c, L, i, bg, bw, bh):
    c.drawImage(bg, -i * W, 0, bw, bh, mask=None)
    c.setStrokeColorRGB(*ACCENT)
    c.setLineWidth(3)
    c.setStrokeAlpha(0.55)
    c.line(-i * W, 268, -i * W + bw, 268)     # continuous, in canvas coordinates
    c.setStrokeAlpha(1)

    lw = 168
    c.drawImage(white_logo(), MARGIN, H - 118, width=lw, height=lw * 146 / 375,
                mask='auto')
    c.setFont('DM700', 26)
    c.setFillColorRGB(*ACCENT)
    c.drawRightString(W - MARGIN, H - 100, f'{i+1} / {N}')

    gap, rr = 26, 6
    total = (N - 1) * gap
    for k in range(N):
        c.setFillColorRGB(*PAPER)
        c.setFillAlpha(1 if k == i else 0.32)
        c.circle(W / 2 - total / 2 + k * gap, 120, rr, stroke=0, fill=1)
    c.setFillAlpha(1)
    if i == 0:
        c.setFont('DM700', 30)
        c.setFillColorRGB(*ACCENT)
        c.drawRightString(W - MARGIN, 108, 'SWIPE →')


def main():
    bg, bw, bh = wide_photo()
    for i in range(N):
        path = OUT / f'A-{i+1}-of-{N}.pdf'
        c = rl_canvas.Canvas(str(path), pagesize=(W, H))
        c.setTitle('Example College — Industry connected AI hackathon')
        L = Layout(path.stem)
        chrome(c, L, i, bg, bw, bh)
        s = Stack()

        if i == 0:
            # Slide 1 exists to stop the scroll. One idea, at the biggest size
            # the column will carry, and one readable line under it.
            display(c, L, s, ['INDUSTRY', 'CONNECTED', 'AI HACKATHON.'], 172, 58)
            body(c, s, 'sub', 'Example College’s first. Four days building a working AI product '
                              'with mentors and judges from industry.', 40, PAPER, 34)
            body(c, s, 'meta', '23–26 October 2026 · Example Campus', 34, ACCENT, 0, font='DM700')
        elif i == 1:
            display(c, L, s, ['FOUR DAYS.', 'ONE TEAM.', 'ONE PRODUCT.'], 150, 54)
            bullets(c, s, 'facts', [
                'Mentors and judges from companies building AI',
                'Teams built for you — builders, business minds, designers',
                'No experience needed. Free to apply.',
            ], 34, 0)
        else:
            display(c, L, s, ['WHAT IF YOU', 'BUILT IT?'], 156, 50)
            body(c, s, 'sub', 'Bring your what if. Build it with your team, here.',
                 42, PAPER, 26, font='DM500')
            body(c, s, 'detail', 'Four days. Your team. A working AI product. '
                                 'From 23 October at Example Campus.', 34, MUTED, 42)
            body(c, s, 'footer', 'EXAMPLE.ORG/HACKATHON  •  ALL SKILL LEVELS WELCOME',
                 30, PAPER, 0, font='DM700')

        s.render(c, L)
        c.showPage()
        c.save()
        WARNINGS.extend(L.problems)
        print(f'  {path.name:16} {len(L.boxes)} blocks, {len(L.problems)} overlap(s)')

    print()
    if WARNINGS:
        print('WARNINGS:')
        for w in dict.fromkeys(WARNINGS):
            print('  !', w)
    else:
        print(f'no warnings — no overlaps, nothing below the {MIN_TEXT}pt text floor')


if __name__ == '__main__':
    main()
