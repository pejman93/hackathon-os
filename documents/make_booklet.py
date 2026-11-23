#!/usr/bin/env python3
"""Field Notes: the participants' booklet. How to find a problem, shape it into a product,
and pick the tools to build it.

    python documents/make_booklet.py
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pptx_kit as K                                                       # noqa: E402
from pptx_kit import BRAND, INK, SLATE, Para, Run                          # noqa: E402
import make_pack as MP                                                     # noqa: E402
import make_pptx as MX                                                     # noqa: E402
from make_guide import BOTTOM, LM, SIZE, W, Flow, columns                  # noqa: E402

OUT = HERE.parent / 'output' / 'documents'
NAME = 'Hackathon_Field_Notes'
MAIL = 'hackathon@example.org'
LABEL_W = 120


def link(text, url):
    return f'[{text}]({url})'


def tool(name, url, shown, what):
    return f'**{name}** ({link(shown, url)}). {what}'


def tools(f, title, rows, gap=7):
    f.h2(title, gap=gap)
    f.items([tool(*r) for r in rows], 'dot', title)


def label_table(f, rows, name):
    f.table([LABEL_W, W - LABEL_W], rows, name, outer=True, first='label', size=SIZE)


# ======================================================================= pages
def page_1(s):
    f = Flow(s, LM, MP.BANNER_FIRST + 24, W)
    f.lead('How to find a problem worth solving, turn it into a product, and pick the tools to build it '
           'in four days.')

    f.h('Four days, one working product')
    f.p('A hackathon gives a small team a fixed number of days to build something that works. Ours has four:',
        after=4)
    label_table(f, [
        ('First day', 'Meet your team, choose a problem, pitch the idea, plan the build.'),
        ('Second day', '**Build.** By midday, something should run from start to finish, however rough.'),
        ('Third day', '**Finish.** New features stop in the afternoon. Then fix, rehearse and hand in.'),
        ('Last day', '**Show it** to the judges, live.'),
    ], 'Four days')
    f.p('Take away the choosing and the presenting, and you have about two and a half days of building. '
        'That is enough to do one useful thing properly.',
        'Teams that finish tend to get three things right: they pick a narrow problem, they get something '
        'running early, and nobody on the team is left idle. On a mixed team, the people who aren’t writing '
        'code are the easiest to lose. Give them real work: talking to users, working out the price, writing '
        'the demo script, designing the screens.')

    f.h('Why “entrepreneurship”')
    f.p('Adding AI to a product now takes an afternoon. Finding someone who needs it, and would pay for it, '
        'takes much longer. That second part is what this hackathon is about. You can go in one of two directions:',
        after=4)
    label_table(f, [
        ('A new company', 'You would sell the product to customers yourself.'),
        ('Inside a company', 'The product runs inside an existing organisation. For that you need a manager who '
                             'backs it and a budget to pay for it.'),
    ], 'Directions')

    f.h('What you show on the last day')
    f.items([
        '**A product that runs live,** which someone who didn’t build it can use.',
        '**Real calls to an AI model** inside it. Faked or hard-coded answers don’t count.',
        '**One specific user** with one specific problem.',
        '**A price,** and roughly what it costs per month to run.',
        '**Your GitHub link and slides,** handed in at the end of the third day.',
    ], 'dot', 'Last day')

    f.photos(['campus', 'workspace', 'team', 'stage'],
             'Example Campus, 1 Example Street: where the first and last day happen.')
    return f.y


def page_2(s):
    f = Flow(s, LM, MP.BANNER_NEXT + 22, W)
    f.h('Where the points are')
    f.table([52, W - 52], [
        ('30%', 'Does it work live?'),
        ('20%', 'Does it solve a real problem for a real user?'),
        ('20%', 'Who pays, how much, and why would they switch?'),
        ('15%', 'What does it cost to run, and what does it depend on?'),
        ('15%', 'How good is the demo?'),
    ], 'Judging', first='big', size=SIZE)
    f.y -= 2
    f.p('The middle three rows add up to **55% of the score,** and none of them is about code. That is why every '
        'team has business and design people, and why a business mentor visits every team on the first day.')

    f.h('Finding the problem')
    f.p('Start from people, not from technology. The question to ask is: **who loses hours, and on what?**', after=4)
    a, b = columns(s, f.y + 2)
    a.h2('Where to look', gap=0)
    a.items([
        '**Jobs you’ve had.** The weekly task that should have been automatic.',
        '**Anyone who runs something.** A shop, a dental practice, a café, a one-person agency. Ask what they '
        'keep putting off until Sunday evening.',
        '**Your own paperwork.** Applications, invoices, appointments, forms.',
        '**The floors around you.** Example Campus is full of small companies. A chat at the coffee machine counts as research.',
    ], 'dot', 'Where to look')
    b.h2('Five questions for each candidate', gap=0)
    b.items([
        'Does it happen every week?',
        'Can someone put a number on it, in hours or in euros?',
        'Are people already working around it, with a spreadsheet, copy-paste or an intern? '
        'A workaround shows the pain is real.',
        'Is the core of it reading, sorting, drafting, searching documents or summarising? '
        'AI is reliable at these.',
        'Could a rough version run by the middle of the second day?',
    ], 'num', 'Five questions')
    b.y -= 3
    b.p('**Four or five yeses:** keep it. **Fewer:** move on to the next one.', after=0)
    f.y = max(a.y, b.y)

    f.h('Ask a better question')
    f.p('Design teams brainstorm from a question that starts with **“How might we…”**. It keeps you on the '
        'problem before you fall for one solution.', after=4)
    label_table(f, [
        ('Too wide', 'How might we help schools with admin? Nobody knows where to begin.'),
        ('Too narrow', 'How might we build a chatbot for enrolment emails? The answer is already in the question.'),
        ('About right', 'How might we stop the office answering the same enrolment questions every week? This '
                        'leaves room for a chatbot, drafted replies, a better enrolment page, or something nobody '
                        'has thought of yet.'),
    ], 'How might we')
    f.p('Write five versions, then vote for the one that leads to the most ideas.', after=0)
    return f.y


def page_3(s):
    f = Flow(s, LM, MP.BANNER_NEXT + 22, W)
    f.h('Test it on a real person')
    f.p('An AI model will agree with almost any idea you show it, so talk to someone who actually has the '
        'problem. The Mom Test by Rob Fitzpatrick gives three rules:', after=4)
    f.items([
        '**Ask about their week, not your idea.** “Walk me through the last time this happened” tells you '
        'something. “Would you use an app that…” doesn’t.',
        '**What they did last week is a fact.** What they say they would do is a guess.',
        '**Praise is free.** A request to try it with their real emails means something.',
    ], 'dot', 'Mom Test')
    f.p('Then cut the idea down: **one user, one task, one screen.** Everything else goes on a “later” list, '
        'and that list waits until after the last day.')

    f.h('Your idea pitch')
    f.p('Before lunch on the first day, your team needs six answers. Together they make up your idea pitch.',
        after=4)
    label_table(f, [
        ('1  Problem', 'One sentence: who spends how much time on which task, and why.'),
        ('2  User', 'One role you could find and talk to. “Office manager at a language school” works. '
                    '“Schools” doesn’t.'),
        ('3  Product', 'What it does, in one line.'),
        ('4  What the AI does', 'Name the job: reads, sorts, drafts, searches documents or summarises. If you can’t '
                               'name it, the AI is decoration.'),
        ('5  Name', 'One name, for the product and your team. Five minutes, no more.'),
        ('6  Business case', 'Who pays, and how much? What do they use today, and why would they switch? What does '
                             'it cost per month to run? For an existing company: who backs it, and whose budget '
                             'pays?'),
    ], 'Six answers')

    f.h('An example pitch')
    f.p('Invented, to show the level of detail. Your idea can be completely different.', color=SLATE, after=4)
    label_table(f, [
        ('Problem', 'The office manager at a small language school spends about six hours a week answering the '
                    'same enrolment questions by email, because course dates, prices and levels sit in three '
                    'different documents.'),
        ('User', 'Office managers at language schools with 100–500 students.'),
        ('Product', 'A tool that drafts a reply to every enrolment email from the school’s own course information. '
                    'The office manager checks the draft and sends it.'),
        ('What the AI does', 'Reads the email, finds the right course details, writes the answer.'),
        ('Name', '**ReplyDesk**'),
        ('Business case', '€49 a month per school. Today the office replies by hand; this saves about five hours a '
                          'week. Running costs stay under €10 a month.'),
    ], 'Example')
    return f.y


def page_4(s):
    f = Flow(s, LM, MP.BANNER_NEXT + 22, W)
    f.h('Tools for building')
    f.p('Choose your tools with your mentor on the first day, and stay with them. Teams that switch halfway '
        'through rarely have anything running by the last day.', after=4)
    f.table([150, W - 150], [
        ('No developer', 'Google AI Studio or Lovable, your AI API key, Google Sheets'),
        ('One or two developers', 'The coding tools from your mentor, or Cursor, with Streamlit and Supabase'),
        ('An automation', 'n8n or Make, your AI API key, Google Forms and Sheets'),
        ('A voice assistant', 'ElevenLabs and your AI API key'),
    ], 'Starting points', head=('Your team', 'Start with'), size=SIZE)

    a, b = columns(s, f.y - 2)
    tools(a, 'Build from a description', [
        ('Google AI Studio', 'https://aistudio.google.com', 'aistudio.google.com',
         'Full apps with a live preview, connected to Sheets, Drive and Docs. Free.'),
        ('Lovable', 'https://lovable.dev', 'lovable.dev',
         'Web apps with logins and a database. Free projects are public.'),
        ('Bolt', 'https://bolt.new', 'bolt.new', 'Quick apps you can keep editing as code.'),
        ('v0', 'https://v0.app', 'v0.app', 'Apps and interfaces, one click to publish.'),
    ])
    a.h2('Code with an AI agent', gap=7)
    a.items([
        '**The AI tools we provide** reach your team through your mentor.',
        tool('Cursor', 'https://cursor.com', 'cursor.com', 'An AI code editor that works like VS Code.'),
        tool('Google Antigravity', 'https://antigravity.google', 'antigravity.google',
             'Free with a Google account, with a weekly limit.'),
    ], 'dot', 'Code with an AI agent')

    tools(b, 'Automate a workflow', [
        ('n8n', 'https://n8n.io/workflows', 'n8n.io/workflows',
         'Automations with AI steps, and thousands of templates to copy.'),
        ('Make', 'https://www.make.com', 'make.com', 'Visual automations, 1,000 free credits a month.'),
        ('Dify', 'https://dify.ai', 'dify.ai', 'Chatbots that answer from a company’s own documents.'),
    ])
    tools(b, 'Make it usable', [
        ('Streamlit', 'https://streamlit.io', 'streamlit.io', 'An interface in a few lines of Python.'),
        ('Supabase', 'https://supabase.com', 'supabase.com', 'A database with logins built in.'),
        ('Tally', 'https://tally.so', 'tally.so', 'Forms.'),
        ('ElevenLabs', 'https://elevenlabs.io', 'elevenlabs.io', 'Natural-sounding voices.'),
        ('Figma', 'https://www.figma.com', 'figma.com', 'Screens and click-through designs.'),
    ])
    f.y = max(a.y, b.y)

    f.h('Your AI API key')
    f.p('An API key is a password that lets your product call an AI model. **Every call costs money.** Your mentor '
        'gives one key to each team on the first day, together with the link to its documentation.', after=4)
    f.items([
        'Keep it in a .env file. Never put it in your code or on GitHub.',
        'Share it only in your team channel.',
        'All keys are switched off after the last day.',
    ], 'dot', 'Key rules')
    return f.y


def page_5(s):
    f = Flow(s, LM, MP.BANNER_NEXT + 22, W)
    a, b = columns(s, f.y)
    a.h('Free alternatives')
    a.items([
        tool('Ollama', 'https://ollama.com', 'ollama.com',
             'Runs open models on your own laptop, with no key and no cost. A strong argument when a client '
             'doesn’t want their data to leave the building.'),
        tool('Hugging Face', 'https://huggingface.co', 'huggingface.co',
             'Open models for speech, images, translation and classification.'),
    ], 'dot', 'Free alternatives')

    a.h('Data you can use')
    a.p('No real personal data. Use these instead:', after=4)
    a.items([
        tool('Mockaroo', 'https://www.mockaroo.com', 'mockaroo.com', 'Realistic fake customers, orders and invoices.'),
        tool('Kaggle', 'https://www.kaggle.com/datasets', 'kaggle.com/datasets',
             'Public data on retail, finance, HR and more.'),
        tool('Berlin Open Data', 'https://daten.berlin.de', 'daten.berlin.de', 'Public data on the city.'),
        tool('EU Open Data', 'https://data.europa.eu', 'data.europa.eu', 'Public data across the EU.'),
    ], 'dot', 'Data')

    b.h('Agents that act on their own')
    b.p(f'**Hermes Agent** ({link("hermes-agent.nousresearch.com", "https://hermes-agent.nousresearch.com")}) '
        'is open source, from Nous Research. It works through a task step by step, remembers what it learned, '
        f'and writes new skills for itself. **OpenClaw** ({link("openclaw.ai", "https://openclaw.ai")}) is the '
        'best-known agent of this kind.',
        'Both are worth exploring, with care:', after=4)
    b.items([
        'They act on your behalf, so they ask for access to email and files. Use a separate account, not your '
        'own inbox.',
        'Don’t install add-ons from unknown sources. Researchers found hundreds of malicious ones in '
        'OpenClaw’s store.',
    ], 'dot', 'Agents care')

    b.h('Research and the pitch')
    b.items([
        tool('NotebookLM', 'https://notebooklm.google.com', 'notebooklm.google.com',
             'Put in your interview notes and ask questions across all of them.'),
        tool('Lean Canvas', 'https://miro.com/templates/lean-canvas/', 'miro.com/templates/lean-canvas',
             'Your business case on a single page.'),
        tool('Gamma', 'https://gamma.app', 'gamma.app', 'Quick first drafts of slides. Final slides go in our '
             'template.'),
    ], 'dot', 'Research')
    f.y = max(a.y, b.y)

    f.h('Worth reading')
    f.items([
        '**The Mom Test,** Rob Fitzpatrick. How to learn from customers when everyone is being polite.',
    ], 'dot', 'Reading')

    f.h('AI policy')
    f.p('You can build with any AI tool. Two conditions: you can explain every part of your product, and your '
        'final slides list which tools you used and what for.', after=4)
    f.p('Tools and free plans checked 22 October 2026.', size=8.5, color=SLATE, after=0)
    return f.y


def page_6(s):
    f = Flow(s, LM, MP.BANNER_NEXT + 22, W)
    f.h('Finishing well')
    f.items([
        '**Show your mentor something running at every check-in.** A rough version that runs tells them more '
        'than a plan does.',
        '**Record a two-minute video of your demo working on the third day.** If the live demo fails on the '
        'last day, play the video and keep presenting.',
        '**Free credits on any tool belong to the whole team.** Don’t use them up on the first night.',
        '**Write down what each tool would cost per month as you go.** The judges will ask.',
        '**The clocks go back one hour** on the night between the second and third day.',
    ], 'dot', 'Finishing well')

    f.h('Help and contact')
    label_table(f, [
        ('When you’re stuck', 'Ask your team first, then your mentor, then post in **#help** on Discord.'),
        ('Times and rooms', 'Your Participant Guide and **#announcements** on Discord.'),
        ('Email', f'[{MAIL}](mailto:{MAIL})'),
        ('Phone', '[+49 30 23125 000](tel:+493023125000)'),
    ], 'Contact')

    f.h('Words you’ll hear')
    label_table(f, [
        ('MVP', 'Minimum viable product: the smallest version that works and can be shown to a user.'),
        ('Prompt', 'The instructions your product sends to the AI model, together with the user’s input.'),
        ('Automation', 'A fixed chain of steps that runs by itself: a form comes in, the AI sorts it, a row '
                       'appears in a sheet.'),
        ('Agent', 'An AI that decides its own next steps and uses tools to finish a task.'),
        ('MCP', 'Model Context Protocol: a standard way to connect an AI model to other tools and data.'),
        ('Feature freeze', 'The point on the third day after which you only fix, and add nothing new.'),
    ], 'Words')

    f.y = BOTTOM - 40
    K.text(s, LM, f.y, W, 34, Para([Run('SMALL START. ', 30, True, INK, K.BC),
                                    Run('WORKING FINISH.', 30, True, BRAND, K.BC)], line=32), 'Closing line')
    f.y += 32
    return f.y


PAGES = [page_1, page_2, page_3, page_4, page_5, page_6]


def build():
    prs = K.new_deck()
    K.brand_links(prs)
    report = []
    for n, page in enumerate(PAGES, start=1):
        s = K.new_slide(prs)
        first = n == 1
        MX.banner(s, MP.BANNER_FIRST if first else MP.BANNER_NEXT, ('FIELD ', 'NOTES'),
                  '23–26 OCTOBER 2026  ·  EXAMPLE CAMPUS' if first else None)
        end = page(s)
        MX.footer(s, n, len(PAGES))
        report.append((n, end))
    path = OUT / f'{NAME}.pptx'
    prs.core_properties.title = 'AI Entrepreneurship Hackathon — Field Notes'
    prs.core_properties.author = 'Example College'
    prs.core_properties.subject = 'Finding a problem, shaping the idea, and the tools to build it'
    prs.save(path)
    return path, report


if __name__ == '__main__':
    path, report = build()
    print(path.name)
    for n, end in report:
        room = BOTTOM - end
        print(f'  page {n}: content ends at {end:5.0f} pt, {room:4.0f} pt to spare'
              + ('' if room >= 0 else '   <-- OVERFLOWS THE PAGE'))
