#!/usr/bin/env python3
"""TV hero cards: lockup and copy on the left, QR code on the right. Three versions.

    python marketing/social/make-hero.py
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

W, H = 1920, 1080
MARGIN = 100
QR_SIDE = 340
QR_X = W - MARGIN - QR_SIDE
GUTTER = 96
COL = QR_X - GUTTER - MARGIN            # left column width

INK    = (0x12/255, 0x13/255, 0x16/255)
PAPER  = (0xf2/255, 0xf1/255, 0xe9/255)
ACCENT = (0x7e/255, 0x98/255, 0xff/255)
MUTED  = (0xae/255, 0xb1/255, 0xb9/255)

URL = 'https://example.org/hackathon/#apply'

TITLE_A, TITLE_B = 'WHAT IF YOU ', 'BUILT IT?'
SUB = 'Bring your what if. Build it with your team, here.'
DETAIL = ('Four days. Your team. A working AI product. '
          'From 23 October at Example Campus.')
FOOTER = 'EXAMPLE.ORG/HACKATHON  •  ALL SKILL LEVELS WELCOME'
QR_LABEL = 'SCAN TO APPLY NOW'

CAP = 0.72        # cap height as a fraction of font size, Barlow/DM Sans
DESC = 0.22       # descender depth

WARNINGS = []

for w in (600, 700, 800):
    pdfmetrics.registerFont(TTFont(f'BC{w}', FONTS / f'BarlowCondensed-{w}.ttf'))
for w in (400, 500, 700):
    pdfmetrics.registerFont(TTFont(f'DM{w}', FONTS / f'DMSans-{w}.ttf'))


# ------------------------------------------------------------------ assets
def cic_mark():
    """Example Campus, as supplied, unaltered.

    The file they sent stacks a grey "powered by" above the orange mark. That
    grey is #5A5A5C — 2.1:1 on our ink ground, which is invisible on a screen
    across a lobby. Recolouring another organisation's artwork is the wrong
    fix, so the mark is used exactly as given and the descriptor is re-set in
    our own typeface beside it. Example Campus orange (#FE8100) is untouched, and is far
    enough from our coral (#FF704B) that the two never read as the same ink.
    """
    return ImageReader(str(PROJ / 'brand' / 'logos' / 'partner-mark.png'))


def white_logo():
    dst = CACHE / 'logo-white.png'
    if not dst.exists():
        im = Image.open(PROJ / 'website/assets/logo.png').convert('RGBA')
        a = im.split()[3]
        w = Image.new('L', im.size, 255)
        Image.merge('RGBA', (w, w, w, a)).save(dst)
    return ImageReader(str(dst))


def photo(name, wash):
    """Uniform darkening, no centre scrim: copy runs down the left and the QR
    sits on the right, so a centre-weighted veil would brighten precisely the
    empty middle and dim both columns that actually carry content."""
    dst = CACHE / f'hero-{name}-{wash}.jpg'
    if not dst.exists():
        src = next((PROJ / 'sample-data' / 'photos').glob(f'{name}*'))
        im = ImageOps.fit(Image.open(src).convert('RGB'), (W, H), Image.LANCZOS)
        im = ImageOps.grayscale(im).convert('RGB')
        tint = Image.new('RGB', im.size, tuple(int(v * 255) for v in INK))
        Image.blend(im, tint, wash).save(dst, quality=92)
    return ImageReader(str(dst))


# -------------------------------------------------------------------- text
def fit(c, text, font, target, start, floor=8):
    s = start
    while s > floor and c.stringWidth(text, font, s) > target:
        s -= 0.5
    return s


def tracked_width(c, text, font, size, track):
    return c.stringWidth(text, font, size) + track * max(0, len(text) - 1)


def draw_tracked(c, x, baseline, text, font, size, track):
    # Letter spacing lives on the text object in reportlab, not the canvas.
    # The text object inherits the canvas fill colour, so set that first.
    to = c.beginText(x, baseline)
    to.setFont(font, size)
    to.setCharSpace(track)
    to.textOut(text)
    # Character spacing is PDF graphics state, not a property of this text
    # object. Left set, it applies to every string drawn afterwards: the
    # POWERED BY label was quietly letter-spacing the title and both body lines
    # by 1.5pt, and making them wider than stringWidth() reported. Reset it.
    to.setCharSpace(0)
    c.drawText(to)
    return tracked_width(c, text, font, size, track)


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


# ---------------------------------------------------------------- the stack
class Stack:
    """Blocks declare height and trailing gap; the whole column is then
    optically centred. No block ever knows its own absolute position, so a
    size change cannot silently push one block through another."""

    def __init__(self):
        self.items = []

    def add(self, name, height, gap, draw):
        self.items.append([name, height, gap, draw])

    def render(self, c, L, canvas_h):
        total = sum(i[1] for i in self.items) + sum(i[2] for i in self.items[:-1])
        if total > canvas_h - 2 * 70:
            WARNINGS.append(f'left column is {total:.0f}pt tall, taller than the safe area')
        top = (canvas_h + total) / 2
        for name, h, gap, draw in self.items:
            draw(c, top)
            L.place(name, MARGIN, top - h, COL, h)
            top -= h + gap
        return total


# --------------------------------------------------------------- components
def lockup(c, top, logo_w=246):
    """logo · slanted divider · AI ENTREPRENEURSHIP / HACKATHON.
    `top` is the top of the logo artwork; returns the block height."""
    lh = logo_w * 146 / 375
    c.drawImage(white_logo(), MARGIN, top - lh, width=logo_w, height=lh, mask='auto')

    dx = MARGIN + logo_w + lh * 0.30
    c.setStrokeColorRGB(*PAPER)
    c.setLineWidth(1.6)
    c.setStrokeAlpha(0.55)
    c.line(dx, top - lh * 0.96, dx + lh * 0.24, top - lh * 0.06)
    c.setStrokeAlpha(1)

    tx = dx + lh * 0.24 + lh * 0.34
    small, big = lh * 0.235, lh * 0.50
    c.setFillColorRGB(*PAPER)
    c.setFont('DM700', small)
    c.drawString(tx, top - lh * 0.40, 'AI ENTREPRENEURSHIP')
    c.setFont('BC800', big)
    c.drawString(tx, top - lh * 0.94, 'HACKATHON')
    right = tx + max(c.stringWidth('AI ENTREPRENEURSHIP', 'DM700', small),
                     c.stringWidth('HACKATHON', 'BC800', big))

    # ---- partner credit, on the same baseline strip as our own lockup ----
    mid = top - lh * 0.50
    rule_x = right + 54
    c.setStrokeColorRGB(*PAPER)
    c.setLineWidth(1)
    c.setStrokeAlpha(0.28)
    c.line(rule_x, mid - lh * 0.46, rule_x, mid + lh * 0.46)
    c.setStrokeAlpha(1)

    label, label_size = 'POWERED BY', 15
    lx = rule_x + 38
    c.setFillColorRGB(*MUTED)
    lw = draw_tracked(c, lx, mid - label_size * CAP / 2, label,
                      'DM700', label_size, 1.5)

    mark_h = 92
    mark_w = mark_h * 1.218                    # measured from the supplied file
    mx = lx + lw + 26
    c.drawImage(cic_mark(), mx, mid - mark_h / 2, width=mark_w, height=mark_h,
                mask='auto')

    strip = (mx + mark_w) - MARGIN
    if strip > COL:
        WARNINGS.append(f'lockup strip is {strip:.0f}pt, wider than the {COL}pt column')
    return lh


def qr_column(c, L, cy, side=QR_SIDE, panel=False):
    """QR plus its label, as one optically centred block on the right."""
    label_size = 26
    label_gap = 30
    block_h = side + label_gap + label_size * CAP
    top = cy + block_h / 2
    x, y = QR_X, top - side

    if panel:
        pad = 34
        c.setFillColorRGB(*PAPER)
        c.setFillAlpha(0.10)
        c.roundRect(x - pad, y - label_gap - label_size - pad + 8,
                    side + pad * 2, side + label_gap + label_size + pad * 2 - 8,
                    10, stroke=0, fill=1)
        c.setFillAlpha(1)

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
    if mod < 6:
        WARNINGS.append(f'QR module {mod:.1f}px — small for a floor screen')

    lw = tracked_width(c, QR_LABEL, 'DM700', label_size, 1.4)
    c.setFillColorRGB(*ACCENT)
    draw_tracked(c, x + (side - lw) / 2, y - label_gap - label_size * CAP,
                 QR_LABEL, 'DM700', label_size, 1.4)
    L.place('qr', x, y - label_gap - label_size, side, block_h)
    return mod


# ----------------------------------------------------------------- versions
def build(c, L, version):
    two_line = version in ('v2', 'v3')
    c.drawImage(photo('crowd', 0.82), 0, 0, W, H, mask=None)

    s = Stack()

    # 1 — the lockup
    lh = 246 * 146 / 375
    s.add('lockup', lh, 58, lambda c, top: lockup(c, top))

    # 2 — the title
    if two_line:
        t1, t2 = 'WHAT IF YOU', 'BUILT IT?'
        size = min(fit(c, t1, 'BC800', COL, 200), fit(c, t2, 'BC800', COL, 200))
        lead = size * 0.84
        h = CAP * size + lead - CAP * size + CAP * size   # two cap-heights + leading gap
        h = lead + CAP * size

        def draw_title(c, top, size=size, lead=lead):
            c.setFont('BC800', size)
            c.setFillColorRGB(*PAPER)
            c.drawString(MARGIN, top - CAP * size, 'WHAT IF YOU')
            c.setFillColorRGB(*ACCENT)
            c.drawString(MARGIN, top - CAP * size - lead, 'BUILT IT?')
    else:
        full = TITLE_A.rstrip() + '  ' + TITLE_B      # approximates the explicit gap
        size = fit(c, full, 'BC800', COL, 156)
        h = CAP * size

        def draw_title(c, top, size=size):
            c.setFont('BC800', size)
            c.setFillColorRGB(*PAPER)
            c.drawString(MARGIN, top - CAP * size, TITLE_A.rstrip())
            c.setFillColorRGB(*ACCENT)
            # Barlow Condensed's word space is very narrow; at display sizes a
            # single space between two differently coloured runs reads as no
            # space at all. Set the gap explicitly.
            gap = size * 0.20
            c.drawString(MARGIN + c.stringWidth(TITLE_A.rstrip(), 'BC800', size) + gap,
                         top - CAP * size, TITLE_B)
    s.add('title', h, 46 if two_line else 42, draw_title)

    # 3 — the invitation
    sub_size = fit(c, SUB, 'DM500', COL, 44)
    s.add('sub', CAP * sub_size + DESC * sub_size, 22,
          lambda c, top, z=sub_size: (c.setFont('DM500', z),
                                      c.setFillColorRGB(*PAPER),
                                      c.drawString(MARGIN, top - CAP * z, SUB)))

    # 4 — the detail, wrapped
    det_size = 31
    det_lines = wrap(c, DETAIL, 'DM400', det_size, COL)
    det_lead = det_size * 1.38
    s.add('detail', (len(det_lines) - 1) * det_lead + CAP * det_size + DESC * det_size, 44,
          lambda c, top, z=det_size, ls=det_lines, ld=det_lead: [
              (c.setFont('DM400', z), c.setFillColorRGB(*MUTED),
               c.drawString(MARGIN, top - CAP * z - i * ld, ln))
              for i, ln in enumerate(ls)])

    # 5 — the address line, smallest
    foot_size = 23
    s.add('footer', CAP * foot_size, 0,
          lambda c, top, z=foot_size: (c.setFillColorRGB(*PAPER),
                                       draw_tracked(c, MARGIN, top - CAP * z,
                                                    FOOTER, 'DM700', z, 1.6)))

    total = s.render(c, L, H)

    if version == 'v2':
        rx = QR_X - GUTTER / 2
        c.setStrokeColorRGB(*PAPER)
        c.setLineWidth(1)
        c.setStrokeAlpha(0.20)
        c.line(rx, (H - total) / 2, rx, (H + total) / 2)
        c.setStrokeAlpha(1)
    if version == 'v3':
        top = (H + total) / 2
        c.setStrokeColorRGB(*ACCENT)
        c.setLineWidth(3)
        c.line(MARGIN, top - lh - 26, MARGIN + 132, top - lh - 26)

    qr_column(c, L, H / 2, panel=(version == 'v3'))


def main():
    for v in ('v1', 'v2', 'v3'):
        path = OUT / f'tv-hero-{v}-1920x1080.pdf'
        c = rl_canvas.Canvas(str(path), pagesize=(W, H))
        c.setTitle('Example College AI Entrepreneurship Hackathon — What if you built it?')
        L = Layout(path.stem)
        build(c, L, v)
        for name, (x0, y0, x1, y1) in L.boxes:
            if x0 < MARGIN - 2 or x1 > W - MARGIN + 2 or y0 < 60 or y1 > H - 60:
                WARNINGS.append(f'{path.stem}: {name!r} leaves the safe area')
        c.showPage()
        c.save()
        WARNINGS.extend(L.problems)
        print(f'  {path.name:34} {len(L.boxes)} blocks, {len(L.problems)} overlap(s)')
    print()
    if WARNINGS:
        print('WARNINGS:')
        for w in dict.fromkeys(WARNINGS):
            print('  !', w)
    else:
        print('no warnings — overlap, safe-area and QR checks all pass')


if __name__ == '__main__':
    main()
