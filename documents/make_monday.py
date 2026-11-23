#!/usr/bin/env python3
"""The Demo Day slides: welcome, line-up, one slide per team and the audience vote.

    python documents/make_monday.py

Team members come from sample-data/documents/roster.csv.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import make_day2 as D2                                                    # noqa: E402
import make_kickoff as KO                                                 # noqa: E402
import pptx_kit as K                                                      # noqa: E402
from make_kickoff import ACCENT, PAPER, SOFT, X0, X1, T, head, kicker, p, Para, Run   # noqa: E402

OUT = HERE.parent / 'output' / 'documents' / 'Hackathon_Demo_Day_Slides.pptx'
REVIEW_URL = 'https://example.org/review'      # Example College on Google Maps
LINEUP = [(1, 'NoteRelay', 'Grace Hopper'), (2, 'StudyLoop', 'Norbert Wiener'),
          (3, 'RenewRadar', 'Alan Turing'), (4, 'ShipCheck', 'Konrad Zuse')]

# and the demo video link. Members: packs/Final_Roster.csv.
TEAM_SLIDES = {
    1: ('For freelancers at networking events: talk for 20 seconds, and AI turns it into clean notes '
        'with a drafted follow-up.', 'https://example.org/demo'),
    2: ('Personalised maths and science practice for students, with a clear view for teachers of '
        'where to help.', 'https://example.org/demo'),
    3: ('Early warning for customer teams: a health score for every account, and next steps to keep '
        'it.', 'https://example.org/demo'),
    4: ('Built an app with AI? ShipCheck shows you what is risky and fixes the safe parts.',
        'https://example.org/demo'),
}


def members(n):
    import csv
    rows = csv.DictReader(open(HERE.parent / 'sample-data' / 'documents' / 'roster.csv', encoding='utf-8'))
    return [f"{r['first']} {r['last']}".strip() for r in rows
            if r['team'] == str(n) and r['role'] == 'Participant' and r['status'] == 'in']


def welcome(s):
    D2.base(s)
    kicker(s, 'DEMO DAY  ·  MONDAY 26 OCTOBER', 150, w=440)
    T(s, X0, 176, 460, 190, head('FOUR DAYS.', 'FOUR TEAMS.', size=88, accent=(1,), line=84), 'Headline')
    T(s, X0, 368, 440, 70, p('On Friday they met. Today they show what they built.', 22, PAPER, line=30), 'Line')
    KO.photo(s, KO.ASSETS / 'photo-polaroids.jpg', 598, 52, 300, 436, 'Photo',
             'An illustrated scene from the event', r=14)
    KO.notes(s, 'Good afternoon, and welcome to Demo Day of the AI Entrepreneurship Hackathon!\n'
                'Thank you to Example Campus, to our judges, our mentors and our staff team.\n'
                'Four days ago, most of these people had never met. On Friday they formed four teams. '
                'Today, each team shows a working AI product, built in four days.')


def lineup(s):
    D2.base(s)
    kicker(s, 'TODAY’S DEMOS', 104)
    T(s, X0, 128, X1 - X0, 70, head('THE LINE-UP', size=64), 'Headline')
    y0, pitch = 222, 62
    for i, (n, product, mentor) in enumerate(LINEUP):
        y = y0 + i * pitch
        KO.dot(s, X0, y + 4, 44, KO.TEAM[n], f'Team {n} dot')
        T(s, X0, y + 4, 44, 44, p(str(n), 26, '121316', True, KO.BC, line=26, align='ctr'), f'Team {n} number',
          anchor='ctr')
        T(s, X0 + 64, y, 330, 52, p(product.upper(), 34, PAPER, True, KO.BC, line=36), f'Team {n} product',
          anchor='ctr')
        T(s, X0 + 266, y, 260, 52, Para([Run(f'Team {n}', 15, True, SOFT), Run(f'   Mentor: {mentor}', 15, False, SOFT)],
                                         line=20), f'Team {n} info', anchor='ctr')
    x = 664
    T(s, x, 222, X1 - x, 20, p('EACH TEAM', 12.5, SOFT, True, spc=1.6), 'Format label')
    T(s, x, 246, X1 - x, 120, [
        Para([Run('8', 54, True, ACCENT, KO.BC), Run('  min live demo', 18, False, PAPER)], line=56),
        Para([Run('4', 54, True, ACCENT, KO.BC), Run('  min questions', 18, False, PAPER)], line=56)], 'Format')
    T(s, x, 384, X1 - x, 90, [p('AFTER THE LAST DEMO', 12.5, SOFT, True, spc=1.6, after=6),
                              p('You vote for the Audience Award on Slido.', 17, PAPER, line=24)], 'Vote')
    KO.notes(s, 'Here is the line-up: Team 1 NoteRelay, Team 2 StudyLoop, Team 3 RenewRadar, Team 4 ShipCheck.\n'
                'Each team has 8 minutes of live demo, then 4 minutes of questions from the judges.\n'
                'Introduce the judges by name and ask them to raise a hand.\n'
                'And everyone in the room: watch closely. After the last demo you vote for the Audience Award on '
                'Slido, the same QR as on Friday.\n'
                'Please welcome Team 1, NoteRelay!')


def team_slide(s, n, product, mentor):
    from pptx.enum.shapes import MSO_SHAPE
    line, video = TEAM_SLIDES[n]
    D2.base(s)
    kicker(s, f'TEAM {n} OF 4  ·  DEMO', 130)
    KO.dot(s, X0, 166, 64, KO.TEAM[n], 'Team dot')
    T(s, X0, 166, 64, 64, p(str(n), 38, '121316', True, KO.BC, line=38, align='ctr'), 'Team number', anchor='ctr')
    T(s, X0 + 86, 150, X1 - X0 - 86, 100, head(product.upper(), size=104, line=98), 'Product')
    T(s, X0, 270, X1 - X0, 70, p(line, 22, PAPER, line=30), 'One line')
    # the play button: the whole shape is a link to the demo video
    btn = KO.shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, X0, 362, 250, 48, KO.TEAM[n], 'Play demo video')
    btn.adjustments[0] = 0.5
    btn.click_action.hyperlink.address = video
    tf = btn.text_frame
    tf.text = 'PLAY DEMO VIDEO'
    from pptx.enum.text import PP_ALIGN
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    run = tf.paragraphs[0].runs[0]
    run.font.size = KO.Pt(16)
    run.font.bold = True
    run.font.name = KO.DM
    run.font.color.rgb = KO.RGBColor.from_string('121316')
    T(s, X0, 436, X1 - X0, 60, [
        Para([Run('Team  ', 14, True, SOFT), Run('  ·  '.join(members(n)), 14, False, PAPER)], line=20, after=4),
        Para([Run('Mentor  ', 14, True, SOFT), Run(mentor, 14, False, PAPER)], line=20)], 'Team and mentor')
    KO.notes(s, f'Team {n}, {product}. Click "Play demo video": it opens the 1-minute video in the browser. '
                f'Afterwards, come back to the slides (Cmd+Tab).\n'
                f'Then: "Please welcome Team {n}, {product}, to the stage!" 8 minutes of live demo, '
                f'then 4 minutes of questions from the judges.')


def vote(s):
    D2.base(s)
    kicker(s, 'AUDIENCE AWARD', 150, w=440)
    T(s, X0, 176, 480, 190, head('YOUR VOTE.', 'SCAN NOW.', size=88, accent=(1,), line=84), 'Headline')
    T(s, X0, 366, 460, 70, p('Which product would you use? One vote per phone.', 22, PAPER, line=30), 'Line')
    KO.qr_panel(s, KO.ASSETS / 'slido-qr.png', 596, 110, 300, 'QR code to vote on Slido', 'Same QR as on Friday')
    KO.notes(s, 'After the last demo. In Slido, start the poll "Audience Award: which product would you use?" '
                '(results are hidden). Leave this slide up while the judges decide.\n'
                'When the judges are back: stop the poll, read the four numbers, and put them into the '
                'Audience Award slide (Hackathon_Audience_Award.pptx: right-click the chart > Edit Data).')


def build():
    D2.make_dark_bg()
    KO.crop(KO.SRC / 'photo-polaroids.jpg', KO.ASSETS / 'photo-polaroids.jpg', 300 / 436, cx=0.5, cy=0.5,
            width=1100)
    prs = KO.new_deck()
    K.brand_links(prs)
    welcome(K.new_slide(prs))
    s = K.new_slide(prs)
    KO.s_end(s)
    # Google review QR in the free corner under the door
    K.qr_png(REVIEW_URL, KO.ASSETS / 'review-qr.png', scale=20)
    side = 110
    qx, qy = 812, 418
    KO.card(s, qx, qy, side, side, 'Review QR panel', 'FFFFFF', alpha=1, r=10)
    pad = 6
    K.picture(s, KO.ASSETS / 'review-qr.png', qx + pad, qy + pad, side - 2 * pad, side - 2 * pad, 'Review QR',
              'QR code to review Example College on Google Maps')
    T(s, 660, qy + 30, qx - 12 - 660, 50, [p('Review us', 16, PAPER, True, line=21, align='r'),
                                          p('on Google', 16, PAPER, True, line=21, align='r')], 'Review text')
    KO.notes(s, 'Your short speech (1–2 minutes). At the end: "If you enjoyed these days, scan the code and leave us '
                'a Google review."\nFor example:\n'
                'At Example College we say: you build here. That is what happened this weekend: people from different '
                'backgrounds, builders, business people, designers, came together and built real products in four '
                'days. Whatever the result today, you have done something most people only talk about.\n'
                'Now, let’s see what they built.')
    lineup(K.new_slide(prs))
    for n, product, mentor in LINEUP:
        team_slide(K.new_slide(prs), n, product, mentor)
    vote(K.new_slide(prs))
    prs.core_properties.title = 'AI Entrepreneurship Hackathon — Demo Day'
    prs.core_properties.author = 'Example College'
    prs.save(OUT)
    return OUT


if __name__ == '__main__':
    print(build().name)
