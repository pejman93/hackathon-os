"""The mentor pack, as data.

Same block types and the same renderers as the participant pack (content.py); see
pack_spec.py. Edit the words here, then rebuild with --mentors.

**double asterisks** mark bold. Nothing else is markup.
"""
from content import DAYS as P_DAYS, MAILBOX, SITE


def when(day, words):
    """The clock time of the participant-pack item that mentions `words`."""
    hits = [t for t, text in P_DAYS[day]['items'] if words.lower() in text.lower()]
    assert len(hits) == 1, f'{words!r} matches {len(hits)} items on day {day + 1} of content.py'
    return hits[0]


FRI, SAT, SUN, MON = range(4)
T_START = P_DAYS[FRI]['items'][0][0]              # 09:00
T_TEAMS = when(FRI, 'Teams and mentors')          # 10:00
T_BRAINSTORM = when(FRI, 'Brainstorm')            # 10:30
T_PITCHES = when(FRI, 'Idea pitches')             # 11:30
T_LUNCH = when(FRI, 'Lunch')                      # 12:30
T_PLAN = when(FRI, 'Development plan')            # 13:30
T_SPLIT = when(FRI, 'split the roles')            # 15:00
T_BUILD = when(FRI, 'Start building')             # 16:30
T_FRI_END = P_DAYS[FRI]['items'][-1][0]           # 18:00
T_SAT_CALL = when(SAT, 'All-hands')               # 09:00
T_CHECK = when(SAT, 'Checkpoint')                 # 14:00
T_CLINIC = when(SAT, 'Scope clinic')              # 15:00
T_EOD = when(SAT, 'End-of-day')                   # 17:00
T_SAT_END = when(SAT, 'Soft end')                 # 18:00
T_SUN_CALL = when(SUN, 'All-hands')               # 09:00
T_FREEZE = when(SUN, 'Feature freeze')            # 16:00
T_REHEARSAL = when(SUN, 'Demo rehearsal')         # 16:30
T_HANDIN = when(SUN, 'Hand in')                   # 18:00
T_SUN_END = P_DAYS[SUN]['items'][-1][0]           # 18:30
T_FIXES = when(MON, 'Last fixes')                 # 09:30
T_MON_LUNCH = when(MON, 'Lunch')                  # 12:30
T_DEMOS = when(MON, 'Live demos')                 # 13:30
T_DECIDE = when(MON, 'judges decide')             # 15:30
T_AWARDS = when(MON, 'Awards')                    # 16:30
T_PHOTOS = when(MON, 'Photos')                    # 17:00

DAYS = [
    dict(
        label=P_DAYS[FRI]['label'], place='ON CAMPUS', hours=P_DAYS[FRI]['hours'],
        tagline='The day that decides everything.',
        items=[
            (T_START, 'Welcome, rules, a live example and short talks'),
            (T_TEAMS, '**You meet your team.** Teams and mentors are announced'),
            (T_BRAINSTORM, 'Brainstorm: help them pick a problem'),
            (T_PITCHES, 'Idea pitches'),
            (T_LUNCH, '**Lunch**'),
            (T_PLAN, '**Development plan** with your team'),
            (T_SPLIT, 'Plan the work and split the roles'),
            (T_BUILD, 'Your team starts building'),
            (T_FRI_END, 'End'),
        ],
        foot=('YOUR TIME', 'The full day, about 8 hours. This is the one that matters.'),
    ),
    dict(
        label=P_DAYS[SAT]['label'], place='ONLINE', hours=f'{T_CHECK} AND {T_EOD}',
        tagline='Does it run yet?',
        items=[
            (T_SAT_CALL, 'All-hands call for the teams. Then they build'),
            (T_CHECK, '**Checkpoint.** Your team shows you something that runs'),
            (T_CLINIC, 'Scope clinic: teams cut what does not fit'),
            (T_EOD, '**End-of-day session** with your team'),
            (T_SAT_END, 'Soft end'),
        ],
        foot=('YOUR TIME', 'About 1 hour: the checkpoint and the end-of-day session, '
                           'about half an hour each.'),
    ),
    dict(
        label=P_DAYS[SUN]['label'], place='ONLINE', hours=T_REHEARSAL,
        tagline='Freeze, rehearse, hand in.',
        items=[
            (T_SUN_CALL, 'All-hands call for the teams. Then they build'),
            (T_FREEZE, '**Feature freeze.** After this, only bug fixes and rehearsal'),
            (T_REHEARSAL, '**Demo rehearsal** with your team'),
            (T_HANDIN, 'Your team hands in its work'),
            (T_SUN_END, 'End'),
        ],
        foot=('YOUR TIME', 'About 1 hour, around the demo rehearsal.'),
    ),
    dict(
        label=P_DAYS[MON]['label'], place='ON CAMPUS', hours='OPTIONAL',
        tagline='Come and watch them present.',
        items=[
            (T_FIXES, 'Last fixes and rehearsal on the real screen'),
            (T_MON_LUNCH, 'Lunch'),
            (T_DEMOS, '**Live demos** to the judges'),
            (T_DECIDE, 'The judges decide'),
            (T_AWARDS, 'Awards'),
            (T_PHOTOS, 'Photos and networking'),
        ],
        foot=('YOUR TIME', f'Optional. If you can come for one part, come for the demos at {T_DEMOS}.'),
    ),
]

