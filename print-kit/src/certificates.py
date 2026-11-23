"""A4 landscape certificates: participation, winner, audience award, mentor and staff.

CSV columns: type, first, last, team, product.
  type = participation | winner | audience | mentor | staff | staff lead
  team = a team name, or its number (1-4), which prints as "Team 1"
"""
import csv
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.utils import ImageReader
from brand import *

PARTNER_LOGOS = [  # (file, height in mm) - plain logos, no wording
    (LOGOS / "partner-mark.png", 11.0),
    (LOGOS / "partner-mark-2.png", 12.0),
]

PW, PH = landscape(A4)          # 297 x 210 mm
L, R = 24 * mm, PW - 24 * mm    # content edges
T = lambda d: PH - d * mm       # mm from the top -> page y

KICKER = {
    "participation": "CERTIFICATE OF PARTICIPATION",
    "winner": "CERTIFICATE · WINNING TEAM",
    "audience": "CERTIFICATE · AUDIENCE AWARD",
    "mentor": "CERTIFICATE OF APPRECIATION",
    "staff": "CERTIFICATE OF APPRECIATION",
    "staff lead": "CERTIFICATE OF APPRECIATION",
}
# (name, title, signature image: dark ink on transparent, cropped to the ink, printed height in mm)
SIGNERS = [("Charles Babbage", "Co-Founder & President, Example College", HERE / "sig_president.png", 14.0),
           ("Ada Lovelace", "Hackathon Lead, Example College", HERE / "sig_lead.png", 17.0)]

GOLD_LIGHT, GOLD, GOLD_DARK, GOLD_TEXT = hexc("#f4d983"), hexc("#d4a52a"), hexc("#8a6410"), hexc("#5c4005")


NB = "\u00a0"


def esc(s):
    """Escape for a Paragraph and keep the words of a name on one line."""
    s = (s or "").strip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return s.replace(" ", NB)


def team_label(team):
    """'2' -> 'Team 2'; a real team name stays as it is."""
    team = (team or "").strip()
    return f"Team {team}" if team.isdigit() else team


def body_text(kind, team, product):
    numbered = (team or "").strip().isdigit()
    team, product = esc(team_label(team)), esc(product)
    date = NB.join(["23\u201326", "October", "2026"])
    event = f"Example College’s first AI{NB}Entrepreneurship{NB}Hackathon, {date} at Example{NB}Campus"
    if kind == "participation":
        s = f"took part in {event}"
        with_team = f"with <b>{team}</b>" if numbered else f"with team <b>{team}</b>"
        if product and team:
            s += f", and built <b>{product}</b>, a working AI product, {with_team} in four days"
        elif team:
            s += f", and built a working AI product {with_team} in four days"
        else:
            s += ", and built a working AI product in four days"
        return s + "."
    if kind == "winner":
        s = f"was part of <b>{team or 'the winning team'}</b>, the winning team at {event}"
        if product:
            s += f", for building <b>{product}</b>"
        return s + "."
    if kind == "audience":
        s = f"was part of <b>{team or 'the team'}</b>, winner of the Audience Award at {event}"
        if product:
            s += f", for building <b>{product}</b>"
        return s + "."
    if kind == "staff lead":
        return (f"led the staff team at {event}, and kept the four days running smoothly for the teams, "
                f"mentors and guests.")
    if kind == "staff":
        return (f"was part of the staff team at {event}, and helped the four days run smoothly for the teams, "
                f"mentors and guests.")
    who = (f"<b>{team}</b>" if numbered else f"team <b>{team}</b>") if team else "the teams"
    return f"mentored {who} at {event}, and helped turn an idea into a working product in four days."


