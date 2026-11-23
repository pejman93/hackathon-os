#!/usr/bin/env python3
"""The Business Mentor Plan and the Judge Plan: two pages each, same look as the other plans.

    python documents/make_role_plans.py

Both plans open with the same overview, written once in about_page().
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pptx_kit as K                                                       # noqa: E402
import make_pack as MP                                                     # noqa: E402
import make_pptx as MX                                                     # noqa: E402
from make_guide import BOTTOM, LM, SIZE, W, Flow                           # noqa: E402
from make_staff import TIME_W                                              # noqa: E402

OUT = HERE.parent / 'output' / 'documents'
LABEL_W = 112


# ============================================================ shared overview
def about_page(s, lead):
    f = Flow(s, LM, MP.BANNER_FIRST + 24, W)
    f.lead(lead)

    f.h('About the hackathon')
    f.p('Over four days, about 20 students and professionals of all skill levels work in four teams to build '
        '**a working AI product that solves a real problem for a real user.** “Entrepreneurship” here means '
        'thinking like a founder: building something people would use and pay for, either as a new venture or '
        'as a product inside an existing company (intrapreneurship).',
        '**Why Example College.** We educate the entrepreneurs of the future. Our tech programmes are project-based: students '
        'learn by building real products, not only by studying them. And AI has changed who can build. Product '
        'development is no longer only for engineers: with today’s AI tools, anyone with a clear problem and a '
        'good idea can help shape a working product. This hackathon puts that into practice.')

    f.h('How it works')
    f.table([LABEL_W, W - LABEL_W], [
        ('Teams', 'Four teams of about five, put together on purpose so they are balanced. Each team mixes '
                  'builders, business, design and UX, and pitch and story, at different levels of experience.'),
        ('Mentors', 'Each team has its own mentor for all four days, who helps it pick an idea it can finish, plan '
                    'the work and get unstuck. Business mentors work across all teams on Friday.'),
        ('Our team', 'Our staff team runs the venue and supports the teams throughout, on site and on Discord.'),
        ('AI tools', 'We give every team AI tools and access to large language models, so each '
                     'product has real AI inside.'),
    ], 'How it works', outer=True, first='label', size=SIZE)

    f.h('The four days at a glance')
    f.table([LABEL_W, W - LABEL_W], [
        ('Fri 23 Oct', '**At Example Campus, 09:00–17:30.** Kick-off and team reveal, brainstorm, idea pitch, '
                       'development plan with the mentors, then building starts.'),
        ('Sat 24 & Sun 25', '**Building, on campus or online on Discord.** Mentor checkpoints at 12:30 and 17:00. '
                            'Sunday: feature freeze at 16:00, hand-in at 17:30.'),
        ('Mon 26 Oct', '**At Example Campus from 14:00.** Presentations until 16:00, then awards, and networking until '
                       '17:30.'),
    ], 'Four days', outer=True, first='label', size=SIZE)
    return f


# ========================================================== business mentors
def bm_page_1(s):
    f = about_page(s, 'Thank you for joining us as a business mentor. This plan explains what the hackathon is, '
                      'how it works, and what we would like from you on **Friday 23 October**.')
    return f.y


def bm_page_2(s):
    f = Flow(s, LM, MP.BANNER_NEXT + 24, W)
    f.h('Your role')
    f.p('You are not assigned to one team. You work across all four and look at each idea from the business side: '
        'as a new venture (entrepreneurship), or as a product inside an existing organisation (intrapreneurship).',
        after=4)
    f.table([LABEL_W, W - LABEL_W], [
        ('The customer', 'Who exactly has the problem? One real user or role, not “everyone”.'),
        ('Why switch', 'What do they use today, and why would they switch to this?'),
        ('Price and cost', 'What would they pay, and what does it cost per month to run?'),
        ('Inside a company', 'For intrapreneurial ideas: who in the organisation would sponsor it, and whose '
                             'budget pays for it?'),
    ], 'What you look at', outer=True, first='label', size=SIZE)
    f.p('These are the areas the judges score on Monday: a real user, the business case, and whether it could '
        'keep running. Together they make up **55% of the score.**', after=0)

    f.h('Your Friday at Example Campus')
    f.p('**The times are a guide.** Teams move at different speeds and focus on different tasks, so join each team '
        'when the moment is right.', after=4)
    f.table([TIME_W, W - TIME_W], [
        ('08:30', 'Arrive and get your badge at the entrance.'),
        ('09:00–10:30', 'Kick-off and team reveal.'),
        ('10:30–12:00', '**Brainstorm.** Visit each team for about 15 minutes. Test the customer and the problem '
                        'early, before the idea is fixed.'),
        ('12:00–13:00', 'Lunch.'),
        ('13:00–14:00', '**Idea pitch.** Give each team one or two business questions as feedback. No scoring.'),
        ('14:00–15:00', '**Development plan.** Check that each team has a clear business case and knows what it '
                        'will test over the weekend.'),
        ('From 15:00', '**Business session** with the business-role member of each team. They carry the business '
                       'work through the weekend.'),
    ], 'Friday', first='time', size=9.1)

    f.h('How to work with the teams')
    f.items([
        '**Advise, don’t decide.** The team owns the idea.',
        'Don’t push your own ideas, and don’t change a team’s direction once its plan is set.',
        'Talk to the team’s mentor first, so the team doesn’t get conflicting advice.',
        'Give all four teams the same time and attention.',
        '**If you also judge on Monday:** you coached all four teams equally, so that stays fair. Please arrive '
        'at 13:30 for the judges’ briefing.',
    ], 'dot', 'How to work with the teams')
    return f.y


# ==================================================================== judges
def j_page_1(s):
    f = about_page(s, 'Thank you for joining us as a judge. This plan explains what the hackathon is, how the teams '
                      'got to Monday, and how judging works on **Monday 26 October**.')
    return f.y


def j_page_2(s):
    f = Flow(s, LM, MP.BANNER_NEXT + 24, W)
    f.h('Your Monday at Example Campus')
    f.table([TIME_W, W - TIME_W], [
        ('13:30', 'Arrive at the Example Campus reception and get your badge. **Judges’ briefing.**'),
        ('14:00–16:00', '**Presentations and judging.** Each team gives an 8-minute live demo, then 4 minutes of '
                        'questions. Score each team on your own right after its demo. After the last team, the '
                        'judges compare scores and agree on the result.'),
        ('16:00–16:30', '**Awards.**'),
        ('16:30–17:30', 'Networking.'),
    ], 'Monday', first='time', size=9.1)

    f.h('How to score')
    f.p('Score each team from 1 to 5 on each question. The teams know these questions: they are in their guide.',
        after=4)
    f.table([52, W - 52], [
        ('30%', '**Does it work live?** Someone who didn’t build it can try it, and real AI is inside: the product '
                'calls an AI model for real.'),
        ('20%', '**Does it solve a real problem for a real user?** A specific person or role, not “everyone”.'),
        ('20%', '**Does the business case hold up?** Who pays, how much, and why they would switch. For an idea '
                'inside a company: who would sponsor it.'),
        ('15%', '**Could it keep running?** What it costs per month, and what it depends on.'),
        ('15%', '**How good is the demo?** A clear story, a clear user, on time.'),
    ], 'Scoring', first='big', size=SIZE)

    f.h('Judging fairly')
    f.items([
        'Score on your own first, then compare.',
        'A mentor never judges their own team. A business mentor on the panel coached all four teams equally.',
        'Judge what works, not polish: the teams built this in two and a half days.',
        'AI tools were allowed for building. Teams should be able to explain every part and say which AI tools '
        'they used, so it is fair to ask.',
    ], 'dot', 'Judging fairly')
    f.h2('Good questions to ask', gap=2)
    f.items([
        'Who exactly is the user, and have you spoken to one?',
        'What would it cost per month to run for 100 users?',
        'What happens when the AI gets it wrong?',
        'Which part did the AI write, and can you explain how it works?',
    ], 'dot', 'Good questions')
    return f.y


PLANS = [
    ('Hackathon_Business_Mentor_Plan', ('BUSINESS MENTOR ', 'PLAN'), [bm_page_1, bm_page_2],
     'AI Entrepreneurship Hackathon — Business Mentor Plan', 'What the hackathon is, and your Friday'),
    ('Hackathon_Judge_Plan', ('JUDGE ', 'PLAN'), [j_page_1, j_page_2],
     'AI Entrepreneurship Hackathon — Judge Plan', 'What the hackathon is, and how judging works on Monday'),
]


def build(name, title, pages, doc_title, subject):
    prs = K.new_deck()
    K.brand_links(prs)
    report = []
    for n, page in enumerate(pages, start=1):
        s = K.new_slide(prs)
        first = n == 1
        MX.banner(s, MP.BANNER_FIRST if first else MP.BANNER_NEXT, title,
                  '23–26 OCTOBER 2026  ·  EXAMPLE CAMPUS' if first else None)
        end = page(s)
        MX.footer(s, n, len(pages))
        report.append((n, end))
    path = OUT / f'{name}.pptx'
    prs.core_properties.title = doc_title
    prs.core_properties.author = 'Example College'
    prs.core_properties.subject = subject
    prs.save(path)
    return path, report


if __name__ == '__main__':
    for plan in PLANS:
        path, report = build(*plan)
        print(path.name)
        for n, end in report:
            room = BOTTOM - end
            print(f'  page {n}: content ends at {end:5.0f} pt, {room:4.0f} pt to spare'
                  + ('' if room >= 0 else '   <-- OVERFLOWS THE PAGE'))
