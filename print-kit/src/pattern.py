"""A4 pattern page: the logo lockup repeated, for printing on the back of notes and handouts."""
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from brand import *

H = 14 * mm                      # height of each lockup
ROW = 30 * mm                    # distance between rows
ANGLE = 0                        # straight rows read sharpest


def make(out):
    pw, ph = A4
    c = canvas.Canvas(out, pagesize=A4, initialFontName="DM-R")
    c.setTitle("AI Entrepreneurship Hackathon - pattern page")
    # draw the lockup once as a reusable form, then place it many times (keeps the file small)
    # full-strength brand colours: Example College blue logo, black words
    c.beginForm("lockup")
    width = lockup(c, 0, H, H, logo_color=BRAND, text_color=INK, font="BC-XB")
    c.endForm()
    step = width + 18 * mm
    c.saveState()
    c.translate(pw / 2, ph / 2)
    c.rotate(ANGLE)
    span = (pw ** 2 + ph ** 2) ** 0.5 / 2 + step      # cover the page whatever the angle
    row, y = 0, -span
    while y < span:
        x = -span - (step / 2 if row % 2 else 0)
        while x < span:
            c.saveState()
            c.translate(x, y)
            c.doForm("lockup")
            c.restoreState()
            x += step
        y += ROW
        row += 1
    c.restoreState()
    c.showPage()
    c.save()


if __name__ == "__main__":
    make(sys.argv[1])
