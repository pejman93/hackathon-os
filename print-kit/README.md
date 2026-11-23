# Print kit

Everything that gets printed for the event, built as PDF from a few CSV files.

```bash
python print-kit/src/build.py
```

| Output | From |
|---|---|
| Lanyard badges, front and back | `badges.csv` |
| Team and number stickers (Avery Zweckform L4785) | `teams.csv` |
| Certificates: participation, winner, audience award, mentor, staff | `certificates.csv`, `awards.csv` |
| Team list and team desk signs | `team_list.csv` |
| Direction signs and a pattern page | built in |

The lists are checked before anything is built. A wrong role or a winner without a team stops the
build, and the message names the file and the line.

To use your own lists, set `PRINT_KIT_DATA` to a folder with the same CSV files. Keep that folder
out of git, because it holds real names.
