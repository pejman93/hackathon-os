#!/usr/bin/env python3
"""Build a pack: a designed PDF to send, and a Word file to edit.

    python documents/make_pack.py              the participant pack
    python documents/make_pack.py --mentors    the mentor pack

Both files are rendered from one content file (content.py, or content_mentors.py; see
pack_spec.py), so they cannot drift apart. The PDF uses the event typefaces. The Word file
uses Arial, the one face that exists on every machine that opens it.
"""
import pathlib, re, sys
from xml.sax.saxutils import escape

from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, KeepTogether,
                                NextPageTemplate, PageBreak, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / 'output' / 'documents'
PROJ = HERE.parent
FONTS = PROJ / 'brand' / 'fonts'
BUILD = HERE.parent / 'output' / 'documents' / '_build'
BUILD.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(HERE))
from pack_spec import BLOCKS, MAILBOX, SITE, SPEC, day_foot    # noqa: E402

NAME, TITLE = SPEC['name'], SPEC['title']

PAGE_W, PAGE_H = A4
LM = RM = 48
BANNER_FIRST, BANNER_NEXT = 84, 44
BOTTOM = 56
TEXT_W = PAGE_W - LM - RM


def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


INK, PAPER, ACCENT, BRAND = '#121316', '#f2f1e9', '#7e98ff', '#141a9d'
BODY, SLATE, RULE, HAZE = '#23252b', '#5d6068', '#dcdad0', '#b9bac4'

for w in (600, 700, 800):
    pdfmetrics.registerFont(TTFont(f'BC{w}', FONTS / f'BarlowCondensed-{w}.ttf'))
for w in (400, 500, 700):
    pdfmetrics.registerFont(TTFont(f'DM{w}', FONTS / f'DMSans-{w}.ttf'))
pdfmetrics.registerFontFamily('DM400', normal='DM400', bold='DM700',
                              italic='DM400', boldItalic='DM700')
pdfmetrics.registerFontFamily('DM500', normal='DM500', bold='DM700',
                              italic='DM500', boldItalic='DM700')


# ====================================================================== assets
def banner_bg(first):
    """Crop the Overview's own header artwork to the strip this banner needs."""
    h_pt = BANNER_FIRST if first else BANNER_NEXT
    dst = BUILD / f'banner-bg-{h_pt}.jpg'
    if not dst.exists():
        im = Image.open(HERE / 'assets' / 'overview-banner-bg.jpg').convert('RGB')
        want = round(im.width * h_pt / PAGE_W)
        top = (im.height - want) // 2 if first else 46      # the slim strip sits on the faces
        im.crop((0, top, im.width, top + want)).save(dst, quality=93)
    return ImageReader(str(dst))


def white_logo():
    dst = BUILD / 'logo-white.png'
    if not dst.exists():
        im = Image.open(PROJ / 'website/assets/logo.png').convert('RGBA')
        a = im.split()[3]
        w = Image.new('L', im.size, 255)
        Image.merge('RGBA', (w, w, w, a)).save(dst)
    return ImageReader(str(dst))


def venue_mark():
    return ImageReader(str(PROJ / 'brand' / 'logos' / 'partner-mark.png'))


PHOTO_SHARE = (381, 318, 318, 255)      # the Overview's own proportions
PHOTO_GAP, PHOTO_H = 6, 104


def photo_strip(names, total_w):
    """Crop the four venue photographs to one height and round their corners.
    Returns [(path, width_pt, height_pt)]. Corners are flattened onto white so
    the same files work in Word, which has no clipping path."""
    from PIL import ImageDraw, ImageOps
    usable = total_w - PHOTO_GAP * (len(names) - 1)
    out = []
    for name, share in zip(names, PHOTO_SHARE):
        w = usable * share / sum(PHOTO_SHARE)
        dst = BUILD / f'photo-{name}-{round(total_w)}.jpg'
        if not dst.exists():
            src = next((PROJ / 'sample-data' / 'photos').glob(name + '*'))
            px = (round(w * 4), round(PHOTO_H * 4))
            im = ImageOps.fit(Image.open(src).convert('RGB'), px, Image.LANCZOS)
            mask = Image.new('L', px, 0)
            ImageDraw.Draw(mask).rounded_rectangle([0, 0, px[0] - 1, px[1] - 1], radius=22, fill=255)
            Image.composite(im, Image.new('RGB', px, 'white'), mask).save(dst, quality=90)
        out.append((dst, w, PHOTO_H))
    return out


