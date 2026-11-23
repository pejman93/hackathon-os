#!/usr/bin/env python3
"""The Staff Plan: two pages attached to the email to the staff team.

    python documents/make_staff.py

Same look and layout code as the Participant Guide.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pptx_kit as K                                                       # noqa: E402
from pptx_kit import BRAND, Run                                            # noqa: E402
import make_pack as MP                                                     # noqa: E402
import make_pptx as MX                                                     # noqa: E402
from make_guide import BOTTOM, LM, SIZE, W, Flow, columns                  # noqa: E402

OUT = HERE.parent / 'output' / 'documents'
NAME = 'Hackathon_Staff_Plan'
TIME_W = round(Run('08:30–09:00', 9.0, True, BRAND).width('08:30–09:00')) + 10


def day(f, title, note, rows):
    f.h2(title, note)
    f.table([TIME_W, f.w - TIME_W], rows, title, first='time', size=9.1)


# ======================================================================= pages
def page_1(s):
    f = Flow(s, LM, MP.BANNER_FIRST + 24, W)
    f.lead('This is the staff plan for the hackathon, Wednesday 21 to Monday 26 October. '
           '**Please read all of it.** The times are fixed: be in your place when each slot starts.')

    f.h('Who’s who')
    f.table([112, W - 112], [
        ('Staff lead', '**Hedy Lamarr.** He runs the staff team and decides who stands where. If '
                       'something changes or someone is missing, he reassigns the roles.'),
        ('Staff team', 'Hedy, Joan, Annie, Mary'),
        ('Photo and video', 'George (marketing)'),
        ('Hackathon lead', '**Ada Lovelace.** For anything the staff lead can’t solve.'),
        ('Where', 'Example Campus, 1 Example Street, 10115 Berlin. Lobby and reception area, Garden room '
                  '(lunch, 1st floor), hackathon room (2nd floor).'),
        ('Report', '**Discord, channel #staff.** Post there straight away.'),
    ], 'Who is who', outer=True, first='label', size=SIZE)

    f.h('Rules')
    f.items([
        '**Be on time.** If you will be late or can’t come, tell Hedy and post in #staff before your '
        'slot starts.',
        '**Report everything in #staff, straight away:** anything broken, any danger, any change, and every '
        'case that needs escalating. Don’t wait until later.',
        '**Hedy decides.** If something comes up that isn’t in this plan, he says who does it.',
        '**Don’t interfere with the teams’ work.** Stay close, and help when they ask.',
        '**Keep the hackathon strictly separate from the new student intake.** Only hackathon people go into '
        'the hackathon rooms and the food room. **Emmy:** please tell the academic team, and Tony, that '
        'nobody from the intake should interfere with the hackathon.',
        '**Sunday 25 October: the clocks go back one hour** during the night. 08:00 on Sunday is the new time. '
        'Your phone changes by itself.',
    ], 'num', 'Rules')

    f.h('Before the hackathon')
    day(f, 'Wednesday 21 October', 'All day  ·  Example College office', [
        ('All day', 'Prepare the name badges, lanyards, room labels, door signs and certificates. Put everything '
                    'in the Example College office.'),
        ('All day', 'Call the participants and make sure they are coming on Friday.'),
    ])
    f.p('Everything must be done by the end of Wednesday.', after=0)
    day(f, 'Thursday 22 October', 'Example Campus', [
        ('14:00–16:00', 'Prepare the rooms. Test the screens.'),
        ('16:00–17:00', 'Check that the food and drinks are in their correct place.'),
        ('20:00–20:30', 'Arrange the chairs in the lobby and reception area.'),
    ])
    return f.y


def page_2(s):
    f = Flow(s, LM, MP.BANNER_NEXT + 24, W)
    f.h('Friday 23 October')
    f.table([TIME_W, W - TIME_W], [
        ('07:00–07:30', '**Tech check:** mic, display, speakers.'),
        ('07:30–08:00', '**Final check:** lanyards, badges, participant list.'),
        ('08:00–08:30', '**Final check** of the rooms and signs.'),
        ('08:30–09:00', '**Welcome the participants and mentors.** Hand out badges, bags and lanyards, and guide '
                        'everyone to the lobby and the chairs. **Entrance:** Hedy and Joan. '
                        '**Inside:** Annie and Mary.'),
        ('09:00–10:30', 'One at the **entrance** for latecomers. One keeps checking the **food room and the '
                        'hackathon room**. Two in the **lobby**: one looks after the panel, one looks after the '
                        'people. Hedy decides who is where.'),
        ('10:30–11:00', '**Move to the hackathon room (2nd floor).** Hedy and Joan guide the teams, mentors '
                        'and participants. Annie stands at the hackathon room door and shows each team to its '
                        'place. Joan checks for anyone left behind and goes back to the lobby until everyone '
                        'is up.'),
        ('11:00–12:00', '**Prepare lunch.** One staff member waits outside the hackathon room in case a team '
                        'needs something.'),
        ('12:00–12:15', '**Guide the teams to lunch,** from the hackathon room (2nd floor) to the Garden room '
                        '(1st floor).'),
        ('12:15–12:45', '**Two staff:** stop anyone who isn’t part of the hackathon from entering the food room. '
                        '**One staff:** check the chairs, mic and display in the lobby.'),
        ('12:45–13:00', '**Guide everyone to the lobby:** one in the lobby, one in the lunch rooms and cafeteria, '
                        'one in the hackathon rooms.'),
        ('13:00–13:45', '**Idea pitch.** Annie waits at the 2nd-floor door. Two staff in the lobby, ready in '
                        'case something is needed or goes wrong.'),
        ('13:45–14:15', '**Guide the teams** back to the hackathon room (2nd floor).'),
        ('14:15–17:00', '**All staff on site.** Hedy stays close by but doesn’t interfere with the teams.'),
        ('17:00–18:00', '**Guide the participants and teams out.**'),
    ], 'Friday', first='time', size=9.1)

    a, b = columns(s, f.y + 4)
    a.h2('Saturday 24 and Sunday 25 October', gap=0)
    a.p('Same plan both days.', after=2)
    a.table([TIME_W, a.w - TIME_W], [
        ('08:00', '**Staff check-in.**'),
        ('08:30–09:00', 'Check the snacks, signs and drinks.'),
        ('09:00–10:00', 'Guide the participants to the hackathon room, or book empty rooms if needed.'),
        ('12:00–13:00', 'Check the snacks and drinks.'),
        ('17:30–18:30', 'Guide everyone out.'),
    ], 'Weekend', first='time', size=9.1)
    a.p('**Sunday: the clocks go back one hour** during the night. 08:00 is the new time.', after=0)

    b.h2('Monday 26 October', 'Final day', gap=0)
    b.table([TIME_W, b.w - TIME_W], [
        ('08:00–10:00', 'Check in. Guide the participants who come early to the hackathon room.'),
        ('13:00–14:00', '**Welcome the participants at the entrance.** Check badges, lanyards and the '
                        'attendance list, and guide them to the final in the lobby.'),
        ('14:00–15:00', 'One stays at the **entrance** for latecomers. Everyone else in the **lobby**: one at '
                        'the stage, one helps with seating and drinks.'),
        ('15:00–16:00', '**Networking and awards.** Everyone ready in case something breaks or a technical '
                        'error happens.'),
        ('16:00–17:00', 'Networking and photos.'),
        ('17:00–18:00', 'Guide people out.'),
    ], 'Monday', first='time', size=9.1)

    return max(a.y, b.y)


PAGES = [page_1, page_2]


def build():
    prs = K.new_deck()
    K.brand_links(prs)
    report = []
    for n, page in enumerate(PAGES, start=1):
        s = K.new_slide(prs)
        first = n == 1
        MX.banner(s, MP.BANNER_FIRST if first else MP.BANNER_NEXT, ('STAFF ', 'PLAN'),
                  '21–26 OCTOBER 2026  ·  EXAMPLE CAMPUS' if first else None)
        end = page(s)
        MX.footer(s, n, len(PAGES))
        report.append((n, end))
    path = OUT / f'{NAME}.pptx'
    prs.core_properties.title = 'AI Entrepreneurship Hackathon — Staff Plan'
    prs.core_properties.author = 'Example College'
    prs.core_properties.subject = 'Who is where, at what time, and who to tell'
    prs.save(path)
    return path, report


if __name__ == '__main__':
    path, report = build()
    print(path.name)
    for n, end in report:
        room = BOTTOM - end
        print(f'  page {n}: content ends at {end:5.0f} pt, {room:4.0f} pt to spare'
              + ('' if room >= 0 else '   <-- OVERFLOWS THE PAGE'))
