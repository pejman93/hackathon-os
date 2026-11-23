"""The participant pack, as data.

One source for both outputs: make_pack.py renders this list twice, once as the designed
PDF and once as the editable Word file, so the two can never say different things.
Edit the words here, then rebuild.

**double asterisks** mark bold. Nothing else is markup.
"""

MAILBOX = 'hackathon@example.org'
SITE = 'example.org/hackathon'

DAYS = [
    dict(
        label='FRIDAY 23 OCTOBER', place='ON CAMPUS', hours='09:00 – 18:00',
        tagline='Find your team. Pick your problem.',
        items=[
            ('09:00', 'Welcome and rules'),
            ('09:20', 'A live example of the kind of product we mean'),
            ('09:40', 'Short talks from Example College and industry'),
            ('10:00', 'Teams and mentors announced'),
            ('10:30', 'Brainstorm: pick a problem'),
            ('11:30', 'Idea pitches'),
            ('12:30', '**Lunch**'),
            ('13:30', 'Development plan with your mentor'),
            ('15:00', 'Plan the work and split the roles'),
            ('16:30', 'Start building'),
            ('18:00', 'End'),
        ],
        food='Lunch at 12:30. Coffee and refreshments all day.',
    ),
    dict(
        label='SATURDAY 24 OCTOBER', place='HYBRID', hours='09:00 – 18:00',
        tagline='Try. Build. Ask for help.',
        items=[
            ('09:00', 'All-hands call, 15 minutes'),
            ('09:15', 'Build'),
            ('14:00', '**Checkpoint** with your mentor: every team shows something that runs'),
            ('15:00', 'Scope clinic: cut what does not fit'),
            ('17:00', 'End-of-day session with your mentor'),
            ('18:00', 'Soft end'),
        ],
        food='Coffee and refreshments on campus. Lunch is on your own.',
    ),
    dict(
        label='SUNDAY 25 OCTOBER', place='HYBRID', hours='09:00 – 18:30',
        tagline='Make it work. Make it make sense.',
        items=[
            ('09:00', 'All-hands call'),
            ('09:15', 'Build'),
            ('16:00', '**Feature freeze.** After this, only bug fixes and rehearsal'),
            ('16:30', 'Demo rehearsal with your mentor'),
            ('18:00', '**Hand in** your repository link, summary slide and demo plan'),
            ('18:30', 'End'),
        ],
        food='Coffee and refreshments on campus. Lunch is on your own.',
    ),
    dict(
        label='MONDAY 26 OCTOBER', place='ON CAMPUS', hours='09:00 – 17:00',
        tagline='Show what you made.',
        items=[
            ('09:00', 'All-hands'),
            ('09:30', 'Last fixes and rehearsal on the real screen'),
            ('12:30', '**Lunch**'),
            ('13:30', '**Live demos**'),
            ('15:30', 'The judges decide'),
            ('16:30', 'Awards'),
            ('17:00', 'Photos and networking'),
        ],
        food='Lunch at 12:30. Coffee and refreshments all day.',
    ),
]

