#!/usr/bin/env python3
"""A demo-table set: three messages, the same four printable pieces each, with a QR code and the event details.

    python marketing/event-table/make-table-set.py
"""
import pathlib

import segno
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as rl_canvas

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parents[1] / 'output' / 'marketing' / 'event-table'
OUT.mkdir(parents=True, exist_ok=True)
PROJ = HERE.parents[1]
FONTS = PROJ / 'brand' / 'fonts'
W, H = A4

URL = 'https://example.org/hackathon/#apply'
SITE = 'example.org/hackathon'
# Two messages, each built as the same four pieces. `split` is how many headline
# lines take the first colour; the rest take the accent. Both headlines are
# approved lines: the provocation set, and Instagram carousel A.
MESSAGES = {
    '': dict(
        head=('AI TAKES JOBS?', 'THEN TAKE', 'THE BUSINESS.'), split=1,
        sub='Four days. Your team. A working AI product.',
        promise='You do not need a team, an idea or coding skills. Bring your curiosity.'),
    'industry-': dict(
        head=('INDUSTRY', 'CONNECTED', 'AI HACKATHON.'), split=2,
        sub='Four days. Your team. Mentors and judges from industry.',
        promise='Build a working AI product with people from companies building AI. No experience needed.'),
    # The wording of the TV cards on the Example Campus floors, word for word: headline, two
    # lines, and the footer line in place of the date line and the address bar.
    'whatif-': dict(
        head=('WHAT IF YOU', 'BUILT IT?'), split=1,
        sub='Bring your what if. Build it with your team, here.',
        promise='Four days. Your team. A working AI product. From 23 October at Example Campus.',
        promise_on_dark=True,
        flyer_details=('Four days. Your team. A working AI product.', 'From 23 October at Example Campus.'),
        footer=('EXAMPLE.ORG/HACKATHON', 'ALL SKILL LEVELS WELCOME')),
}
HEAD, SPLIT, SUB, PROMISE, M = (), 1, '', '', {}     # set by use() before each piece is drawn


def use(prefix):
    global HEAD, SPLIT, SUB, PROMISE, M
    M = MESSAGES[prefix]
    HEAD, SPLIT, SUB, PROMISE = M['head'], M['split'], M['sub'], M['promise']


FACTS = '23–26 OCT 2026  ·  EXAMPLE CAMPUS  ·  ALL SKILL LEVELS WELCOME'


def rgb(h):
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


INK, PAPER, WHITE = rgb('121316'), rgb('f2f1e9'), (1, 1, 1)
ACCENT, BRAND = rgb('7e98ff'), rgb('141a9d')
MUTED, SLATE, GLOW, EDGE = rgb('aeb1b9'), rgb('4f525a'), rgb('1b1d42'), rgb('dcdad0')

THEME = {
    'dark': dict(ground=INK, head=(PAPER, ACCENT), strong=PAPER, text=MUTED, call=PAPER, link=ACCENT,
                 logo=PROJ / 'brand' / 'logos' / 'logo-white.png', qr_panel=PAPER),
    'light': dict(ground=PAPER, head=(INK, BRAND), strong=INK, text=SLATE, call=BRAND, link=INK,
                  logo=PROJ / 'website/assets/logo.png', qr_panel=WHITE),
}
VENUE = PROJ / 'brand' / 'logos' / 'partner-mark.png'

for w in (700, 800):
    pdfmetrics.registerFont(TTFont(f'BC{w}', FONTS / f'BarlowCondensed-{w}.ttf'))
for w in (400, 500, 700):
    pdfmetrics.registerFont(TTFont(f'DM{w}', FONTS / f'DMSans-{w}.ttf'))

NOTES = []


# ------------------------------------------------------------------ helpers
def width(text, font, size, track=0):
    return pdfmetrics.stringWidth(text, font, size) + track * max(0, len(text) - 1)


def fit(text, font, target, start, track=0, floor=5):
    size = start
    while size > floor and width(text, font, size, track) > target:
        size -= 0.1
    return size