def arc_text(c, cx, cy, radius, text, font, size, track, color, top=True):
    """Text set along a circle: across the top (reading outward) or the bottom (upright)."""
    import math
    widths = [pdfmetrics.stringWidth(ch, font, size) + track for ch in text]
    total = sum(widths) - track
    c.setFillColorRGB(*color)
    c.setFont(font, size)
    theta = (math.pi / 2 + total / radius / 2) if top else (3 * math.pi / 2 - total / radius / 2)
    for ch, w in zip(text, widths):
        half = (w - track) / 2 / radius
        a = theta - half if top else theta + half
        c.saveState()
        c.translate(cx + radius * math.cos(a), cy + radius * math.sin(a))
        c.rotate(math.degrees(a) - 90 if top else math.degrees(a) + 90)
        c.drawCentredString(0, 0, ch)
        c.restoreState()
        theta = theta - w / radius if top else theta + w / radius


# ----------------------------------------------------------------- medals (3D look)
import math

STAMP_ALPHA = 0.78   # how solid the first-edition stamps print (1 = fully solid)

# light, mid, dark, deep, text, text_highlight
PALETTES = {
    "winner":        dict(light=hexc("#fbe9a6"), mid=hexc("#d8a62b"), dark=hexc("#9a6d0e"), deep=hexc("#5e4006"),
                          text=hexc("#4a3204"), glint=hexc("#fff3c4")),
    "participation": dict(light=hexc("#6f7cf0"), mid=hexc("#1f28b0"), dark=hexc("#10166f"), deep=hexc("#080b3d"),
                          text=hexc("#ffffff"), glint=hexc("#0a0e4a")),
    "audience":      dict(light=hexc("#dfe5ff"), mid=hexc("#7e98ff"), dark=hexc("#4a5fd0"), deep=hexc("#26338a"),
                          text=hexc("#10166f"), glint=hexc("#eef1ff")),
    "mentor":        dict(light=hexc("#f7f7f8"), mid=hexc("#c3c6cc"), dark=hexc("#80848c"), deep=hexc("#45484e"),
                          text=hexc("#1b1c20"), glint=hexc("#ffffff")),
}
PALETTES["staff"] = PALETTES["staff lead"] = PALETTES["mentor"]   # staff: the mentor look


def star(c, x, y, r, color):
    p = c.beginPath()
    for k in range(10):
        rr = r if k % 2 == 0 else r * 0.45
        a = math.pi / 2 + k * math.pi / 5
        (p.moveTo if k == 0 else p.lineTo)(x + rr * math.cos(a), y + rr * math.sin(a))
    p.close()
    c.setFillColorRGB(*color)
    c.drawPath(p, stroke=0, fill=1)


def serrated(c, cx, cy, r, teeth=64, depth=0.045):
    p = c.beginPath()
    for k in range(teeth * 2 + 1):
        a = math.pi * k / teeth
        rr = r if k % 2 == 0 else r * (1 - depth)
        (p.moveTo if k == 0 else p.lineTo)(cx + rr * math.cos(a), cy + rr * math.sin(a))
    p.close()
    return p


def ring_path(c, cx, cy, r_out, r_in):
    p = c.beginPath()
    p.circle(cx, cy, r_out)
    p.circle(cx, cy, r_in)
    return p


def fill_linear(c, path, x0, y0, x1, y1, colors, positions=None, even_odd=False):
    c.saveState()
    c.clipPath(path, stroke=0, fill=0, fillMode=0 if even_odd else 1)
    c.linearGradient(x0, y0, x1, y1, colors, positions=positions, extend=True)
    c.restoreState()


def fill_radial(c, path, x, y, radius, colors, positions=None, even_odd=False):
    c.saveState()
    c.clipPath(path, stroke=0, fill=0, fillMode=0 if even_odd else 1)
    c.radialGradient(x, y, radius, colors, positions=positions, extend=True)
    c.restoreState()


def soft_shadow(c, path_fn, dx, dy, steps=7, alpha=0.05, grow=0.35 * mm):
    """A soft drop shadow: the same shape, offset and stacked with low opacity."""
    c.saveState()
    c.setFillColorRGB(0, 0, 0)
    c.setFillAlpha(alpha)
    for k in range(steps, 0, -1):
        c.drawPath(path_fn(dx, dy, k * grow), stroke=0, fill=1)
    c.restoreState()


