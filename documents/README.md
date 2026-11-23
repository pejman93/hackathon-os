# Documents

Every guide, plan, slide deck and calendar file for the event, generated from code so that a change
in one place reaches every format.

```bash
python tools/build_all.py documents
```

| Audience | Files |
|---|---|
| Participants | Participant Guide, Participant Pack (PDF, Word, PowerPoint), Field Notes booklet, calendar file, idea pitch template |
| Mentors | Mentor Plan, Mentor Pack, calendar file with every session |
| Judges and staff | Judge Plan, Business Mentor Plan, Staff Plan, paper score sheet |
| On stage | Kick-off, day 2, day 3, Demo Day, audience award and awards slide decks |

- **One source, three formats.** A pack's words live in one content file and are rendered to PDF,
  Word and PowerPoint, so the versions cannot disagree.
- **Real, editable slides.** Every text is a live text box and the audience chart is a native chart.
- **Calendar files that survive daylight saving.** Times carry their time-zone rules, which matters
  when the clocks change during the event.

Results go to `output/documents/`.