def say(c, x, y, text, font, size, colour, align='l', track=0):
    """One line of text. Letter-spacing is reset afterwards: it is graphics
    state, and left set it widens every string drawn after this one."""
    w = width(text, font, size, track)
    x = x - w if align == 'r' else x - w / 2 if align == 'c' else x
    t = c.beginText(x, y)
    t.setFont(font, size)
    t.setFillColorRGB(*colour)
    t.setCharSpace(track)
    t.textOut(text)
    t.setCharSpace(0)
    c.drawText(t)
    return w


def qr(c, x, y, side, panel, radius, what):
    """The application QR as vector modules on a light panel, dark on light."""
    matrix = [list(r) for r in segno.make(URL, error='h').matrix]
    n, quiet = len(matrix), 4
    mod = side / (n + quiet * 2)
    c.setFillColorRGB(*panel)
    c.roundRect(x, y, side, side, radius, stroke=0, fill=1)
    c.setFillColorRGB(*INK)
    for r, row in enumerate(matrix):
        run = None
        for col in range(n + 1):
            on = col < n and row[col]
            if on and run is None:
                run = col
            elif not on and run is not None:
                c.rect(x + (quiet + run) * mod, y + side - (quiet + r + 1) * mod,
                       (col - run) * mod, mod, stroke=0, fill=1)
                run = None
    module_mm = mod / mm
    NOTES.append(f'{what}: QR {side / mm:.0f} mm, module {module_mm:.2f} mm'
                 + ('' if module_mm >= 0.6 else '   <-- BELOW THE 0.6 mm SCANNING FLOOR'))


def lockup(c, x, top, logo_w, th):
    """Example College logo · slanted divider · AI ENTREPRENEURSHIP / HACKATHON."""
    k = logo_w / 118
    lh = logo_w * 146 / 375
    c.drawImage(ImageReader(str(th['logo'])), x, top - lh, logo_w, lh, mask='auto')
    c.setStrokeColorRGB(*th['text'])
    c.setLineWidth(max(0.5, 0.9 * k))
    c.line(x + logo_w + 17 * k, top - lh + 2 * k, x + logo_w + 27 * k, top - lh + 34 * k)
    tx = x + logo_w + 36 * k
    say(c, tx, top - lh + 25 * k, 'AI ENTREPRENEURSHIP', 'DM700', 7.6 * k, th['strong'])
    say(c, tx, top - lh + 8 * k, 'HACKATHON', 'BC800', 15 * k, th['strong'])
    return top - lh + lh * (146 - 74.5) / 146          # the logo's optical centre line


def cic_credit(c, right, cy, mark_h, th):
    mark_w = mark_h * 1522 / 1250
    c.drawImage(ImageReader(str(VENUE)), right - mark_w, cy - mark_h / 2, mark_w, mark_h, mask='auto')
    lab = mark_h * 0.145
    say(c, right - mark_w - mark_h * 0.24, cy - lab * 0.36, 'POWERED BY', 'DM700', lab, th['strong'], 'r', track=lab * 0.17)


def headline(c, x, cap_top, size, th, align):
    """Returns the baseline of the last line."""
    y = cap_top - 0.72 * size
    for i, line in enumerate(HEAD):
        say(c, x, y, line, 'BC800', size, th['head'][0 if i < SPLIT else 1], align)
        if i < len(HEAD) - 1:
            y -= 0.83 * size
    return y


def glow(c, cx, cy, r):
    """Indigo glow from concentric discs: survives any printer, unlike a mesh."""
    for i in range(60, 0, -1):
        t = i / 60
        c.setFillColorRGB(*[INK[k] + (GLOW[k] - INK[k]) * (1 - t) ** 2 for k in range(3)])
        c.circle(cx, cy, r * t, stroke=0, fill=1)


