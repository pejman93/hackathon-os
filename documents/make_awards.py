#!/usr/bin/env python3
"""The awards: four slides for the end of Demo Day.

    python documents/make_awards.py

Drumroll, Audience Award chart, the winner over animated fireworks, and a thank-you with a QR code.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import make_audience_chart as AC                                          # noqa: E402
import make_day2 as D2                                                    # noqa: E402
import make_kickoff as KO                                                 # noqa: E402
import pptx_kit as K                                                      # noqa: E402
from make_kickoff import PAPER, SOFT, X0, X1, T, head, kicker, p, Para, Run   # noqa: E402

OUT = HERE.parent / 'output' / 'documents' / 'Hackathon_Awards_Slides.pptx'
VOTES = [9, 6, 4, 8]                           # sample votes
SITE = 'https://example.org/hackathon'
GOLD = 'F4D983'
WINNER = ('ShipCheck', 4, ['Sofia Kovalevskaya', 'Jean Bartik', 'Dennis Ritchie', 'Kathleen Booth',
                           'Marvin Minsky'], 'Konrad Zuse')


def drumroll(s):
    D2.slide(s, 'AI ENTREPRENEURSHIP HACKATHON 2026', ('THE', 'AWARDS.'),
             'Two awards today: the Audience Award, chosen by you, and the winner, chosen by the judges.',
             meme='meme-drumroll.gif', alt='Reaction card')
    KO.notes(s, 'The judges have decided. Two awards: first the Audience Award, chosen by the room, '
                'then the winner, chosen by the judges. Drumroll, please!')


def winner(s):
    product, n, team, mentor = WINNER
    # fireworks over the whole slide, darkened a little so the text stays readable
    pic = K.picture(s, KO.SRC / 'fireworks-wide.gif', 0, 0, KO.W, KO.H, 'Fireworks', 'Fireworks in the night sky')
    cut = (1 - (KO.H / KO.W) / (267 / 400)) / 2        # the GIF is 3:2; crop top and bottom to fill 16:9
    pic.crop_top = pic.crop_bottom = cut
    KO.card(s, 0, 0, KO.W, KO.H, 'Shade', '0A0B10', alpha=0.48, r=0)
    KO.lockup(s)
    T(s, X0, 112, X1 - X0, 20, p('THE WINNER  ·  CHOSEN BY THE JUDGES', 14, GOLD, True, spc=2.2, align='ctr'),
      'Kicker')
    T(s, X0, 140, X1 - X0, 50, head('CONGRATULATIONS!', size=46, line=46, align='ctr'), 'Congratulations')
    T(s, X0, 196, X1 - X0, 150, p(product.upper(), 150, GOLD, True, KO.BC, line=142, align='ctr'), 'Winner')
    T(s, X0, 352, X1 - X0, 30, p(f'TEAM {n}', 22, PAPER, True, KO.BC, line=24, spc=2, align='ctr'), 'Team')
    T(s, X0, 396, X1 - X0, 60, [p('  ·  '.join(team), 17, PAPER, line=24, align='ctr', after=4),
                                Para([Run('Mentor  ', 15, True, SOFT), Run(mentor, 15, False, PAPER)], line=21,
                                     align='ctr')], 'Members')
    KO.notes(s, 'And the winner of the AI Entrepreneurship Hackathon 2026, chosen by the judges, is… '
                '(pause) …Team 4, ShipCheck!\n'
                'Please come to the stage: Sofia, Jean, Dennis, Kathleen, Marvin, and your mentor Konrad.\n'
                'Certificates: print-kit/output/3b-award-certificates.pdf, pages 1–5. Then a photo with the judges.')


def thanks(s):
    D2.base(s)
    kicker(s, 'AI ENTREPRENEURSHIP HACKATHON 2026', 140, w=480)
    T(s, X0, 166, 500, 100, head('THANK YOU.', size=96, accent=(0,), line=90), 'Headline')
    T(s, X0, 274, 470, 90, p('To all participants, mentors, judges, our staff team, and Example Campus.', 22, PAPER,
                             line=30), 'Thanks')
    T(s, X0, 372, 470, 90, [p('STAY IN TOUCH', 13, SOFT, True, spc=1.8, after=6),
                            p('Scan for future hackathons, and to get in touch with Example College.', 18, PAPER, line=25)],
      'Stay in touch')
    K.qr_png(SITE, KO.ASSETS / 'site-qr.png', scale=20)
    KO.qr_panel(s, KO.ASSETS / 'site-qr.png', 596, 110, 300, 'QR code to example.org/hackathon',
                'example.org/hackathon')
    KO.notes(s, 'Thank you to everyone: participants, mentors, judges, our staff team, and Example Campus for hosting us.\n'
                'Scan the code for future hackathons and to stay in touch with Example College. '
                'Now: photos, networking and drinks until 17:30.')


def build():
    D2.make_dark_bg()
    prs = KO.new_deck()
    K.brand_links(prs)
    drumroll(K.new_slide(prs))
    AC.chart_slide(K.new_slide(prs), VOTES)
    winner(K.new_slide(prs))
    thanks(K.new_slide(prs))
    prs.core_properties.title = 'AI Entrepreneurship Hackathon — Awards'
    prs.core_properties.author = 'Example College'
    prs.save(OUT)
    return OUT


if __name__ == '__main__':
    print(build().name)
