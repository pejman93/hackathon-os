#!/usr/bin/env python3
"""The Friday kick-off deck: 16:9, few words per slide, every text a real editable text box.

    python documents/make_kickoff.py

Animated cards play in PowerPoint's slide show.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from lxml import etree                                                    # noqa: E402
from pptx import Presentation                                            # noqa: E402
from pptx.dml.color import RGBColor                                       # noqa: E402
from pptx.enum.shapes import MSO_SHAPE                                    # noqa: E402
from pptx.oxml.ns import qn                                               # noqa: E402
from pptx.util import Emu, Pt                                             # noqa: E402

import pptx_kit as K                                                      # noqa: E402
from pptx_kit import BC, DM, Para, Run                                    # noqa: E402

ROOT = HERE.parent
OUT = HERE.parent / 'output' / 'documents' / 'Hackathon_Kickoff_Slides.pptx'
ASSETS = ROOT / 'output' / 'documents' / '_build' / 'kickoff'
SRC = HERE / 'assets'
ASSETS.mkdir(parents=True, exist_ok=True)

SLIDO_URL = 'https://example.org/poll'

W, H = 960, 540                    # 16:9 in points (13.333 x 7.5 in)
X0, X1 = 64, 896                   # left and right margins
PAPER, ACCENT, INK = 'F2F1E9', '7E98FF', '121316'
SOFT = 'C3CBFF'                    # small text on the blue
NAVY = '060A45'                    # card fill, see-through
TEAM = {1: '5B8CFF', 2: '33C27C', 3: 'FF9142', 4: 'B08CFF'}

TEAMS = [
    (1, 'Grace', ['Alonzo', 'Edsger', 'Maryam', 'Sophie', 'Srinivasa']),
    (2, 'Norbert', ['Blaise', 'Carl', 'Kurt', 'Mary', 'Omar', 'Rozsa']),
    (3, 'Alan', ['Harish', 'John', 'Karen']),
    (4, 'Konrad', ['Dennis', 'Jean', 'Kathleen', 'Marvin', 'Sofia']),
]


# =================================================================== assets
def crop(src, dst, aspect, cx=0.5, cy=0.5, width=1600):
    """Cut the largest box of the given width/height ratio around (cx, cy), then resize."""
    from PIL import Image
    im = Image.open(src).convert('RGB')
    w, h = im.size
    if w / h > aspect:
        cw, ch = round(h * aspect), h
    else:
        cw, ch = w, round(w / aspect)
    x = min(max(round(cx * w - cw / 2), 0), w - cw)
    y = min(max(round(cy * h - ch / 2), 0), h - ch)
    im = im.crop((x, y, x + cw, y + ch))
    im.resize((width, round(width / aspect)), Image.LANCZOS).save(dst, quality=88)
    return dst


def make_assets():
    import shutil
    crop(SRC / 'background.jpg', ASSETS / 'bg.jpg', 16 / 9, width=1920)
    crop(SRC / 'you-build-here-art.jpg', ASSETS / 'art.jpg', 16 / 9, cy=0.5, width=1600)
    crop(SRC / 'photo-team.jpg', ASSETS / 'photo-team.jpg', 300 / 380, cx=0.56, width=900)
    crop(SRC / 'photo-brainstorm.jpg', ASSETS / 'photo-brainstorm.jpg', 320 / 300, cx=0.5, width=960)
    K.qr_png(SLIDO_URL, ASSETS / 'slido-qr.png', scale=20)
    shutil.copy(SRC / 'logo-white-plain.png', ASSETS / 'logo-white.png')


def discord_url():
    return 'https://example.org/discord'


# =============================================================== primitives
def new_deck():
    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(12192000), Emu(6858000)
    return prs


def _alpha(sh, alpha):
    clr = sh._element.spPr.find(qn('a:solidFill')).find(qn('a:srgbClr'))
    etree.SubElement(clr, qn('a:alpha')).set('val', str(int(alpha * 100000)))
    return sh


def card(s, x, y, w, h, name, fill=NAVY, alpha=0.45, r=12):
    sh = K.rect(s, x, y, w, h, fill, name, radius=r)
    return _alpha(sh, alpha) if alpha < 1 else sh


def shape(s, kind, x, y, w, h, fill, name):
    sh = s.shapes.add_shape(kind, Pt(x), Pt(y), Pt(w), Pt(h))
    sh.name = name
    sh.fill.solid()
    sh.fill.fore_color.rgb = RGBColor.from_string(fill)
    sh.line.fill.background()
    sh.shadow.inherit = False
    return K._plain(sh)


def dot(s, x, y, d, fill, name):
    shape(s, MSO_SHAPE.OVAL, x, y, d, d, fill, name)


def photo(s, path, x, y, w, h, name, alt, r=16):
    """A picture with rounded corners (the picture's own outline, so it stays one object)."""
    pic = K.picture(s, path, x, y, w, h, name, alt)
    geom = pic._element.spPr.find(qn('a:prstGeom'))
    geom.set('prst', 'roundRect')
    av = geom.find(qn('a:avLst'))
    if av is None:
        av = etree.SubElement(geom, qn('a:avLst'))
    etree.SubElement(av, qn('a:gd')).attrib.update({'name': 'adj', 'fmla': f'val {int(r / min(w, h) * 100000)}'})
    return pic


def T(s, x, y, w, h, paras, name, anchor='t'):
    return K.text(s, x, y, w, h, paras, name, anchor)


def p(text, size, color=PAPER, bold=False, font=DM, line=None, after=0, align='l', spc=0):
    return Para(Run(text, size, bold, color, font, spc), line=line, after=after, align=align)


def head(*lines, size=72, accent=(), line=None, align='l'):
    """Barlow Condensed caps. A line index in accent is blue; a tuple line alternates white/blue."""
    line = line or round(size * 0.94, 1)
    out = []
    for i, ln in enumerate(lines):
        if isinstance(ln, tuple):
            runs = [Run(t, size, True, ACCENT if j % 2 else PAPER, BC) for j, t in enumerate(ln) if t]
            out.append(Para(runs, line=line, align=align))
        else:
            out.append(Para(Run(ln, size, True, ACCENT if i in accent else PAPER, BC), line=line, align=align))
    return out


def kicker(s, text, y, x=X0, w=None, align='l'):
    T(s, x, y, w or X1 - x, 20, p(text, 13, SOFT, True, spc=1.8, align=align), 'Kicker')


def background(s):
    K.picture(s, ASSETS / 'bg.jpg', 0, 0, W, H, 'Background', '')


def lockup(s, x=X0, y=34, h=22):
    lw = h * 2733 / 800
    K.picture(s, ASSETS / 'logo-white.png', x, y, lw, h, 'Example College logo',
              'Example College of Business and Technology')
    dx = x + lw + 12
    K.line(s, dx, y + h + 1, dx + 6, y - 1, PAPER, 'Divider', width=0.8)
    T(s, dx + 16, y - 1, 200, h + 4, [p('AI ENTREPRENEURSHIP', 8, PAPER, True, BC, line=10, spc=0.6),
                                      p('HACKATHON', 12.5, PAPER, True, BC, line=13, spc=0.4)], 'Event name')


def base(s):
    background(s)
    lockup(s)


def qr_panel(s, img, x, y, side, alt, caption=None):
    pad = side * 0.06
    card(s, x, y, side, side, 'QR panel', 'FFFFFF', alpha=1, r=16)
    K.picture(s, img, x + pad, y + pad, side - 2 * pad, side - 2 * pad, 'QR code', alt)
    if caption:
        T(s, x - 40, y + side + 12, side + 80, 26, p(caption, 18, PAPER, align='ctr'), 'QR caption')


def notes(s, text):
    s.notes_slide.notes_text_frame.text = text


# =================================================================== slides
def s_title(s):
    base(s)
    kicker(s, '23–26 OCTOBER 2026  ·  EXAMPLE CAMPUS', 150)
    T(s, X0, 178, 500, 240, head('FOUR DAYS.', 'ONE WORKING', 'AI PRODUCT.', size=84, accent=(2,), line=78),
      'Title')
    T(s, X0, 432, 480, 28, p('AI Entrepreneurship Hackathon', 20, SOFT), 'Subtitle')
    photo(s, ASSETS / 'photo-team.jpg', 596, 80, 300, 380, 'Photo', 'A team working together at laptops')
    notes(s, '09:00. Welcome everyone to the AI Entrepreneurship Hackathon.\n'
             'Next: phones out for Slido.')


def s_scan(s):
    base(s)
    kicker(s, 'BEFORE WE START', 160)
    T(s, X0, 186, 500, 100, head('SCAN TO JOIN', size=96, line=90), 'Headline')
    T(s, X0, 296, 460, 60, p('Two quick questions, live on screen.', 22, SOFT, line=30), 'Line')
    qr_panel(s, ASSETS / 'slido-qr.png', 596, 120, 300, 'QR code to join Slido')
    notes(s, 'Give everyone 30 seconds to scan.\n'
             'Then Cmd+Tab to the Slido tab (in Present mode). Start the first poll: "One founder. '
             'A 6-month-old AI startup ... For how much?" Let people vote for about a minute and show the '
             'result. Do NOT say the answer.\n'
             'Cmd+Tab back to PowerPoint: the next slide is the answer.')


def s_answer(s):
    base(s)
    kicker(s, 'THE ANSWER', 100)
    T(s, X0, 158, 700, 170, p('$80M', 190, ACCENT, True, BC, line=172), 'Answer')
    T(s, X0, 336, 760, 36, p('One founder. Six months old. No outside funding.', 28, PAPER, True, line=34), 'Fact')
    T(s, X0, 378, 760, 28, p('Base44, an AI app builder, bought by Wix in June 2025.', 19, SOFT), 'Source')
    T(s, X0, 438, 760, 60, head('YOU HAVE FOUR DAYS.', size=52), 'Punchline')
    notes(s, 'The answer is $80 million.\n'
             'Base44: one founder, six months old, bootstrapped. Wix bought it in June 2025.\n'
             'Point: with AI, a very small team can build something real, fast. You have four days.')


def s_karl(s):
    base(s)
    kicker(s, 'OPENING TALK  ·  AI ENTREPRENEURSHIP', 176)
    T(s, X0, 202, X1 - X0, 110, head('JOHN MCCARTHY', size=120, line=110), 'Name')
    T(s, X0 + 2, 322, 600, 34, p('Head of AI Business, Example Corp', 26, SOFT), 'Role')
    notes(s, 'John McCarthy, Head of AI Business at Example Corp: about 10 minutes, somewhere between 09:15 and '
             '09:45. Introduce him and hand over.')


def s_four_days(s):
    base(s)
    kicker(s, '23–26 OCTOBER', 110)
    T(s, X0, 134, X1 - X0, 80, head('THE FOUR DAYS', size=72), 'Headline')
    days = [('FRI 23', 'EXAMPLE CAMPUS', 'Teams, idea, plan'),
            ('SAT 24', 'CAMPUS OR ONLINE', 'Build'),
            ('SUN 25', 'CAMPUS OR ONLINE', 'Build. Hand-in 17:30'),
            ('MON 26', 'EXAMPLE CAMPUS', 'Demos 14:00, awards')]
    cw, gap = (X1 - X0 - 3 * 16) / 4, 16
    for i, (d, where, txt) in enumerate(days):
        x = X0 + i * (cw + gap)
        card(s, x, 252, cw, 196, f'Day {i + 1}')
        T(s, x + 22, 274, cw - 44, 50, p(d, 46, PAPER, True, BC, line=46), f'Day {i + 1} date')
        T(s, x + 22, 330, cw - 44, 18, p(where, 11.5, SOFT, True, spc=1.2), f'Day {i + 1} place')
        T(s, x + 22, 372, cw - 44, 60, p(txt, 19, PAPER, line=26), f'Day {i + 1} text')
    notes(s, 'Friday and Monday here at Example Campus. Saturday and Sunday on campus or from home, with a 09:00 Zoom '
             'call and mentor check-ins at 12:30 and 17:00.\n'
             'Sunday: feature freeze 16:00, hand-in 17:30. Monday: demos from 14:00.\n'
             'Remind them: the clocks go back one hour on Saturday night.')


def s_today(s):
    base(s)
    kicker(s, 'TODAY  ·  FRIDAY 23 OCTOBER', 110)
    T(s, X0, 134, 380, 170, head('YOUR', 'FRIDAY', size=96, accent=(1,), line=88), 'Headline')
    card(s, X0, 340, 340, 112, 'Key hour card')
    T(s, X0 + 22, 340, 296, 112, [p('THE KEY HOUR', 12, SOFT, True, spc=1.4, after=6),
                                   Para([Run('14:00, development plan. ', 16, True, PAPER),
                                         Run('Decide what you build, and what you leave out.', 16, False, SOFT)],
                                        line=22)], 'Key hour text', anchor='ctr')
    rows = [('09:00', 'Kick-off', True, True), ('10:00', 'Teams and mentors revealed', True, False),
            ('10:30', 'Brainstorm', False, False), ('12:00', 'Lunch', False, False),
            ('13:00', 'Idea pitch', True, False), ('14:00', 'Development plan with your mentor', True, False),
            ('15:00', 'Split the tasks', False, False), ('16:00', 'Start building', False, False),
            ('17:00', 'End-of-day session with your mentor', False, False), ('17:30', 'End of day', False, False)]
    x, y0, pitch = 474, 98, 39.5
    K.line(s, x + 5, y0 + 19, x + 5, y0 + 19 + 9 * pitch, '7F89D8', 'Timeline', width=1.2)
    for i, (t, label, strong, now) in enumerate(rows):
        y = y0 + i * pitch
        if now:
            card(s, x - 14, y + 1, X1 - x + 14, 36, 'You are here', 'FFFFFF', alpha=0.12, r=18)
        dot(s, x, y + 14, 10, ACCENT if strong else '8C95E0', f'Row {i + 1} dot')
        T(s, x + 24, y, 64, 38, p(t, 22, ACCENT if strong else SOFT, True, BC, line=24), f'Row {i + 1} time',
          anchor='ctr')
        runs = [Run(label, 16.5, strong, PAPER if strong else 'DDE1FF')]
        if now:
            runs.append(Run('   ← now', 13, True, ACCENT))
        T(s, x + 92, y, X1 - x - 96, 38, Para(runs, line=20), f'Row {i + 1} label', anchor='ctr')
    notes(s, 'Today at a glance. 10:00 the teams, 13:00 each team pitches its idea in a few minutes, '
             '14:00 the development plan with the mentor: the most important hour of the day.')


def s_demos(s):
    base(s)
    kicker(s, 'LIVE DEMOS', 110)
    T(s, X0, 134, X1 - X0, 150, head('WHAT DOES AN AI', 'PRODUCT LOOK LIKE?', size=80, accent=(1,), line=76),
      'Headline')
    cw = (X1 - X0 - 16) / 2
    for i, (name, role) in enumerate([('MARVIN MINSKY', 'Example College student'), ('ALAN', 'Mentor')]):
        x = X0 + i * (cw + 16)
        card(s, x, 330, cw, 112, f'Demo {i + 1} card')
        T(s, x + 26, 350, cw - 52, 44, p(name, 40, PAPER, True, BC, line=42), f'Demo {i + 1} name')
        T(s, x + 26, 398, cw - 52, 26, p(role, 18, SOFT), f'Demo {i + 1} role')
    notes(s, 'Two live demos of real AI products, about 6 to 7 minutes each: Marvin Minsky (Example College student) and '
             'Alan (one of our mentors).\n'
             'Ask the room to watch for three things: who the user is, what problem it solves, and where the AI '
             'does real work. The judges ask the same on Monday.')


def s_demo(s, n, name, role, note):
    base(s)
    kicker(s, f'LIVE DEMO {n} OF 2', 176)
    T(s, X0, 202, X1 - X0, 130, head(name, size=130, line=120), 'Name')
    T(s, X0 + 4, 336, 600, 34, p(role, 26, SOFT), 'Role')
    notes(s, note)


def s_criteria(s):
    base(s)
    kicker(s, 'MONDAY 26 OCTOBER  ·  14:00', 96)
    T(s, X0, 120, X1 - X0, 74, head('JUDGING CRITERIA', size=68), 'Headline')
    T(s, X0, 196, X1 - X0, 24, p('8-minute live demo, then 4 minutes of questions.', 18, SOFT), 'Format')
    crit = [('30%', 'Working product', 'Runs live, with real AI inside'),
            ('20%', 'Real problem, real user', 'A specific person or role'),
            ('20%', 'Business case', 'Who pays, how much, and why they would switch'),
            ('15%', 'Sustainability', 'Monthly running cost and dependencies'),
            ('15%', 'Demo and pitch', 'A clear story, on time')]
    y0, pitch = 244, 52
    for i, (pct, name, desc) in enumerate(crit):
        y = y0 + i * pitch
        if i:
            K.line(s, X0, y - 6, X1, y - 6, '8C95E0', f'Rule {i}', width=0.6, alpha=0.5)
        T(s, X0, y, 90, 40, p(pct, 34, ACCENT, True, BC, line=34), f'Criterion {i + 1} weight', anchor='ctr')
        T(s, X0 + 110, y, 300, 40, p(name, 20, PAPER, True), f'Criterion {i + 1}', anchor='ctr')
        T(s, X0 + 420, y, X1 - X0 - 420, 40, p(desc, 17, SOFT), f'Criterion {i + 1} detail', anchor='ctr')
    notes(s, 'Monday from 14:00 here at Example Campus: 8 minutes of live demo, 4 minutes of questions per team.\n'
             'Industry judges score each team from 1 to 5 on these five, weighted as shown. '
             'A mentor never judges their own team. Hand-in is Sunday 17:30.')


def s_meme_money(s):
    base(s)
    T(s, X0, 92, X1 - X0, 60, head('MAKE THE JUDGES SAY THIS.', size=56, align='ctr'), 'Headline')
    gw, gh = 500, 313
    K.picture(s, SRC / 'meme-take-my-money.gif', (W - gw) / 2, 176, gw, gh, 'Meme',
              'Reaction card')
    notes(s, 'The business case counts: who pays, how much, and why they would switch. '
             'On Monday you want the judges to feel like this.')


def s_question_2(s):
    base(s)
    kicker(s, 'BEFORE WE REVEAL THE TEAMS', 176)
    T(s, X0, 202, 520, 190, head('ONE MORE', 'QUESTION', size=96, accent=(1,), line=88), 'Headline')
    qr_panel(s, ASSETS / 'slido-qr.png', 676, 150, 220, 'QR code to join Slido', 'Not in yet? Scan.')
    notes(s, 'Cmd+Tab to Slido and start the poll "What do you bring to your team?". Show the result.\n'
             'Say: every team was put together with a mix of these, on purpose. Then the Discord slide and the '
             'reveal.')


def s_discord(s, url):
    base(s)
    kicker(s, 'NOT ON DISCORD YET?', 160)
    T(s, X0, 186, 500, 110, head('JOIN NOW', size=112, line=104), 'Headline')
    T(s, X0, 306, 460, 60, p('Scan, join, and use your real name.', 22, SOFT, line=30), 'Line')
    K.qr_png(url, ASSETS / 'discord-qr.png', scale=20)
    qr_panel(s, ASSETS / 'discord-qr.png', 596, 110, 300, 'QR code to join Discord', url.replace('https://', ''))
    notes(s, 'For anyone not on Discord yet. Leave this up for a minute.\n'
             'Staff at the entrance have the list of who has not joined.')


def s_teams(s):
    base(s)
    kicker(s, '10:00  ·  TEAMS AND MENTORS', 92)
    T(s, X0, 114, X1 - X0, 60, head('MEET YOUR TEAMS', size=60), 'Headline')
    cw = (X1 - X0 - 3 * 14) / 4
    for i, (n, mentor, people) in enumerate(TEAMS):
        x, y = X0 + i * (cw + 14), 186
        card(s, x, y, cw, 314, f'Team {n} card', alpha=0.5)
        shape(s, MSO_SHAPE.ROUND_2_SAME_RECTANGLE, x, y, cw, 58, TEAM[n], f'Team {n} header').adjustments[0] = 0.2
        T(s, x + 20, y, cw - 40, 58, p(f'TEAM {n}', 36, INK, True, BC, line=36), f'Team {n} name', anchor='ctr')
        T(s, x + 20, y + 72, cw - 40, 16, p('MENTOR', 11, SOFT, True, spc=1.4), f'Team {n} mentor label')
        T(s, x + 20, y + 88, cw - 40, 30, p(mentor.upper(), 28, PAPER, True, BC, line=30), f'Team {n} mentor')
        K.line(s, x + 20, y + 130, x + cw - 20, y + 130, '8C95E0', f'Team {n} rule', width=0.6, alpha=0.6)
        T(s, x + 20, y + 142, cw - 40, 6 * 26, [p(m, 17, PAPER, line=26) for m in people], f'Team {n} members')
    notes(s, '10:00, the reveal. Read each team and ask its mentor to raise a hand.\n'
             'Teams sit together with their mentor. Staff give everyone their Team role on Discord now.')


def s_next(s):
    base(s)
    kicker(s, 'UP NEXT  ·  10:30', 150)
    T(s, X0, 176, 500, 100, head('BRAINSTORM', size=104, accent=(0,), line=96), 'Headline')
    T(s, X0, 292, 470, 70, p('Pick one real user with one real problem.', 24, PAPER, line=32), 'Goal')
    T(s, X0, 400, 480, 80, [
        Para([Run('12:00  ', 17, True, ACCENT), Run('Lunch', 17, False, SOFT)], line=26),
        Para([Run('13:00  ', 17, True, ACCENT), Run('Idea pitch', 17, False, SOFT)], line=26),
        Para([Run('14:00  ', 17, True, ACCENT), Run('Development plan', 17, False, SOFT)], line=26)], 'After')
    photo(s, ASSETS / 'photo-brainstorm.jpg', 576, 120, 320, 300, 'Photo', 'A team brainstorming with sticky notes')
    notes(s, 'Brainstorm with your team and mentor until 12:00. One real user, one real problem, '
             'small enough to work by Sunday 16:00. Talk to a business mentor early.')


def s_ready(s):
    base(s)
    T(s, X0, 70, X1 - X0, 100, head('READY?', size=100, line=96, align='ctr'), 'Headline')
    gw, gh = 640, 320
    K.picture(s, SRC / 'meme-lets-ride.gif', (W - gw) / 2, 180, gw, gh, 'Meme', 'Reaction card')
    notes(s, 'Ready? Let\'s go.')


def s_end(s):
    K.picture(s, ASSETS / 'art.jpg', 0, 0, W, H, 'Art', 'A head whose outline becomes stairs up to an open door')
    lw = 330
    K.picture(s, ASSETS / 'logo-white.png', 445, 70, lw, lw * 800 / 2733, 'Example College logo',
              'Example College of Business and Technology')
    T(s, 440, 196, 420, 190, head('YOU BUILD', 'HERE.', size=96, accent=(1,), line=88), 'Headline')
    notes(s, 'Close the kick-off. Teams go with their mentors to start the brainstorm.')


# =================================================================== build
def build():
    make_assets()
    url = discord_url()
    prs = new_deck()
    K.brand_links(prs)
    plan = [s_title, s_scan, s_answer, s_karl, s_four_days, s_today, s_demos,
            lambda s: s_demo(s, 1, 'MARVIN MINSKY', 'Example College student', 'Marvin plugs in his laptop. About 6 to 7 minutes.'),
            lambda s: s_demo(s, 2, 'ALAN', 'Mentor', 'Alan plugs in. About 6 to 7 minutes. Then ask the room: '
                                                     'who was the user, what was the problem, where was the AI?'),
            s_criteria, s_meme_money, s_question_2, lambda s: s_discord(s, url), s_teams, s_next, s_ready, s_end]
    for make in plan:
        make(K.new_slide(prs))
    prs.core_properties.title = 'AI Entrepreneurship Hackathon — Kick-off'
    prs.core_properties.author = 'Example College'
    prs.core_properties.subject = 'Friday 23 October 2026, Example Campus'
    prs.save(OUT)
    return OUT, len(plan)


if __name__ == '__main__':
    path, n = build()
    print(path.name, n, 'slides')
