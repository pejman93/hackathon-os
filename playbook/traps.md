# Traps worth knowing

Small things that cost hours when you meet them during an event week.

## Email

- **Mail merge can drop attachments.** If everyone needs a calendar file, attach it to a normal
  email or send calendar invitations.
- **Test every merge on yourself.** A wrong field sends "Hi @name" to everyone at once.
- **Use Bcc for groups,** so nobody sees the whole list.

## Schedule and promises

- **Lock times before documents go out.** A time changed later has to be corrected everywhere.
- **Check the guide against the people plan.** A drop-in session nobody is staffed for is a broken
  promise.
- **Name the exact tools.** If the guide says one AI provider and teams get another, you will spend
  day 1 explaining it.

## Google Forms and Sheets

- **Publish new Google Forms before a script tries to open or close them.**
- **Paste Apps Script as UTF-8,** or dashes and accents break.
- **Form answers shift formulas.** Each answer inserts a row, which moves any reference that starts
  at row 2 and can leave a results tab empty. Whole-column references cannot shift, so
  [`Judging.gs`](../backend/judging/Judging.gs) uses them.
- **Column headings are keys.** Renaming one can split answers into two columns.
- **Never edit the applications sheet.** Let other sheets read it.

## Websites

- **Link previews read the raw HTML.** Crawlers do not run JavaScript, so a "preview" banner removed
  by script still appears when the page is shared. The
  [WordPress build](../website/wordpress/build.py) strips it from the markup.
- **Send forms as `text/plain`.** That avoids the CORS preflight request Apps Script cannot answer.
- **Give each submission an ID.** A retry after a lost reply then updates the row instead of filing
  the person twice.

## Discord

- **Invite links can give a role automatically.** Give any role that can moderate by hand.
- **Check nicknames are real names,** and remove duplicate accounts.

## People and data

- **Keep personal data in one sheet,** shared with as few people as possible.
- **Collect paper sign-in sheets back** at the end of the day.
- **Pick one set of team colours** and use it on the boards, slides and stickers.
