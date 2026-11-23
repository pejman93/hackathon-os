"""Team desk signs: a fold-over tent, a flat A4 and an upright A4 version."""
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from brand import *

TEAMS = [
    ("1", hexc("#E69F00")),   # orange
    ("2", hexc("#009E73")),   # green
    ("3", hexc("#CC79A7")),   # pink
    ("4", hexc("#F0E442")),   # yellow
]

PW, PH = landscape(A4)            # 297 x 210 mm
FACE_H = PH / 2                   # each side of the tent: 297 x 105 mm
EDGE = 7 * mm                     # printers can't print to the paper edge


def band(c, x_bottom, width, bottom, top, slope=0.27):
    shift = (top - bottom) * slope
    p = c.beginPath()
    p.moveTo(x_bottom, bottom)
    p.lineTo(x_bottom + width, bottom)
    p.lineTo(x_bottom + width + shift, top)
    p.lineTo(x_bottom + shift, top)
    p.close()
    return p


def face(c, number, color):
    """One side of the tent, drawn upright with (0, 0) at the bottom-left of the face.
    The bottom of the face is the table edge; the top is the fold."""
    x0, x1 = EDGE, PW - EDGE
    y0, y1 = EDGE, FACE_H                  # no margin at the fold: the colour runs over it
    c.saveState()
    clip = c.beginPath()
    clip.rect(x0, y0, x1 - x0, y1 - y0)
    c.clipPath(clip, stroke=0, fill=0)
    c.setFillColorRGB(*color)
    c.rect(x0, y0, x1 - x0, y1 - y0, stroke=0, fill=1)
    # the slash from the logo lockup: a soft white band behind the number and a thin ink one
    c.setFillColorRGB(1, 1, 1)
    c.setFillAlpha(0.28)
    c.drawPath(band(c, x1 - 118 * mm, 70 * mm, y0, y1), stroke=0, fill=1)
    c.setFillAlpha(1)
    c.setFillColorRGB(*INK)
    c.drawPath(band(c, x1 - 128 * mm, 4 * mm, y0, y1), stroke=0, fill=1)
    c.restoreState()

    # the big number, ink, in the white band
    size = 245
    tracked(c, x1 - 52 * mm, y0 + 11 * mm, number, "BC-XB", size, 0, INK, "center")

    # left: logo lockup, TEAM, and a white strip to write the team name on
    left = x0 + 12 * mm
    lockup(c, left, y1 - 9 * mm, 7 * mm, logo_color=INK, text_color=INK)
    tracked(c, left, y0 + 40 * mm, f"TEAM {number}", "BC-XB", 92, 1.2, INK)
    # write-on strip
    sw, sh = 128 * mm, 17 * mm
    c.setFillColorRGB(1, 1, 1)
    c.roundRect(left, y0 + 10 * mm, sw, sh, sh / 2, stroke=0, fill=1)
    tracked(c, left + 7 * mm, y0 + 10 * mm + sh / 2 - CAP * 7 / 2, "TEAM NAME", "DM-SB", 7, 1.6, GREY)


def flat(c, number, color):
    """The same design on a full A4 landscape page, for standing in a holder or taping up."""
    x0, x1, y0, y1 = EDGE, PW - EDGE, EDGE, PH - EDGE
    c.saveState()
    clip = c.beginPath()
    clip.rect(x0, y0, x1 - x0, y1 - y0)
    c.clipPath(clip, stroke=0, fill=0)
    c.setFillColorRGB(*color)
    c.rect(x0, y0, x1 - x0, y1 - y0, stroke=0, fill=1)
    c.setFillColorRGB(1, 1, 1)
    c.setFillAlpha(0.28)
    c.drawPath(band(c, x1 - 150 * mm, 88 * mm, y0, y1), stroke=0, fill=1)
    c.setFillAlpha(1)
    c.setFillColorRGB(*INK)
    c.drawPath(band(c, x1 - 162 * mm, 5 * mm, y0, y1), stroke=0, fill=1)
    c.restoreState()

    tracked(c, x1 - 58 * mm, y0 + 22 * mm, number, "BC-XB", 440, 0, INK, "center")

    left = x0 + 14 * mm
    lockup(c, left, y1 - 14 * mm, 10 * mm, logo_color=INK, text_color=INK)
    tracked(c, left, y0 + 62 * mm, f"TEAM {number}", "BC-XB", 100, 1.3, INK)
    sw, sh = 104 * mm, 24 * mm
    c.setFillColorRGB(1, 1, 1)
    c.roundRect(left, y0 + 20 * mm, sw, sh, sh / 2, stroke=0, fill=1)
    tracked(c, left + 9 * mm, y0 + 20 * mm + sh / 2 - CAP * 8 / 2, "TEAM NAME", "DM-SB", 8, 1.8, GREY)


