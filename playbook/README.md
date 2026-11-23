# Playbook: run a hackathon, step by step

The checklist behind this repository, counted back from the first event day. Copy it for your
event, replace the weeks with real dates, and tick things off. Each step names the tool that does
the work.

## Week −12: decide, and start partner talks

- [ ] Fix the dates and the venue.
- [ ] Agree the budget and the format with whoever signs them off.
- [ ] Name the standing team: lead, technical assistant, operations, marketing and media,
      partners, mentors and judges.
- [ ] Write a partner packet of 2 to 3 pages. Start with personal introductions.
- [ ] Set your colours, fonts and logos in [`brand/brand.json`](../brand/brand.json).

## Week −8: launch

- [ ] Put the application page live: [`website/`](../website) and
      [`backend/applications`](../backend/applications).
- [ ] Add the mentor sign-up form on the same page.
- [ ] Email everyone on your sign-up list ([`backend/signups`](../backend/signups)).
- [ ] Run the campaign: posters, screens and social posts from [`marketing/`](../marketing).
- [ ] Write a photo and video brief: shot list, good light, camera brief.

## Week −5: applications close

- [ ] Close applications. Count each person once.
- [ ] Build the selection list in a separate sheet that **reads** the applications sheet and never
      edits it.
- [ ] Give each person one role (builder, business, design and UX, pitch and story, generalist)
      and one level (L1, L2 or L3).
- [ ] Form small mixed teams.
- [ ] Keep a waiting list, because some people will drop out.

## Week −3: people

- [ ] Confirm the judges.
- [ ] Give a guest speaker a fixed slot, a proper welcome and time for questions.
- [ ] Send the mentor plan and one calendar file with all sessions
      ([`make_mentor_plan.py`](../documents/make_mentor_plan.py),
      [`make_mentor_calendar.py`](../documents/make_mentor_calendar.py)).
- [ ] Send the business mentor and judge plans ([`make_role_plans.py`](../documents/make_role_plans.py)).
- [ ] Send the staff plan and calendar invitations ([`make_staff.py`](../documents/make_staff.py)).

## Week −2: final preparations

- [ ] Lock the schedule and the hand-in deadline **before** the guide goes out.
- [ ] Decide which AI tools teams will get before the guide goes out.
- [ ] Check every promise in the guide against the people plan.
- [ ] Send the selection email and the participant guide
      ([`make_guide.py`](../documents/make_guide.py), [templates](email-templates)).
      Send any mail merge to yourself first.
- [ ] Hold a 30-minute onboarding call with each tech mentor.
- [ ] Set up Discord: invite links with automatic roles, the staff role given by hand, team roles
      given after the reveal.
- [ ] Print badges, lanyards, stickers, desk signs and a certificate for every outcome
      ([`print-kit/`](../print-kit)).
- [ ] Order simple, filling food with vegetarian and vegan options.
- [ ] 24 hours before: send a reminder with the field notes and the Discord link.

## The event

- [ ] Start day 1 with real time for ideas: about 4 hours of brainstorming.
- [ ] Run the kick-off: slides, live polls and the idea pitch template
      ([`make_kickoff.py`](../documents/make_kickoff.py),
      [`make_pitch_template.py`](../documents/make_pitch_template.py)).
- [ ] Give each team one AI key with a spending limit and a short expiry, posted only in that
      team's own channel.
- [ ] Open the hand-in: team folders, form and responses sheet
      ([`backend/hand-in`](../backend/hand-in)).
- [ ] Score with the judging form and live results sheet ([`backend/judging`](../backend/judging)).
      Test the results sheet with a test answer before the day.
- [ ] Run the audience vote with results hidden until the reveal.
- [ ] Collect any paper attendance sheet back: it holds personal data.

## Weeks +1 to +4: after

- [ ] The same evening: switch off the team AI keys, delete the participant invite and make team
      channels read-only.
- [ ] Send certificates and thank-you emails.
- [ ] Turn the event page into a recap with sign-ups for the next edition.
- [ ] Send each partner a short report within 2 weeks.
- [ ] Offer the teams a place to keep demoing ([template](email-templates/demo-table-dates.txt)).
- [ ] Hold a [retro](runbooks/retro.md), and update this playbook and [`traps.md`](traps.md).
