# New edition

Read first: the [playbook](../README.md) and the [traps](../traps.md).

## Create the folder

1. Make `events/<name>/`, next to any earlier editions.
2. Inside, add `event.json`, `STATUS.md` and a `private/` folder for anything with people's names.
3. Add a `.gitignore` that ignores `private/`.

## Record decisions

- Settle only the questions that block the next step.
- Write each answer into `event.json` with who decided and when:
  `{"value": ..., "source": "<who>, <date>"}`.
- Unknown values stay `null` with `"status": "NOT CONFIRMED"`. Never fill a gap with a guess.
- Note each decision in `STATUS.md` with its date.

## Turn the playbook into dates

1. Week −N is the Monday N weeks before the first event day. Weeks +N count from the last day.
2. Copy the checklist from the playbook into `STATUS.md` with real dates.
3. Flag any week that has already passed.
