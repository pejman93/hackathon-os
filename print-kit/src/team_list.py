"""A two-sided A4 list of the teams and who is in each."""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from brand import *
from team_desk import TEAMS, band

PW, PH = A4
EDGE = 7 * mm
M = 16 * mm                      # content margin from the paper edge
CARD = hexc("#0d1170")           # darker Example College blue for the cards


def background(c):
    x0, x1, y0, y1 = EDGE, PW - EDGE, EDGE, PH - EDGE
    c.saveState()
    clip = c.beginPath()
    clip.rect(x0, y0, x1 - x0, y1 - y0)
    c.clipPath(clip, stroke=0, fill=0)
    c.setFillColorRGB(*BRAND)
    c.rect(x0, y0, x1 - x0, y1 - y0, stroke=0, fill=1)
    c.setFillColorRGB(1, 1, 1)
    c.setFillAlpha(0.06)
    c.drawPath(band(c, PW - 120 * mm, 70 * mm, y0, y1, slope=0.2), stroke=0, fill=1)
    c.setFillAlpha(1)
    c.setFillColorRGB(*ACCENT)
    c.drawPath(band(c, PW - 132 * mm, 2 * mm, y0, y1, slope=0.2), stroke=0, fill=1)
    c.restoreState()
    lockup(c, M, PH - 17 * mm, 9 * mm, logo_color=WHITE, text_color=WHITE)


def by_team(rows):
    teams = {}
    for r in rows:
        t = teams.setdefault(r["team"], {"mentor": "", "members": []})
        if r["role"].lower() == "mentor":
            t["mentor"] = r["name"]
        else:
            t["members"].append(r["name"])
    return teams


def page_meet(c, teams):
    background(c)
    top = PH - 44 * mm
    tracked(c, M, top, "23–26 OCTOBER 2026  ·  TEAMS AND MENTORS", "DM-SB", 9, 2.2, ACCENT)
    tracked(c, M, top - 27 * mm, "MEET YOUR TEAMS", "BC-XB", fit_size("MEET YOUR TEAMS", "BC-XB", PW - 2 * M, 80, 30), 0, PAPER)

    gap = 7 * mm
    cw = (PW - 2 * M - gap) / 2
    ch = 101 * mm
    y_first = top - 36 * mm                      # top of the first row of cards
    for k, (number, color) in enumerate(TEAMS):
        t = teams.get(number, {"mentor": "", "members": []})
        col, row = k % 2, k // 2
        x = M + col * (cw + gap)
        ytop = y_first - row * (ch + gap)
        # card body
        c.setFillColorRGB(*CARD)
        c.roundRect(x, ytop - ch, cw, ch, 4 * mm, stroke=0, fill=1)
        # team-colour header (rounded top, square bottom)
        hh = 19 * mm
        c.setFillColorRGB(*color)
        c.roundRect(x, ytop - hh, cw, hh, 4 * mm, stroke=0, fill=1)
        c.rect(x, ytop - hh, cw, 5 * mm, stroke=0, fill=1)
        tracked(c, x + 7 * mm, ytop - hh + (hh - CAP * 40) / 2, f"TEAM {number}", "BC-XB", 40, 0.4, INK)
        # mentor
        px = x + 7 * mm
        y = ytop - hh - 9 * mm
        tracked(c, px, y, "MENTOR", "DM-SB", 7.5, 2, ACCENT)
        y -= 10 * mm
        tracked(c, px, y, t["mentor"].upper(), "BC-XB", fit_size(t["mentor"].upper(), "BC-XB", cw - 14 * mm, 30, 14), 0.3, PAPER)
        y -= 5 * mm
        c.setStrokeColorRGB(*ACCENT)
        c.setLineWidth(0.6)
        c.line(px, y, x + cw - 7 * mm, y)
        # members
        y -= 9 * mm
        lead = min(7.4 * mm, (y - (ytop - ch + 6 * mm)) / max(len(t["members"]) - 1, 1))
        for name in t["members"]:
            tracked(c, px, y, name, "DM-M", fit_size(name, "DM-M", cw - 14 * mm, 15, 9), 0, WHITE)
            y -= lead


def page_building(c, teams):
    background(c)
    # the message, big
    size = min(fit_size(l, "BC-XB", PW - 2 * M, 140, 40) for l in ("THESE PEOPLE", "ARE BUILDING"))
    big = min(fit_size("NOW.", "BC-XB", PW - 2 * M, 400, 40), size * 2.3)
    y = PH - 36 * mm - CAP * size
    tracked(c, M, y, "THESE PEOPLE", "BC-XB", size, 0, PAPER)
    y -= size * 0.92
    tracked(c, M, y, "ARE BUILDING", "BC-XB", size, 0, PAPER)
    y -= CAP * big + 7 * mm
    tracked(c, M - big * 0.012, y, "NOW.", "BC-XB", big, 0, ACCENT)
    tracked(c, M, y - 13 * mm, "Four teams, four days, one working product each. Say hi, but let them build.",
            "DM-M", 12.5, 0, WHITE)

    # the teams, small, in four columns
    gap = 5 * mm
    cw = (PW - 2 * M - 3 * gap) / 4
    top = 96 * mm
    for k, (number, color) in enumerate(TEAMS):
        t = teams.get(number, {"mentor": "", "members": []})
        x = M + k * (cw + gap)
        ph = 9 * mm
        c.setFillColorRGB(*color)
        c.roundRect(x, top - ph, cw, ph, ph / 2, stroke=0, fill=1)
        tracked(c, x + cw / 2, top - ph + (ph - CAP * 17) / 2, f"TEAM {number}", "BC-XB", 17, 0.3, INK, "center")
        y = top - ph - 8 * mm
        tracked(c, x + 2 * mm, y, "MENTOR", "DM-SB", 6, 1.5, ACCENT)
        y -= 5.5 * mm
        tracked(c, x + 2 * mm, y, t["mentor"], "DM-SB", fit_size(t["mentor"], "DM-SB", cw - 4 * mm, 11, 7), 0, PAPER)
        y -= 8 * mm
        for name in t["members"]:
            tracked(c, x + 2 * mm, y, name, "DM-R", fit_size(name, "DM-R", cw - 4 * mm, 10.5, 7), 0, WHITE)
            y -= 5.6 * mm


def make(rows, out):
    teams = by_team(rows)
    c = canvas.Canvas(out, pagesize=A4, initialFontName="DM-R")
    c.setTitle("AI Entrepreneurship Hackathon - team list")
    page_meet(c, teams)
    c.showPage()
    page_building(c, teams)
    c.showPage()
    c.save()
