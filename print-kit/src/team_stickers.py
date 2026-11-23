"""Team-name stickers on Avery Zweckform L4785 labels, with a plain-paper check version."""
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from brand import *

W, H, R = 80, 50, 4
XS, YS = (18, 113), (13, 68, 123, 178, 233)
BLEED, SAFE = 3, 5


def sticker(c, ox, oy, team, check=False):
    """(ox, oy) = bottom-left corner of the label in points."""
    if check:
        c.setStrokeColorRGB(*GREY)
        c.setLineWidth(0.3)
        c.setDash(2, 2)
        c.roundRect(ox, oy, W * mm, H * mm, R * mm, stroke=1, fill=0)
        c.setDash()
    else:
        c.setFillColorRGB(*INK)
        c.rect(ox - BLEED * mm, oy - BLEED * mm, (W + 2 * BLEED) * mm, (H + 2 * BLEED) * mm, stroke=0, fill=1)
    if not team:
        return
    text_c = INK if check else PAPER
    left, top, bottom = ox + SAFE * mm, oy + (H - SAFE) * mm, oy + SAFE * mm
    usable = (W - 2 * SAFE) * mm

    tracked(c, left, top - CAP * 9, "TEAM", "BC-B", 9, 2.2, INK if check else ACCENT)

    words = team.strip().upper()
    one = fit_size(words, "BC-XB", usable, 42, 10, 0.005)
    lines, size = [words], one
    if one < 30 and " " in words:
        # two lines, split where the halves are most even, if that prints bigger
        parts = words.split(" ")
        best = min(range(1, len(parts)), key=lambda k: abs(len(" ".join(parts[:k])) - len(" ".join(parts[k:]))))
        two = [" ".join(parts[:best]), " ".join(parts[best:])]
        two_size = min(fit_size(l, "BC-XB", usable, 32, 10, 0.005) for l in two)
        if two_size > one:
            lines, size = two, two_size
    lead = size * 0.98
    for k, line in enumerate(reversed(lines)):
        tracked(c, left, bottom + k * lead, line, "BC-XB", size, 0.005 * size, text_c)


def main(src, out, scale=1.0, check=False):
    make([l.rstrip("\n") for l in open(src, encoding="utf-8") if l.strip()], out, scale, check)


def make(teams, out, scale=1.0, check=False):
    """teams: a list with one entry per sticker (repeat a name for more copies)."""
    pw, ph = A4
    c = canvas.Canvas(out, pagesize=A4, initialFontName="DM-R")
    c.setTitle("AI Entrepreneurship Hackathon - team stickers (Avery L4785)")
    per = len(XS) * len(YS)
    for i in range(0, max(len(teams), 1), per):
        c.saveState()
        apply_scale(c, pw, ph, scale)
        for j, team in enumerate(teams[i:i + per]):
            col, row = j % 2, j // 2
            ox = XS[col] * mm
            oy = ph - (YS[row] + H) * mm
            sticker(c, ox, oy, team, check)
        c.restoreState()
        if check:
            c.setFont("DM-R", 6.5)
            c.setFillColorRGB(*GREY)
            c.drawCentredString(pw / 2, 5 * mm, "ALIGNMENT CHECK - plain paper only. Hold against a label sheet in front of a window.")
        c.showPage()
    c.save()


if __name__ == "__main__":
    sc = next((float(a.split("=")[1]) for a in sys.argv if a.startswith("--scale=")), 1.0)
    main(sys.argv[1], sys.argv[2], sc, "--check" in sys.argv)
