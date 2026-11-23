#!/usr/bin/env python3
"""The Mentor Plan: two pages attached to the email to the mentors.

    python documents/make_mentor_plan.py

Same look and layout code as the Participant Guide and the Staff Plan.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pptx_kit as K                                                       # noqa: E402
import make_pack as MP                                                     # noqa: E402
import make_pptx as MX                                                     # noqa: E402
from make_guide import BOTTOM, LM, SIZE, W, Flow, columns                  # noqa: E402
from make_staff import TIME_W, day                                         # noqa: E402

OUT = HERE.parent / 'output' / 'documents'
NAME = 'Hackathon_Mentor_Plan'


# ======================================================================= pages
def page_1(s):
    f = Flow(s, LM, MP.BANNER_FIRST + 24, W)
    f.lead('Thank you for mentoring. This plan shows where you need to be, when, and what your team needs from '
           'you at each step. **Your job isn’t to build for the team.** It’s to keep them on a small, doable '
           'idea, help them plan, and make sure everyone has real work.')

    f.h('At a glance')
    f.table([104, W - 104], [
        ('Where', 'Example Campus, 1 Example Street, 10115 Berlin. **Friday and Monday on site.** Saturday and '
                  'Sunday online on Discord (campus is optional).'),
        ('Friday', '**Please arrive at 08:30** for your badge. Teams are revealed at 10:00. We finish at 17:30.'),
        ('Sat and Sun', '**Online.** 09:00 morning call on Zoom, then 12:30 checkpoint and 17:00 end-of-day '
                        'session with your team on Discord.'),
        ('Monday', '**At Example Campus from 14:00:** presentations, awards and networking until 17:30.'),
        ('AI key', 'We give you your team’s **AI API key** on Friday. Share it only in your team’s private '
                   'Discord channel, never in public channels or on GitHub.'),
        ('Problems', '**#mentors** on Discord, or tell Ada directly.'),
    ], 'At a glance', outer=True, first='label', size=SIZE)

    f.h('Friday 23 October')
    f.table([TIME_W, W - TIME_W], [
        ('08:30', 'Arrive at Example Campus and get your badge at the entrance.'),
        ('09:00–10:00', '**Kick-off.**'),
        ('10:00–10:30', '**Teams revealed.** Meet your team.'),
        ('10:30–12:00', '**Brainstorm.** Help the team land on one idea. Some arrive with an idea, some with '
                        'something vague. Make sure it can be built in three days: cut it down and narrow it. '
                        'Then the team picks a **team name** and a **product name** and makes a **3–4 slide idea '
                        'pitch**: the problem, who has it, the solution, and where the AI is.'),
        ('12:00–13:00', 'Lunch.'),
        ('13:00–14:00', '**Idea pitch** on stage, at most 6–7 minutes per team.'),
        ('14:00–15:00', '**Development plan.** The most valuable hour you’ll give as a mentor (see page 2).'),
        ('15:00–16:00', '**Roles.** Let members pick roles that fit their skills. Teamwork first, and everyone '
                        'gets a real task.'),
        ('16:00–17:00', '**Building** starts.'),
        ('17:00–17:30', '**End-of-day session** with your team.'),
    ], 'Friday', first='time', size=9.1)
    return f.y


def page_2(s):
    f = Flow(s, LM, MP.BANNER_NEXT + 24, W)
    f.h('The development plan')
    f.table([104, W - 104], [
        ('What it is', 'A one-page map from the idea to Sunday’s demo: who the user is, **the one feature that '
                       'must work**, the build steps in order, who does what, and what must run by Saturday 12:30 '
                       'and Sunday 12:30.'),
        ('Why it matters', 'Teams with a clear plan ask for help less, lose less time and work better together. '
                           'Their chance of a working demo goes up.'),
        ('Tools', 'A shared Google Doc or Miro board for the plan. GitHub Projects, Trello or Notion for the '
                  'task list. draw.io or Figma for the screens.'),
        ('Example', '“An AI assistant that drafts replies to a café’s customer emails.” **Must work:** paste in '
                    'an email, get a reply in the café’s tone. **Steps:** a simple web page, then the AI call '
                    'with the café’s menu and rules, then a copy button. **Only if there’s time:** connect it to '
                    'Gmail. **Roles:** one builder does the AI call, one the page; the business person writes the '
                    'pitch and tests it with five real emails.'),
    ], 'Development plan', outer=True, first='label', size=SIZE)

    a, b = columns(s, f.y + 4)
    day(a, 'Saturday 24 October', 'Online', [
        ('09:00', 'Morning call on Zoom. Then every team works in its Discord team channel, also those on '
                  'campus.'),
        ('12:30', '**Checkpoint**, 20–30 minutes: progress, blockers, and is the team working together?'),
        ('15:00', 'Drop-in help from our business mentors, for teams whose idea has grown too big.'),
        ('17:00', '**End-of-day session.** The team recaps the day. Check that all went smoothly, get them '
                  'excited for tomorrow, and send them off to rest.'),
    ])
    day(b, 'Sunday 25 October', 'Online', [
        ('09:00', 'Morning call on Zoom. The clocks went back one hour last night.'),
        ('12:30', '**Checkpoint.** The MVP should run, the business side should match what it does, and the AI '
                  'should be visible in it.'),
        ('16:00', 'Feature freeze: only fixes from now on.'),
        ('17:00', '**End-of-day session:** full demo rehearsal, small fixes done.'),
        ('17:30', 'Teams hand in their GitHub link and final slides.'),
    ])

    f.y = max(a.y, b.y) + 2
    a, b = columns(s, f.y)
    day(a, 'Monday 26 October', 'Example Campus', [
        ('14:00–16:00', '**Presentations.** Please be there a little before 14:00.'),
        ('16:00–16:30', '**Awards.**'),
        ('16:30–17:30', 'Networking. End at 17:30.'),
    ])
    b.h2('Good to know', gap=0)
    b.items([
        'Don’t build it for them. Ask questions, cut scope, unblock.',
        'Talk to your team in its Discord channel, not in private messages.',
        'If someone isn’t contributing, give them a concrete task. If it continues, tell us.',
        'You never judge your own team.',
    ], 'dot', 'Good to know')
    return max(a.y, b.y)


PAGES = [page_1, page_2]


def build():
    prs = K.new_deck()
    K.brand_links(prs)
    report = []
    for n, page in enumerate(PAGES, start=1):
        s = K.new_slide(prs)
        first = n == 1
        MX.banner(s, MP.BANNER_FIRST if first else MP.BANNER_NEXT, ('MENTOR ', 'PLAN'),
                  '23–26 OCTOBER 2026  ·  EXAMPLE CAMPUS' if first else None)
        end = page(s)
        MX.footer(s, n, len(PAGES))
        report.append((n, end))
    path = OUT / f'{NAME}.pptx'
    prs.core_properties.title = 'AI Entrepreneurship Hackathon — Mentor Plan'
    prs.core_properties.author = 'Example College'
    prs.core_properties.subject = 'When to be where, and what your team needs from you at each step'
    prs.save(path)
    return path, report


if __name__ == '__main__':
    path, report = build()
    print(path.name)
    for n, end in report:
        room = BOTTOM - end
        print(f'  page {n}: content ends at {end:5.0f} pt, {room:4.0f} pt to spare'
              + ('' if room >= 0 else '   <-- OVERFLOWS THE PAGE'))