# ------------------------------------------------------- poster 1, dark
def poster_dark(c):
    th = THEME['dark']
    c.setFillColorRGB(*INK)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    glow(c, W / 2, H * 0.60, 330)
    cy = lockup(c, 48, H - 50, 118, th)
    cic_credit(c, W - 48, cy, 46, th)

    # bottom up: address bar, facts, APPLY NOW, the code
    if M.get('footer'):
        line = '   •   '.join(M['footer'])
        say(c, W / 2, 58, line, 'DM700', fit(line, 'DM700', W - 96, 12, track=0.8), PAPER, 'c', track=0.8)
        call_y, qy = 92, 128
    else:
        bar_w, bar_h = 330, 40
        c.setFillColorRGB(*ACCENT)
        c.roundRect((W - bar_w) / 2, 40, bar_w, bar_h, 4, stroke=0, fill=1)
        say(c, W / 2, 53, SITE, 'DM700', 15, INK, 'c')
        say(c, W / 2, 96, FACTS, 'DM500', 10.2, MUTED, 'c')
        call_y, qy = 124, 160
    say(c, W / 2, call_y, 'APPLY NOW', 'BC800', 31, PAPER, 'c', track=0.6)
    side = 228
    qr(c, (W - side) / 2, qy, side, th['qr_panel'], 10, 'poster 1')

    # the headline takes what is left, between the logo band and the code
    cap_top, sub_drop, gap = 702, 31, 34
    more = 23 if M.get('promise_on_dark') else 0            # a second line under the first
    band = cap_top - (qy + side + gap)
    size = min(min(fit(t, 'BC800', W - 96, 124) for t in HEAD),
               (band - sub_drop - more) / (0.72 + 0.83 * (len(HEAD) - 1)))
    block = (0.72 + 0.83 * (len(HEAD) - 1)) * size + sub_drop + more
    last = headline(c, W / 2, cap_top - (band - block) / 2, size, th, 'c')
    if more:
        say(c, W / 2, last - sub_drop, SUB, 'DM700', fit(SUB, 'DM700', W - 96, 16.5), PAPER, 'c')
        say(c, W / 2, last - sub_drop - more, PROMISE, 'DM400', fit(PROMISE, 'DM400', W - 96, 13.4), MUTED, 'c')
    else:
        say(c, W / 2, last - sub_drop, SUB, 'DM500', fit(SUB, 'DM500', W - 96, 15.5), MUTED, 'c')
    NOTES.append(f'poster 1: headline {size:.0f} pt')


def panel_text(c, x, mid, lines):
    """The words beside a code, as one block centred on the code's middle.
    Each line: (text, font, size, colour, tracking, cap height, space after)."""
    total = sum(cap + after for *_, cap, after in lines)
    y = mid + total / 2
    for text, font, size, colour, track, cap, after in lines:
        y -= cap
        if text is None:
            w = say(c, x, y, 'or go to ', 'DM400', size, MUTED)
            say(c, x + w, y, SITE, 'DM700', size, PAPER)
        else:
            say(c, x, y, text, font, size, colour, track=track)
        y -= after


# ------------------------------------------------------ poster 2, light
def poster_light(c):
    th = THEME['light']
    c.setFillColorRGB(*PAPER)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    cy = lockup(c, 48, H - 50, 118, th)
    cic_credit(c, W - 48, cy, 46, th)

    # the apply panel: dark, full width, code on the left and the words beside it
    ph = 282
    c.setFillColorRGB(*INK)
    c.rect(0, 0, W, ph, stroke=0, fill=1)
    side = 198
    qx, qy = 48, (ph - side) / 2
    qr(c, qx, qy, side, WHITE, 10, 'poster 2')
    tx = qx + side + 34
    room = W - 48 - tx
    call = fit('APPLY NOW', 'BC800', room, 70, track=0.8)
    f_size = fit(FACTS, 'DM500', room, 9.6, floor=7.5)
    lines = [('SCAN THE CODE', 'DM700', 8.2, ACCENT, 2.3, 0.72 * 8.2, 13),
             ('APPLY NOW', 'BC800', call, PAPER, 0.8, 0.70 * call, 19),
             (None, None, 12.8, None, 0, 0.52 * 12.8, 14),          # "or go to <address>"
             (FACTS, 'DM500', f_size, MUTED, 0, 0.70 * f_size, 0)]
    if M.get('footer'):
        a, b = M['footer']
        a_size = fit(a, 'DM700', room, 13, track=0.7)
        lines[2:] = [(a, 'DM700', a_size, PAPER, 0.7, 0.70 * a_size, 13),
                     (b, 'DM500', 9.6, MUTED, 0.9, 0.70 * 9.6, 0)]
    panel_text(c, tx, qy + side / 2, lines)

    # headline, left, in the cream field between the logo band and the panel
    size = min(fit(t, 'BC800', W - 96, 126) for t in HEAD)
    p_size = fit(PROMISE, 'DM400', W - 96, 13.6)
    block = (0.72 + 0.83 * (len(HEAD) - 1)) * size + 36 + 24
    top, bottom = H - 122, ph
    cap_top = top - (top - bottom - block) * 0.46
    last = headline(c, 48, cap_top, size, th, 'l')
    say(c, 50, last - 36, SUB, 'DM700', fit(SUB, 'DM700', W - 98, 17), INK)
    say(c, 50, last - 60, PROMISE, 'DM400', p_size, SLATE)
    NOTES.append(f'poster 2: headline {size:.0f} pt, {last - 60 - ph:.0f} pt of air above the apply panel')