def portrait(c, number, color):
    """Upright A4 version: logo at the top, TEAM, the giant number, and the name strip."""
    pw, ph = A4
    x0, x1, y0, y1 = EDGE, pw - EDGE, EDGE, ph - EDGE
    cx = pw / 2
    c.saveState()
    clip = c.beginPath()
    clip.rect(x0, y0, x1 - x0, y1 - y0)
    c.clipPath(clip, stroke=0, fill=0)
    c.setFillColorRGB(*color)
    c.rect(x0, y0, x1 - x0, y1 - y0, stroke=0, fill=1)
    # the slash, running through the number
    c.setFillColorRGB(1, 1, 1)
    c.setFillAlpha(0.28)
    c.drawPath(band(c, cx - 80 * mm, 92 * mm, y0, y1, slope=0.14), stroke=0, fill=1)
    c.setFillAlpha(1)
    c.setFillColorRGB(*INK)
    c.drawPath(band(c, x0 + 1 * mm, 5 * mm, y0, y1, slope=0.14), stroke=0, fill=1)
    c.restoreState()

    # logo lockup, centred at the top
    lh = 11 * mm
    c.saveState()
    c.translate(-10000, 0)
    lw = lockup(c, 0, 0, lh)          # measure only (drawn off the page)
    c.restoreState()
    lockup(c, cx - lw / 2, y1 - 14 * mm, lh, logo_color=INK, text_color=INK)

    tracked(c, cx, y1 - 64 * mm, "TEAM", "BC-XB", 120, 6, INK, "center")
    tracked(c, cx, y0 + 58 * mm, number, "BC-XB", 520, 0, INK, "center")

    sw, sh = 150 * mm, 26 * mm
    c.setFillColorRGB(1, 1, 1)
    c.roundRect(cx - sw / 2, y0 + 18 * mm, sw, sh, sh / 2, stroke=0, fill=1)
    tracked(c, cx, y0 + 18 * mm + sh / 2 - CAP * 8 / 2, "TEAM NAME", "DM-SB", 8, 1.8, GREY, "center")


def make_portrait(out):
    c = canvas.Canvas(out, pagesize=A4, initialFontName="DM-R")
    c.setTitle("AI Entrepreneurship Hackathon - team desk signs (upright)")
    for number, color in TEAMS:
        portrait(c, number, color)
        c.showPage()
    c.save()


def make_flat(out):
    c = canvas.Canvas(out, pagesize=(PW, PH), initialFontName="DM-R")
    c.setTitle("AI Entrepreneurship Hackathon - team desk signs (flat)")
    for number, color in TEAMS:
        flat(c, number, color)
        c.showPage()
    c.save()


def fold_marks(c):
    c.setStrokeColorRGB(*GREY)
    c.setLineWidth(0.4)
    y = FACE_H
    c.line(0.5 * mm, y, EDGE - 1.5 * mm, y)
    c.line(PW - EDGE + 1.5 * mm, y, PW - 0.5 * mm, y)
    c.setFont("DM-R", 5.5)
    c.setFillColorRGB(*GREY)
    c.drawString(1 * mm, y + 1.2 * mm, "fold")


def make(out):
    c = canvas.Canvas(out, pagesize=(PW, PH), initialFontName="DM-R")
    c.setTitle("AI Entrepreneurship Hackathon - team desk signs")
    for number, color in TEAMS:
        # bottom half: upright
        face(c, number, color)
        # top half: the same face turned 180 degrees, so it reads upright once folded
        c.saveState()
        c.translate(PW, PH)
        c.rotate(180)
        face(c, number, color)
        c.restoreState()
        fold_marks(c)
        c.showPage()
    c.save()


if __name__ == "__main__":
    make(sys.argv[1])
    if len(sys.argv) > 2:
        make_flat(sys.argv[2])