def embossed_text(c, x, y, text, font, size, track, pal):
    """Text pressed into metal: a thin glint on one side, the ink on top."""
    off = 0.35
    tracked(c, x + off, y - off, text, font, size, track, pal["glint"], "center")
    tracked(c, x, y, text, font, size, track, pal["text"], "center")


def ribbon(c, x0, y0, angle_deg, length, width, pal):
    a = math.radians(angle_deg)
    dx, dy = math.sin(a), -math.cos(a)
    nx, ny = math.cos(a), math.sin(a)
    hw, notch = width / 2, width * 0.55
    pts = [(x0 - nx * hw, y0 - ny * hw), (x0 + nx * hw, y0 + ny * hw),
           (x0 + nx * hw + dx * length, y0 + ny * hw + dy * length),
           (x0 + dx * (length - notch), y0 + dy * (length - notch)),
           (x0 - nx * hw + dx * length, y0 - ny * hw + dy * length)]

    def shape(ox=0, oy=0, g=0):
        p = c.beginPath()
        p.moveTo(pts[0][0] + ox, pts[0][1] + oy)
        for px, py in pts[1:]:
            p.lineTo(px + ox, py + oy)
        p.close()
        return p

    soft_shadow(c, lambda ox, oy, g: shape(ox, oy, g), 0.6 * mm, -0.8 * mm, steps=4, alpha=0.06)
    # shaded across its width: dark edges, light fold in the middle
    fill_linear(c, shape(), x0 - nx * hw, y0 - ny * hw, x0 + nx * hw, y0 + ny * hw,
                (pal["deep"], pal["mid"], pal["light"], pal["mid"], pal["dark"]), positions=(0, 0.3, 0.5, 0.7, 1))


