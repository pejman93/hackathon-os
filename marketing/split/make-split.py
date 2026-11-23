#!/usr/bin/env python3
"""Split-panel screens: details on one side, wordmark and QR code on the other.

    python marketing/split/make-split.py
"""
import math, pathlib, sys
import segno
from PIL import Image
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / 'screens'))
from layout import Layout

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parents[1] / 'output' / 'marketing' / 'split'
OUT.mkdir(parents=True, exist_ok=True)
PROJ = HERE.parents[1]
FONTS = PROJ / 'brand' / 'fonts'
CACHE = OUT / '_cache'
CACHE.mkdir(exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1920, 1080
SPLIT = 1205                       # panel starts here
PW = W - SPLIT                     # panel width
PCX = SPLIT + PW / 2               # panel centre
MARGIN = 72
DW = SPLIT - MARGIN - 110          # usable width on the detail side

INK    = (0x12/255, 0x13/255, 0x16/255)
PAPER  = (0xf2/255, 0xf1/255, 0xe9/255)
ACCENT = (0x7e/255, 0x98/255, 0xff/255)
BRAND  = (0x14/255, 0x1a/255, 0x9d/255)
CORAL  = (0xff/255, 0x70/255, 0x4b/255)
MUTED  = (0xae/255, 0xb1/255, 0xb9/255)
SLATE  = (0x4a/255, 0x4d/255, 0x55/255)
DEEP   = (0x1b/255, 0x1d/255, 0x42/255)

URL = 'https://example.org/hackathon/#apply'

# The panel is a dark ground in both palettes, so the logo is white in both —
# the cream-ground rule never applies to it here.
THEMES = {
    'dark': dict(bg=INK,   fg=PAPER, accent=ACCENT, body=MUTED,
                 panel=DEEP,  panel_fg=PAPER, panel_accent=ACCENT,
                 rule=(1, 1, 1), rule_a=0.16, card=(1, 1, 1), card_a=0.05),
    'college': dict(bg=PAPER, fg=INK,   accent=BRAND,  body=SLATE,
                 panel=BRAND, panel_fg=PAPER, panel_accent=(0xa9/255, 0xb8/255, 0xff/255),
                 rule=(0, 0, 0), rule_a=0.16, card=(0, 0, 0), card_a=0.04),
}

for w in (600, 700, 800):
    pdfmetrics.registerFont(TTFont(f'BC{w}', FONTS / f'BarlowCondensed-{w}.ttf'))
for w in (400, 500, 700):
    pdfmetrics.registerFont(TTFont(f'DM{w}', FONTS / f'DMSans-{w}.ttf'))

WARNINGS = []


def luminance(c):
    f = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * f[0] + 0.7152 * f[1] + 0.0722 * f[2]


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def check(fg, bg, label, floor=4.5):
    r = contrast(fg, bg)
    if r < floor:
        WARNINGS.append(f'{label}: contrast {r:.2f} (needs {floor:.1f})')


def white_logo():
    dst = CACHE / 'logo-white.png'
    if not dst.exists():
        im = Image.open(PROJ / 'website/assets/logo.png').convert('RGBA')
        a = im.split()[3]
        w = Image.new('L', im.size, 255)
        Image.merge('RGBA', (w, w, w, a)).save(dst)
    return ImageReader(str(dst))


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


# ------------------------------------------------------------------ panel
def panel(c, t, L):
    """Constant across all three designs: this is the bit people learn to
    recognise from the far end of a corridor."""
    c.setFillColorRGB(*t['panel'])
    c.rect(SPLIT, 0, PW, H, stroke=0, fill=1)
    L.place('panel', SPLIT, 0, PW, H,
            may_overlap=('logo', 'wordmark', 'qr', 'qrlabel', 'applynow'))

    lw = 214
    c.drawImage(white_logo(), PCX - lw / 2, 918, width=lw, height=lw * 146 / 375,
                mask='auto')
    L.place('logo', PCX - lw / 2, 918, lw, lw * 146 / 375, may_overlap=('panel',))

    words = ['AI', 'ENTREPRENEURSHIP', 'HACKATHON']
    size = min(fit(c, w, 'BC800', PW - 92, 74) for w in words)
    lh = size * 0.86
    top = 848
    for i, word in enumerate(words):
        c.setFont('BC800', size)
        c.setFillColorRGB(*(t['panel_accent'] if word == 'HACKATHON' else t['panel_fg']))
        c.drawCentredString(PCX, top - i * lh, word)
    L.place('wordmark', SPLIT + 46, top - 2 * lh - size * 0.24, PW - 92,
            2 * lh + size * 0.96, may_overlap=('panel',))

    side = 330
    draw_qr(c, PCX - side / 2, 322, side, t, L)

    # The circle straddles the split so the two halves read as one object.
    draw_circle(c, SPLIT, 214, 82, [('APPLY', 'BC800', 33, 31), ('NOW', 'BC800', 33, 31)], L)


def draw_qr(c, x, y, side, t, L):
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
    c.setFont('DM700', 16)
    c.setFillColorRGB(*t['panel_fg'])
    c.drawCentredString(x + side / 2, y - 30, 'SCAN TO APPLY')
    L.place('qr', x, y - 44, side, side + 44, may_overlap=('panel',))
    L.place('qrlabel', x, y - 44, side, 1, may_overlap=('panel', 'qr'))
    if mod < 6:
        WARNINGS.append(f'QR module {mod:.1f}px')


def draw_circle(c, cx, cy, r, lines, L):
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
                WARNINGS.append(f'circle {text!r} breaks the arc')
    L.place('applynow', cx - r, cy - r, 2 * r, 2 * r, may_overlap=('panel', 'qr'))


def head(c, t, L, eyebrow, lines, max_size=96, top=846):
    c.setFont('DM700', 18)
    c.setFillColorRGB(*t['accent'])
    c.drawString(MARGIN, top, eyebrow)
    L.text = getattr(L, 'text')
    L.place('eyebrow', MARGIN, top - 5, c.stringWidth(eyebrow, 'DM700', 18), 22)

    size = min(fit(c, s, 'BC800', DW, max_size) for s, _ in lines)
    lh = size * 0.84
    first = top - 46 - size * 0.72
    for i, (s, col) in enumerate(lines):
        c.setFont('BC800', size)
        c.setFillColorRGB(*col)
        c.drawString(MARGIN, first - i * lh, s)
    w = max(c.stringWidth(s, 'BC800', size) for s, _ in lines)
    L.place('headline', MARGIN, first - (len(lines) - 1) * lh - size * 0.24, w,
            (len(lines) - 1) * lh + size * 0.96)
    return first - (len(lines) - 1) * lh


DAYS = [
    ('FRI 23 OCT', 'EXAMPLE CAMPUS', 'Meet your team. Pick the problem. Start building.'),
    ('SAT 24 OCT', 'REMOTE',     'Build. Midday checkpoint, evening session with your mentor.'),
    ('SUN 25 OCT', 'REMOTE',     'Make it work. Feature freeze, then rehearse.'),
    ('MON 26 OCT', 'EXAMPLE CAMPUS', 'Demo live to the judges. Awards.'),
]

PITCH = ('Teams design, build and ship a working AI product in four days — '
         'on campus.')


def footer(c, t, L, text):
    c.setStrokeColorRGB(*t['rule'])
    c.setLineWidth(1)
    c.setStrokeAlpha(t['rule_a'])
    c.line(MARGIN, 108, SPLIT - 110, 108)
    c.setStrokeAlpha(1)
    c.setFont('DM500', 19)
    c.setFillColorRGB(*t['body'])
    c.drawString(MARGIN, 68, text)
    L.place('footer', MARGIN, 62, c.stringWidth(text, 'DM500', 19), 25)


# ============================================================== designs
def d_timeline(c, t, L):
    """A spine. The clearest way to show four days that are not all alike."""
    y = head(c, t, L, 'Example College’S FIRST AI ENTREPRENEURSHIP HACKATHON',
             [('BRING YOUR', t['fg']), ('WHAT IF.', t['accent'])])
    lines = para(c, PITCH, 'DM400', 24, MARGIN, y - 52, DW - 40, 34, t['body'])
    L.place('pitch', MARGIN, y - 52 - (len(lines) - 1) * 34 - 6, DW - 40,
            (len(lines) - 1) * 34 + 24)

    top, row = 524, 102
    c.setStrokeColorRGB(*t['accent'])
    c.setLineWidth(2)
    c.setStrokeAlpha(0.35)
    c.line(MARGIN + 7, top - 3 * row - 16, MARGIN + 7, top + 12)
    c.setStrokeAlpha(1)
    for i, (day, place, body) in enumerate(DAYS):
        ry = top - i * row
        c.setFillColorRGB(*t['accent'])
        c.circle(MARGIN + 7, ry + 10, 7, stroke=0, fill=1)
        c.setFont('BC800', 34)
        c.setFillColorRGB(*t['fg'])
        c.drawString(MARGIN + 34, ry, day)
        c.setFont('DM700', 13)
        c.setFillColorRGB(*t['accent'])
        c.drawString(MARGIN + 34 + c.stringWidth(day, 'BC800', 34) + 16, ry + 3, place)
        c.setFont('DM400', 17)
        c.setFillColorRGB(*t['body'])
        c.drawString(MARGIN + 34, ry - 26, body)
        L.place(f'day{i}', MARGIN, ry - 36, DW, 62)

    footer(c, t, L, 'APPLY BY 4 OCTOBER 2026  ·  FREE  ·  ALL SKILL LEVELS')


def d_numbers(c, t, L):
    """Three numbers and a sentence. Reads from the far end of a corridor."""
    y = head(c, t, L, 'FRIDAY 23 TO MONDAY 26 OCTOBER 2026',
             [('TEAMS COMPETE.', t['fg']), ('PRODUCTS SHIP.', t['accent'])])
    lines = para(c, PITCH, 'DM400', 24, MARGIN, y - 52, DW - 40, 34, t['body'])
    L.place('pitch', MARGIN, y - 52 - (len(lines) - 1) * 34 - 6, DW - 40,
            (len(lines) - 1) * 34 + 24)

    stats = [('4', 'DAYS', 'Two on campus,\nthe weekend remote'),
             ('1', 'TEAM', 'Built for you, mixed\non purpose'),
             ('1', 'PRODUCT', 'Working, demoed live\nto the judges')]
    cw, gap, cy, ch = 316, 24, 300, 232
    for i, (num, label, body) in enumerate(stats):
        cx = MARGIN + i * (cw + gap)
        c.setFillColorRGB(*t['card'])
        c.setFillAlpha(t['card_a'])
        c.roundRect(cx, cy, cw, ch, 6, stroke=0, fill=1)
        c.setFillAlpha(1)
        c.setFillColorRGB(*t['accent'])
        c.rect(cx, cy, 3, ch, stroke=0, fill=1)
        c.setFont('BC800', 96)
        c.drawString(cx + 24, cy + ch - 104, num)
        c.setFont('BC800', 34)
        c.setFillColorRGB(*t['fg'])
        c.drawString(cx + 24 + c.stringWidth(num, 'BC800', 96) + 14, cy + ch - 104, label)
        c.setFont('DM400', 16)
        c.setFillColorRGB(*t['body'])
        for j, line in enumerate(body.split('\n')):
            c.drawString(cx + 24, cy + ch - 146 - j * 23, line)
        L.place(f'stat{i}', cx, cy, cw, ch)

    dates = '  ·  '.join(d[0] for d in DAYS)
    c.setFont('DM700', 19)
    c.setFillColorRGB(*t['fg'])
    c.drawString(MARGIN, 228, dates)
    L.place('dates', MARGIN, 222, c.stringWidth(dates, 'DM700', 19), 25)
    footer(c, t, L, 'APPLY BY 4 OCTOBER 2026  ·  FREE  ·  NO CV  ·  ALL SKILL LEVELS')


def d_facts(c, t, L):
    """Two columns: what it is on the left, when it happens on the right."""
    y = head(c, t, L, 'EXAMPLE CAMPUS · 1 EXAMPLE STREET',
             [('DESIGN IT.', t['fg']), ('BUILD IT.', t['fg']),
              ('SHIP IT.', t['accent'])], max_size=84)
    lines = para(c, PITCH, 'DM400', 22, MARGIN, y - 48, 470, 31, t['body'])
    L.place('pitch', MARGIN, y - 48 - (len(lines) - 1) * 31 - 6, 470,
            (len(lines) - 1) * 31 + 22)

    facts = [('WHO IT IS FOR', 'Anyone who wants to build. Students and people from outside the college. No experience needed.'),
             ('WHAT YOU BUILD', 'An AI product a business would pay to use. An app, an agent, an automation — your team’s call.'),
             ('WHAT IT COSTS', 'Nothing. About three minutes to apply, ten short questions, no CV.')]
    fy = 470
    for i, (title, body) in enumerate(facts):
        c.setFont('BC800', 28)
        c.setFillColorRGB(*t['accent'])
        c.drawString(MARGIN, fy, title)
        bl = para(c, body, 'DM400', 16, MARGIN, fy - 26, 470, 22, t['body'])
        L.place(f'fact{i}', MARGIN, fy - 26 - (len(bl) - 1) * 22 - 6, 470,
                (len(bl) - 1) * 22 + 60)
        fy -= 26 + len(bl) * 22 + 34

    cx = MARGIN + 560
    c.setFont('BC800', 28)
    c.setFillColorRGB(*t['accent'])
    c.drawString(cx, 470, 'THE FOUR DAYS')
    L.place('dayshead', cx, 464, 300, 34)
    for i, (day, place, _) in enumerate(DAYS):
        ry = 424 - i * 62
        c.setFont('BC800', 30)
        c.setFillColorRGB(*t['fg'])
        c.drawString(cx, ry, day)
        c.setFont('DM400', 15)
        c.setFillColorRGB(*t['body'])
        c.drawString(cx, ry - 20, place)
        L.place(f'day{i}', cx, ry - 28, 300, 54)

    footer(c, t, L, 'APPLY BY 4 OCTOBER 2026')


DESIGNS = [('01-timeline', d_timeline), ('02-numbers', d_numbers), ('03-facts', d_facts)]


def main():
    for tn, base in THEMES.items():
        t = dict(base, name=tn)
        check(t['fg'], t['bg'], f'{tn}: headline')
        check(t['body'], t['bg'], f'{tn}: body', 4.0)
        check(t['accent'], t['bg'], f'{tn}: accent')
        check(t['panel_fg'], t['panel'], f'{tn}: panel text')
        check(t['panel_accent'], t['panel'], f'{tn}: panel accent')
        check(INK, CORAL, f'{tn}: coral circle')
        for slug, fn in DESIGNS:
            path = OUT / f'{slug}-{tn}.pdf'
            c = rl_canvas.Canvas(str(path), pagesize=(W, H))
            c.setTitle(f'Example College Hackathon — {slug} ({tn})')
            L = Layout(f'{slug}-{tn}')
            c.setFillColorRGB(*t['bg'])
            c.rect(0, 0, W, H, stroke=0, fill=1)
            c.setStrokeColorRGB(*t['rule'])
            c.setLineWidth(1)
            c.setStrokeAlpha(0.05)
            for i in range(1, 8):
                c.line(SPLIT * i / 8, 0, SPLIT * i / 8, H)
            c.setStrokeAlpha(1)
            panel(c, t, L)
            fn(c, t, L)
            c.showPage()
            c.save()
            WARNINGS.extend(L.problems)
            print(f'  {path.name:28} {len(L.boxes):2} elements, {len(L.problems)} overlap(s)')
    print()
    if WARNINGS:
        print('WARNINGS:')
        for w in dict.fromkeys(WARNINGS):
            print('  !', w)
    else:
        print('no warnings — contrast, arc, overlap and QR checks all pass')


if __name__ == '__main__':
    main()
