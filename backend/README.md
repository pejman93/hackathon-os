# Backend

Four Google Apps Script programs. There is no server to run or pay for: Google Sheets is the
database, and each script is deployed from the sheet it belongs to.

| Folder | What it does |
|---|---|
| [`applications/`](applications/Code.gs) | Receives participant and mentor applications from the website |
| [`signups/`](signups/Signups.gs) | Receives "Notify me" and partner requests, and emails the team once per request |
| [`hand-in/`](hand-in/HandIn.gs) | Creates one Drive folder per team, the hand-in form and a timer that opens it |
| [`judging/`](judging/Judging.gs) | Creates the judging form and a live results sheet with weighted scores and ranking |

## Details worth a look

- **No CORS preflight.** The site posts `text/plain`, because Apps Script cannot answer `OPTIONS`.
- **Safe retries.** Each submission has an ID, so a resend updates the row instead of adding it twice.
- **Columns by name.** Answers are matched to header text, so a sheet can be reordered at any time.
- **A lock around every write,** so two people submitting together cannot take the same row.
- **Spam honeypot.** A hidden field filled in by bots gets a polite "ok" and writes nothing.
- **Formulas that survive form inserts.** The judging sheet uses whole-column references.

## Set up

Each file starts with its own steps. The short version: create a Google Sheet, open
**Extensions > Apps Script**, paste the file, then **Deploy > New deployment > Web app**.
`Judging.gs` goes in the same Apps Script project as `HandIn.gs` and uses its `publish_()` helper.

Tests with a fake of Google's services: `node tests/apps_script.test.js`.