def medal(c, cx, cy, r, kind, ribbons=False, stamp=False, label=None):
    """Embossed award seal: serrated metal edge, raised rim, curved text, recessed centre.
    stamp=True: a little see-through and slightly tilted, like an ink stamp (no shadow, no gloss).
    label: the word(s) in the centre, one per line, e.g. ["PARTICIPANT"] or ["BUSINESS", "MENTOR"]."""
    pal = PALETTES[kind]
    if stamp:
        c.saveState()
        c.translate(cx, cy)
        c.rotate(-9)
        c.translate(-cx, -cy)
        c.setFillAlpha(STAMP_ALPHA)
        c.setStrokeAlpha(STAMP_ALPHA)
    if ribbons:
        ribbon(c, cx - r * 0.35, cy - r * 0.55, -22, r * 1.25, r * 0.42, pal)
        ribbon(c, cx + r * 0.35, cy - r * 0.55, 22, r * 1.25, r * 0.42, pal)

    # drop shadow under the seal
    if not stamp:
        soft_shadow(c, lambda ox, oy, g: serrated(c, cx + ox, cy + oy, r + g), 0.9 * mm, -1.3 * mm)

    # 1. serrated edge: lit from the top left
    fill_radial(c, serrated(c, cx, cy, r), cx - r * 0.45, cy + r * 0.45, r * 1.7,
                (pal["light"], pal["mid"], pal["dark"]), positions=(0, 0.45, 1))
    # 2. raised outer rim: light on top, dark underneath
    fill_linear(c, ring_path(c, cx, cy, r * 0.90, r * 0.84), cx, cy + r, cx, cy - r,
                (pal["light"], pal["mid"], pal["deep"]), positions=(0, 0.5, 1), even_odd=True)
    # 3. text band
    fill_radial(c, ring_path(c, cx, cy, r * 0.84, r * 0.61), cx - r * 0.3, cy + r * 0.3, r * 1.3,
                (pal["light"], pal["mid"], pal["dark"]), positions=(0, 0.55, 1), even_odd=True)
    # 4. recessed inner rim: dark on top, light underneath (the opposite of a raised rim)
    fill_linear(c, ring_path(c, cx, cy, r * 0.61, r * 0.555), cx, cy + r, cx, cy - r,
                (pal["deep"], pal["mid"], pal["light"]), positions=(0, 0.5, 1), even_odd=True)
    # 5. centre disc with a soft highlight
    centre = c.beginPath()
    centre.circle(cx, cy, r * 0.555)
    fill_radial(c, centre, cx - r * 0.18, cy + r * 0.22, r * 0.75,
                (pal["light"], pal["mid"], pal["dark"]), positions=(0, 0.6, 1))
    # 6. glossy highlight, top left
    c.saveState()
    c.setFillColorRGB(1, 1, 1)
    c.setFillAlpha(0 if stamp else 0.18)
    hl = c.beginPath()
    hl.ellipse(cx - r * 0.62, cy + r * 0.12, r * 0.9, r * 0.55)
    clip = c.beginPath()
    clip.circle(cx, cy, r * 0.9)
    c.clipPath(clip, stroke=0, fill=0)
    c.drawPath(hl, stroke=0, fill=1)
    c.restoreState()

    # curved text and the two stars where it meets
    band = 7.6
    arc_text(c, cx, cy, r * 0.665, "AI ENTREPRENEURSHIP", "BC-B", band, 1.4, pal["text"], top=True)
    arc_text(c, cx, cy, r * 0.775, "HACKATHON  ·  2026", "BC-B", band, 1.4, pal["text"], top=False)
    for a in (math.pi, 0):
        star(c, cx + r * 0.715 * math.cos(a), cy + r * 0.715 * math.sin(a) + 0.4 * mm, 1.1 * mm, pal["text"])

    # centre text
    for k, dx in enumerate((-3.6 * mm, 0, 3.6 * mm)):
        star(c, cx + dx, cy + r * 0.30 + (0.8 * mm if k == 1 else 0), 1.3 * mm if k == 1 else 1.0 * mm, pal["text"])
    if kind == "winner":
        embossed_text(c, cx, cy - 2.4 * mm, "WINNER", "BC-XB", 19, 0.5, pal)
    else:
        # the role in the centre, shrunk to fit the disc
        lines = label or (["AUDIENCE", "AWARD"] if kind == "audience" else ["PARTICIPANT"])
        max_w = r * 0.98
        size = 15.0
        while size > 8 and max(text_width(s, "BC-XB", size, 0.05 * size) for s in lines) > max_w:
            size -= 0.25
        ys = [cy - 2.4 * mm] if len(lines) == 1 else [cy - 0.4 * mm, cy - 5.6 * mm]
        for s, y in zip(lines, ys):
            embossed_text(c, cx, y, s, "BC-XB", size, 0.05 * size, pal)
    if kind == "winner":
        c.setStrokeColorRGB(*pal["text"])
        c.setLineWidth(0.6)
        c.line(cx - 6 * mm, cy - 5.0 * mm, cx + 6 * mm, cy - 5.0 * mm)
    if stamp:
        c.restoreState()


# ------------------------------------------------- watermark and frame
# One colour per certificate type, for the guilloche watermark and the double frame.
TINT = {"winner": GOLD, "participation": BRAND, "audience": hexc("#4a5fd0"), "mentor": hexc("#5d6068")}
TINT["staff"] = TINT["staff lead"] = TINT["mentor"]
WATERMARK_TINT = dict(TINT, winner=hexc("#b08a1e"))   # the winner's light gold barely showed


def woven_ring(c, cx, cy, r0, amp, waves, strands, steps=1800):
    """A guilloche band: `strands` thin waves around a circle, each shifted a little, so they weave."""
    for k in range(strands):
        phase = 2 * math.pi * k / strands
        p = c.beginPath()
        for i in range(steps + 1):
            a = 2 * math.pi * i / steps
            r = r0 + amp * math.sin(waves * a + phase)
            (p.moveTo if i == 0 else p.lineTo)(cx + r * math.cos(a), cy + r * math.sin(a))
        c.drawPath(p, stroke=1, fill=0)


