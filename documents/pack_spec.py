"""Which pack is being built.

Two packs share one set of renderers: the participant pack (content.py) and the mentor
pack (content_mentors.py). Everything that differs between them, apart from the words
themselves, is in this file.

    python documents/make_pack.py              the participant pack (the default)
    python documents/make_pack.py --mentors    the mentor pack
    python documents/make_pptx.py --mentors    its PowerPoint file
"""
import importlib
import sys

PACKS = {
    'participants': dict(
        module='content',
        name='Hackathon_Participant_Pack',
        banner=('PARTICIPANT ', 'PACK'),
        title='AI Entrepreneurship Hackathon — Participant Pack',
        subject='What happens on each day, what you build and what to bring',
        keywords='hackathon, participants, Example College, Example Campus',
        cache='',                 # suffix for this pack's cached banner files
    ),
    'mentors': dict(
        module='content_mentors',
        name='Hackathon_Mentor_Pack',
        banner=('MENTOR ', 'PACK'),
        title='AI Entrepreneurship Hackathon — Mentor Pack',
        subject='Your role, your time and what your team has to deliver',
        keywords='hackathon, mentors, Example College, Example Campus',
        cache='-mentors',
    ),
}

KEY = 'mentors' if '--mentors' in sys.argv else 'participants'
SPEC = PACKS[KEY]

_content = importlib.import_module(SPEC['module'])
BLOCKS, MAILBOX, SITE = _content.BLOCKS, _content.MAILBOX, _content.SITE


def day_foot(day):
    """The last line of a day card: (LABEL, text). Participants see FOOD;
    a pack can put something else there with day['foot']."""
    return day.get('foot') or ('FOOD', day['food'])
