#!/usr/bin/env python3
"""The four hackathon days as ONE calendar file, to attach to the selection email.

    python documents/make_calendar.py

Opening the file offers "add to calendar" in Google Calendar, Apple Calendar and Outlook.
It is a plain calendar file (METHOD:PUBLISH), not an invitation: nobody is asked to accept,
and no reply is sent to anyone. Times are Berlin local time with the time-zone rules
included, because the clocks go back during the event.
"""
import pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / 'output' / 'documents' / 'Hackathon_2026.ics'
VENUE = 'Example Campus, 1 Example Street, 10115 Berlin'
TAIL = ' Questions: hackathon@example.org'

EVENTS = [   # date, start, end, title, place, note
    ('20261023', '083000', '173000', 'AI Entrepreneurship Hackathon: Day 1 (at Example Campus)', VENUE,
     'Be at the Example Campus reception at 08:30. Our team will be waiting for you. We start at 09:00 sharp and '
     'finish at 17:30. Bring your laptop and charger.'),
    ('20261024', '090000', '173000', 'AI Entrepreneurship Hackathon: Day 2 (campus or home)',
     'Example Campus, or from home on Discord',
     '09:00 morning call on Zoom (the link is in #announcements on Discord). Then you build with your team, '
     'on campus or from home. 12:30 check-in with your mentor. 17:00 end-of-day session.'),
    ('20261025', '090000', '173000', 'AI Entrepreneurship Hackathon: Day 3 (campus or home)',
     'Example Campus, or from home on Discord',
     '09:00 morning call on Zoom. 16:00 feature freeze. 17:30 hand in your GitHub link and final slides. '
     'The clocks went back one hour last night.'),
    ('20261026', '140000', '170000', 'AI Entrepreneurship Hackathon: Demo day (at Example Campus)', VENUE,
     'Be at the Example Campus reception shortly before 14:00. Live demos at 14:00, awards at 15:30. '
     'The morning is free for last fixes.'),
]


def esc(text):
    return text.replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,').replace('\n', '\\n')


def fold(line):
    """Lines may be at most 75 bytes; longer ones continue on the next line after a space."""
    out, cur = [], ''
    for ch in line:
        if len((cur + ch).encode('utf-8')) > (75 if not out else 74):
            out.append(cur)
            cur = ch
        else:
            cur += ch
    out.append(cur)
    return '\r\n '.join(out)


def build():
    L = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Example College//AI Entrepreneurship Hackathon 2026//EN',
         'CALSCALE:GREGORIAN', 'METHOD:PUBLISH', 'X-WR-CALNAME:AI Entrepreneurship Hackathon',
         'X-WR-TIMEZONE:Europe/Berlin',
         'BEGIN:VTIMEZONE', 'TZID:Europe/Berlin',
         'BEGIN:DAYLIGHT', 'TZOFFSETFROM:+0100', 'TZOFFSETTO:+0200', 'TZNAME:CEST',
         'DTSTART:19700329T020000', 'RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU', 'END:DAYLIGHT',
         'BEGIN:STANDARD', 'TZOFFSETFROM:+0200', 'TZOFFSETTO:+0100', 'TZNAME:CET',
         'DTSTART:19701025T030000', 'RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU', 'END:STANDARD',
         'END:VTIMEZONE']
    for i, (day, start, end, title, place, note) in enumerate(EVENTS, start=1):
        L += ['BEGIN:VEVENT',
              f'UID:hackathon-2026-day{i}@example.org',
              'DTSTAMP:20261014T000000Z',
              f'DTSTART;TZID=Europe/Berlin:{day}T{start}',
              f'DTEND;TZID=Europe/Berlin:{day}T{end}',
              'SUMMARY:' + esc(title),
              'LOCATION:' + esc(place),
              'DESCRIPTION:' + esc(note + TAIL),
              'URL:https://example.org/hackathon',
              'STATUS:CONFIRMED', 'TRANSP:OPAQUE',
              'END:VEVENT']
    L.append('END:VCALENDAR')
    OUT.write_bytes(('\r\n'.join(fold(x) for x in L) + '\r\n').encode('utf-8'))
    return OUT


if __name__ == '__main__':
    print(build().name)