def watermark(c, kind):
    """Behind everything, very light: two woven guilloche rings and the Example College shield in the middle."""
    color = WATERMARK_TINT[kind]
    cx, cy = PW * 0.58, PH * 0.47
    c.saveState()
    c.setStrokeColorRGB(*color)
    c.setStrokeAlpha(0.16)
    c.setLineWidth(0.28)
    woven_ring(c, cx, cy, 64 * mm, 3.2 * mm, 30, 6)
    woven_ring(c, cx, cy, 47 * mm, 2.4 * mm, 22, 5)
    c.setStrokeAlpha(0.12)
    for r in (69 * mm, 41 * mm):
        c.circle(cx, cy, r, stroke=1, fill=0)
    c.restoreState()

    # the shield only (the left part of the logo), clipped out of the vector logo
    h = 60 * mm                                   # logo height; the shield is about 73% of it
    lw = h * LOGO_RATIO
    sw, sh = 0.205 * lw, 0.735 * h
    left, top = cx - sw / 2, cy + sh / 2
    c.saveState()
    clip = c.beginPath()
    clip.rect(left, top - sh, sw, sh)
    c.clipPath(clip, stroke=0, fill=0)
    c.setFillAlpha(0.075)
    draw_logo(c, left, top, h, color)
    c.restoreState()


def frame(c, kind):
    """A double frame (strong outer rule, fine inner rule) with small diamonds in the corners."""
    color = TINT[kind]
    if kind == "winner":
        outer, inner, w_out = GOLD, GOLD_DARK, 2.4
    else:
        outer, inner, w_out = color, color, 1.6
    c.setStrokeColorRGB(*outer)
    c.setLineWidth(w_out)
    c.rect(11 * mm, 11 * mm, PW - 22 * mm, PH - 22 * mm, stroke=1, fill=0)
    c.setStrokeColorRGB(*inner)
    c.setLineWidth(0.6)
    c.rect(13.4 * mm, 13.4 * mm, PW - 26.8 * mm, PH - 26.8 * mm, stroke=1, fill=0)
    c.setFillColorRGB(*outer)
    for x, y in ((13.4, 13.4), (PW / mm - 13.4, 13.4), (13.4, PH / mm - 13.4), (PW / mm - 13.4, PH / mm - 13.4)):
        d = c.beginPath()
        s = 2.0 * mm
        d.moveTo(x * mm, y * mm + s)
        d.lineTo(x * mm + s, y * mm)
        d.lineTo(x * mm, y * mm - s)
        d.lineTo(x * mm - s, y * mm)
        d.close()
        c.drawPath(d, stroke=0, fill=1)