def tracked(c, x, y, text, font, size, track, align='left'):
    w = pdfmetrics.stringWidth(text, font, size) + track * max(0, len(text) - 1)
    if align == 'right':
        x -= w
    t = c.beginText(x, y)
    t.setFont(font, size)
    t.setCharSpace(track)
    t.textOut(text)
    # Character spacing is graphics state, not a property of this text object:
    # left set, it leaks into every string drawn afterwards, which is then
    # wider than stringWidth() says. That put PACK on top of PARTICIPANT.
    t.setCharSpace(0)
    c.drawText(t)
    return w


def draw_banner(c, y0, first):
    """Example College lockup · document title · POWERED BY the venue."""
    h = BANNER_FIRST if first else BANNER_NEXT
    k = 1.0 if first else 0.72
    cy = y0 + h / 2
    c.saveState()
    c.drawImage(banner_bg(first), 0, y0, PAGE_W, h, mask=None)

    # lockup
    logo_w = 77 * k
    logo_h = logo_w * 146 / 375
    c.drawImage(white_logo(), 40, cy - logo_h / 2, logo_w, logo_h, mask='auto')
    dx = 40 + logo_w + 9 * k
    c.setStrokeColorRGB(*rgb(PAPER))
    c.setStrokeAlpha(0.5)
    c.setLineWidth(0.7)
    c.line(dx, cy - logo_h * 0.56, dx + 6 * k, cy + logo_h * 0.56)
    c.setStrokeAlpha(1)
    tx = dx + 15 * k
    small, big = 7 * k, 14 * k
    c.setFillColorRGB(*rgb(PAPER))
    tracked(c, tx, cy + 4.45 * k, 'AI ENTREPRENEURSHIP', 'BC600', small, 0.35 * k)
    c.setFont('BC700', big)
    c.drawString(tx, cy - 9.35 * k, 'HACKATHON')
    lock_right = tx + max(pdfmetrics.stringWidth('HACKATHON', 'BC700', big),
                          pdfmetrics.stringWidth('AI ENTREPRENEURSHIP', 'BC600', small) + 0.35 * k * 18)

    # Example Campus credit, right
    mark_h = 40 if first else 27
    mark_w = mark_h * 1522 / 1250
    mx = PAGE_W - 40 - mark_w
    c.drawImage(venue_mark(), mx, cy - mark_h / 2, mark_w, mark_h, mask='auto')
    c.setFillColorRGB(*rgb(PAPER))
    c.setFillAlpha(0.88)
    lab = 5.8 if first else 4.9
    lw = tracked(c, mx - 9, cy - lab * 0.36, 'POWERED BY', 'DM700', lab, 1.0, align='right')
    c.setFillAlpha(1)
    rule_x = mx - 9 - lw - 11
    c.setStrokeColorRGB(*rgb(PAPER))
    c.setStrokeAlpha(0.30)
    c.setLineWidth(0.6)
    c.line(rule_x, cy - mark_h * 0.42, rule_x, cy + mark_h * 0.42)
    c.setStrokeAlpha(1)

    # title, between the two
    title_x = lock_right + (30 if first else 22)
    room = rule_x - 14 - title_x
    size = 28 if first else 13.5
    a, b = SPEC['banner']
    while pdfmetrics.stringWidth(a + b, 'BC700', size) > room and size > 8:
        size -= 0.5
    base = cy - 4 if first else cy - size * 0.35
    c.setFont('BC700', size)
    c.setFillColorRGB(*rgb(PAPER))
    c.drawString(title_x, base, a)
    c.setFillColorRGB(*rgb(ACCENT))
    c.drawString(title_x + pdfmetrics.stringWidth(a, 'BC700', size), base, b)
    if first:
        c.setFillColorRGB(*rgb(HAZE))
        tracked(c, title_x + 0.5, cy - 16.2, '23–26 OCTOBER 2026  ·  EXAMPLE CAMPUS', 'DM500', 6.6, 1.15)
    c.restoreState()