# ----------------------------------------------------------- one flyer card
CARD_W, CARD_H = 93 * mm, 136.5 * mm


def flyer(c, x, y, mode):
    th = THEME[mode]
    c.saveState()
    c.translate(x, y)
    clip = c.beginPath()
    clip.roundRect(0, 0, CARD_W, CARD_H, 9)
    c.clipPath(clip, stroke=0, fill=0)
    c.setFillColorRGB(*th['ground'])
    c.rect(0, 0, CARD_W, CARD_H, stroke=0, fill=1)
    if mode == 'dark':
        glow(c, CARD_W / 2, CARD_H * 0.62, 150)
    m = 17
    lockup(c, m, CARD_H - m, 78, th)

    size = min(fit(t, 'BC800', CARD_W - 2 * m, 60) for t in HEAD)
    last = headline(c, CARD_W / 2, CARD_H - 64, size, th, 'c')
    say(c, CARD_W / 2, last - 17, SUB, 'DM500', fit(SUB, 'DM500', CARD_W - 2 * m, 8.9), th['strong'], 'c')
    low = last - 29.5                                  # baseline of the lowest line under the headline
    if M.get('flyer_details'):
        for i, line in enumerate(M['flyer_details']):
            low = last - 30 - i * 11.4
            say(c, CARD_W / 2, low, line, 'DM500', fit(line, 'DM500', CARD_W - 2 * m, 7.8), th['text'], 'c')
    else:
        f_size = fit(FACTS, 'DM500', CARD_W - 2 * m, 6.7, track=0.15)
        say(c, CARD_W / 2, low, FACTS, 'DM500', f_size, th['text'], 'c', track=0.15)

    # bottom up: address, APPLY NOW, the code. The code takes the room that is left.
    if M.get('footer'):
        line = '  •  '.join(M['footer'])
        say(c, CARD_W / 2, 17, line, 'DM700', fit(line, 'DM700', CARD_W - 2 * m, 7.4, track=0.25), th['link'], 'c',
            track=0.25)
    else:
        say(c, CARD_W / 2, 17, SITE, 'DM700', 8.8, th['link'], 'c')
    say(c, CARD_W / 2, 33, 'APPLY NOW', 'BC800', 18, th['call'], 'c', track=0.4)
    q_bottom = 33 + 0.70 * 18 + 9
    side = min(120, (low - 13) - q_bottom)
    qr(c, (CARD_W - side) / 2, q_bottom + ((low - 13) - q_bottom - side) / 2, side, th['qr_panel'], 6,
       f'flyer ({mode})')
    c.restoreState()
    if mode == 'light':                                # cream on white needs an edge to cut a shape out of the sheet
        c.setStrokeColorRGB(*EDGE)
        c.setLineWidth(0.6)
        c.roundRect(x, y, CARD_W, CARD_H, 9, stroke=1, fill=0)
    return size


def flyer_sheet(c, mode):
    margin, gutter = 6 * mm, 12 * mm                   # a centre cut leaves 6 mm of white on every side
    for row in range(2):
        for col in range(2):
            size = flyer(c, margin + col * (CARD_W + gutter), margin + row * (CARD_H + gutter), mode)
    # where to cut: once down, once across
    c.setStrokeColorRGB(0.62, 0.62, 0.62)
    c.setLineWidth(0.4)
    c.setDash(1.2, 3)
    c.line(W / 2, 5 * mm, W / 2, H - 5 * mm)
    c.line(5 * mm, H / 2, W - 5 * mm, H / 2)
    c.setDash()
    NOTES.append(f'flyer ({mode}): card {CARD_W / mm:.0f} x {CARD_H / mm:.1f} mm, headline {size:.0f} pt')


