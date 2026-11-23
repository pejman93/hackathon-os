#!/usr/bin/env python3
"""The Participant Guide: the file attached to the selection email.

    python documents/make_guide.py

Edit the words below and rebuild, or edit the .pptx by hand and export it from PowerPoint
(File > Export > PDF).
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pptx_kit as K                                                       # noqa: E402
from pptx_kit import BC, BODY, BRAND, INK, PAGE_H, PAGE_W, RULE, SLATE, Para, Run, md   # noqa: E402
import make_pack as MP                                                     # noqa: E402
import make_pptx as MX                                                     # noqa: E402

OUT = HERE.parent / 'output' / 'documents'
NAME = 'Hackathon_Participant_Guide'
LM = 48
W = PAGE_W - 2 * LM
BOTTOM = PAGE_H - 40 - 12                 # nothing may go below this; the footer rule is at -40

MAIL = 'hackathon@example.org'
MAILTO = f'[{MAIL}](mailto:{MAIL})'
DISCORD = '[example.org/discord](https://example.org/discord)'
PHONE = '[+49 30 23125 000](tel:+493023125000)'       # Example College; printed once, in Contact on the last page
MAPS = '[Open the map](https://example.org/map)'

SIZE, LINE = 9.5, 13.6
K.DOT_COLOR = BRAND            # one blue on the page: bullets take the college blue too


# ====================================================================== layout
class Flow:
    """A column of blocks. Each call draws at the cursor and moves it down."""

    def __init__(self, slide, x, y, w):
        self.s, self.x, self.y, self.w, self.top = slide, x, y, w, y

    def _text(self, paras, name):
        h = K.height(paras, self.w)
        K.text(self.s, self.x, self.y, self.w, h, paras, name)
        return h

    def eyebrow(self, text):
        self._text([Para(Run(text, 7.8, True, BRAND, spc=2.0), line=10.6)], 'Eyebrow')
        self.y += 10.6 + 6

    def lead(self, text):
        self.y += self._text([Para(md(text, 11.6, INK), line=16.6)], 'Opening') + 7

    def h(self, text):
        if self.y > self.top + 1:
            self.y += 11
        K.text(self.s, self.x, self.y, self.w, 18,
               Para(Run(text.upper(), 15.5, True, BRAND, BC, spc=0.3), line=17.5), 'Heading: ' + text)
        self.y += 23

    def h2(self, text, note=None, gap=5):
        if self.y > self.top + 1:
            self.y += gap
        runs = [Run(text, 10.4, True, INK)]
        if note:
            runs.append(Run('   ' + note, 9.0, color=SLATE))
        self.y += self._text([Para(runs, line=14.2)], 'Subheading: ' + text) + 3.5

    def p(self, *texts, size=SIZE, color=BODY, after=6, name='Text'):
        line = round(size * 1.432, 1)
        self.y += self._text([Para(md(t, size, color), line=line, after=after) for t in texts], name) + after

    def items(self, items, kind='dot', name='List', size=SIZE, after=3.4):
        ind = {'dot': 12, 'num': 16, 'box': 17}[kind]
        paras = [Para(md(t, size), line=LINE, after=after, marL=ind, indent=-ind, bullet=kind) for t in items]
        self.y += self._text(paras, name) + 7

    def table(self, widths, rows, name, head=None, outer=False, size=9.2, first='plain'):
        """rows of strings. first: how the first column is set
        ('plain', 'label' = small blue capitals, 'time' = bold blue, 'big' = large blue)."""
        def cell(text, c):
            if c == 0 and first == 'label':
                return [Para(Run(text.upper(), 7.5, True, BRAND, spc=0.7), line=10.6, before=1.9)]
            if c == 0 and first == 'time':
                return [Para(Run(text, 9.0, True, BRAND), line=12.8)]
            if c == 0 and first == 'big':
                return [Para(Run(text, 15, True, BRAND, BC), line=15.4)]
            return [Para(md(text, size), line=12.8, before=1.6 if first == 'big' else 0)]
        body = []
        if head:
            body.append([[Para(Run(t.upper(), 7.3, True, SLATE, spc=0.9), line=10.2)] for t in head])
        body += [[cell(t, c) for c, t in enumerate(r)] for r in rows]
        pad = [(4.2, 10, 4.4, 6)] + [(4.2, 6, 4.4, 10)] * (len(widths) - 1) if outer else (3.3, 0, 3.5, 8)
        _, h = K.table(self.s, self.x, self.y, widths, body, name, pad=pad,
                       outer='B9BAC4' if outer else None, head_rule='B9BAC4' if head else None)
        self.y += h + 9

    def photos(self, names, caption):
        x = self.x
        alts = ('Example Campus, the brick building seen from the street', 'A shared work floor at Example Campus',
                'A team room at Example Campus', 'The wooden staircase at Example Campus')
        for (path, pw, ph), alt in zip(MP.photo_strip(names, self.w), alts):
            K.picture(self.s, path, x, self.y, pw, ph, 'Photo', alt)
            x += pw + MP.PHOTO_GAP
        self.y += MP.PHOTO_H + 6
        self.p(caption, size=8.5, color=SLATE, after=0, name='Photo caption')


def columns(slide, y, gap=22):
    w = (W - gap) / 2
    return Flow(slide, LM, y, w), Flow(slide, LM + w + gap, y, w)


def day(f, title, where, rows):
    f.h2(title, where)
    f.table([44, f.w - 44], rows, title, first='time', size=9.1)


# ======================================================================= pages
def page_1(s):
    f = Flow(s, LM, MP.BANNER_FIRST + 24, W)
    f.lead('Welcome to the first hackathon at the Example College of Business and Technology. '
           'We’re delighted to have you here.')
    f.p('This guide has everything you need to know for the four days, plus the links you’ll use along the way.',
        '**It’s not an exam and nobody is graded.** The most valuable thing you can do is support your team '
        'and make sure everyone has something real to work on.')

    f.h('At a glance')
    f.table([126, W - 126], [
        ('Friday 23 Oct', '**At Example Campus.** Be at the reception at **08:30**, where our team will be waiting '
                          'for you. We start at 09:00 and finish at 17:30.'),
        ('Sat 24 & Sun 25 Oct', '**Campus or home, your choice.** 09:00 to 17:30.'),
        ('Monday 26 Oct', '**At Example Campus from 14:00.** The morning is free.'),
        ('Where', 'Example Campus, 1 Example Street, 10115 Berlin'),
        ('Before Wed 21 Oct', f'Join our Discord with your real name: {DISCORD}'),
        ('Questions', MAILTO),
    ], 'At a glance', outer=True, first='label', size=SIZE)

    f.h('What you’ll build')
    f.p('In four days, your team builds a working AI product that helps a business. It can be an app, an AI '
        'agent or an automation. Your team picks the idea on Friday, together with your mentor. Nobody hands '
        'you a problem: you choose it.',
        'Keep it small enough to finish in two and a half days. **A simple thing that works beats a clever '
        'thing that doesn’t.**')

    f.h('Goals')
    f.items([
        '**Collaboration.** Experience teamwork with people from different backgrounds and stories. In today’s '
        'digital world, working well with others is as important as your own skills.',
        '**AI skill development.** Work hands-on with the OpenAI API and AI tools, and learn by building.',
        '**Think like an entrepreneur or intrapreneur.** By designing and launching an AI product, you learn '
        'how businesses compete and what customers need, whether you start your own company one day or work '
        'inside an existing one.',
        '**Enjoyment.** Have fun while building something together, and enjoy our refreshments.',
    ], 'num', 'Goals')

    f.photos(['campus', 'workspace', 'team', 'stage'],
             'Example Campus, 1 Example Street: the building, a shared work floor, a team room and the staircase.')
    return f.y


def page_2(s):
    f = Flow(s, LM, MP.BANNER_NEXT + 22, W)
    f.h('Your team and your mentor')
    f.p('We’ve put you in a small team with a mix of skills: people who build, people who work out the business '
        'side, and people who design and present. You’ll meet your team and your mentor on Friday morning.',
        '**Your mentor stays with your team for all four days.** They help you pick an idea you can finish, plan '
        'the work, get unstuck (code included), and make sure everyone has something to do. Your mentor also '
        'gives your team the AI tools and API access we provide.',
        'Our business mentor moves between all the teams and helps with the business side: who would use it, '
        'what they’d pay, and what it costs to run.')

    f.h('The four days')
    a, b = columns(s, f.y)
    day(a, 'Friday 23 October', 'Example Campus', [
        ('08:30', 'Arrive at the Example Campus reception. Our team will be there waiting for you'),
        ('09:00', 'Welcome and how the four days work'),
        ('09:20', 'A live example of the kind of product we mean'),
        ('09:40', 'A few words from Example College'),
        ('10:00', '**Teams and mentors revealed**'),
        ('10:30', 'Brainstorm with your team and pick your idea'),
        ('12:00', 'Lunch'),
        ('13:00', '**Idea pitch:** each team presents its idea in a few minutes'),
        ('14:00', 'Development plan with your mentor'),
        ('15:00', 'Split the tasks'),
        ('16:00', 'Start building'),
        ('17:00', 'End-of-day session with your mentor'),
        ('17:30', 'End of day'),
    ])
    day(b, 'Saturday 24 October', 'Campus or home', [
        ('09:00', 'Morning call on Zoom (15 min)'),
        ('09:15', 'Build'),
        ('12:30', '**Check-in with your mentor:** show something that runs, even if it’s rough'),
        ('15:00', 'Drop-in help: if your idea has grown too big, we help you cut it down'),
        ('17:00', 'End-of-day session with your mentor'),
        ('17:30', 'End of day'),
    ])
    b.y += 4
    day(b, 'Sunday 25 October', 'Campus or home', [
        ('09:00', 'Morning call on Zoom'),
        ('09:15', 'Build'),
        ('12:30', 'Check-in with your mentor'),
        ('16:00', '**Feature freeze:** no new features, only fixes'),
        ('17:00', 'End-of-day session with your mentor: demo rehearsal'),
        ('17:30', '**Hand in** your GitHub link and final slides (in the shared Drive). End of day'),
    ])
    y = max(a.y, b.y) + 6
    a, b = columns(s, y)
    day(a, 'Monday 26 October', 'Example Campus, from 14:00', [
        ('Morning', 'Free for last fixes, wherever suits you. No need to come in'),
        ('14:00', '**Live demos:** 8 minutes per team plus 4 minutes of questions'),
        ('15:00', 'Judges decide (short break)'),
        ('15:30', 'Awards'),
        ('16:00', 'Photos and networking'),
        ('17:00', 'End'),
    ])
    b.h2('About the weekend')
    b.p('Saturday and Sunday work the same way wherever you are. Come to the campus if you like working '
        'together in person, or join from home. Your mentor, the morning call and your team channel are there '
        'for both.',
        '**Please join all four days.** If something gets in the way, tell us as early as you can.')
    return max(a.y, b.y)


def page_3(s):
    f = Flow(s, LM, MP.BANNER_NEXT + 22, W)
    f.h('Getting there')
    f.p(f'**Example Campus, 1 Example Street, 10115 Berlin**   ·   {MAPS}', after=5)
    f.table([170, 180, W - 350], [
        ('Metro M1', 'Harbour Street', 'about 10 minutes'),
        ('Train R1, R2', 'Central Station', 'about 15 minutes'),
        ('Bus 100', 'Example Street', 'about 2 minutes'),
    ], 'Getting there', head=('By', 'Get off at', 'Then walk'))

    f.h2('When you arrive')
    f.items([
        'Go into the building and head to the Example Campus reception.',
        'Our team will be there waiting for you: on Friday from 08:30, and on Monday shortly before 14:00.',
        'We’ll take you up to the hackathon rooms. Example Campus guests can’t go up on their own, so please wait for us '
        'at reception.',
    ], 'num', 'When you arrive')
    f.y -= 2
    f.p(f'**Running late or can’t find us?** Message us on Discord, write to {MAILTO}, or call Example College '
        '(the number is on the last page).')

    # two short lists side by side: what to do before, and what to expect on the day
    a, b = columns(s, f.y + 11)
    a.h('Before you arrive')
    a.items([
        f'**Join Discord** with your real name by Wednesday 21 October: {DISCORD}',
        '**Create a free GitHub account** at [github.com](https://github.com), if you don’t have one.',
        '**Check that your laptop works,** and pack the charger.',
    ], 'box', 'Before you arrive')
    b.h('Practical info')
    b.items([
        '**Food:** lunch on Friday. Snacks, coffee, tea and water whenever you’re on campus.',
        '**Language:** English.',
        '**Photos:** we’ll take photos on Friday and Monday. If you’d rather not be in them, just tell us.',
    ], 'dot', 'Practical info')
    f.y = max(a.y, b.y)

    f.h('What you show on Monday')
    f.items([
        '**A product that runs live.** Someone who didn’t build it can try it.',
        '**Real AI inside.** Your product calls an AI model for real. Faked answers don’t count.',
        '**One real user with one real problem.** A specific person or role, not “everyone”.',
        '**A price.** What you’d charge, and roughly what it costs per month to run.',
        '**Your GitHub link and final slides,** handed in by Sunday 17:30, using our template.',
        '**No real personal data.** Use made-up or public data only.',
    ], 'dot', 'What you show on Monday')

    f.h('Questions people ask')
    a, b = columns(s, f.y)
    qa = [
        ('I can’t code. Is that a problem?', 'No. Every team needs business and design people too.'),
        ('Do I have to come to campus on the weekend?',
         'No. Come if you like, or work from home. It works the same either way.'),
        ('Do I need to come on Monday morning?', 'No. We start at 14:00 with the demos.'),
        ('Can I switch teams?', 'Teams are put together on purpose so they’re balanced. If something isn’t '
                                'working, talk to your mentor.'),
        ('What if I’m stuck?', 'Ask your team first, then your mentor, then post in #help.'),
    ]
    for col, part in ((a, qa[:3]), (b, qa[3:])):
        paras = []
        for q, ans in part:
            paras.append(Para(Run(q, SIZE, True, INK), line=LINE, after=1.5))
            paras.append(Para(md(ans, SIZE), line=LINE, after=8))
        col.y += col._text(paras, 'Questions') + 4
    return max(a.y, b.y)


def page_4(s):
    f = Flow(s, LM, MP.BANNER_NEXT + 22, W)
    f.h('How judging works')
    f.p('Judges from the industry score each team from 1 to 5 on:', after=4)
    f.table([52, W - 52], [
        ('30%', 'Does it work live?'),
        ('20%', 'Does it solve a real problem for a real user?'),
        ('20%', 'Does the business case hold up: who pays, how much, and why they’d switch?'),
        ('15%', 'Could it keep running: what does it cost per month, and what does it depend on?'),
        ('15%', 'How good is the demo?'),
    ], 'Judging', first='big', size=SIZE)
    f.y -= 2
    f.p('Judges score on their own first, then compare. A mentor never judges their own team.')

    f.h('AI policy')
    f.p('This is an AI hackathon, so AI tools are welcome for building: ChatGPT, Copilot, Cursor, '
        'whatever helps you. Two things we ask:', after=4)
    f.items([
        'Be able to explain every part of your product when the judges ask.',
        'Say in your final slides which AI tools you used, and for what.',
    ], 'num', 'AI policy')

    f.h('AI tools and your API key')
    f.p('**We provide the AI tools and the API access your team needs.** We hand them to your mentor, who shares '
        'them with your team on Friday. This includes one OpenAI API key per team, with a spending limit. An API '
        'key is a password that lets your product use OpenAI’s AI models.', after=4)
    f.items([
        'Keep the key in a .env file. Never put it in your code or on GitHub.',
        'Never post it outside your team channel.',
        'Every use costs money, so use it with care.',
        'We switch all keys off after Monday.',
    ], 'dot', 'API key rules')

    f.h('Tools and links')
    f.p('**From us:** Discord  ·  Zoom for the morning calls (links in #announcements)  ·  a shared Drive folder  '
        '·  the idea-pitch and final-presentation templates  ·  AI tools and one OpenAI API key per team, '
        'through your mentor', after=5)
    f.p('**To build with:**', after=2)
    f.items([
        'OpenAI docs: [platform.openai.com/docs](https://platform.openai.com/docs)',
        'A quick interface: Streamlit or Gradio (Python), or no-code builders like Lovable, v0 or Bolt',
        'Code: [github.com](https://github.com)',
        'Planning and screens: draw.io or Figma',
    ], 'dot', 'To build with')
    f.y -= 2
    f.p('Use what your team already knows.')

    return f.y


def page_5(s):
    f = Flow(s, LM, MP.BANNER_NEXT + 22, W)
    f.h('Discord: how we’ll use it')
    f.p('Discord is a free chat app with text channels, voice and video calls, and screen sharing. It’s our main '
        'space during the hackathon, and how we stay connected on Saturday and Sunday, whether you’re on campus '
        'or at home.', after=4)
    a, b = columns(s, f.y + 4)

    a.h2('1. Get an account', gap=0)
    a.items([
        'Go to [discord.com](https://discord.com), or download the app for Mac, Windows, iPhone or Android.',
        'Already have an account? Use it. You don’t need a new one.',
        'New to Discord? Create your account a few days early and verify your email right away (check your '
        'spam folder).',
        'We recommend the desktop app for screen sharing, but the browser works too.',
    ], 'dot', 'Get an account')
    a.h2('2. Join our server')
    a.p(f'Click {DISCORD}. You’ll land in our server, **Example College Tech Community**.')
    a.h2('3. Set your nickname', '(required)')
    a.items([
        'Click the server name at the top left, then **Edit Per-server Profile**, then **Nickname**.',
        'Type your real first and last name, for example **Lena Weber**.',
        'This only changes your name in our server, not anywhere else on Discord.',
        'Without your real name we can’t match you to the participant list or add you to your team channel.',
    ], 'dot', 'Set your nickname')
    a.h2('4. You’re in')
    a.p('You get the **Participant** role automatically when you join, so you see the whole hackathon area right '
        'away. Please read #rules first.',
        'Only your private team channel is missing. It appears on Friday, after the teams are revealed.')
    a.h2('What you’ll see')
    a.items([
        '**#announcements:** schedule changes, links and deadlines. Turn on notifications for this one.',
        '**#resources:** templates, the shared Drive folder, the judging criteria.',
        '**#general:** chat with everyone. Say hi: your name, what you’re good at (code, business or design), '
        'and one idea you’d like to try.',
        '**#help:** stuck? Start a new post with one question. Say what you tried and what happened. Mentors and '
        'staff answer there.',
    ], 'dot', 'What you will see')

    b.h2('On Friday: your team channel', gap=0)
    b.items([
        'Teams are revealed on Friday morning at Example Campus.',
        'Shortly after, your team’s private channels appear: one text channel and one voice channel. Only your '
        'team, your mentor and staff can see them.',
        'Then add your team number to your nickname, for example **Lena Weber · T2**.',
    ], 'dot', 'Team channel')
    b.h2('Saturday and Sunday', '(campus or home)')
    b.items([
        'Working from home? Join your team’s voice channel. You can talk, use video and share your screen, with '
        'teammates on campus too.',
        'The 09:00 morning call each day is on Zoom. The link is posted in #announcements.',
        'Your mentor will reach you in your team channel. If someone you don’t know messages you directly, '
        'Discord may put it in Message Requests, so check there too.',
    ], 'dot', 'Weekend')
    b.h2('A few rules')
    b.items([
        'Never post API keys or passwords outside your team channel.',
        'No real personal data, only made-up or public data.',
        'Ask questions in #help rather than in private messages, so others learn too.',
    ], 'dot', 'Rules')
    b.h2('Something not working?')
    b.items([
        '**No verification email:** check spam, or resend it from Discord’s settings.',
        '**The invite link doesn’t work:** write to us and we’ll send a new one.',
        '**You joined but can’t see the hackathon channels:** write to us and we’ll fix it.',
        '**No team channel yet:** that’s normal until Friday, after the teams are revealed.',
        '**Can’t or don’t want to use Discord?** Tell us and we’ll keep you updated by email and Zoom.',
    ], 'dot', 'Troubleshooting')
    b.h2('Contact')
    b.p(f'Email: {MAILTO}', f'Example College phone: {PHONE}', after=2)
    return max(a.y, b.y)


PAGES = [page_1, page_2, page_3, page_4, page_5]


def build():
    prs = K.new_deck()
    K.brand_links(prs)
    report = []
    for n, page in enumerate(PAGES, start=1):
        s = K.new_slide(prs)
        first = n == 1
        MX.banner(s, MP.BANNER_FIRST if first else MP.BANNER_NEXT, ('PARTICIPANT ', 'GUIDE'),
                  '23–26 OCTOBER 2026  ·  EXAMPLE CAMPUS' if first else None)
        end = page(s)
        MX.footer(s, n, len(PAGES))
        report.append((n, end))
    path = OUT / f'{NAME}.pptx'
    prs.core_properties.title = 'AI Entrepreneurship Hackathon — Participant Guide'
    prs.core_properties.author = 'Example College'
    prs.core_properties.subject = 'When to be where, how the four days work, and how to join Discord'
    prs.save(path)
    return path, report


if __name__ == '__main__':
    path, report = build()
    print(path.name)
    for n, end in report:
        room = BOTTOM - end
        print(f'  page {n}: content ends at {end:5.0f} pt, {room:4.0f} pt to spare'
              + ('' if room >= 0 else '   <-- OVERFLOWS THE PAGE'))