def banner_png(first):
    """The same banner as a full-width image for the Word header, drawn with Pillow at 300 dpi."""
    from PIL import ImageDraw, ImageFont
    h = BANNER_FIRST if first else BANNER_NEXT
    k, s = (1.0 if first else 0.72), 300 / 72
    cy = h / 2
    banner_bg(first)
    white_logo()
    colour = lambda c: tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))
    paper, accent, haze = colour(PAPER), colour(ACCENT), colour(HAZE)
    im = Image.open(BUILD / f'banner-bg-{h}.jpg').convert('RGBA').resize((round(PAGE_W * s), round(h * s)), Image.LANCZOS)
    layer = Image.new('RGBA', im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    def picture(path, x, y, w, pic_h):
        p = Image.open(path).convert('RGBA').resize((round(w * s), round(pic_h * s)), Image.LANCZOS)
        layer.alpha_composite(p, (round(x * s), round((h - y - pic_h) * s)))

    def rule(x1, y1, x2, y2, alpha, width):
        d.line([(x1 * s, (h - y1) * s), (x2 * s, (h - y2) * s)], fill=paper + (alpha,), width=max(1, round(width * s)))

    def text(x, y, value, face, size, fill, track=0):
        font = ImageFont.truetype(str(FONTS / f'{face}.ttf'), size * s)
        for ch in value:
            d.text((x * s, (h - y) * s), ch, font=font, fill=fill, anchor='ls')
            x += font.getlength(ch) / s + track
        return x

    logo_w = 77 * k
    logo_h = logo_w * 146 / 375
    picture(BUILD / 'logo-white.png', 40, cy - logo_h / 2, logo_w, logo_h)
    dx = 40 + logo_w + 9 * k
    rule(dx, cy - logo_h * 0.56, dx + 6 * k, cy + logo_h * 0.56, 128, 0.7)
    tx = dx + 15 * k
    small, big = 7 * k, 14 * k
    text(tx, cy + 4.45 * k, 'AI ENTREPRENEURSHIP', 'BarlowCondensed-600', small, paper, 0.35 * k)
    text(tx, cy - 9.35 * k, 'HACKATHON', 'BarlowCondensed-700', big, paper)
    lock_right = tx + max(pdfmetrics.stringWidth('HACKATHON', 'BC700', big),
                          pdfmetrics.stringWidth('AI ENTREPRENEURSHIP', 'BC600', small) + 0.35 * k * 18)
    mark_h = 40 if first else 27
    mark_w = mark_h * 1522 / 1250
    mx = PAGE_W - 40 - mark_w
    picture(PROJ / 'brand' / 'logos' / 'partner-mark.png', mx, cy - mark_h / 2, mark_w, mark_h)
    lab = 5.8 if first else 4.9
    lw = pdfmetrics.stringWidth('POWERED BY', 'DM700', lab) + 1.0 * 9
    text(mx - 9 - lw, cy - lab * 0.36, 'POWERED BY', 'DMSans-700', lab, paper + (224,), 1.0)
    rule_x = mx - 9 - lw - 11
    rule(rule_x, cy - mark_h * 0.42, rule_x, cy + mark_h * 0.42, 76, 0.6)
    title_x = lock_right + (30 if first else 22)
    room = rule_x - 14 - title_x
    size = 28 if first else 13.5
    a, b = SPEC['banner']
    while pdfmetrics.stringWidth(a + b, 'BC700', size) > room and size > 8:
        size -= 0.5
    base = cy - 4 if first else cy - size * 0.35
    end = text(title_x, base, a, 'BarlowCondensed-700', size, paper)
    text(end, base, b, 'BarlowCondensed-700', size, accent)
    if first:
        text(title_x + 0.5, cy - 16.2, '23–26 OCTOBER 2026  ·  EXAMPLE CAMPUS', 'DMSans-500', 6.6, haze, 1.15)
    png = BUILD / f"banner{SPEC['cache']}-{h}.png"
    Image.alpha_composite(im, layer).convert('RGB').save(png)
    return png


# ================================================================== PDF pieces
def md(text):
    """**bold** -> <b>bold</b>, with everything else escaped."""
    return re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', escape(text))


def style(name, font='DM400', size=9.8, lead=None, color=BODY, **kw):
    return ParagraphStyle(name, fontName=font, fontSize=size, leading=lead or size * 1.46,
                          textColor=color, **kw)


S = dict(
    lead=style('lead', size=11.6, lead=16.8, color=INK, spaceAfter=7),
    p=style('p', spaceAfter=6.5),
    h=style('h', font='BC700', size=15.5, lead=17, color=BRAND, spaceBefore=13, spaceAfter=5,
            keepWithNext=1),
    small=style('small', size=8.5, lead=12.4, color=SLATE, spaceBefore=5, spaceAfter=2),
    cell=style('cell', size=9.6, lead=13.6),
    label=style('label', font='DM700', size=7.5, lead=10.5, color=BRAND),
    time=style('time', font='DM700', size=8.8, lead=12.6, color=BRAND),
    item=style('item', size=9.1, lead=12.6),
    tag=style('tag', font='BC700', size=14.5, lead=15.5, color=INK, spaceAfter=1),
    meta=style('meta', font='DM700', size=8.4, lead=11.5, color=BODY, spaceBefore=2, spaceAfter=5),
    food=style('food', size=8.4, lead=11.8, color=SLATE),
    pct=style('pct', font='BC700', size=17, lead=18, color=BRAND),
    quote=style('quote', font='DM500', size=11.2, lead=15.6, color=INK),
    q=style('q', font='DM700', size=9.5, lead=13, color=INK, spaceAfter=1.5, keepWithNext=1),
    a=style('a', size=9.1, lead=13, color='#33353c', spaceAfter=8.5),
    ctitle=style('ctitle', font='BC700', size=17, lead=18, color=PAPER, spaceAfter=3),
    ctext=style('ctext', size=9, lead=13, color='#d9d8d0'),
    cright=style('cright', size=9, lead=14, color=PAPER, alignment=2),
)


class Eyebrow(Flowable):
    """Small tracked capitals. Paragraph cannot letter-space, so this draws it."""

    def __init__(self, text, color=BRAND, size=7.4, track=1.55, after=5):
        super().__init__()
        self.text, self.color, self.size, self.track, self.after = text, color, size, track, after

    def wrap(self, aw, ah):
        return aw, self.size + self.after

    def draw(self):
        self.canv.setFillColorRGB(*rgb(self.color))
        tracked(self.canv, 0, self.after + 0.6, self.text, 'DM700', self.size, self.track)


class Dot(Flowable):
    """A bullet, drawn. DM Sans has no ■ glyph, so a typed one prints as tofu."""

    def wrap(self, aw, ah):
        return 6, 10

    def draw(self):
        self.canv.setFillColorRGB(*rgb(ACCENT))
        self.canv.rect(0, 3.1, 4.6, 4.6, stroke=0, fill=1)


class Box(Flowable):
    """An empty tick-box for the checklist."""

    def wrap(self, aw, ah):
        return 9, 11

    def draw(self):
        self.canv.setStrokeColorRGB(*rgb(BRAND))
        self.canv.setLineWidth(0.9)
        self.canv.roundRect(0.5, 1.2, 8, 8, 1.4, stroke=1, fill=0)


def grid(rows, widths, extra=(), pad=(4.5, 4.5), lines=True):
    t = Table(rows, colWidths=widths)
    cmds = [('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), pad[0]), ('BOTTOMPADDING', (0, 0), (-1, -1), pad[1])]
    if lines:
        cmds.append(('LINEBELOW', (0, 0), (-1, -2), 0.5, RULE))
    t.setStyle(TableStyle(cmds + list(extra)))
    return t


def day_card(d, width):
    inner = width - 24
    times = Table([[Paragraph(t, S['time']), Paragraph(md(x), S['item'])] for t, x in d['items']],
                  colWidths=[34, inner - 34])
    times.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'),
                               ('LEFTPADDING', (0, 0), (-1, -1), 0),
                               ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                               ('TOPPADDING', (0, 0), (-1, -1), 1.5),
                               ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5)]))
    return [Eyebrow(d['label'], after=4.5),
            Paragraph(escape(d['tagline']), S['tag']),
            Paragraph(f"{d['place']}  ·  {d['hours']}", S['meta']),
            times,
            Spacer(1, 6),
            Paragraph('<b><font color="%s">%s</font></b>&nbsp;&nbsp;%s'
                      % (BRAND, escape(day_foot(d)[0]), escape(day_foot(d)[1])), S['food'])]


