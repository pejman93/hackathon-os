"""Direction signs for the venue, A4 and A3."""
import math
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, A3, landscape
from reportlab.lib.units import mm
from brand import *

# direction: "right", "left" or "up-right";  room: adds the word ROOM
SIGNS = [
    dict(direction="right", room=False),
    dict(direction="right", room=False),
    dict(direction="up-right", room=True, floor="2ND FLOOR"),
    dict(direction="left", room=True),
    dict(direction="left", room=False),
]

W, H = landscape(A4)            # design size; A3 is the same drawing scaled up
INSET = 8 * mm                  # white frame: printers can't print to the paper edge anyway


def arrow(c, cx, cy, length, angle_deg, color):
    """A bold signage arrow centred on (cx, cy), pointing at angle_deg (0 = right)."""
    L, t, hh = length, length * 0.26, length * 0.62    # length, shaft thickness, head height
    head = L * 0.46                                     # head depth
    pts = [(-L / 2, -t / 2), (L / 2 - head, -t / 2), (L / 2 - head, -hh / 2), (L / 2, 0),
           (L / 2 - head, hh / 2), (L / 2 - head, t / 2), (-L / 2, t / 2)]
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    p = c.beginPath()
    for k, (x, y) in enumerate(pts):
        X, Y = cx + x * ca - y * sa, cy + x * sa + y * ca
        (p.moveTo if k == 0 else p.lineTo)(X, Y)
    p.close()
    c.setFillColorRGB(*color)
    c.drawPath(p, stroke=0, fill=1)


def band(c, x_bottom, width, top, bottom, slope=0.27):
    shift = (top - bottom) * slope
    p = c.beginPath()
    p.moveTo(x_bottom, bottom)
    p.lineTo(x_bottom + width, bottom)
    p.lineTo(x_bottom + width + shift, top)
    p.lineTo(x_bottom + shift, top)
    p.close()
    return p


def sign(c, direction, room, floor=None):
    """High-contrast wayfinding: a solid Example College-blue arrow panel with a huge white arrow, cut off by
    the slash from the logo lockup, and the words in ink on white."""
    px, py, pw, ph = INSET, INSET, W - 2 * INSET, H - 2 * INSET
    left_side = direction == "left"
    slant = ph * 0.27                       # same lean as the slash in the lockup

    # arrow panel, edge to the inset frame, slanted inner edge
    p = c.beginPath()
    if left_side:
        x_bot = px + 92 * mm                # inner edge at the bottom; top is further right ("/")
        p.moveTo(px, py); p.lineTo(x_bot, py); p.lineTo(x_bot + slant, py + ph); p.lineTo(px, py + ph)
    else:
        x_bot = px + pw - 126 * mm
        p.moveTo(x_bot, py); p.lineTo(px + pw, py); p.lineTo(px + pw, py + ph); p.lineTo(x_bot + slant, py + ph)
    p.close()
    c.setFillColorRGB(*BRAND)
    c.drawPath(p, stroke=0, fill=1)
    # a thin light-blue echo of the slash, just inside the white side
    e = c.beginPath()
    off = 7 * mm if left_side else -7 * mm
    w_ = 3 * mm
    xb = x_bot + off + (0 if left_side else -w_)
    e.moveTo(xb, py); e.lineTo(xb + w_, py); e.lineTo(xb + w_ + slant, py + ph); e.lineTo(xb + slant, py + ph)
    e.close()
    c.setFillColorRGB(*ACCENT)
    c.drawPath(e, stroke=0, fill=1)

    # the arrow, white on blue
    acy = py + ph / 2
    if left_side:
        acx, ang, length = px + (x_bot + slant / 2 - px) / 2, 180, 84 * mm
    elif direction == "right":
        acx, ang, length = (x_bot + slant / 2 + px + pw) / 2 + 3 * mm, 0, 82 * mm
    else:
        acx, ang, length = (x_bot + slant / 2 + px + pw) / 2 + 4 * mm, 45, 80 * mm
    arrow(c, acx, acy, length, ang, WHITE)

    # words, ink on white
    if left_side:
        t_left = x_bot + slant + 16 * mm
        t_right = px + pw - 16 * mm
    else:
        t_left = px + 16 * mm
        t_right = x_bot - 16 * mm
    text_w = t_right - t_left
    tx, anchor = (t_right, "right") if left_side else (t_left, "left")
    s1 = fit_size("AI ENTREPRENEURSHIP", "BC-XB", text_w, 200, 20, 0.01)
    s2 = fit_size("HACKATHON", "BC-XB", text_w, 220, 20, 0.01)
    tag_h = 20 * mm if room else 0
    gap = 5 * mm
    block = CAP * s1 + gap + CAP * s2 + ((gap + tag_h) if room else 0)
    y = acy + block / 2 - CAP * s1
    tracked(c, tx, y, "AI ENTREPRENEURSHIP", "BC-XB", s1, 0.01 * s1, BRAND, anchor)
    y -= gap + CAP * s2
    tracked(c, tx, y, "HACKATHON", "BC-XB", s2, 0.01 * s2, INK, anchor)
    if room:
        ts = 40
        label_w = text_width("ROOM", "BC-XB", ts, 0.18 * ts)
        tag_w = label_w + 14 * mm
        tag_x = (t_right - tag_w) if left_side else t_left
        tag_y = y - gap - tag_h
        c.setFillColorRGB(*INK)
        c.roundRect(tag_x, tag_y, tag_w, tag_h, tag_h / 2, stroke=0, fill=1)
        tracked(c, tag_x + tag_w / 2, tag_y + tag_h / 2 - CAP * ts / 2, "ROOM", "BC-XB", ts, 0.18 * ts, WHITE, "center")
        if floor:
            # a second pill beside ROOM, in Example College blue
            fw = text_width(floor, "BC-XB", ts, 0.12 * ts) + 14 * mm
            fx = (tag_x - 4 * mm - fw) if left_side else (tag_x + tag_w + 4 * mm)
            c.setFillColorRGB(*BRAND)
            c.roundRect(fx, tag_y, fw, tag_h, tag_h / 2, stroke=0, fill=1)
            tracked(c, fx + fw / 2, tag_y + tag_h / 2 - CAP * ts / 2, floor, "BC-XB", ts, 0.12 * ts, WHITE, "center")

    # Example College logo, original blue, in the white corner
    logo_h = 10 * mm
    lw = logo_h * LOGO_RATIO
    lx = (t_right - lw) if left_side else t_left
    draw_logo(c, lx, py + 12 * mm + logo_h, logo_h, BRAND)

    # thin frame line so the white side reads as a sign, not a blank page
    c.setStrokeColorRGB(*INK)
    c.setLineWidth(1.2)
    c.roundRect(px, py, pw, ph, 0, stroke=1, fill=0)


def make(out, pagesize):
    pw, ph = landscape(pagesize)
    k = pw / W
    c = canvas.Canvas(out, pagesize=(pw, ph), initialFontName="DM-R")
    c.setTitle("AI Entrepreneurship Hackathon - direction signs")
    for s in SIGNS:
        c.saveState()
        c.scale(k, k)
        sign(c, s["direction"], s["room"], s.get("floor"))
        c.restoreState()
        c.showPage()
    c.save()


if __name__ == "__main__":
    make(sys.argv[1], A4)
    make(sys.argv[2], A3)
