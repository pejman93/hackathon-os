"""Lanyard badges, 98 x 140 mm, four to an A4 sheet with crop marks and a punch cross."""
import csv
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from brand import *

CW, CH = 98 * mm, 140 * mm          # one badge
BLEED = 3 * mm
X0 = (210 - 2 * 98) / 2 * mm        # 7 mm side margin of the sheet
Y0 = (297 - 2 * 140) / 2 * mm       # 8.5 mm top / bottom margin of the sheet
M = 6 * mm                          # side margin of the name panel

PANEL = hexc("#f7f6f0")             # cream name panel
SOFT = hexc("#3c3e44")              # surname
ORG = BRAND                         # organisation line

# Background per role group, the two slanted bands, the role text, and the logo colours.
# bg = badge colour, band1/band2 = the two slanted bands, logo = Example College logo + lockup colour.
# Participant + Mentor: strip/text = the small role strip under the name panel.
# Everyone else: on_bg = colour of the big role word printed straight on the background.
STYLE = {
    "PARTICIPANT":     dict(bg=ACCENT, band1=BRAND,  band2=PAPER,  strip=INK,    text=PAPER, logo=INK),
    "MENTOR":          dict(bg=INK,    band1=ACCENT, band2=BRAND,  strip=ACCENT, text=INK,   logo=WHITE),
    "BUSINESS MENTOR": dict(bg=INK,    band1=PAPER,  band2=ACCENT, on_bg=ACCENT, logo=WHITE),
    "JUDGE":           dict(bg=BRAND,  band1=ACCENT, band2=INK,    on_bg=WHITE,  logo=WHITE),
    "SPEAKER":         dict(bg=BRAND,  band1=PAPER,  band2=ACCENT, on_bg=PAPER,  logo=WHITE),
    "CREW":            dict(bg=PAPER,  band1=INK,    band2=ACCENT, on_bg=INK,    logo=INK),
}
ROLES = STYLE                       # build.py checks roles against this
HAS_TEAM = {"PARTICIPANT", "MENTOR"}

PARTNER_LOGOS = [                   # (file, height in mm) - plain logos, no wording
    (LOGOS / "partner-mark.png", 5.6),
    (LOGOS / "partner-mark-2.png", 6.2),
]

# Vertical plan, in mm from the TOP of the badge
PUNCH_Y = 7.0
HEAD_TOP, HEAD_H = 14.0, 6.4        # lockup left, logo chip right
PANEL_TOP = 27.0
BOX_W, BOX_H = 84.0, 54.0           # sticker 80 x 50: 2 mm play all round
TEAM = dict(first=42.5, size=34, last=50.0, org=56.5, box_gap=4.0, panel_pad=4.0)
SOLO = dict(first=46.0, size=46, last=56.0, org=63.5, date=72.5, date_org=77.0, panel_bottom=86.0)


# ----------------------------------------------------------------- pieces
def slanted_band(c, x_top, width, top, bottom, slope=0.27):
    """A parallelogram leaning like the slash in the logo lockup."""
    shift = (top - bottom) * slope
    p = c.beginPath()
    p.moveTo(x_top, top)
    p.lineTo(x_top + width, top)
    p.lineTo(x_top + width - shift, bottom)
    p.lineTo(x_top - shift, bottom)
    p.close()
    return p


def background(c, ox, oy, st, clip_rect, solo=False):
    bx, by, bw, bh = clip_rect
    c.saveState()
    clip = c.beginPath()
    clip.rect(bx, by, bw, bh)
    c.clipPath(clip, stroke=0, fill=0)
    c.setFillColorRGB(*st["bg"])
    c.rect(bx, by, bw, bh, stroke=0, fill=1)
    top, bottom = oy + CH + BLEED, oy - BLEED
    # one wide band and one narrow band, crossing the badge from the top right
    c.setFillColorRGB(*st["band1"])
    # on badges without a sticker the bands sit further right, so the lower left stays
    # plain background for the role word
    b1, b2 = (0.95, 1.30) if solo else (0.78, 1.13)
    c.drawPath(slanted_band(c, ox + b1 * CW, 0.30 * CW, top, bottom), stroke=0, fill=1)
    c.setFillColorRGB(*st["band2"])
    c.drawPath(slanted_band(c, ox + b2 * CW, 0.07 * CW, top, bottom), stroke=0, fill=1)
    c.restoreState()