def flow():
    out = []
    for blk in BLOCKS:
        kind = blk[0]
        if kind == 'eyebrow':
            out.append(Eyebrow(blk[1], size=7.8, track=2.0, after=7))
        elif kind in ('lead', 'p', 'small'):
            out.append(Paragraph(md(blk[1]), S[kind]))
        elif kind == 'h':
            out.append(Paragraph(escape(blk[1]), S['h']))
        elif kind == 'pagebreak':
            out.append(PageBreak())
        elif kind == 'glance':
            rows = [[Eyebrow(blk[1], after=2), '']]
            rows += [[Paragraph(a, S['label']), Paragraph(md(b), S['cell'])] for a, b in blk[2]]
            t = Table(rows, colWidths=[98, TEXT_W - 98 - 28])
            t.setStyle(TableStyle([
                ('SPAN', (0, 0), (-1, 0)), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 1), (-1, -1), 4.2), ('BOTTOMPADDING', (0, 1), (-1, -1), 4.4),
                ('TOPPADDING', (0, 1), (0, -1), 6.4),
                ('LINEBELOW', (0, 1), (-1, -2), 0.5, RULE)]))
            card = Table([[t]], colWidths=[TEXT_W])
            card.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), PAPER),
                                      ('ROUNDEDCORNERS', [7, 7, 7, 7]),
                                      ('LEFTPADDING', (0, 0), (-1, -1), 14),
                                      ('RIGHTPADDING', (0, 0), (-1, -1), 14),
                                      ('TOPPADDING', (0, 0), (-1, -1), 13),
                                      ('BOTTOMPADDING', (0, 0), (-1, -1), 8)]))
            out += [Spacer(1, 5), card, Spacer(1, 2)]
        elif kind == 'checks':
            rows = [[Box(), Paragraph(md(x), S['cell'])] for x in blk[1]]
            out.append(grid(rows, [18, TEXT_W - 18], pad=(3.6, 3.6), lines=False))
        elif kind == 'bullets':
            rows = [[Dot(), Paragraph(md(x), S['cell'])] for x in blk[1]]
            out.append(grid(rows, [13, TEXT_W - 13], pad=(2.6, 2.6), lines=False))
            out.append(Spacer(1, 4))
        elif kind == 'days':
            gap = 12
            w = (TEXT_W - gap) / 2
            d = blk[1]
            rows = [[day_card(d[0], w), '', day_card(d[1], w)],
                    ['', '', ''],
                    [day_card(d[2], w), '', day_card(d[3], w)]]
            t = Table(rows, colWidths=[w, gap, w], rowHeights=[None, gap, None])
            cards = [(0, 0), (2, 0), (0, 2), (2, 2)]
            cmds = [('VALIGN', (0, 0), (-1, -1), 'TOP')]
            for cx, cyy in cards:
                cmds += [('BACKGROUND', (cx, cyy), (cx, cyy), PAPER),
                         ('LINEABOVE', (cx, cyy), (cx, cyy), 2.2, BRAND),
                         ('LEFTPADDING', (cx, cyy), (cx, cyy), 12),
                         ('RIGHTPADDING', (cx, cyy), (cx, cyy), 12),
                         ('TOPPADDING', (cx, cyy), (cx, cyy), 12),
                         ('BOTTOMPADDING', (cx, cyy), (cx, cyy), 11)]
            t.setStyle(TableStyle(cmds))
            out += [Spacer(1, 3), t]
        elif kind == 'quote':
            t = Table([[Paragraph(escape(blk[1]), S['quote'])]], colWidths=[TEXT_W])
            t.setStyle(TableStyle([('LINEBEFORE', (0, 0), (0, 0), 2.6, ACCENT),
                                   ('LEFTPADDING', (0, 0), (-1, -1), 11),
                                   ('TOPPADDING', (0, 0), (-1, -1), 2),
                                   ('BOTTOMPADDING', (0, 0), (-1, -1), 3)]))
            out += [Spacer(1, 2), t, Spacer(1, 8)]
        elif kind == 'judging':
            rows = [[Paragraph(p, S['pct']), Paragraph(md(x), S['cell'])] for p, x in blk[1]]
            out.append(grid(rows, [48, TEXT_W - 48], pad=(4, 5),
                            extra=[('TOPPADDING', (1, 0), (1, -1), 6.5)]))
            out.append(Spacer(1, 8))
        elif kind == 'pairs':
            rows = [[Paragraph(a, S['label']), Paragraph(md(b), S['cell'])] for a, b in blk[1]]
            out.append(grid(rows, [112, TEXT_W - 112], pad=(5, 5),
                            extra=[('TOPPADDING', (0, 0), (0, -1), 7.2)]))
        elif kind == 'faq':
            items = blk[1]
            half = (len(items) + 1) // 2
            gap = 20
            w = (TEXT_W - gap) / 2
            cols = [[x for q, a in part for x in (Paragraph(escape(q), S['q']),
                                                  Paragraph(md(a), S['a']))]
                    for part in (items[:half], items[half:])]
            t = Table([[cols[0], '', cols[1]]], colWidths=[w, gap, w])
            t.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                   ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                   ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                   ('TOPPADDING', (0, 0), (-1, -1), 2),
                                   ('BOTTOMPADDING', (0, 0), (-1, -1), 0)]))
            out.append(t)
        elif kind == 'photos':
            from reportlab.platypus import Image as RLImage
            strip = photo_strip(blk[1], TEXT_W)
            row, widths = [], []
            for i, (path, w, h) in enumerate(strip):
                if i:
                    row.append(''); widths.append(PHOTO_GAP)
                row.append(RLImage(str(path), width=w, height=h)); widths.append(w)
            t = Table([row], colWidths=widths)
            t.setStyle(TableStyle([('LEFTPADDING', (0, 0), (-1, -1), 0),
                                   ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                   ('TOPPADDING', (0, 0), (-1, -1), 0),
                                   ('BOTTOMPADDING', (0, 0), (-1, -1), 0)]))
            out += [Spacer(1, 2), t, Paragraph(md(blk[2]), S['small'])]
        elif kind == 'closing':
            d = blk[1]
            left = [Eyebrow(d['eyebrow'], color=ACCENT, after=6),
                    Paragraph(escape(d['title']), S['ctitle']),
                    Paragraph(escape(d['text']), S['ctext'])]
            right = [Paragraph(f"<b>{escape(d['name'])}</b>, {escape(d['role'])}", S['cright']),
                     Paragraph('<font color="%s">%s</font>' % (ACCENT, escape(d['lines'][0])), S['cright']),
                     Paragraph(escape(d['lines'][1]), S['cright'])]
            t = Table([[left, right]], colWidths=[TEXT_W * 0.60, TEXT_W * 0.40])
            t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), INK),
                                   ('ROUNDEDCORNERS', [7, 7, 7, 7]),
                                   ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                   ('LEFTPADDING', (0, 0), (-1, -1), 18),
                                   ('RIGHTPADDING', (0, 0), (-1, -1), 18),
                                   ('TOPPADDING', (0, 0), (-1, -1), 16),
                                   ('BOTTOMPADDING', (0, 0), (-1, -1), 15)]))
            out += [Spacer(1, 10), t]      # sections() keeps it with the block above
        else:
            raise ValueError(kind)
    return sections(out)


