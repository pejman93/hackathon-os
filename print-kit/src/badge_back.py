"""The back of the lanyard badge: event facts and a QR code, four to an A4 sheet."""
import json
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from brand import *
from lanyard import CW, CH, X0, Y0, BLEED, M, PANEL, PUNCH_Y

QR = json.load(open(HERE / "qr_hackathon.json"))


def band(c, x_top, width, top, bottom, slope=0.27):
    """Slanted band leaning the other way from the front (as if seen from behind)."""
    shift = (top - bottom) * slope
    p = c.beginPath()
    p.moveTo(x_top, top)
    p.lineTo(x_top + width, top)
    p.lineTo(x_top + width + shift, bottom)
    p.lineTo(x_top + shift, bottom)
    p.close()
    return p


def qr(c, x, y, size):
    """The QR code as solid squares, (x, y) = bottom-left, `size` = width of the code itself."""
    mods = QR["modules"]
    n = len(mods)
    s = size / n
    c.setFillColorRGB(*INK)
    for r, row in enumerate(mods):
        run = None
        for col, v in enumerate(row + [0]):
            if v and run is None:
                run = col
            elif not v and run is not None:
                c.rect(x + run * s, y + size - (r + 1) * s, (col - run) * s + 0.05, s + 0.05, stroke=0, fill=1)
                run = None


def back(c, ox, oy, clip_rect):
    T = lambda d: oy + CH - d * mm
    bx, by, bw, bh = clip_rect

    # background: Example College blue with an ink band and a thin light-blue band
    c.saveState()
    clip = c.beginPath()
    clip.rect(bx, by, bw, bh)
    c.clipPath(clip, stroke=0, fill=0)
    c.setFillColorRGB(*BRAND)
    c.rect(bx, by, bw, bh, stroke=0, fill=1)
    top, bottom = oy + CH + BLEED, oy - BLEED
    c.setFillColorRGB(*INK)
    c.drawPath(band(c, ox + 0.69 * CW, 0.34 * CW, top, bottom), stroke=0, fill=1)
    c.setFillColorRGB(*ACCENT)
    c.drawPath(band(c, ox + 0.625 * CW, 0.035 * CW, top, bottom), stroke=0, fill=1)
    c.restoreState()

    cx = ox + CW / 2
    x = ox + M

    # punch mark
    c.setStrokeColorRGB(*PAPER)
    c.setLineWidth(0.4)
    c.line(cx - 2 * mm, T(PUNCH_Y), cx + 2 * mm, T(PUNCH_Y))
    c.line(cx, T(PUNCH_Y) - 2 * mm, cx, T(PUNCH_Y) + 2 * mm)

    # header
    lockup(c, x, T(15), 5.0 * mm, logo_color=WHITE, text_color=WHITE)

    # the college's line, small: the back is the quiet side of the badge
    tracked(c, x, T(40), "We educate", "DD-B", 12, -0.1, WHITE)
    tracked(c, x, T(45.2), "the entrepreneurs", "DD-B", 12, -0.1, WHITE)
    tracked(c, x, T(50.4), "of the future.", "DD-B", 12, -0.1, WHITE)
    tracked(c, x, T(56.5), "23–26 October 2026  ·  Example Campus", "DM-M", 7.2, 0, ACCENT)

    # QR code on a cream card, dark on light so every phone reads it
    chip = 22 * mm
    qx, qy = x, T(64) - chip
    c.setFillColorRGB(*PANEL)
    c.roundRect(qx, qy, chip, chip, 2 * mm, stroke=0, fill=1)
    n = len(QR["modules"])
    code = chip - 2 * 4 * (chip / (n + 8))          # 4-module quiet zone all round
    qr(c, qx + (chip - code) / 2, qy + (chip - code) / 2, code)
    tracked(c, x, qy - 4 * mm, "example.org/hackathon", "DM-SB", 6.5, 0, ACCENT)

    # the college
    c.setStrokeColorRGB(*ACCENT)
    c.setLineWidth(0.5)
    c.line(x, T(121), x + 40 * mm, T(121))
    tracked(c, x, T(126), "Example College of Business and Technology", "DM-SB", 7.2, 0, WHITE)
    tracked(c, x, T(130), "1 Example Street  ·  10115 Berlin", "DM-R", 6.6, 0, PAPER)
    tracked(c, x, T(133.6), "example.org", "DM-R", 6.6, 0, ACCENT)


def make(out, scale=1.0):
    pw, ph = A4
    c = canvas.Canvas(out, pagesize=A4, initialFontName="DM-R")
    c.setTitle("AI Entrepreneurship Hackathon - badge backs")
    c.saveState()
    apply_scale(c, pw, ph, scale)
    for j in range(4):
        col, row = j % 2, j // 2
        ox = X0 + col * CW
        oy = ph - Y0 - (row + 1) * CH
        l = BLEED if col == 0 else 0
        r = BLEED if col == 1 else 0
        t = BLEED if row == 0 else 0
        b = BLEED if row == 1 else 0
        back(c, ox, oy, (ox - l, oy - b, CW + l + r, CH + t + b))
    c.restoreState()
    c.showPage()
    c.save()


if __name__ == "__main__":
    sc = next((float(a.split("=")[1]) for a in sys.argv if a.startswith("--scale=")), 1.0)
    make(sys.argv[1], sc)
