"""Sheets of TEAM 1 to TEAM 4 stickers on Avery Zweckform L4785 labels."""
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from brand import *
from team_stickers import W, H, XS, YS, BLEED, SAFE
from team_desk import TEAMS, band


def sticker(c, ox, oy, number, color):
    """(ox, oy) = bottom-left corner of the label in points."""
    ax, ay = ox - BLEED * mm, oy - BLEED * mm
    aw, ah = (W + 2 * BLEED) * mm, (H + 2 * BLEED) * mm
    c.saveState()
    clip = c.beginPath()
    clip.rect(ax, ay, aw, ah)
    c.clipPath(clip, stroke=0, fill=0)
    c.setFillColorRGB(*INK)
    c.rect(ax, ay, aw, ah, stroke=0, fill=1)
    # the slash: a thin accent line, then the team-colour band behind the number
    c.setFillColorRGB(*ACCENT)
    c.drawPath(band(c, ox + 30 * mm, 1.6 * mm, ay, ay + ah), stroke=0, fill=1)
    c.setFillColorRGB(*color)                      # team colour from the slash to the right edge
    c.drawPath(band(c, ox + 35 * mm, 70 * mm, ay, ay + ah), stroke=0, fill=1)
    c.restoreState()

    # number: ink on the team colour, right-aligned in the safe area, 36 mm tall
    size = 36 * mm / CAP
    mid_y = oy + H * mm / 2
    tracked(c, ox + (W - SAFE) * mm, mid_y - CAP * size / 2, number, "BC-XB", size, 0, INK, "right")

    # TEAM, cream, on the black
    left = ox + SAFE * mm
    tracked(c, left, mid_y - CAP * 30 / 2, "TEAM", "BC-XB", 30, 0.6, PAPER)


def make(out, scale=1.0):
    pw, ph = A4
    c = canvas.Canvas(out, pagesize=A4, initialFontName="DM-R")
    c.setTitle("AI Entrepreneurship Hackathon - team number stickers (Avery L4785)")
    for number, color in TEAMS:
        c.saveState()
        apply_scale(c, pw, ph, scale)
        for j in range(len(XS) * len(YS)):
            col, row = j % 2, j // 2
            sticker(c, XS[col] * mm, ph - (YS[row] + H) * mm, number, color)
        c.restoreState()
        c.showPage()
    c.save()


if __name__ == "__main__":
    sc = next((float(a.split("=")[1]) for a in sys.argv if a.startswith("--scale=")), 1.0)
    make(sys.argv[1], sc)