def sections(flowables):
    """Group everything from one heading to the next into a KeepTogether."""
    out, cur = [], []

    def flush():
        if cur:
            out.append(KeepTogether(list(cur)))
            cur.clear()

    for f in flowables:
        is_heading = isinstance(f, Paragraph) and f.style.name == 'h'
        if isinstance(f, PageBreak):
            flush()
            out.append(f)
        elif is_heading:
            flush()
            cur.append(f)
        elif cur:
            cur.append(f)
        else:
            out.append(f)
    flush()
    return out


class NumberedCanvas(rl_canvas.Canvas):
    """Holds every page back until the total is known, for 'Page 2 of 4'."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self._pages = []

    def showPage(self):
        self._pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._pages)
        for state in self._pages:
            self.__dict__.update(state)
            self.setStrokeColorRGB(*rgb(RULE))
            self.setLineWidth(0.6)
            self.line(LM, 40, PAGE_W - RM, 40)
            self.setFillColorRGB(*rgb(SLATE))
            self.setFont('DM400', 7.8)
            self.drawString(LM, 27, f'{MAILBOX}   ·   {SITE}')
            self.drawRightString(PAGE_W - RM, 27, f'Page {self._pageNumber} of {total}')
            super().showPage()
        super().save()


def build_pdf():
    path = OUT / f'{NAME}.pdf'
    doc = BaseDocTemplate(str(path), pagesize=A4, title=TITLE, author='Example College',
                          subject=SPEC['subject'],
                          leftMargin=LM, rightMargin=RM)

    def frame(banner):
        top_gap = 26 if banner == BANNER_FIRST else 22
        return Frame(LM, BOTTOM, TEXT_W, PAGE_H - banner - top_gap - BOTTOM,
                     leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)

    doc.addPageTemplates([
        PageTemplate('first', [frame(BANNER_FIRST)],
                     onPage=lambda c, d: draw_banner(c, PAGE_H - BANNER_FIRST, True)),
        PageTemplate('next', [frame(BANNER_NEXT)],
                     onPage=lambda c, d: draw_banner(c, PAGE_H - BANNER_NEXT, False)),
    ])
    doc.build([NextPageTemplate('next')] + flow(), canvasmaker=NumberedCanvas)
    return path


if __name__ == '__main__':
    pdf = build_pdf()
    n = len(re.findall(rb'/Type\s*/Page\b(?!s)', pdf.read_bytes()))
    print(f'{pdf.name}: {n} pages')
    if '--pdf-only' not in sys.argv:
        from make_docx import build_docx
        print(build_docx(banner_png(True), banner_png(False)).name)
