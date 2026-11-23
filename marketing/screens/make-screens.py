#!/usr/bin/env python3
"""Floor-screen artwork: 16:9, three designs, each in two palettes.

    python marketing/screens/make-screens.py
"""
import math, pathlib
import segno
from layout import Layout
from PIL import Image, ImageOps
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parents[1] / 'output' / 'marketing' / 'screens'
OUT.mkdir(parents=True, exist_ok=True)
PROJ = HERE.parents[1]
FONTS = PROJ / 'brand' / 'fonts'
CACHE = OUT / '_cache'
CACHE.mkdir(exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1920, 1080                                    # 16:9, 1pt == 1px here

INK    = (0x12/255, 0x13/255, 0x16/255)
PAPER  = (0xf2/255, 0xf1/255, 0xe9/255)
ACCENT = (0x7e/255, 0x98/255, 0xff/255)              # lifted blue, for dark grounds
BRAND  = (0x14/255, 0x1a/255, 0x9d/255)              # college indigo, for cream grounds
CORAL  = (0xff/255, 0x70/255, 0x4b/255)
MUTED  = (0xae/255, 0xb1/255, 0xb9/255)
SLATE  = (0x4a/255, 0x4d/255, 0x55/255)
GLOW   = (0x1b/255, 0x1d/255, 0x42/255)

URL = 'https://example.org/hackathon/#apply'

THEMES = {
    'dark': dict(bg=INK,   fg=PAPER, accent=ACCENT, body=MUTED, glow=GLOW,
                 bar=ACCENT, barfg=INK, logo='white', grid=(1, 1, 1), grid_a=0.035,
                 rule=(1, 1, 1), rule_a=0.14, card=(1, 1, 1), card_a=0.05),
    'college': dict(bg=PAPER, fg=INK,   accent=BRAND,  body=SLATE, glow=None,
                 bar=BRAND,  barfg=PAPER, logo='blue', grid=(0, 0, 0), grid_a=0.05,
                 rule=(0, 0, 0), rule_a=0.14, card=(0, 0, 0), card_a=0.04),
}

for w in (600, 700, 800):
    pdfmetrics.registerFont(TTFont(f'BC{w}', FONTS / f'BarlowCondensed-{w}.ttf'))
for w in (400, 500, 700):
    pdfmetrics.registerFont(TTFont(f'DM{w}', FONTS / f'DMSans-{w}.ttf'))

WARNINGS = []


# ------------------------------------------------------------------ colour
def luminance(c):
    f = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * f[0] + 0.7152 * f[1] + 0.0722 * f[2]


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def check_contrast(fg, bg, label, floor=4.5):
    r = contrast(fg, bg)
    if r < floor:
        WARNINGS.append(f'{label}: contrast {r:.2f} (needs {floor})')
    return r


# ------------------------------------------------------------------ assets
def logo_for(theme):
    """White on dark, original blue on cream — never the other way round."""
    src = PROJ / 'website/assets/logo.png'
    if THEMES[theme]['logo'] == 'blue':
        return ImageReader(str(src))
    dst = CACHE / 'logo-white.png'
    if not dst.exists():
        im = Image.open(src).convert('RGBA')
        a = im.split()[3]
        white = Image.new('L', im.size, 255)
        Image.merge('RGBA', (white, white, white, a)).save(dst)
    return ImageReader(str(dst))


def portrait(name, zoom=1.0, ybias=0.82, px=360):
    """Square, greyscale, centre-cropped. Portraits stay black and white at all
    times — that is an identity rule, not a stylistic choice here."""
    dst = CACHE / f'p-{name}-{zoom}-{ybias}.png'
    if not dst.exists():
        src = next((PROJ / 'website' / 'assets' / 'people').glob(f'{name}.*'))
        im = Image.open(src).convert('L')
        w, h = im.size
        side = min(w, h) / zoom
        top = (h - side) / 2 * ybias
        im = im.crop((int((w - side) / 2), int(top),
                      int((w + side) / 2), int(top + side)))
        im.resize((px, px), Image.LANCZOS).save(dst)
    return ImageReader(str(dst))


def scrim(theme):
    """A left-to-right alpha ramp in the ground colour, so type over a
    photograph always has the same contrast wherever the picture is bright.

    Built as an image rather than stacked rectangles: overlapping rects
    accumulate alpha unevenly and leave a hard vertical seam where the widest
    one ends, which is exactly what the first version of this did."""
    dst = CACHE / f'scrim-{theme}.png'
    if not dst.exists():
        base = tuple(int(v * 255) for v in THEMES[theme]['bg'])
        grad = Image.new('RGBA', (W, 1))
        for x in range(W):
            k = (x / W - 0.28) / 0.52              # 0 at 28% across, 1 at 80%
            k = max(0.0, min(1.0, k))
            grad.putpixel((x, 0), base + (int(238 * (1 - k ** 0.85)),))
        grad.resize((W, H), Image.NEAREST).save(dst)
    return ImageReader(str(dst))


def backdrop(theme, name, darken):
    """A Example Campus photograph, desaturated and pushed under an indigo wash so it reads
    as ground rather than picture. Only used on the dark palette: on cream a
    photograph fights the type instead of supporting it."""
    if THEMES[theme]['bg'] != INK:
        return None
    dst = CACHE / f'bg-{name}-{darken}.jpg'
    if not dst.exists():
        src = next((PROJ / 'sample-data' / 'photos').glob(f'{name}*'))
        im = Image.open(src).convert('RGB')
        im = ImageOps.fit(im, (W, H), Image.LANCZOS)
        im = ImageOps.grayscale(im).convert('RGB')
        wash = Image.new('RGB', im.size, tuple(int(v * 255) for v in GLOW))
        im = Image.blend(im, wash, darken)
        im.save(dst, quality=88)
    return ImageReader(str(dst))


# ------------------------------------------------------------------- text
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
    c.setFont(font, size)
    c.setFillColorRGB(*colour)
    for i, line in enumerate(wrap(c, text, font, size, width)):
        c.drawString(x, y - i * leading, line)
    return y - (len(wrap(c, text, font, size, width)) - 1) * leading


# --------------------------------------------------------------------- QR
def draw_qr(c, x, y, side, t, L, label='SCAN TO APPLY'):
    """Always dark modules on a light panel, in both palettes. An inverted code
    is refused by a minority of scanners, and a screen in a corridor gets one
    attempt."""
    qr = segno.make(URL, error='h')
    m = [list(r) for r in qr.matrix]
    n, border = len(m), 4
    mod = side / (n + border * 2)

    c.setFillColorRGB(1, 1, 1)
    c.setStrokeColorRGB(*t['rule'])
    c.setStrokeAlpha(0.22)
    c.setLineWidth(1.5)
    c.roundRect(x, y, side, side, 8, stroke=1, fill=1)
    c.setStrokeAlpha(1)
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

    c.setFont('DM700', 15)
    c.setFillColorRGB(*t['body'])
    c.drawCentredString(x + side / 2, y - 26, label)
    L.place('qr', x, y - 40, side, side + 40)
    # 6 px per module is the practical floor for a screen read across a lobby
    if mod < 6:
        WARNINGS.append(f'QR module {mod:.1f}px — small for a floor screen')
    return mod


# ------------------------------------------------------------------ stamp
def draw_stamp(c, cx, cy, r, lines):
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
                WARNINGS.append(f'stamp {text!r} breaks the arc')


# ------------------------------------------------------------------ shell
def shell(c, t, L, bg_img=None):
    c.setFillColorRGB(*t['bg'])
    c.rect(0, 0, W, H, stroke=0, fill=1)
    if bg_img is not None:
        c.drawImage(bg_img, 0, 0, W, H, mask=None)
        # A photograph is busiest exactly where the headline sits.
        c.drawImage(scrim(t['name']), 0, 0, W, H, mask='auto')
    elif t['glow']:
        for i in range(60, 0, -1):
            k = i / 60
            c.setFillColorRGB(*[t['bg'][j] + (t['glow'][j] - t['bg'][j]) * (1 - k) ** 2
                                for j in range(3)])
            c.circle(W * 0.34, H * 0.55, 760 * k, stroke=0, fill=1)

    c.setStrokeColorRGB(*t['grid'])
    c.setLineWidth(1)
    c.setStrokeAlpha(t['grid_a'])
    for i in range(1, 12):
        c.line(W * i / 12, 0, W * i / 12, H)
    for i in range(1, 7):
        c.line(0, H * i / 7, W, H * i / 7)
    c.setStrokeAlpha(1)

    lw = 190
    c.drawImage(logo_for(t['name']), 72, H - 118, width=lw, height=lw * 146 / 375,
                mask='auto')
    c.setStrokeColorRGB(*t['fg'])
    c.setLineWidth(1.4)
    c.setStrokeAlpha(0.5)
    c.line(72 + lw + 26, H - 116, 72 + lw + 42, H - 66)
    c.setStrokeAlpha(1)
    c.setFillColorRGB(*t['fg'])
    c.setFont('DM700', 12)
    c.drawString(72 + lw + 58, H - 80, 'AI ENTREPRENEURSHIP')
    c.setFont('BC800', 25)
    c.drawString(72 + lw + 58, H - 108, 'HACKATHON')

    L.place('logo', 72, H - 118, lw + 58 + 210, 74)
    # The circle is the call to action, not the date. The deadline still
    # appears in every footer below — "apply now" with no date gives nobody a
    # reason to do it today.
    draw_stamp(c, W - 132, H - 96, 66, [
        ('APPLY', 'BC800', 34, 32),
        ('NOW',   'BC800', 34, 32),
    ])
    L.place('stamp', W - 132 - 66, H - 96 - 66, 132, 132)


def footer(c, t, L, text):
    c.setStrokeColorRGB(*t['rule'])
    c.setLineWidth(1)
    c.setStrokeAlpha(t['rule_a'])
    c.line(72, 118, W - 72, 118)
    c.setStrokeAlpha(1)
    c.setFont('DM500', 20)
    c.setFillColorRGB(*t['body'])
    c.drawString(72, 74, text)
    L.text(c, 'footer-left', 72, 74, text, 'DM500', 20)
    c.setFont('DM700', 21)
    c.setFillColorRGB(*t['accent'])
    url = 'example.org/hackathon'
    c.drawRightString(W - 72, 74, url)
    L.text(c, 'footer-url', W - 72 - c.stringWidth(url, 'DM700', 21), 74, url, 'DM700', 21)


# ================================================================ designs
# Vertical grid shared by all three, so the set reads as a set:
#   header band  940-1080      logo lockup and coral stamp
#   eyebrow      baseline 856
#   headline     first baseline 754
#   footer rule  118, footer baseline 74
EYEBROW_Y, HEAD_Y = 856, 754


def heading(c, t, L, eyebrow, lines, max_w, max_size):
    c.setFont('DM700', 19)
    c.setFillColorRGB(*t['accent'])
    c.drawString(72, EYEBROW_Y, eyebrow)
    L.text(c, 'eyebrow', 72, EYEBROW_Y, eyebrow, 'DM700', 19)

    size = min(fit(c, s, 'BC800', max_w, max_size) for s, _ in lines)
    lh = size * 0.84
    for i, (text, col) in enumerate(lines):
        c.setFont('BC800', size)
        c.setFillColorRGB(*col)
        c.drawString(72, HEAD_Y - i * lh, text)
    L.lines(c, 'headline', 72, HEAD_Y, [s for s, _ in lines], 'BC800', size, lh)
    return HEAD_Y - (len(lines) - 1) * lh, size


def design_offer(c, t, L):
    """Answers "is this for me?" — the only question a lobby screen has time
    to answer."""
    shell(c, t, L, backdrop(t['name'], 'workspace', 0.82))
    heading(c, t, L, 'Example College\u2019S FIRST AI ENTREPRENEURSHIP HACKATHON',
            [('BRING AN IDEA.', t['fg']), ('OR JUST BRING', t['fg']),
             ('YOURSELF.', t['accent'])], 880, 100)

    intro = ('Four days building an AI product a business would pay to use. '
             'You do not need a team, an idea, or a line of code to start.')
    para(c, intro, 'DM400', 25, 72, 500, 880, 36, t['body'])
    L.lines(c, 'intro', 72, 500, wrap(c, intro, 'DM400', 25, 880), 'DM400', 25, 36)

    cards = [
        ('NO TEAM NEEDED', 'We build balanced teams for you. Builders, business minds and designers, mixed on purpose.'),
        ('NO CODE NEEDED', 'Every skill level is welcome. Beginners belong here \u2014 that is the whole point.'),
        ('NO COST',        'Free to apply. About three minutes, ten short questions, and no CV.'),
    ]
    cw, gap, cy, ch = 400, 32, 190, 230
    for i, (title, body) in enumerate(cards):
        cx = 72 + i * (cw + gap)
        c.setFillColorRGB(*t['card'])
        c.setFillAlpha(t['card_a'])
        c.roundRect(cx, cy, cw, ch, 6, stroke=0, fill=1)
        c.setFillAlpha(1)
        c.setFillColorRGB(*t['accent'])
        c.rect(cx, cy, 3, ch, stroke=0, fill=1)
        c.setFont('BC800', 32)
        c.setFillColorRGB(*t['fg'])
        c.drawString(cx + 26, cy + ch - 54, title)
        para(c, body, 'DM400', 17, cx + 26, cy + ch - 92, cw - 52, 25, t['body'])
        L.place(f'card{i}', cx, cy, cw, ch)

    draw_qr(c, W - 72 - 340, 450, 340, t, L)
    footer(c, t, L, '23\u201326 OCT 2026  \u00b7  EXAMPLE CAMPUS, LOHM\u00dcHLENSTRASSE 65  \u00b7  APPLY BY 4 OCT')


def design_days(c, t, L):
    """What actually happens. Removes the "what am I signing up for" objection
    the posters have no room to address."""
    shell(c, t, L)
    heading(c, t, L, 'FRIDAY 23 TO MONDAY 26 OCTOBER 2026',
            [('FOUR DAYS.', t['fg']), ('ONE WORKING', t['fg']),
             ('AI PRODUCT.', t['accent'])], 700, 92)

    note = 'Every team gets its own mentor for the whole event, and an OpenAI API key to build with.'
    para(c, note, 'DM400', 23, 72, 545, 700, 33, t['body'])
    L.lines(c, 'note', 72, 545, wrap(c, note, 'DM400', 23, 700), 'DM400', 23, 33)

    days = [
        ('01', 'FRI 23 OCT', 'ON CAMPUS', 'Meet your team. Pick the problem. Start building.'),
        ('02', 'SAT 24 OCT', 'REMOTE',    'Build, with a midday checkpoint and an evening session.'),
        ('03', 'SUN 25 OCT', 'REMOTE',    'Make it work. Feature freeze, then rehearse the demo.'),
        ('04', 'MON 26 OCT', 'ON CAMPUS', 'Demo live to the judging panel. Awards.'),
    ]
    cx0, cw, gap, cy, ch = 880, 232, 22, 250, 300
    for i, (num, day, place_, body) in enumerate(days):
        cx = cx0 + i * (cw + gap)
        c.setFillColorRGB(*t['card'])
        c.setFillAlpha(t['card_a'])
        c.roundRect(cx, cy, cw, ch, 6, stroke=0, fill=1)
        c.setFillAlpha(1)
        c.setFillColorRGB(*t['accent'])
        c.setFont('BC800', 58)
        c.drawString(cx + 22, cy + ch - 62, num)
        c.setFillColorRGB(*t['fg'])
        c.setFont('DM700', 17)
        c.drawString(cx + 22, cy + ch - 106, day)
        c.setFillColorRGB(*t['body'])
        c.setFont('DM500', 14)
        c.drawString(cx + 22, cy + ch - 128, place_)
        para(c, body, 'DM400', 16, cx + 22, cy + ch - 162, cw - 44, 23, t['body'])
        L.place(f'day{i}', cx, cy, cw, ch)

    draw_qr(c, 72, 190, 300, t, L)
    footer(c, t, L, 'EXAMPLE CAMPUS  \u00b7  ALL SKILL LEVELS  \u00b7  FREE TO APPLY  \u00b7  APPLY BY 4 OCT')


PEOPLE = [
    ('grace', 'Grace', 'MENTOR', 'AI Engineer', 1.0, 0.82),
    ('alan', 'Alan', 'MENTOR', 'Machine Learning Engineer', 1.0, 0.82),
    ('konrad', 'Konrad', 'MENTOR', 'Software Developer', 1.0, 0.82),
    ('katherine', 'Katherine', 'BUSINESS MENTOR & JUDGE', 'University Lecturer', 1.0, 0.82),
    ('dorothy', 'Dorothy', 'BUSINESS MENTOR & JUDGE', 'Business Consultant', 1.0, 0.82),
    ('ada', 'Ada', 'HACKATHON LEAD', 'Hackathon Lead', 1.0, 0.82),
    ('charles', 'Charles', 'JUDGE', 'College President', 1.0, 0.82),
    ('john', 'John', 'PANELIST & JUDGE', 'Keynote Speaker', 1.0, 0.82),
    ('emmy', 'Emmy', 'CEO', 'College CEO', 1.0, 0.82),
]


def design_people(c, t, L):
    """Nine faces. On a screen these do what a paragraph cannot: prove the
    mentoring is real and that senior people actually turn up."""
    shell(c, t, L)
    c.setFont('DM700', 19)
    c.setFillColorRGB(*t['accent'])
    c.drawString(72, EYEBROW_Y, 'MENTORS, JUDGES AND YOUR HOSTS')
    L.text(c, 'eyebrow', 72, EYEBROW_Y, 'MENTORS, JUDGES AND YOUR HOSTS', 'DM700', 19)

    size = 92
    c.setFont('BC800', size)
    c.setFillColorRGB(*t['fg'])
    c.drawString(72, HEAD_Y, 'THE PEOPLE IN')
    c.drawString(72, HEAD_Y - 78, 'YOUR ')
    w0 = c.stringWidth('YOUR ', 'BC800', size)
    c.setFillColorRGB(*t['accent'])
    c.drawString(72 + w0, HEAD_Y - 78, 'CORNER.')
    L.lines(c, 'headline', 72, HEAD_Y, ['THE PEOPLE IN', 'YOUR CORNER.'], 'BC800', size, 78)

    note = 'Every team is assigned a mentor for the whole four days.'
    para(c, note, 'DM400', 23, 800, 700, 700, 33, t['body'])
    L.lines(c, 'note', 800, 700, wrap(c, note, 'DM400', 23, 700), 'DM400', 23, 33)

    n = len(PEOPLE)
    gap = 14
    cell = (W - 144 - gap * (n - 1)) / n
    top = 560
    for i, (slug, name, role, title, zoom, ybias) in enumerate(PEOPLE):
        px = 72 + i * (cell + gap)
        c.drawImage(portrait(slug, zoom, ybias), px, top - cell, cell, cell, mask=None)
        c.setFont('BC800', 30)
        c.setFillColorRGB(*t['fg'])
        c.drawString(px, top - cell - 34, name)
        role_lines = wrap(c, role, 'DM700', 10.5, cell)
        c.setFont('DM700', 10.5)
        c.setFillColorRGB(*t['accent'])
        for j, line in enumerate(role_lines):
            c.drawString(px, top - cell - 54 - j * 14, line)
        title_top = top - cell - 54 - len(role_lines) * 14 - 8
        title_lines = wrap(c, title, 'DM400', 11, cell)
        c.setFont('DM400', 11)
        c.setFillColorRGB(*t['body'])
        for j, line in enumerate(title_lines):
            c.drawString(px, title_top - j * 14, line)
        bottom = title_top - (len(title_lines) - 1) * 14 - 4
        L.place(f'person{i}', px, bottom, cell, top - bottom)

    draw_qr(c, W - 72 - 300, 600, 300, t, L)

    c.setFont('BC800', 44)
    c.setFillColorRGB(*t['fg'])
    c.drawString(72, 195, 'ALL SKILL LEVELS WELCOME.')
    L.text(c, 'strap', 72, 195, 'ALL SKILL LEVELS WELCOME.', 'BC800', 44)
    sub = 'Free to apply \u00b7 About three minutes \u00b7 No CV \u00b7 23\u201326 October 2026, Example Campus'
    c.setFont('DM400', 20)
    c.setFillColorRGB(*t['body'])
    c.drawString(72, 158, sub)
    L.text(c, 'strapsub', 72, 158, sub, 'DM400', 20)
    footer(c, t, L, 'APPLY BY 4 OCTOBER 2026')


DESIGNS = [('01-opportunity', design_offer),
           ('02-four-days', design_days),
           ('03-the-people', design_people)]


def main():
    for theme_name, t in THEMES.items():
        t = dict(t, name=theme_name)
        check_contrast(t['fg'], t['bg'], f'{theme_name}: headline')
        check_contrast(t['body'], t['bg'], f'{theme_name}: body', 4.0)
        check_contrast(t['accent'], t['bg'], f'{theme_name}: accent')
        check_contrast(t['barfg'], t['bar'], f'{theme_name}: cta bar')
        for slug, fn in DESIGNS:
            path = OUT / f'{slug}-{theme_name}.pdf'
            c = rl_canvas.Canvas(str(path), pagesize=(W, H))
            c.setTitle(f'Example College Hackathon — {slug} ({theme_name})')
            L = Layout(f'{slug}-{theme_name}')
            fn(c, t, L)
            c.showPage()
            c.save()
            WARNINGS.extend(L.problems)
            print(f'  {path.name:34} {len(L.boxes)} elements, '
                  f'{len(L.problems)} overlap(s)')

    print()
    if WARNINGS:
        print('WARNINGS:')
        for w in dict.fromkeys(WARNINGS):
            print('  !', w)
    else:
        print('no warnings — contrast, arc and QR checks all pass')


if __name__ == '__main__':
    main()
