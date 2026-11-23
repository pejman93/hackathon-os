/**
 * Sign-ups for the next edition: receives the two small forms on the recap page.
 *   notify  -> tab "Notify me"  people who want to hear when applications open
 *   partner -> tab "Partners"   organisations that want to sponsor, host or bring
 *                               a problem; each one is also emailed to SIGNUP_INBOX
 *
 * It lives in its own spreadsheet on purpose, so the applications sheet is never
 * touched. Deploy it as a web app the same way as backend/applications/Code.gs,
 * then set the /exec URL as HACKATHON_SIGNUP_ENDPOINT when building the site.
 *
 * Content-Type is text/plain so the browser sends no CORS preflight. Columns are
 * matched by header text, never by position.
 */

var SIGNUP_TABS = {
  notify: 'Notify me',
  partner: 'Partners'
};
var SIGNUP_INBOX = 'hackathon@example.org';
var ID_COLUMN = 'Submission ID';
var RECEIVED_COLUMN = 'Received';

function doPost(e) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(20000);
    if (!e || !e.postData || !e.postData.contents) return json({ ok: false, error: 'empty request' });
    var body = JSON.parse(e.postData.contents);

    // Honeypot: a hidden field no person fills in. Answer as if it worked so
    // the bot does not retry, but write nothing.
    if (body.website) return json({ ok: true });

    var tabName = SIGNUP_TABS[body.type];
    if (!tabName) return json({ ok: false, error: 'unknown form type' });

    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(tabName) || ss.insertSheet(tabName);

    var fields = body.fields || {};
    var record = {};
    record[RECEIVED_COLUMN] = new Date();
    record[ID_COLUMN] = body.submissionId || '';
    Object.keys(fields).forEach(function (k) { record[k] = String(fields[k]).slice(0, 2000); });

    var header = readHeader(sheet);
    if (header.length === 0) {
      header = Object.keys(record);
      sheet.getRange(1, 1, 1, header.length).setNumberFormat('@').setValues([header]).setFontWeight('bold');
      sheet.setFrozenRows(1);
    }
    Object.keys(record).forEach(function (key) {
      if (header.indexOf(key) === -1) {
        sheet.getRange(1, header.length + 1).setNumberFormat('@').setValue(key).setFontWeight('bold');
        header.push(key);
      }
    });
    var idIndex = header.indexOf(ID_COLUMN);
    if (idIndex !== -1) sheet.hideColumns(idIndex + 1);

    // A resend after a lost reply carries the same id: update that row instead
    // of adding the person twice, and do not email the inbox twice either.
    var targetRow = 0;
    if (body.submissionId && idIndex !== -1 && sheet.getLastRow() > 1) {
      var ids = sheet.getRange(2, idIndex + 1, sheet.getLastRow() - 1, 1).getValues();
      for (var i = 0; i < ids.length; i++) {
        if (ids[i][0] === body.submissionId) { targetRow = i + 2; break; }
      }
    }
    var row = header.map(function (name) { return record[name] !== undefined ? record[name] : ''; });
    if (targetRow) sheet.getRange(targetRow, 1, 1, row.length).setValues([row]);
    else sheet.appendRow(row);

    if (body.type === 'partner' && !targetRow) {
      try {
        MailApp.sendEmail({
          to: SIGNUP_INBOX,
          replyTo: fields['Email'] || SIGNUP_INBOX,
          subject: 'Partner request: ' + (fields['Organisation'] || fields['Name'] || 'hackathon page'),
          body: 'A partner request came in through the hackathon page.\n\n' +
                'Name: ' + (fields['Name'] || '') + '\n' +
                'Email: ' + (fields['Email'] || '') + '\n' +
                'Organisation: ' + (fields['Organisation'] || '') + '\n\n' +
                (fields['Message'] || '') + '\n\n' +
                'Reply to this email to answer them. All requests: ' + ss.getUrl()
        });
      } catch (mailError) { /* the row is saved; a failed email must not fail the form */ }
    }
    return json({ ok: true, duplicate: Boolean(targetRow) });
  } catch (err) {
    return json({ ok: false, error: String(err) });
  } finally {
    try { lock.releaseLock(); } catch (ignored) {}
  }
}

function readHeader(sheet) {
  if (sheet.getLastRow() === 0 || sheet.getLastColumn() === 0) return [];
  var values = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0]
                    .map(function (v) { return String(v).trim(); });
  while (values.length && values[values.length - 1] === '') values.pop();
  return values;
}

/** Opening the /exec URL in a browser shows this. Handy check that it is live. */
function doGet() {
  return json({ ok: true, service: 'hackathon sign-ups' });
}

function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
