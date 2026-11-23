"""Shared print helpers: fonts, colours, tracked text, the vector logo and the logo lockup."""
import json
from pathlib import Path
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from reportlab.pdfbase.pdfmetrics import registerFontFamily

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FONTS = ROOT / "brand" / "fonts"
LOGOS = ROOT / "brand" / "logos"

for name, file in [("BC-R", "BarlowCondensed-Regular"), ("BC-M", "BarlowCondensed-Medium"),
                   ("BC-SB", "BarlowCondensed-SemiBold"), ("BC-B", "BarlowCondensed-Bold"),
                   ("BC-XB", "BarlowCondensed-ExtraBold"), ("DM-R", "DMSans-Regular"),
                   ("DM-M", "DMSans-Medium"), ("DM-SB", "DMSans-SemiBold"),
                   ("DD-R", "DMSans-DisplayRegular"), ("DD-M", "DMSans-DisplayMedium"),
                   ("DD-B", "DMSans-DisplayBold"), ("DD-XB", "DMSans-DisplayExtraBold")]:
    pdfmetrics.registerFont(TTFont(name, str(FONTS / f"{file}.ttf")))
registerFontFamily("DM-R", normal="DM-R", bold="DM-SB", italic="DM-R", boldItalic="DM-SB")

CAP = 0.70  # cap height of Barlow Condensed and DM Sans, as a share of the font size


def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


INK, PAPER, ACCENT = hexc("#121316"), hexc("#f2f1e9"), hexc("#7e98ff")
BRAND, WHITE = hexc("#141a9d"), (1, 1, 1)
GREY, LIGHT = hexc("#8a8b90"), hexc("#c9cacd")

PT = 0.3528  # mm per point


# ----------------------------------------------------------------- text helpers
def text_width(text, font, size, track=0.0):
    return sum(pdfmetrics.stringWidth(ch, font, size) for ch in text) + track * max(len(text) - 1, 0)


def tracked(c, x, y, text, font, size, track=0.0, color=INK, anchor="left"):
    """Draw text with letter spacing (track in points). Returns its width in points."""
    w = text_width(text, font, size, track)
    if anchor == "right":
        x -= w
    elif anchor == "center":
        x -= w / 2
    c.setFillColorRGB(*color)
    c.setFont(font, size)
    for ch in text:
        c.drawString(x, y, ch)
        x += pdfmetrics.stringWidth(ch, font, size) + track
    return w


def fit_size(text, font, max_w, start, minimum, track_em=0.0):
    """Largest size from `start` down to `minimum` at which text fits in max_w points."""
    size = start
    while size > minimum and text_width(text, font, size, track_em * size) > max_w:
        size -= 0.25
    return size


# ----------------------------------------------------------------- the logo
_LOGO = json.loads((LOGOS / "logo_vec.json").read_text())
LOGO_RATIO = _LOGO["w"] / _LOGO["h"]  # width / height of the logo's ink


def draw_logo(c, x, top, height, color=BRAND):
    """The logo as clean vector outlines, from brand/logos/logo_vec.json.
    (x, top) is the top-left of the logo's ink, in points; height in points."""
    s = height / _LOGO["h"]
    X = lambda px: x + px * s
    Y = lambda py: top - py * s
    p = c.beginPath()
    for curve in _LOGO["curves"]:
        sx, sy = curve["start"]
        p.moveTo(X(sx), Y(sy))
        for seg in curve["segs"]:
            if seg[0] == "L":
                (cx, cy), (ex, ey) = seg[1], seg[2]
                p.lineTo(X(cx), Y(cy))
                p.lineTo(X(ex), Y(ey))
            else:
                (ax, ay), (bx, by), (ex, ey) = seg[1], seg[2], seg[3]
                p.curveTo(X(ax), Y(ay), X(bx), Y(by), X(ex), Y(ey))
        p.close()
    c.setFillColorRGB(*color)
    c.drawPath(p, stroke=0, fill=1, fillMode=0)  # even-odd keeps the holes in the letters
    return height * LOGO_RATIO


def lockup(c, x, top, height, logo_color=BRAND, text_color=INK, track=0.3, font="BC-B"):
    """Logo · slanted divider · AI ENTREPRENEURSHIP / HACKATHON, all `height` tall.
    Returns the total width in points."""
    lw = draw_logo(c, x, top, height, logo_color)
    # Two lines whose cap tops / baselines line up with the logo's top / bottom.
    size = height / (CAP + 1.12)            # cap + leading = height, leading 1.12 em
    lead = 1.12 * size
    div_x = x + lw + height * 0.30
    c.setStrokeColorRGB(*text_color)
    c.setLineWidth(max(0.5, height * 0.018))
    c.line(div_x, top - height - height * 0.02, div_x + height * 0.22, top + height * 0.02)
    tx = div_x + height * 0.22 + height * 0.30
    w1 = tracked(c, tx, top - CAP * size, "AI ENTREPRENEURSHIP", font, size, track * size / 10, text_color)
    tracked(c, tx, top - CAP * size - lead, "HACKATHON", font, size, track * size / 10, text_color)
    return (tx - x) + w1


# ----------------------------------------------------------------- page helpers
def apply_scale(c, page_w, page_h, scale):
    """Enlarge the whole page around its centre (cancels a printer that shrinks pages)."""
    if scale != 1.0:
        c.translate(page_w / 2, page_h / 2)
        c.scale(scale, scale)
        c.translate(-page_w / 2, -page_h / 2)
