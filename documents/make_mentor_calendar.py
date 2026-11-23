#!/usr/bin/env python3
"""The mentors' sessions as ONE calendar file, attached to the mentor email.

    python documents/make_mentor_calendar.py

One block per session. A file instead of calendar invitations, so mentors get one email
rather than one per session. It is a plain calendar file (METHOD:PUBLISH).
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from make_calendar import esc, fold                                        # noqa: E402

OUT = HERE.parent / 'output' / 'documents' / 'Hackathon_Mentor_Sessions.ics'
VENUE = 'Example Campus, 1 Example Street, 10115 Berlin'
ZOOM = 'Online: Zoom (link in #announcements on Discord)'
TEAM = 'Online: your team’s Discord channel'
TAIL = ' Full plan: Hackathon_Mentor_Plan.pdf. Problems: #mentors on Discord.'

SESSIONS = [   # date, start, end, title, place, note
    ('20261023', '083000', '090000', 'Arrive at Example Campus', VENUE, 'Get your badge at the entrance.'),
    ('20261023', '090000', '100000', 'Kick-off', VENUE, 'Welcome and how the four days work.'),
    ('20261023', '100000', '103000', 'Teams revealed', VENUE, 'Meet your team.'),
    ('20261023', '103000', '120000', 'Brainstorm with your team', VENUE,
     'Help the team land on one idea that can be built in three days: cut it down and narrow it. Then: team '
     'name, product name and a 3–4 slide idea pitch.'),
    ('20261023', '120000', '130000', 'Lunch', VENUE, ''),
    ('20261023', '130000', '140000', 'Idea pitch', VENUE, 'Each team presents on stage, at most 6–7 minutes.'),
    ('20261023', '140000', '150000', 'Development plan', VENUE,
     'The most valuable hour: the user, the one feature that must work, the steps, who does what, and what must '
     'run by Saturday 12:30 and Sunday 12:30.'),
    ('20261023', '150000', '160000', 'Roles', VENUE,
     'Members pick roles that fit their skills. Everyone gets a real task.'),
    ('20261023', '160000', '170000', 'Building starts', VENUE, ''),
    ('20261023', '170000', '173000', 'End-of-day session with your team', VENUE, ''),
    ('20261024', '090000', '091500', 'Morning call', ZOOM, 'Then every team works in its Discord team channel.'),
    ('20261024', '123000', '130000', 'Checkpoint with your team', TEAM,
     '20–30 minutes: progress, blockers, and is the team working together?'),
    ('20261024', '170000', '173000', 'End-of-day session with your team', TEAM,
     'The team recaps the day. Get them excited for tomorrow and send them off to rest.'),
    ('20261025', '090000', '091500', 'Morning call', ZOOM, 'The clocks went back one hour last night.'),
    ('20261025', '123000', '130000', 'Checkpoint with your team', TEAM,
     'The MVP should run, the business side should match it, and the AI should be visible.'),
    ('20261025', '170000', '173000', 'End-of-day session: demo rehearsal', TEAM,
     'Full demo rehearsal. Feature freeze was at 16:00; teams hand in at 17:30.'),
    ('20261026', '140000', '160000', 'Presentations', VENUE, 'Please be there a little before 14:00.'),
    ('20261026', '160000', '163000', 'Awards', VENUE, ''),
    ('20261026', '163000', '173000', 'Networking', VENUE, 'End at 17:30.'),
]


def build():
    L = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Example College//AI Entrepreneurship Hackathon 2026 mentors//EN',
         'CALSCALE:GREGORIAN', 'METHOD:PUBLISH', 'X-WR-CALNAME:Hackathon mentor sessions',
         'X-WR-TIMEZONE:Europe/Berlin',
         'BEGIN:VTIMEZONE', 'TZID:Europe/Berlin',
         'BEGIN:DAYLIGHT', 'TZOFFSETFROM:+0100', 'TZOFFSETTO:+0200', 'TZNAME:CEST',
         'DTSTART:19700329T020000', 'RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU', 'END:DAYLIGHT',
         'BEGIN:STANDARD', 'TZOFFSETFROM:+0200', 'TZOFFSETTO:+0100', 'TZNAME:CET',
         'DTSTART:19701025T030000', 'RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU', 'END:STANDARD',
         'END:VTIMEZONE']
    for i, (day, start, end, title, place, note) in enumerate(SESSIONS, start=1):
        L += ['BEGIN:VEVENT',
              f'UID:hackathon-2026-mentor-{i:02d}@example.org',
              'DTSTAMP:20261019T000000Z',
              f'DTSTART;TZID=Europe/Berlin:{day}T{start}',
              f'DTEND;TZID=Europe/Berlin:{day}T{end}',
              'SUMMARY:' + esc('Hackathon: ' + title),
              'LOCATION:' + esc(place),
              'DESCRIPTION:' + esc((note + TAIL).strip()),
              'URL:https://example.org/hackathon',
              'STATUS:CONFIRMED', 'TRANSP:OPAQUE',
              'END:VEVENT']
    L.append('END:VCALENDAR')
    OUT.write_bytes(('\r\n'.join(fold(x) for x in L) + '\r\n').encode('utf-8'))
    return OUT


if __name__ == '__main__':
    print(build().name)