# ------------------------------------------------- the all-in-one A4 poster
def wrap(text, font, size, room):
    out, line = [], ''
    for word in text.split():
        trial = (line + ' ' + word).strip()
        if line and width(trial, font, size) > room:
            out.append(line)
            line = word
        else:
            line = trial
    return out + [line]


ALL = dict(
    hero=('WHAT IF YOU', 'BUILT IT?'),
    sub='Bring your what if. Build it with your team, here.',
    detail='Four days. Your team. A working AI product. From 23 October at Example Campus.',
    # (line, 0 = first colour / 1 = accent), then the sentence under it
    statements=[((('AI TAKES JOBS?', 0), ('THEN TAKE', 1), ('THE BUSINESS.', 1)),
                 'Build an AI product a business would actually pay for.'),
                ((('INDUSTRY', 0), ('CONNECTED', 0), ('AI HACKATHON.', 1)),
                 'With mentors and judges from companies building AI.')],
    facts=[('WHEN', '23–26 October 2026', 'Friday to Monday'),
           ('WHERE', 'Example Campus', '1 Example Street'),
           ('WHO', 'All skill levels', 'No team or idea needed'),
           ('WITH', 'Your own mentor', 'Judges from industry')],
    footer=('EXAMPLE.ORG/HACKATHON', 'ALL SKILL LEVELS WELCOME'),
)