def certificate(c, kind, first, last, team, product):
    watermark(c, kind)
    frame(c, kind)

    # Header: Example College lockup left (the main brand), Example Campus + Example Foundation right
    lockup(c, L, T(26), 11 * mm)
    partner_logos(c, R, T(37))

    # Kicker
    ks, kt = 17.5, 3.4
    kw = text_width(KICKER[kind], "BC-B", ks, kt)
    pad, bh = 5.0 * mm, 11.5 * mm
    by = T(66) - (bh - CAP * ks) / 2
    if kind == "winner":
        box = c.beginPath()
        box.rect(L, by, kw + 2 * pad, bh)
        c.saveState()
        c.clipPath(box, stroke=0, fill=0)
        c.linearGradient(L, by + bh, L + kw + 2 * pad, by, (GOLD_LIGHT, GOLD, GOLD_LIGHT), positions=(0, 0.55, 1), extend=True)
        c.restoreState()
        tracked(c, L + pad, T(66), KICKER[kind], "BC-B", ks, kt, GOLD_TEXT)
    elif kind == "audience":
        c.setFillColorRGB(*ACCENT)
        c.rect(L, by, kw + 2 * pad, bh, stroke=0, fill=1)
        tracked(c, L + pad, T(66), KICKER[kind], "BC-B", ks, kt, INK)
    else:
        c.setFillColorRGB(*(BRAND if kind == "participation" else INK))
        c.rect(L, by, kw + 2 * pad, bh, stroke=0, fill=1)
        tracked(c, L + pad, T(66), KICKER[kind], "BC-B", ks, kt, WHITE)

    # Name: FIRST in ExtraBold, LAST in Regular, one line, same size
    f, l = first.strip().upper(), (last or "").strip().upper()
    gap = " "
    full = f + gap + l
    max_w = R - L - 52 * mm if kind == "winner" else R - L
    size = 70
    while size > 30 and (text_width(f + gap, "BC-XB", size, 0.005 * size) + text_width(l, "BC-R", size, 0.01 * size)) > (R - L):
        size -= 0.5
    base = T(102)
    w = tracked(c, L, base, f + gap, "BC-XB", size, 0.005 * size, INK)
    tracked(c, L + w, base, l, "BC-R", size, 0.01 * size, INK)

    # Body
    style = ParagraphStyle("b", fontName="DM-R", fontSize=13.5, leading=20, textColor=INK)
    p = Paragraph(body_text(kind, team, product), style)
    bw = 190 * mm
    _, bh = p.wrap(bw, 60 * mm)
    p.drawOn(c, L, T(112) - bh)

    # Signatures: the printed signature sits on the line, a little over it like a real one
    line_y = T(158)
    for k, (name, title, sig, sig_h) in enumerate(SIGNERS):
        x = L + k * 84 * mm
        img = ImageReader(str(sig))
        iw, ih = img.getSize()
        h = sig_h * mm
        w = h * iw / ih
        if w > 62 * mm:
            w, h = 62 * mm, 62 * mm * ih / iw
        c.drawImage(img, x + 2 * mm, line_y - 1.5 * mm, w, h, mask="auto")
        c.setStrokeColorRGB(*INK)
        c.setLineWidth(0.6)
        c.line(x, line_y, x + 70 * mm, line_y)
        c.setFillColorRGB(*INK)
        c.setFont("DM-SB", 10)
        c.drawString(x, line_y - 5.5 * mm, name)
        c.setFont("DM-R", 8.5)
        c.drawString(x, line_y - 10 * mm, title)

    if kind == "winner":
        medal(c, R - 27 * mm, T(148), 23 * mm, kind, ribbons=True)
    else:
        label = {"participation": ["PARTICIPANT"], "audience": ["AUDIENCE", "AWARD"],
                 "staff": ["STAFF"], "staff lead": ["STAFF", "LEAD"]}.get(kind)
        if kind == "mentor":                     # a mentor without a team is a business mentor
            label = ["MENTOR"] if (team or "").strip() else ["BUSINESS", "MENTOR"]
        medal(c, R - 26 * mm, T(160), 23 * mm, kind, stamp=True, label=label)


def partner_logos(c, right, base):
    """Example Campus + Example Foundation, right-aligned in the header, bottoms on `base`,
    a hairline between them, no wording."""
    items = []
    for path, h_mm in PARTNER_LOGOS:
        img = ImageReader(str(path))
        iw, ih = img.getSize()
        items.append((img, h_mm * mm * iw / ih, h_mm * mm))
    gap = 7 * mm
    x = right - sum(w for _, w, _ in items) - gap * (len(items) - 1)
    for k, (img, w, h) in enumerate(items):
        if k:
            c.setStrokeColorRGB(*LIGHT)
            c.setLineWidth(0.5)
            c.line(x - gap / 2, base + 0.5 * mm, x - gap / 2, base + 10.5 * mm)
        c.drawImage(img, x, base, w, h, mask="auto")
        x += w + gap


def main(src, out):
    make(list(csv.DictReader(open(src, encoding="utf-8"))), out)


def make(rows, out):
    """rows: dicts with type, first, last, team, product."""
    c = canvas.Canvas(out, pagesize=(PW, PH), initialFontName="DM-R")
    c.setTitle("AI Entrepreneurship Hackathon - certificates")
    for r in rows:
        certificate(c, r["type"].strip().lower(), r["first"], r["last"], r.get("team", ""), r.get("product", ""))
        c.showPage()
    c.save()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