# A mentor and their team must never be told two different times.
for _mine, _theirs in zip(DAYS, P_DAYS):
    _known = {t for t, _ in _theirs['items']}
    _odd = [t for t, _ in _mine['items'] if t not in _known]
    assert not _odd, f"{_mine['label']}: {_odd} is not a time in the participant pack"

BLOCKS = [
    ('eyebrow', 'THANK YOU FOR MENTORING'),
    ('lead', 'Thank you for being a mentor at the AI Entrepreneurship Hackathon, the first '
             'hackathon at the Example College of Business and Technology. We are happy to have '
             'you with us.'),
    ('p', 'This pack tells you what we ask of you, when to be where, and what your team has to '
          'deliver. It takes about five minutes to read. If something is still unclear, write to '
          f'us at **{MAILBOX}**.'),
    ('p', '**The event in short:** in four days, small mixed teams build a working AI product '
          'that helps a business. It can be an app, an AI agent or an automation. On Monday they '
          'demo it live to judges from the industry. Along the way they work out who would use '
          'it and what it would cost. That is the entrepreneurship part: build the thing, then '
          'find out whether it helps anyone.'),

    ('glance', 'AT A GLANCE', [
        ('DATES', 'Friday 23 to Monday 26 October 2026'),
        ('YOUR TIME', f"**Friday:** the full day on campus, {P_DAYS[FRI]['hours']}.   "
                      f'**Saturday:** about one hour, online, at {T_CHECK} and {T_EOD}.   '
                      f'**Sunday:** about one hour, online, at {T_REHEARSAL}.   '
                      f'**Monday:** optional. Come and watch the demos at {T_DEMOS}.'),
        ('YOUR TEAM', f'One team, yours for the four days. You meet them on Friday at {T_TEAMS}.'),
        ('PLACE', 'Example Campus, 1 Example Street, 10115 Berlin'),
        ('GETTING THERE', 'Metro stop Harbour Street is about 10 minutes on foot, Central Station '
                          'about 15 minutes. Bus 100 stops about 2 minutes away.'),
        ('ON ARRIVAL', 'Go to the Example Campus reception and say you are here for the Example College hackathon. '
                       f'We meet you there. We start at {T_START}, so please come a little earlier.'),
        ('THE WEEKEND', 'Saturday and Sunday run on Discord. The campus stays open on both days, '
                        'with rooms, coffee and refreshments, if you would rather be there.'),
        ('FOOD AND DRINKS', f'Lunch on Friday at {T_LUNCH}. Coffee and refreshments on campus on '
                            'all four days.'),
        ('PHOTOS', 'We take photos on Friday and Monday. Tell us if you prefer not to be in them.'),
        ('REACH US', f'{MAILBOX}. During the event: the private mentor channel on Discord, or '
                     'Ada directly, on any day.'),
    ]),

    ('h', 'BEFORE FRIDAY'),
    ('checks', [
        f'**Put the sessions in your calendar:** Friday all day, Saturday at {T_CHECK} and {T_EOD}, '
        f'Sunday at {T_REHEARSAL}.',
        '**Join our Discord server.** We send you the invite by email. There is a private channel for mentors.',
        '**Read what your team has to deliver and how the judges score.** Your team will ask you.',
        '**Tell us now** if you cannot make one of the sessions, or if you have dietary or access needs.',
        '**Nothing else to prepare.** Your experience is the preparation.',
    ]),

    ('pagebreak',),

    ('h', 'THE FOUR DAYS: YOUR PART'),
    ('p', 'Friday and Monday are at Example Campus. On Saturday and Sunday the sessions are online, '
          'and the campus is open if you would rather be there. All times are Berlin time.'),
    ('days', DAYS),
    ('small', 'Times can shift a little on the day. If they do, we tell you on Discord.'),

    ('h', 'YOUR ROLE'),
    ('p', 'You have one team for the four days. **Your job is to keep that team moving:** help '
          'them shape a plan they can finish, unblock them when they are stuck, and be the person '
          'who has done this before.'),
    ('quote', 'The question to keep asking: what is the smallest version of that which still works?'),

    ('pagebreak',),

    ('h', 'FRIDAY DECIDES EVERYTHING'),
    ('p', 'Two things happen on Friday, and both need you.'),
    ('p', '**The idea, in the morning.** Teams reach for something huge. Your job is to get them '
          'to something they can finish in two and a half days. Do not pick the idea for them. '
          'Keep asking for the smallest version that still works, until it is real. A team that '
          'leaves Friday with the right size of idea will finish. A team that does not, will not.'),
    ('p', '**The development plan, in the afternoon.** This is where you are most concrete. Help '
          'them shape the product: what the structure is, what gets built first and what waits. '
          'Which parts can run in parallel, so the whole team is not waiting behind one person. '
          'What to hardcode now and make real later. If they are choosing tools or setting up a '
          'repository and it is going badly, step in. This is not the moment to stand back.'),

    ('h', 'THE WEEKEND'),
    ('p', 'You meet your team online at fixed times. Each session is about half an hour.'),
    ('bullets', [
        f'**Saturday {T_CHECK}, the checkpoint.** They show you something that runs, however '
        'rough. If it does not run, cut features with them until what is left fits the time left.',
        f'**Saturday {T_EOD}, the end-of-day session.** What got done, what is blocked, and what '
        'everyone does tomorrow.',
        f'**Sunday {T_REHEARSAL}, the demo rehearsal.** The feature freeze is at {T_FREEZE}. They '
        'run the demo for you once, from start to finish. Help them show it working first and '
        'explain second, and keep it inside the time.',
    ]),

    ('h', 'MAKE SURE NOBODY DRIFTS'),
    ('p', 'Every session has a second job, and it matters just as much. In a mixed team, people '
          'drift quietly. The shy ones stop asking. The ones who do not code assume there is '
          'nothing for them. By Sunday, two people have contributed nothing and feel bad about it.'),
    ('p', '**Go round the team by name.** If someone has no task, fix that before anything '
          'technical. Teamwork is half of what this event teaches, and it does not happen on its own.'),

    ('h', 'WHAT YOU ARE NOT THERE TO DO'),
    ('p', '**Build the product for them.** It stays theirs, and they must be able to explain every '
          'part of it to the judges on Monday. Show them how, point them to the right tool, fix a '
          'blocker with them. Then hand it back.'),

    ('h', 'YOUR INSIGHT IS THE POINT'),
    ('p', 'You are not there to be neutral. If you have built a product, sold one or watched one '
          'fail, that is exactly what your team needs, and they will not get it anywhere else that '
          'weekend. Say the blunt thing early.'),
    ('p', 'You also have a direct line to us throughout. Ask for anything, flag anything, and tell '
          'us when something is not working. There is a private mentor channel on Discord, and you '
          'can reach Ada directly on any day of the event.'),

    ('pagebreak',),

    ('h', 'WHAT YOUR TEAM HAS TO DELIVER'),
    ('p', 'There are two rules: the product runs live on Monday, and the team can say who would '
          'pay for it and roughly what it costs to run. In detail:'),
    ('bullets', [
        '**A working product.** It runs live in front of the judges. Someone who did not build it can use it.',
        '**Live AI calls.** The product must call the OpenAI API for real. Hardcoded or faked AI output does not count.',
        '**A named user.** One specific person or role, with one specific problem.',
        '**A price.** What they would charge, and roughly what it costs to run per month.',
        '**A repository link and a final presentation**, using our template.',
        '**No real personal data.** Synthetic or public data only.',
    ]),
    ('p', f'**Hand-in is on Sunday at {T_HANDIN}:** the repository link, a summary slide and the '
          'demo plan. Teams also record a two-minute backup video on Sunday, in case the live demo breaks.'),

    ('h', 'HOW THE JUDGES SCORE'),
    ('p', f'On Monday at {T_DEMOS}, every team presents live to a panel of judges from the '
          'industry: **eight minutes to demo, then four minutes of questions**. '
          'The judges score five things, each from 1 to 5:'),
    ('judging', [
        ('30%', '**It runs live.** In the room, and someone who did not build it can use it.'),
        ('20%', '**A real user.** One real person or role with one real problem, and the product helps with it.'),
        ('20%', '**The business case.** One customer, one price, one reason to switch.'),
        ('15%', '**It can keep running.** What it costs per month, and what it depends on.'),
        ('15%', '**The demo.** Shows before it explains, is honest about limits, and stays inside the time.'),
    ]),
    ('p', 'The business case carries real weight. A polished demo with no customer should not '
          'beat a plainer product that someone would pay for. A business mentor also works with '
          'every team on the customer and the price. **You do not judge:** the judges are a '
          'separate panel, and a mentor never judges their own team.'),

    ('h', 'AI POLICY AND TOOLS'),
    ('pairs', [
        ('AI POLICY', 'AI tools are allowed and encouraged for building. Two conditions: the team '
                      'can explain every part of its system, and it says which tools it used and for what.'),
        ('WE PROVIDE', 'Discord, Zoom for the daily calls, slide templates, a shared Drive folder, '
                       'and one OpenAI API key per team with a spending cap.'),
        ('TEAMS OFTEN USE', 'The openai Python SDK. Streamlit or Gradio, or a no-code builder such '
                            'as Lovable, v0 or Bolt. GitHub for the repository.'),
    ]),

    ('pagebreak',),

    ('h', 'QUESTIONS MENTORS ASK'),
    ('faq', [
        ('How much time does it take?',
         'Friday is the full day on campus. Saturday and Sunday are about one hour each, online. '
         'Monday is optional.'),
        ('Do I need to prepare anything?',
         'No. Read this pack and join Discord. That is all.'),
        ('I am a technical mentor. What about the business side?',
         'A business mentor works with every team on the customer and the price. Still, keep '
         'asking your team who would pay for this. It keeps the product small and real.'),
        ('How much should I help with the code?',
         'Unblock, explain and show. Do not build it for them. If a setup problem is eating their '
         'Friday, step in and fix it with them.'),
        ('Someone in my team is not taking part. What do I do?',
         'Talk to them first, by name, and find them a real task. If it does not get better, tell '
         'us in the mentor channel. Do not wait until Sunday.'),
        ('What if I cannot make a session?',
         'Tell us as early as you can, so we can cover it. Your team plans around these sessions.'),
        ('Can I come to campus at the weekend?',
         'Yes. The campus is open on both days, with rooms, coffee and refreshments. The sessions '
         'themselves run online.'),
        ('Do I judge my team?',
         'No. The judges are a separate panel, and a mentor never judges their own team.'),
    ]),

    ('h', 'WHAT YOU GET OUT OF IT'),
    ('bullets', [
        'Four days close to people building AI products, from Example College and the wider Berlin community.',
        'Your name on the event materials.',
        'An open door to keep working with your team afterwards, if you want to.',
    ]),

    ('h', 'WHERE WE MEET'),
    ('photos', ['campus', 'workspace', 'team', 'stage'],
     'Example Campus, 1 Example Street: the building, one of our shared work floors, a team room '
     'and the staircase. The campus is home to startups, companies and the #ai_berlin hub, and '
     'it is where Example College is based.'),

    ('closing', dict(
        eyebrow='SEE YOU ON FRIDAY',
        title='THANK YOU FOR DOING THIS.',
        text=f'Questions before then? Write to us at {MAILBOX}. During the event, use the mentor '
             'channel on Discord.',
        name='Ada Lovelace',
        role='Hackathon Lead',
        lines=[MAILBOX, SITE],
    )),
]