def poster_all(c, mode):
    """Everything on one A4: the three headlines, the facts, the code.
    One big idea at the top, the other two as a pair under it, then what a
    reader needs to decide, then the one thing to do."""
    th, v = THEME[mode], ALL
    left, cw = 48, W - 96
    c.setFillColorRGB(*th['ground'])
    c.rect(0, 0, W, H, stroke=0, fill=1)
    if mode == 'dark':
        glow(c, W * 0.42, H * 0.66, 340)
    cy = lockup(c, 48, H - 50, 118, th)
    cic_credit(c, W - 48, cy, 46, th)

    # ---- measure every block first, then share the spare height between them
    s1 = min(fit(t, 'BC800', cw, 100) for t in v['hero'])
    h_hero = (0.72 + 0.83) * s1 + 30 + 21 + 3
    gutter = 30
    col = (cw - gutter) / 2
    s2 = min(fit(t, 'BC800', col, 46) for lines, _ in v['statements'] for t, _ in lines)
    n_size, n_lead = 10.6, 14.4
    notes = [wrap(n, 'DM400', n_size, col) for _, n in v['statements']]
    h_stmt = (0.72 + 2 * 0.86) * s2 + 15 + n_size * 0.75 + (max(map(len, notes)) - 1) * n_lead + 3
    h_facts = 17 + 15.5 + 13 + 3
    side = 172
    panel = side + 56 if mode == 'light' else 0        # light: the code sits in a dark panel, to the paper's edge
    h_cta, bottom = (panel, 0) if mode == 'light' else (side, 52)
    top = H - 124
    g = (top - bottom - h_hero - h_stmt - h_facts - h_cta) / 3
    assert g >= 18, f'all-in-one ({mode}): only {g:.0f} pt between blocks'

    # ---- the big one
    y = top - 0.72 * s1
    say(c, left, y, v['hero'][0], 'BC800', s1, th['head'][0])
    y -= 0.83 * s1
    say(c, left, y, v['hero'][1], 'BC800', s1, th['head'][1])
    say(c, left + 2, y - 30, v['sub'], 'DM700', fit(v['sub'], 'DM700', cw, 16.5), th['strong'])
    say(c, left + 2, y - 51, v['detail'], 'DM400', fit(v['detail'], 'DM400', cw - 2, 12.8), th['text'])
    y = y - 51 - 3 - g

    # ---- the other two, side by side
    for i, ((lines, _), note) in enumerate(zip(v['statements'], notes)):
        x = left + i * (col + gutter)
        b = y - 0.72 * s2
        for j, (text, k) in enumerate(lines):
            say(c, x, b - j * 0.86 * s2, text, 'BC800', s2, th['head'][k])
        b = b - 2 * 0.86 * s2 - 15 - n_size * 0.75
        for j, line in enumerate(note):
            say(c, x + 1, b - j * n_lead, line, 'DM400', n_size, th['text'])
    c.setStrokeColorRGB(*th['text'])
    c.setStrokeAlpha(0.35)
    c.setLineWidth(0.6)
    c.line(left + col + gutter / 2 - 4, y - 2, left + col + gutter / 2 - 4, y - h_stmt + 2)
    y -= h_stmt + g

    # ---- what a reader needs to decide
    c.line(left, y, left + cw, y)
    c.setStrokeAlpha(1)
    fgap = 16
    fw = (cw - fgap * 3) / 4
    for i, (label, a, b) in enumerate(v['facts']):
        x = left + i * (fw + fgap)
        say(c, x, y - 17, label, 'DM700', 6.8, th['head'][1], track=1.4)
        say(c, x, y - 32.5, a, 'DM700', fit(a, 'DM700', fw, 10.4), th['strong'])
        say(c, x, y - 45.5, b, 'DM400', fit(b, 'DM400', fw, 9.4), th['text'])
    y -= h_facts + g

    # ---- the one thing to do
    if mode == 'light':
        c.setFillColorRGB(*INK)
        c.rect(0, 0, W, panel, stroke=0, fill=1)
        qy = 28
    else:
        qy = bottom
    qr(c, left, qy, side, WHITE if mode == 'light' else PAPER, 10, f'all-in-one ({mode})')
    tx = left + side + 32
    room = W - 48 - tx
    call = fit('APPLY NOW', 'BC800', room, 70, track=0.8)
    a, b = v['footer']
    a_size = fit(a, 'DM700', room, 13, track=0.7)
    panel_text(c, tx, qy + side / 2, [
        ('SCAN THE CODE', 'DM700', 8.2, ACCENT, 2.3, 0.72 * 8.2, 13),
        ('APPLY NOW', 'BC800', call, PAPER, 0.8, 0.70 * call, 19),
        (a, 'DM700', a_size, PAPER, 0.7, 0.70 * a_size, 13),
        (b, 'DM500', 9.6, MUTED, 0.9, 0.70 * 9.6, 0)])
    NOTES.append(f'all-in-one ({mode}): big headline {s1:.0f} pt, pair {s2:.0f} pt, {g:.0f} pt between blocks')


# -------------------------------------------------------------------- build
PIECES = [('poster-1-dark-A4', poster_dark, 'Poster, dark'),
          ('poster-2-light-A4', poster_light, 'Poster, light'),
          ('flyers-4up-dark-A4', lambda c: flyer_sheet(c, 'dark'), 'Flyers, four on a sheet, dark'),
          ('flyers-4up-light-A4', lambda c: flyer_sheet(c, 'light'), 'Flyers, four on a sheet, light')]

if __name__ == '__main__':
    jobs = [(pre, pre + s, d, t) for pre in MESSAGES for s, d, t in PIECES]
    jobs += [('whatif-', f'all-in-one-poster-{mode}-A4', lambda c, mode=mode: poster_all(c, mode),
              f'All-in-one poster, {mode}') for mode in ('dark', 'light')]
    for prefix, slug, draw, title in jobs:
        use(prefix)
        NOTES.append('--- ' + ('ALL IN ONE' if slug.startswith('all-in-one') else ' '.join(HEAD)))
        pdf = OUT / f'{slug}.pdf'
        c = rl_canvas.Canvas(str(pdf), pagesize=A4)
        c.setTitle(f"Example College AI Entrepreneurship Hackathon — {' '.join(HEAD).title()} — {title}")
        c.setAuthor('Example College')
        draw(c)
        c.showPage()
        c.save()
        print(f'{slug}.pdf  +  .png (300 dpi)')
    print()
    for n in dict.fromkeys(NOTES):
        print(' ', n)
