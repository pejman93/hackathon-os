#!/usr/bin/env python3
"""Five slides for the Sunday morning call (day 3, deadline day), same look as day 2.

    python documents/make_day3.py
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import make_day2 as D2                                                    # noqa: E402
import make_kickoff as KO                                                 # noqa: E402
import pptx_kit as K                                                      # noqa: E402
from make_kickoff import ACCENT, PAPER, SOFT, X0, T, head, kicker, p, Para, Run   # noqa: E402

OUT = HERE.parent / 'output' / 'documents' / 'Hackathon_Day3_Slides.pptx'


def timeline(s):
    D2.base(s)
    kicker(s, 'TODAY  ·  SUNDAY 25 OCTOBER', 150, w=400)
    T(s, X0, 176, 340, 190, head('DEADLINE', 'DAY.', size=88, accent=(1,), line=84), 'Headline')
    T(s, X0, 366, 340, 70, p('The clocks went back. Same Zoom link, new time.', 18, SOFT, line=26), 'Line')
    rows = [('10:00', 'Kick-off call', False), ('12:30', 'Check-in with your mentor', False),
            ('16:00', 'Feature freeze', True), ('17:00', 'Demo rehearsal with your mentor', True),
            ('23:59', 'Hand-in deadline', True)]
    for i, (t, label, strong) in enumerate(rows):
        y = 150 + i * 62
        T(s, 450, y, 110, 50, p(t, 40, ACCENT if strong else SOFT, True, KO.BC, line=42), f'Time {i + 1}',
          anchor='ctr')
        T(s, 570, y, 330, 50, p(label, 21, PAPER, strong, line=26), f'Label {i + 1}', anchor='ctr')
    KO.notes(s, 'Here is today. 12:30 check-in with your mentor, like yesterday. At 16:00 the feature freeze, '
                'at 17:00 you rehearse your demo with your mentor, and the hand-in deadline is tonight at 23:59.')


def hand_in(s):
    """No GIF here: this slide is the one they must take seriously. Just what goes where."""
    D2.base(s)
    kicker(s, 'THE HAND-IN  ·  DEADLINE TONIGHT 23:59', 150, w=600)
    T(s, X0, 176, 700, 100, head('HAND IT IN.', size=88, line=84), 'Headline')
    # (text, level): level 1 is a sub-point of the item above it
    cols = [(X0, 'IN YOUR TEAM FOLDER', [('Your final slides, with:', 0),
                                         ('your name, logo and branding', 1),
                                         ('the team members who present', 1),
                                         ('your mentor', 1),
                                         ('A 1-minute demo video', 0)]),
            (500, 'IN THE FORM  ·  FROM 16:00', [('GitHub link', 0), ('Live link, if you have one', 0),
                                                 ('Links to your slides and video', 0), ('How to open or run it', 0)])]
    for x, lab, items in cols:
        T(s, x, 296, 400, 20, p(lab, 13, SOFT, True, spc=1.6), lab.title())
        paras = []
        for it, level in items:
            if level:
                paras.append(Para([Run('–  ', 17, False, SOFT), Run(it, 17, False, SOFT)], line=23, marL=20))
            else:
                paras.append(Para([Run('•  ', 20, True, ACCENT), Run(it, 20, False, PAPER)], line=28, before=4))
        T(s, x, 320, 400, 190, paras, lab.title() + ' items')
    KO.notes(s, 'This is the important one. In your team folder, the link is in your team channel: your final '
                'slides and a 1-minute demo video, just a screen recording of your product working. Your slides show your '
                'name, logo and branding, the team members who present, and your mentor. Name the files like '
                '"Team 1 - Slides" and "Team 1 - Demo". From 16:00, one person per team fills in the form: your '
                'GitHub link, your live link if you have one, the links to your slides and video, and how to open or '
                'run it. I will post the form link at 16:00. Deadline tonight at 23:59.')


def build():
    D2.make_dark_bg()
    prs = KO.new_deck()
    K.brand_links(prs)

    s = K.new_slide(prs)
    D2.slide(s, 'DAY 3  ·  SUNDAY', ('SHIP', 'DAY.'), 'Last building day. By tonight, it’s done.',
             meme='meme-ship-it.gif', alt='Reaction card')
    KO.notes(s, 'Good morning, and welcome to day 3. Today is ship day: the last building day. '
                'By tonight your product is done and handed in.')

    timeline(K.new_slide(prs))

    s = K.new_slide(prs)
    D2.slide(s, 'FEATURE FREEZE  ·  16:00', ('16:00:', 'LET IT GO.'),
             'No new features after 16:00. Only fixes and polish.',
             Para([Run('Make the one thing work, every time.', 15, False, SOFT)], line=22),
             meme='meme-let-it-go.gif', alt='Reaction card')
    KO.notes(s, 'At 16:00, let it go: no new features. From then on, only fix bugs and polish. '
                'Better one thing that works every time than three that sometimes work.')

    hand_in(K.new_slide(prs))

    s = K.new_slide(prs)
    D2.slide(s, 'MONDAY 26 OCTOBER', ('MONDAY:', 'SHOWTIME.'),
             '14:00, Example Campus. 8 minutes of live demo, 4 of questions.',
             Para([Run('Rehearse it today at 17:00.', 15, False, SOFT)], line=22),
             meme='meme-showtime.gif', alt='Reaction card')
    KO.notes(s, 'Tomorrow is showtime: 14:00 at Example Campus. Each team has 8 minutes of live demo and 4 minutes of '
                'questions from the judges. Rehearse it today at 17:00 with your mentor. Questions? Ask now, or in '
                '#help. Good luck today!')

    prs.core_properties.title = 'AI Entrepreneurship Hackathon — Day 3'
    prs.core_properties.author = 'Example College'
    prs.save(OUT)
    return OUT


if __name__ == '__main__':
    print(build().name)