def logo_chip(c, right, top, st):
    """Example Campus + Example Foundation on a small cream chip, so they read on any colour."""
    items = []
    for path, h_mm in PARTNER_LOGOS:
        img = ImageReader(str(path))
        iw, ih = img.getSize()
        items.append((img, h_mm * mm * iw / ih, h_mm * mm))
    gap, pad_x, chip_h = 3 * mm, 2.4 * mm, HEAD_H * mm + 1.6 * mm
    chip_w = sum(w for _, w, _ in items) + gap * (len(items) - 1) + 2 * pad_x
    x0, y0 = right - chip_w, top - chip_h + 0.8 * mm
    c.setFillColorRGB(*PANEL)
    c.roundRect(x0, y0, chip_w, chip_h, 1.6 * mm, stroke=0, fill=1)
    x, base = x0 + pad_x, y0 + (chip_h - max(h for _, _, h in items)) / 2
    for k, (img, w, h) in enumerate(items):
        if k:
            c.setStrokeColorRGB(*LIGHT)
            c.setLineWidth(0.5)
            c.line(x - gap / 2, base + 0.3 * mm, x - gap / 2, base + h - 0.3 * mm)
        c.drawImage(img, x, base, w, h, mask="auto")
        x += w + gap


def name_block(c, x, T, L, first, last, org, width):
    if first:
        f = first.strip()
        size = fit_size(f, "DD-B", width, L["size"], 18, -0.02)
        tracked(c, x, T(L["first"]), f, "DD-B", size, -0.02 * size, INK)
        if last:
            l = last.strip()
            ls = fit_size(l, "DD-R", width, min(size * 0.42, 19), 10, 0)
            tracked(c, x, T(L["last"]), l, "DD-R", ls, 0, SOFT)
    else:
        c.setStrokeColorRGB(*GREY)
        c.setLineWidth(0.5)
        c.line(x, T(L["first"] + 1), x + width, T(L["first"] + 1))
        tracked(c, x, T(L["first"] + 5), "NAME", "DM-SB", 6.5, 1.2, GREY)
    if org and org.strip():
        os_ = fit_size(org.strip(), "DD-M", width, 12.5, 8, 0)
        tracked(c, x, T(L["org"]), org.strip(), "DD-M", os_, 0, ORG)


def role_strip(c, ox, oy, top_y, st, clip_rect):
    """Solid strip from top_y down to the bottom edge (and its bleed), full width."""
    bx, by, bw, bh = clip_rect
    c.saveState()
    clip = c.beginPath()
    clip.rect(bx, by, bw, bh)
    c.clipPath(clip, stroke=0, fill=0)
    c.setFillColorRGB(*st["strip"])
    c.rect(bx, by, bw, top_y - by, stroke=0, fill=1)
    c.restoreState()


def role_text(c, cx, center_y, role, st, big):
    lines = role.split(" ") if (big and len(role) > 9) else [role]
    size = (30 if len(role) <= 9 else 25) if big else 19
    lead = size * 1.02
    first_base = center_y + (len(lines) - 1) * lead / 2 - CAP * size / 2
    for k, line in enumerate(lines):
        fs = fit_size(line, "DD-XB", CW - 2 * M, size, 12, 0.08)
        tracked(c, cx, first_base - k * lead, line, "DD-XB", fs, 0.08 * fs, st["text"], "center")
    return first_base - (len(lines) - 1) * lead


