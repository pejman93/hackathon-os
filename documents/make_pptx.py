#!/usr/bin/env python3
"""The editable PowerPoint files.

    python documents/make_pptx.py
    python documents/make_pptx.py --mentors

A4 portrait, one slide per page, real text boxes. Open, click, type.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pptx_kit as K                                              # noqa: E402
from pptx_kit import (ACCENT, BC, BODY, BRAND, DM, HAZE, INK, PAGE_H, PAGE_W,   # noqa: E402
                      PAPER, RULE, SLATE, Para, Run, md)
from pack_spec import BLOCKS, KEY, MAILBOX, SITE, SPEC, day_foot  # noqa: E402
import make_pack as MP                                            # noqa: E402

OUT = HERE.parent / 'output' / 'documents'
BUILD = HERE.parent / 'output' / 'documents' / '_build'
PROJ = HERE.parent
LM = RM = 48
W = PAGE_W - LM - RM
VENUE_MARK = PROJ / 'brand' / 'logos' / 'partner-mark.png'
APPLY_URL = 'https://example.org/hackathon/#apply'


# ====================================================================== banner
def banner(slide, h, title, date_line=None):
    """Lockup left, title in the middle, Example Campus credit right. Every word is a text box."""
    k = 1.0 if h >= 80 else 0.72
    cy = h / 2
    if h == 90:
        bg = HERE / 'assets' / 'overview-banner-bg.jpg'
    else:
        MP.banner_bg(h == MP.BANNER_FIRST)
        bg = BUILD / f'banner-bg-{h}.jpg'
    K.picture(slide, bg, -1, -0.7, PAGE_W + 2, h + 0.7, 'Banner photo',
              'An illustrated crowd under a dark blue wash')
    MP.white_logo()
    lw = 77 * k
    lh = lw * 146 / 375
    K.picture(slide, BUILD / 'logo-white.png', 40, cy - lh / 2, lw, lh, 'Example College logo',
              'Example College, Example College of Business and Technology')
    dx = 40 + lw + 9 * k
    K.line(slide, dx, cy + lh * 0.56, dx + 6 * k, cy - lh * 0.56, PAPER, 'Lockup divider', 0.7, alpha=0.5)

    tx = dx + 15 * k
    small, big = 7 * k, 14 * k
    wordmark = [Para(Run('AI ENTREPRENEURSHIP', small, color=PAPER, font=BC, spc=0.35 * k), line=small * 1.28),
                Para(Run('HACKATHON', big, bold=True, color=PAPER, font=BC), line=big * 1.08)]
    wm_w = max(wordmark[1].runs[0].width('HACKATHON'), wordmark[0].runs[0].width('AI ENTREPRENEURSHIP')) + 4
    K.text(slide, tx, 0, wm_w, h, wordmark, 'Event wordmark', anchor='ctr')

    mark_h = {90: 42, 84: 40}.get(h, 27)
    mark_w = mark_h * 1522 / 1250
    mx = PAGE_W - 40 - mark_w
    K.picture(slide, VENUE_MARK, mx, cy - mark_h / 2, mark_w, mark_h, 'Example Campus logo', 'Example Campus')
    lab = 5.8 if k == 1 else 4.9
    lab_run = Run('POWERED BY', lab, bold=True, color=PAPER, spc=1.0)
    lab_w = lab_run.width('POWERED BY') + 3
    K.text(slide, mx - 9 - lab_w, 0, lab_w, h, Para(lab_run, line=lab * 1.3, align='r'), 'Powered by', anchor='ctr')
    rule_x = mx - 9 - lab_w - 9
    K.line(slide, rule_x, cy - mark_h * 0.42, rule_x, cy + mark_h * 0.42, PAPER, 'Credit divider', 0.6, alpha=0.3)

    title_x = tx + wm_w + (26 if k == 1 else 18)
    room = rule_x - 12 - title_x
    size = 28 if k == 1 else 13.5
    plain, accent = title
    while Run(plain + accent, size, True, font=BC).width(plain + accent) > room and size > 8:
        size -= 0.5
    paras = [Para([Run(plain, size, True, PAPER, BC), Run(accent, size, True, ACCENT, BC)], line=size * 1.04)]
    if date_line:
        paras.append(Para(Run(date_line, 6.6, color=HAZE, spc=1.15), line=9.5, before=2.5))
    K.text(slide, title_x, 0, room, h, paras, 'Banner title', anchor='ctr')


def footer(slide, n, total):
    y = PAGE_H - 40
    K.line(slide, LM, y, PAGE_W - RM, y, RULE, 'Footer rule', 0.6)
    K.text(slide, LM, y + 6.5, 330, 11, Para(Run(f'{MAILBOX}   ·   {SITE}', 7.8, color=SLATE), line=10.5),
           'Footer contact')
    K.text(slide, PAGE_W - RM - 120, y + 6.5, 120, 11,
           Para(Run(f'Page {n} of {total}', 7.8, color=SLATE), line=10.5, align='r'), 'Page number')


# ================================================================ the pack
def eyebrow(text, color=BRAND, size=7.4, spc=1.55, **kw):
    return Para(Run(text, size, bold=True, color=color, spc=spc), line=size * 1.35, **kw)


def day_paras(d):
    paras = [eyebrow(d['label'], after=3),
             Para(Run(d['tagline'], 14.5, True, INK, BC), line=15.8, after=2),
             Para(Run(f"{d['place']}  ·  {d['hours']}", 8.4, True, BODY), line=11.5, after=6)]
    for when, what in d['items']:
        paras.append(Para([Run(when + '\t', 8.8, True, BRAND)] + md(what, 9.1),
                          line=12.6, after=3, marL=34, indent=-34, tabs=(34,)))
    paras.append(Para([Run(day_foot(d)[0] + '   ', 8.4, True, BRAND), Run(day_foot(d)[1], 8.4, color=SLATE)],
                      line=11.8, before=4))
    return paras


def build_pack():
    prs = K.new_deck()
    pages = [[]]
    for blk in BLOCKS:
        if blk[0] == 'pagebreak':
            pages.append([])
        else:
            pages[-1].append(blk)
    total = len(pages)
    fills = []

    for n, blocks in enumerate(pages, start=1):
        s = K.new_slide(prs)
        first = n == 1
        banner(s, MP.BANNER_FIRST if first else MP.BANNER_NEXT, SPEC['banner'],
               '23–26 OCTOBER 2026  ·  EXAMPLE CAMPUS' if first else None)
        y = (MP.BANNER_FIRST + 26) if first else (MP.BANNER_NEXT + 22)
        top = y
        i = 0
        while i < len(blocks):
            blk = blocks[i]
            kind = blk[0]
            i += 1

            if kind == 'eyebrow':
                K.text(s, LM, y, W, 11, eyebrow(blk[1], size=7.8, spc=2.0), 'Eyebrow')
                y += 11 + 6

            elif kind == 'lead':
                p = [Para(md(blk[1], 11.6, INK), line=16.8)]
                h = K.height(p, W)
                K.text(s, LM, y, W, h, p, 'Opening')
                y += h + 7

            elif kind == 'p':
                # consecutive paragraphs share one box: easier to edit, and they
                # re-flow together when a line is added
                group = [blk[1]]
                while i < len(blocks) and blocks[i][0] == 'p':
                    group.append(blocks[i][1])
                    i += 1
                p = [Para(md(t), line=14.3, after=6.5) for t in group]
                h = K.height(p, W)
                K.text(s, LM, y, W, h, p, 'Text')
                y += h + 6.5

            elif kind == 'small':
                p = [Para(Run(blk[1], 8.5, color=SLATE), line=12.4)]
                h = K.height(p, W)
                K.text(s, LM, y + 2, W, h, p, 'Note')
                y += h + 6

            elif kind == 'h':
                if y > top + 1:
                    y += 8
                K.text(s, LM, y, W, 18, Para(Run(blk[1], 15.5, True, BRAND, BC, spc=0.3), line=17.5), 'Heading: ' + blk[1].title())
                y += 18 + 5

            elif kind == 'glance':
                rows = [[[eyebrow(blk[1], before=6)], None]]
                for label, value in blk[2]:
                    rows.append([[Para(Run(label, 7.5, True, BRAND), line=10.5, before=2.2)],
                                 # the wide separators made the measured line a hair too
                                 # long, which left the TIMES row one empty line too tall
                                 [Para(md(value.replace('   ·   ', '  ·  '), 9.6), line=13.6)]])
                gf, h = K.table(s, LM, y, [104, W - 104], rows, 'At a glance', fill=PAPER,
                                pad=[(4.3, 14, 4.5, 4), (4.3, 6, 4.5, 14)], no_rule=(0,))
                gf.table.cell(0, 0).merge(gf.table.cell(0, 1))
                y += h + 8

            elif kind == 'checks':
                p = [Para(md(t, 9.6), line=13.6, after=4.2, marL=18, indent=-18, bullet='num') for t in blk[1]]
                h = K.height(p, W)
                K.text(s, LM, y, W, h, p, 'Checklist')
                y += h + 6

            elif kind == 'bullets':
                p = [Para(md(t, 9.6), line=13.6, after=4, marL=13, indent=-13, bullet='dot') for t in blk[1]]
                h = K.height(p, W)
                K.text(s, LM, y, W, h, p, 'Requirements')
                y += h + 8

            elif kind == 'days':
                gap = 12
                cw = (W - gap) / 2
                inner = cw - 24
                days = [day_paras(d) for d in blk[1]]
                for r in range(2):
                    pair = days[r * 2:r * 2 + 2]
                    ch = max(K.height(p, inner) for p in pair) + 24
                    for c, p in enumerate(pair):
                        x = LM + c * (cw + gap)
                        K.rect(s, x, y, cw, ch, PAPER, f'Day {r * 2 + c + 1} card')
                        K.rect(s, x, y, cw, 2.2, BRAND, f'Day {r * 2 + c + 1} rule')
                        K.text(s, x + 12, y + 12, inner, ch - 24, p, f'Day {r * 2 + c + 1}')
                    y += ch + gap
                y -= gap - 4

            elif kind == 'quote':
                p = [Para(Run(blk[1], 11.2, color=INK), line=15.6)]
                h = K.height(p, W - 14)
                K.rect(s, LM, y, 2.6, h + 2, ACCENT, 'Quote mark')
                K.text(s, LM + 13, y + 1, W - 14, h, p, 'Pull quote')
                y += h + 11

            elif kind == 'judging':
                rows = [[[Para(Run(pct, 17, True, BRAND, BC), line=18)],
                         [Para(md(t, 9.6), line=13.6, before=2.5)]] for pct, t in blk[1]]
                _, h = K.table(s, LM, y, [48, W - 48], rows, 'Judging criteria', pad=(4, 0, 5, 8))
                y += h + 9

            elif kind == 'pairs':
                rows = [[[Para(Run(a, 7.5, True, BRAND), line=10.5, before=2.2)],
                         [Para(md(b, 9.6), line=13.6)]] for a, b in blk[1]]
                _, h = K.table(s, LM, y, [112, W - 112], rows, 'Tools', pad=(5, 0, 5, 8))
                y += h + 3

            elif kind == 'faq':
                items = blk[1]
                half = (len(items) + 1) // 2
                gap = 20
                cw = (W - gap) / 2
                hs = []
                for c, part in enumerate((items[:half], items[half:])):
                    p = []
                    for q, a in part:
                        p.append(Para(Run(q, 9.5, True, INK), line=13, after=1.5))
                        p.append(Para(md(a, 9.1, '33353C'), line=13, after=8.5))
                    h = K.height(p, cw)
                    hs.append(h)
                    K.text(s, LM + c * (cw + gap), y + 2, cw, h, p, f'Questions, column {c + 1}')
                y += max(hs) + 10

            elif kind == 'photos':
                x = LM
                alts = ('Example Campus, the brick building seen from the street', 'A shared work floor at Example Campus',
                        'A team room at Example Campus', 'The wooden staircase at Example Campus')
                for (path, pw, ph), alt in zip(MP.photo_strip(blk[1], W), alts):
                    K.picture(s, path, x, y + 2, pw, ph, 'Photo', alt)
                    x += pw + MP.PHOTO_GAP
                y += MP.PHOTO_H + 8
                p = [Para(Run(blk[2], 8.5, color=SLATE), line=12.4)]
                h = K.height(p, W)
                K.text(s, LM, y, W, h, p, 'Photo caption')
                y += h + 10

            elif kind == 'closing':
                d = blk[1]
                lw_, rw = W * 0.60 - 36, W * 0.40 - 18
                left = [eyebrow(d['eyebrow'], color=ACCENT, after=5),
                        Para(Run(d['title'], 17, True, PAPER, BC), line=18.5, after=3),
                        Para(Run(d['text'], 9, color='D9D8D0'), line=13)]
                right = [Para([Run(d['name'], 9, True, PAPER), Run(', ' + d['role'], 9, color=PAPER)], line=14, align='r'),
                         Para(Run(d['lines'][0], 9, color=ACCENT), line=14, align='r'),
                         Para(Run(d['lines'][1], 9, color=PAPER), line=14, align='r')]
                ch = K.height(left, lw_) + 32
                K.rect(s, LM, y, W, ch, INK, 'Closing panel', radius=7)
                K.text(s, LM + 18, y + 16, lw_, ch - 32, left, 'Closing text')
                K.text(s, LM + W * 0.60, y, rw, ch, right, 'Contact', anchor='ctr')
                y += ch + 6

            else:
                raise ValueError(kind)

        footer(s, n, total)
        used = y - top
        room = (PAGE_H - 40 - 12) - top
        fills.append((n, used, room))

    path = OUT / f"{SPEC['name']}.pptx"
    prs.core_properties.title = SPEC['title']
    prs.core_properties.author = 'Example College'
    prs.save(path)
    return path, fills


# ============================================================ the invitation
INVITE = dict(
    title=('WHAT IF YOU ', 'BUILT IT?'),
    date='23–26 OCTOBER 2026  ·  EXAMPLE CAMPUS',
    eyebrow='YOU ARE INVITED',
    hook=[('FOUR DAYS. YOUR TEAM.', INK), ('A WORKING AI PRODUCT.', BRAND)],
    lead='The AI Entrepreneurship Hackathon is the first hackathon at the Example College of Business '
         'and Technology. From Friday 23 to Monday 26 October 2026, small teams build an AI product '
         'that helps a real business, and show it live to judges from the industry.',
    promise='You do not need a team, an idea or coding skills. Bring your curiosity.',
    why_title='WHY JOIN',
    why=[('Build something real.', 'Not a slide deck. An app, an AI agent or an automation that runs, built by you and your team.'),
         ('Get closer to the industry.', 'Every team has its own mentor, and judges from the industry see your product live.'),
         ('Find your team.', 'We put you in a small, mixed team: builders, business minds and designers.'),
         ('It is free.', 'No fee. We provide the AI tools, the space, food and refreshments.')],
    days_title='THE FOUR DAYS',
    # invitation: Friday 09:00 – 17:30 and Monday 13:00 – 17:00 on campus, and NO
    # hours for the weekend, only that the rooms are there and online is fine.
    # Mon 09:00 – 17:00), so the two documents differ here until the pack changes.
    days=[('FRI 23 · ON CAMPUS', '09:00 – 17:30 · Example Campus', 'Find your team.', 'Brainstorming, idea pitching and the start of development.'),
          ('SAT 24 · HYBRID', 'Campus or online', 'Build.', 'The campus rooms are free for you to use. You can also join online.'),
          ('SUN 25 · HYBRID', 'Campus or online', 'Build.', 'Same again: use the campus rooms, or join online.'),
          ('MON 26 · ON CAMPUS', '13:00 – 17:00 · Example Campus', 'Show what you made.', 'Live demos for judges from the industry, and awards.')],
    # one short line: the columns above already say where each day happens
    days_note='Times are approximate.',
    who_title='WHO IT IS FOR',
    who='Example College students and people from outside the college. Developers, designers, business minds and '
        'beginners. If you are curious about AI and want to build something, this is for you.',
    photo_caption='Example Campus, 1 Example Street. Home to startups, companies and the #ai_berlin hub.',
    cta_eyebrow='HOW TO JOIN',
    cta_title='APPLY IN THREE MINUTES',
    cta_text='Ten short questions, no CV. Scan the code or go to example.org/hackathon. '
             'After you apply, we invite you to a 15-minute intro call. Places are limited.',
    contact=('Ada Lovelace', 'Hackathon Lead', MAILBOX, SITE),
)


def build_invite():
    v = INVITE
    prs = K.new_deck()
    s = K.new_slide(prs)
    banner(s, 90, v['title'], v['date'])
    L, R = 40, PAGE_W - 40
    CW = R - L
    marks = []

    def put(name, y, h):
        marks.append((name, y, y + h))
        return y + h

    y = 108
    K.text(s, L, y, CW, 11, eyebrow(v['eyebrow'], size=7.5, spc=2.5), 'Eyebrow')
    y = put('eyebrow', y, 11) + 7

    hook = [Para(Run(t, 33, True, c, BC), line=32.5) for t, c in v['hook']]
    h = K.height(hook, CW)
    K.text(s, L, y, CW, h, hook, 'Headline')
    y = put('headline', y, h) + 10

    lead = [Para(md(v['lead'], 11, INK), line=15.8, after=6),
            Para(Run(v['promise'], 11, True, BRAND), line=15.8)]
    h = K.height(lead, CW)
    K.text(s, L, y, CW, h, lead, 'What it is')
    y = put('lead', y, h) + 20

    # ---- why join: 2 x 2 --------------------------------------------------
    K.text(s, L, y, CW, 16, Para(Run(v['why_title'], 12.5, True, BRAND, BC, spc=0.5), line=15), 'Heading: Why join')
    y = put('why heading', y, 16) + 6
    gap = 22
    cw = (CW - gap) / 2
    num_w = 26
    for r in range(2):
        cells = []
        for c in range(2):
            title, body = v['why'][r * 2 + c]
            cells.append([Para(Run(title, 10.5, True, INK), line=14.5, after=1.5),
                          Para(Run(body, 9.3, color=BODY), line=13.2)])
        rh = max(K.height(p, cw - num_w) for p in cells)
        for c, p in enumerate(cells):
            x = L + c * (cw + gap)
            K.text(s, x, y - 1, num_w, 22, Para(Run(f'0{r * 2 + c + 1}', 17, True, BRAND, BC), line=19), f'Reason {r * 2 + c + 1} number')
            K.text(s, x + num_w, y, cw - num_w, rh, p, f'Reason {r * 2 + c + 1}')
        y = put(f'why row {r + 1}', y, rh) + 12
    y += 8

    # ---- the four days ----------------------------------------------------
    K.text(s, L, y, CW, 16, Para(Run(v['days_title'], 12.5, True, BRAND, BC, spc=0.5), line=15), 'Heading: The four days')
    y = put('days heading', y, 16) + 7
    dgap = 18
    dw = (CW - dgap * 3) / 4
    cols = [[Para(Run(a, 7, True, BRAND, spc=1.2), line=9.6, after=1.5),
             Para(Run(hrs, 8.6, True, INK), line=11.8, after=5),
             Para(Run(b, 13, True, INK, BC), line=13.6, after=4),
             Para(Run(t, 8.7, color=BODY), line=12.2)] for a, hrs, b, t in v['days']]
    dh = max(K.height(p, dw) for p in cols)
    for i, p in enumerate(cols):
        K.text(s, L + i * (dw + dgap), y, dw, dh, p, f'Day {i + 1}')
    y = put('days', y, dh) + 8
    note = [Para(Run(v['days_note'], 8.5, color=SLATE), line=12)]
    h = K.height(note, CW)
    K.text(s, L, y, CW, h, note, 'Days note')
    y = put('days note', y, h) + 20

    # ---- who it is for + photos ------------------------------------------
    left_w = 184
    K.text(s, L, y, left_w, 16, Para(Run(v['who_title'], 12.5, True, BRAND, BC, spc=0.5), line=15), 'Heading: Who it is for')
    who = [Para(Run(v['who'], 9.5, color=BODY), line=13.6)]
    wh = K.height(who, left_w)
    K.text(s, L, y + 22, left_w, wh, who, 'Who it is for')
    px = L + left_w + 14
    strip_w = R - px
    scale = None
    alts = ('Example Campus, the brick building seen from the street', 'A shared work floor at Example Campus',
            'A team room at Example Campus', 'The wooden staircase at Example Campus')
    ph = 80
    x = px
    usable = strip_w - 5 * 3
    for (path, pw, _), alt in zip(MP.photo_strip(['campus', 'workspace', 'team', 'stage'], W), alts):
        scale = scale or usable / (W - MP.PHOTO_GAP * 3)
        K.picture(s, path, x, y + 2, pw * scale, MP.PHOTO_H * scale, 'Photo', alt)
        ph = MP.PHOTO_H * scale
        x += pw * scale + 5
    cap = [Para(Run(v['photo_caption'], 7.2, color=SLATE), line=10)]
    K.text(s, px, y + 2 + ph + 4, strip_w, 10, cap, 'Photo caption')
    y = put('who + photos', y, max(22 + wh, ph + 2 + 16))

    # ---- call to action, full bleed --------------------------------------
    block_h = 130
    by = PAGE_H - block_h
    K.rect(s, -1, by, PAGE_W + 2, block_h + 1, INK, 'Call to action panel')
    qr = 78
    qx = R - qr
    K.rect(s, qx - 5, by + 13, qr + 10, qr + 10, 'FFFFFF', 'QR panel', radius=5)
    K.picture(s, K.qr_png(APPLY_URL, BUILD / 'qr-apply.png'), qx, by + 18, qr, qr, 'QR code',
              'QR code that opens the application form at example.org/hackathon')
    K.text(s, qx - 5, by + 13 + qr + 14, qr + 10, 9, Para(Run('SCAN TO APPLY', 6, True, PAPER, spc=1.0), line=8, align='ctr'), 'QR label')
    text_w = qx - 5 - 22 - L
    cta = [eyebrow(v['cta_eyebrow'], color=ACCENT, size=7, spc=2.5, after=5),
           Para(Run(v['cta_title'], 19, True, PAPER, BC), line=20, after=4),
           Para(Run(v['cta_text'], 9.2, color='D9D8D0'), line=13.2, after=7),
           Para([Run(v['contact'][0], 8.6, True, PAPER), Run(f", {v['contact'][1]}   ·   ", 8.6, color=PAPER),
                 Run(v['contact'][2], 8.6, color=ACCENT)], line=12)]
    ch = K.height(cta, text_w)
    K.text(s, L, by + (block_h - ch) / 2, text_w, ch, cta, 'Call to action')
    marks.append(('cta block', by, PAGE_H))

    path = OUT / 'Hackathon_Invitation.pptx'
    prs.core_properties.title = 'AI Entrepreneurship Hackathon — Invitation'
    prs.core_properties.author = 'Example College'
    prs.save(path)
    return path, marks, (y, by)


if __name__ == '__main__':
    if '--invite-only' not in sys.argv:          # leave the pack file untouched
        path, fills = build_pack()
        print(path.name)
        for n, used, room in fills:
            flag = '' if used <= room else '   <-- OVERFLOWS THE PAGE'
            print(f'  page {n}: {100 * used / room:3.0f}% full{flag}')
    if KEY != 'participants':                    # --mentors builds that pack only
        sys.exit(0)
    path, marks, (content_end, block_top) = build_invite()
    print(path.name)
    print(f'  content ends at {content_end:.0f}pt, call-to-action panel starts at {block_top:.0f}pt '
          f'-> {block_top - content_end:.0f}pt clear' + ('' if block_top - content_end >= 12 else '   <-- TOO TIGHT'))
