# Forms and sheets

Working examples: [`backend/`](../../backend).

## A Google Form

1. Use a plain title and a short intro. Make every question you need required.
2. Collect email addresses only if you need them.
3. If people may correct an answer, allow several responses and say "your last answer counts" in the
   thank-you text.
4. Publish it to "Anyone with the link". Changes to a published form are live at once.
5. Link it to a sheet, so answers land in one table.

## Test it from outside

- Open the link while signed out. It must open with no sign-in.
- Send a test answer and check the thank-you text.
- Send it empty. It must say a question is required.
- Delete the test answers afterwards.

## Apps Script

- Publish a new Google Form before a timer tries to open or close it.
- Paste scripts as UTF-8, or the dashes break.
- Rows added by a form shift formulas in other tabs. Use whole-column references, and test the
  results with a test answer before the day.

## Sheets

- Never edit an applications sheet. Other sheets read it.
- Column headings are keys, so never rename them.
- Keep personal data in the sheet, shared with as few people as possible.