# ----------------------------------------------------------------- one badge
def card(c, ox, oy, first, last, role, org="", clip_rect=None):
    """(ox, oy) = bottom-left corner of the badge in points."""
    st = STYLE[role]
    T = lambda d: oy + CH - d * mm
    cx = ox + CW / 2
    pw = CW - 2 * M                                  # panel width
    tw = pw - 10 * mm                                # text width inside the panel

    background(c, ox, oy, st, clip_rect or (ox, oy, CW, CH), solo=role not in HAS_TEAM)

    # punch mark
    c.setStrokeColorRGB(*(INK if st["bg"] in (ACCENT, PAPER) else PAPER))
    c.setLineWidth(0.4)
    c.line(cx - 2 * mm, T(PUNCH_Y), cx + 2 * mm, T(PUNCH_Y))
    c.line(cx, T(PUNCH_Y) - 2 * mm, cx, T(PUNCH_Y) + 2 * mm)

    # header
    text_col = INK if st["logo"] == INK else WHITE
    lockup(c, ox + M, T(HEAD_TOP), HEAD_H * mm, logo_color=st["logo"], text_color=text_col)
    logo_chip(c, ox + CW - M, T(HEAD_TOP) + 0.8 * mm, st)

    px = ox + M
    if role in HAS_TEAM:
        L = TEAM
        box_top = (L["org"] if org else L["last"]) + L["box_gap"]
        panel_bottom = box_top + BOX_H + L["panel_pad"]
        c.setFillColorRGB(*PANEL)
        c.roundRect(px, T(panel_bottom), pw, (panel_bottom - PANEL_TOP) * mm, 4 * mm, stroke=0, fill=1)
        name_block(c, px + 5 * mm, T, L, first, last, org, tw)
        bx = ox + (CW - BOX_W * mm) / 2
        c.setStrokeColorRGB(*LIGHT)
        c.setLineWidth(0.6)
        c.setDash(2, 1.6)
        c.roundRect(bx, T(box_top + BOX_H), BOX_W * mm, BOX_H * mm, 4 * mm, stroke=1, fill=0)
        c.setDash()
        mid = T(box_top + BOX_H / 2)
        tracked(c, cx, mid + 1.0 * mm, "TEAM", "DM-SB", 10, 2.4, LIGHT, "center")
        tracked(c, cx, mid - 4.0 * mm, "Your team sticker goes here", "DM-R", 6.5, 0, LIGHT, "center")
        strip_top = T(panel_bottom + 5)
        role_strip(c, ox, oy, strip_top, st, clip_rect or (ox, oy, CW, CH))
        role_text(c, cx, (strip_top + oy) / 2, role, st, big=False)
    else:
        L = SOLO
        c.setFillColorRGB(*PANEL)
        c.roundRect(px, T(L["panel_bottom"]), pw, (L["panel_bottom"] - PANEL_TOP) * mm, 4 * mm, stroke=0, fill=1)
        name_block(c, px + 5 * mm, T, L, first, last, org, tw)
        tracked(c, px + 5 * mm, T(L["date_org"] if org and org.strip() else L["date"]),
                "23–26 October 2026", "DD-B", 12, -0.1, INK)
        # role word straight on the background, left-aligned, no box
        col = st["on_bg"]
        words = role.split(" ") if len(role) > 9 else [role]
        size = 34 if len(words) == 1 else 26
        lead = size * 1.0
        zone_mid = (T(L["panel_bottom"]) + oy) / 2 + (3 * mm if role == "CREW" else 0)
        base = zone_mid + (len(words) - 1) * lead / 2 - CAP * size / 2
        for k, w in enumerate(words):
            fs = fit_size(w, "DD-XB", 46 * mm, size, 14, 0.06)
            tracked(c, px, base - k * lead, w, "DD-XB", fs, 0.06 * fs, col)
        if role == "CREW":
            tracked(c, px, base - (len(words) - 1) * lead - 7.5 * mm, "Questions? Ask me.", "DD-M", 11, 0, col)


# ----------------------------------------------------------------- sheet
def crop_marks(c, ph):
    c.setStrokeColorRGB(*GREY)
    c.setLineWidth(0.3)
    xs = [X0, X0 + CW, X0 + 2 * CW]
    ys = [ph - Y0, ph - Y0 - CH, ph - Y0 - 2 * CH]
    gap = BLEED + 0.8 * mm
    for x in xs:                                   # vertical cuts: marks above and below the art
        c.line(x, ys[0] + gap, x, ys[0] + gap + 3.5 * mm)
        c.line(x, ys[2] - gap, x, ys[2] - gap - 3.5 * mm)
    for y in ys:                                   # horizontal cuts: marks left and right
        c.line(xs[0] - gap, y, xs[0] - gap - 3.5 * mm, y)
        c.line(xs[2] + gap, y, xs[2] + gap + 3.5 * mm, y)


def main(src, out, scale=1.0):
    make([r for r in csv.DictReader(open(src, encoding="utf-8"))], out, scale)


def make(people, out, scale=1.0):
    """people: dicts with first, last, role, organisation (optional)."""
    pw, ph = A4
    c = canvas.Canvas(out, pagesize=A4, initialFontName="DM-R")
    c.setTitle("AI Entrepreneurship Hackathon - lanyard badges")
    for i in range(0, len(people), 4):
        c.saveState()
        apply_scale(c, pw, ph, scale)
        for j, p in enumerate(people[i:i + 4]):
            col, row = j % 2, j // 2
            ox = X0 + col * CW
            oy = ph - Y0 - (row + 1) * CH
            # bleed only on the outer edges; the inner edges meet the next badge
            l = BLEED if col == 0 else 0
            r = BLEED if col == 1 else 0
            t = BLEED if row == 0 else 0
            b = BLEED if row == 1 else 0
            clip = (ox - l, oy - b, CW + l + r, CH + t + b)
            card(c, ox, oy, p["first"], p["last"], p["role"].strip().upper(), p.get("organisation", ""), clip)
        crop_marks(c, ph)
        c.restoreState()
        c.showPage()
    c.save()


if __name__ == "__main__":
    sc = next((float(a.split("=")[1]) for a in sys.argv if a.startswith("--scale=")), 1.0)
    main(sys.argv[1], sys.argv[2], sc)
