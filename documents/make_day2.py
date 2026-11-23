#!/usr/bin/env python3
"""Four slides for the Saturday morning call (day 2, building).

    python documents/make_day2.py

Dark plain background, few words and one small animated card per slide.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import make_kickoff as KO                                                 # noqa: E402
import pptx_kit as K                                                      # noqa: E402
from make_kickoff import ACCENT, PAPER, SOFT, X0, T, head, kicker, p, Para, Run   # noqa: E402

OUT = HERE.parent / 'output' / 'documents' / 'Hackathon_Day2_Slides.pptx'
DARK_BG = KO.ASSETS / 'bg-dark.jpg'
SRC = KO.SRC


def make_dark_bg():
    """Near-black with one soft blue glow; no grid."""
    KO.make_assets()
    import numpy as np
    from PIL import Image
    w, h = 1920, 1080
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    base, glow = np.array([0x12, 0x13, 0x16], float), np.array([30, 38, 120], float)
    d2 = ((xx - 0.78 * w) ** 2 + (yy - 0.25 * h) ** 2) / (0.45 * w) ** 2
    k = (0.45 * np.exp(-d2 * 2.0))[..., None]
    Image.fromarray(np.clip(base * (1 - k) + glow * k, 0, 255).astype('uint8')).save(DARK_BG, quality=92)


def base(s):
    K.picture(s, DARK_BG, 0, 0, KO.W, KO.H, 'Background', '')
    KO.lockup(s)


def gif(s, name, alt, box=(524, 110, 372, 330)):
    """The GIF as large as fits in the box, centred in it."""
    from PIL import Image
    x, y, bw, bh = box
    w, h = Image.open(SRC / name).size
    k = min(bw / w, bh / h)
    K.picture(s, SRC / name, x + (bw - w * k) / 2, y + (bh - h * k) / 2, w * k, h * k, 'Meme', alt)


def slide(s, kick, lines, line_text, small=None, meme=None, alt=''):
    base(s)
    kicker(s, kick, 150, w=400)
    T(s, X0, 176, 444, 190, head(*lines, size=88, accent=(1,), line=84), 'Headline')
    T(s, X0, 366, 420, 70, p(line_text, 22, PAPER, line=30), 'Line')
    if small:
        T(s, X0, 442, 440, 50, small, 'Small')
    gif(s, meme, alt)


def build():
    make_dark_bg()
    prs = KO.new_deck()
    K.brand_links(prs)
    times = lambda pairs: Para([r for t, w in pairs for r in (Run(t + ' ', 15, True, ACCENT),
                                                               Run(w + '    ', 15, False, SOFT))], line=22)

    s = K.new_slide(prs)
    slide(s, 'DAY 2  ·  SATURDAY', ('YESTERDAY:', 'A LOT.'),
          'Teams, ideas, pitches, plans. You made it.', meme='meme-this-is-fine.gif',
          alt='Reaction card')
    KO.notes(s, 'Good morning! Yesterday was a lot: new teams, ideas, pitches, plans. Well done, you made it.')

    s = K.new_slide(prs)
    slide(s, 'TODAY', ('JUST', 'BUILD.'),
          'No stage, no pitches. Just you, your team and your product.',
          times([('12:30', 'check-in'), ('17:00', 'end-of-day'), ('17:30', 'done')]),
          meme='meme-cat-typing.gif', alt='Reaction card')
    KO.notes(s, 'Today is calm: just build. Campus or home. 12:30 check-in with your mentor, '
                '17:00 end-of-day session, 17:30 done.')

    s = K.new_slide(prs)
    slide(s, 'BY 12:30', ('MAKE IT', 'ALIVE.'),
          'Something that runs from start to finish. Rough is fine.',
          Para([Run('One flow · a real AI call · a task for everyone', 15, False, SOFT)], line=22),
          meme='meme-its-alive.gif', alt='Reaction card')
    KO.notes(s, 'Goal for 12:30: something runs from start to finish, however rough. One flow, a real AI call, '
                'and a task for everyone on the team. Test your AI key this morning.')

    s = K.new_slide(prs)
    slide(s, 'TONIGHT, THEN SUNDAY', ('SLEEP.', 'THEN SHIP.'),
          'Clocks go back tonight: one extra hour of sleep.',
          times([('16:00', 'freeze'), ('17:00', 'rehearsal'), ('17:30', 'hand-in')]),
          meme='meme-sleepy.gif', alt='Reaction card')
    KO.notes(s, 'The clocks go back tonight, so sleep an extra hour. Sunday: 10:00 call (same Zoom link, new '
                'time), 16:00 feature freeze, 17:00 demo rehearsal, 17:30 hand-in. Stuck? Team, mentor, #help.')

    prs.core_properties.title = 'AI Entrepreneurship Hackathon — Day 2'
    prs.core_properties.author = 'Example College'
    prs.save(OUT)
    return OUT


if __name__ == '__main__':
    print(build().name)