BLOCKS = [
    ('eyebrow', 'WELCOME'),
    ('lead', 'Welcome to the AI Entrepreneurship Hackathon, the first hackathon at the '
             'Example College of Business and Technology. We are happy to have you with us.'),
    ('p', 'This pack tells you when to be where, what you build, what we provide and what '
          'we expect from you. Please read it before Friday. If something is still unclear, '
          f'write to us at **{MAILBOX}**.'),

    # Everything practical in one box on page 1: when, where, food, cost.
    # That is what people look for first, and what they come back to check.
    ('glance', 'AT A GLANCE', [
        ('DATES', 'Friday 23 to Monday 26 October 2026'),
        ('TIMES', '**Fri** 09:00 – 18:00   ·   **Sat** 09:00 – 18:00   ·   '
                  '**Sun** 09:00 – 18:30   ·   **Mon** 09:00 – 17:00'),
        ('PLACE', 'Example Campus, 1 Example Street, 10115 Berlin'),
        ('GETTING THERE', 'Metro stop Harbour Street is about 10 minutes on foot, Central Station '
                          'about 15 minutes. Bus 100 stops about 2 minutes away.'),
        ('ON ARRIVAL', 'Go to the Example Campus reception and say you are here for the Example College hackathon. '
                       'We meet you there. We start at 09:00, so please come a little earlier.'),
        ('FORMAT', 'Friday and Monday on campus. Saturday and Sunday are hybrid: '
                   'work from the campus or join online.'),
        ('FOOD AND DRINKS', '**Lunch is provided on Friday and Monday at 12:30.** Coffee and '
                            'refreshments are on campus on all four days. On Saturday and Sunday, '
                            'lunch is on your own.'),
        ('COST', 'Taking part is free. Your team gets an OpenAI API key from us, so you do not '
                 'pay for the AI either.'),
        ('BRING', 'Your laptop and charger. Headphones help for the online calls.'),
        ('PHOTOS', 'We take photos on Friday and Monday. If you would rather not be in them, '
                   'tell us on the day.'),
        ('QUESTIONS', f'{MAILBOX}. During the event, Discord is the fastest way to reach us '
                      'and your mentor.'),
    ]),

    ('h', 'BEFORE FRIDAY'),
    ('checks', [
        '**Put the four days in your calendar**, with the times above.',
        '**Join our Discord server.** We send you the invite by email. Discord is where the weekend happens.',
        '**Create a free GitHub account** if you do not have one. Your team hands in a repository link.',
        '**Check your laptop** and pack the charger.',
        '**Tell us now** if you cannot be there for part of a day, or if you have dietary or access needs.',
        '**Optional:** think about a problem you would like to solve. You do not need an idea. If you have one, bring it.',
    ]),

    ('pagebreak',),

    ('h', 'THE FOUR DAYS'),
    ('p', 'Friday and Monday are at Example Campus. Saturday and Sunday are hybrid: work from the '
          'campus or join online. All times are Berlin time.'),
    ('days', DAYS),
    ('small', 'Times can shift a little on the day. If they do, we tell you on Discord.'),

    ('h', 'THE HYBRID WEEKEND'),
    ('p', 'On Saturday and Sunday you choose where you work. The all-hands calls and the mentor '
          'sessions are online, so you can join from anywhere. We use Discord for the teamwork '
          'and Zoom for the all-hands calls.'),
    ('p', 'The campus stays open on both days for anyone who would rather work there. Rooms are '
          'reserved, and there are coffee and refreshments.'),

    ('pagebreak',),

    ('h', 'WHAT YOU BUILD'),
    ('p', 'In four days, you work in a small team to build a working AI product that helps a '
          'business. It can be an app, an AI agent or an automation. Your team decides.'),
    ('p', 'Most AI hackathons ask one question: does it work? We ask two. **Does it work, and '
          'would anyone pay for it?** So there are two rules: it runs live on Monday, and you can '
          'say who would pay for it and roughly what it costs to run.'),
    ('quote', 'A simple thing that works beats a clever thing that does not.'),
    ('p', 'It is not an exam and it is not assessed. The most valuable thing you can do is support '
          'your team and make sure everyone has something real to work on.'),

    ('h', 'YOUR TEAM AND YOUR MENTOR'),
    ('p', 'We put the teams together, so you do not need to find one. Teams are small and mixed on '
          'purpose: people who build, people who work out the customer and the price, and people '
          'who design and present. You meet your team on Friday at 10:00.'),
    ('p', '**Each team has its own mentor for the whole event.** Your mentor helps when you are '
          'stuck, helps you cut the idea down when it grows too big, and keeps asking who would pay '
          'for this. At the weekend you meet your mentor at the checkpoint and at the end of the '
          'day. A business mentor also works with every team on the business case.'),
    ('p', 'Your mentor does not build the product for you. It stays yours, and you must be able to '
          f'explain every part of it. You can see the mentors and judges at {SITE}.'),

    ('h', 'WHAT YOUR PRODUCT NEEDS'),
    ('bullets', [
        '**A working product.** It runs live in front of the judges. Someone who did not build it can use it.',
        '**Live AI calls.** Your product must call the OpenAI API for real. Hardcoded or faked output does not count.',
        '**A named user.** One specific person or role, with one specific problem.',
        '**A price.** What you would charge, and roughly what it costs you to run per month.',
        '**A repository link and a final presentation**, using our template.',
        '**No real personal data.** Use synthetic or public data only.',
    ]),
    ('p', '**Hand-in is on Sunday at 18:00:** your repository link, a summary slide and your demo '
          'plan. Also record a two-minute backup video of your demo on Sunday, in case the live one breaks.'),

    ('pagebreak',),

    ('h', 'AI POLICY'),
    ('p', 'AI tools are allowed and encouraged for building. This is an AI hackathon. There are two '
          'conditions: you must be able to explain every part of your system when the judges ask, '
          'and you must say which tools you used and for what.'),

    ('h', 'DEMO DAY AND JUDGING'),
    ('p', 'On Monday at 13:30, every team presents its product live to a panel of judges from the '
          'industry. You have **eight minutes to demo, then four minutes of questions**. '
          'Show it working first, then explain.'),
    ('p', 'The judges score five things, each from 1 to 5:'),
    ('judging', [
        ('30%', '**It runs live.** In the room, and someone who did not build it can use it.'),
        ('20%', '**A real user.** One real person or role with one real problem, and your product helps with it.'),
        ('20%', '**The business case.** One customer, one price, one reason to switch.'),
        ('15%', '**It can keep running.** What it costs per month, and what it depends on.'),
        ('15%', '**The demo.** Shows before it explains, is honest about limits, and stays inside the time.'),
    ]),
    ('p', 'This is an entrepreneurship hackathon, so the business case carries real weight. A '
          'polished demo with no customer should not beat a plainer product that someone would pay '
          'for. The judges score on their own first and compare afterwards, and a mentor never '
          'judges their own team. The awards are at 16:30.'),

    ('h', 'TOOLS AND WHAT WE PROVIDE'),
    ('pairs', [
        ('WE PROVIDE', 'Discord, Zoom for the daily calls, slide templates, a shared Drive folder, '
                       'and one OpenAI API key per team with a spending cap.'),
        ('THE AI', 'The openai Python SDK. Documentation: platform.openai.com/docs/api-reference'),
        ('TO MAKE IT DEMOABLE', 'Streamlit or Gradio, or a no-code builder such as Lovable, v0 or Bolt.'),
        ('CODE AND PLANNING', 'GitHub for the repository. draw.io or Figma for the workflow and the interface.'),
    ]),
    ('small', 'Use what your team already knows. We share the templates and the Drive folder before the event.'),

    ('pagebreak',),

    ('h', 'QUESTIONS PEOPLE ASK'),
    ('faq', [
        ('I cannot code. Is there something for me to do?',
         'Yes. Every team needs people who work out who the customer is, what they would pay and '
         'how to explain it. More than half of the score is about the user, the business case and the demo.'),
        ('I do not have an idea.',
         'You do not need one. Teams choose their problem together on Friday morning. If you have '
         'an idea, bring it and pitch it to your team.'),
        ('I have never been to a hackathon.',
         'That is fine. All skill levels are welcome, and your mentor is there to help. Whether you '
         'are ahead or a little behind, there is always a part of this you can take on.'),
        ('Can I choose my team?',
         'No. We put the teams together so that each one has a mix of skills. You may not be with '
         'people you know, and that is part of the experience.'),
        ('Do I have to come to campus at the weekend?',
         'No. Saturday and Sunday are hybrid. Join online or work from the campus, whichever suits '
         'you. Friday and Monday are in person.'),
        ('What if I cannot be there for part of a day?',
         'Tell us before Friday. Your team plans its work around the people in it, so the earlier '
         'we know, the better.'),
        ('Does it cost anything?',
         'No. Taking part is free. Your team also gets an OpenAI API key from us, so you do not pay for the AI.'),
        ('Is it graded?',
         'No. It is not an exam and it is not assessed.'),
        ('Can I use ChatGPT, Copilot or other AI tools to build?',
         'Yes. You just have to be able to explain what you built and say which tools you used.'),
        ('What if our demo breaks?',
         'It happens. That is why you record a two-minute backup video on Sunday.'),
    ]),

    ('h', 'WHERE WE MEET'),
    ('photos', ['campus', 'workspace', 'team', 'stage'],
     'Example Campus, 1 Example Street: the building, one of our shared work floors, a team room '
     'and the staircase. The campus is home to startups, companies and the #ai_berlin hub, and '
     'it is where Example College is based.'),

    ('closing', dict(
        eyebrow='SEE YOU ON FRIDAY',
        title='QUESTIONS BEFORE THEN?',
        text=f'Write to us at {MAILBOX}. During the event, ask your mentor first, then us on Discord.',
        name='Ada Lovelace',
        role='Hackathon Lead',
        lines=[MAILBOX, SITE],
    )),
]
