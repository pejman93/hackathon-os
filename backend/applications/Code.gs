/**
 * Application receiver: takes participant and mentor applications from the
 * event site and appends one row per application to this spreadsheet.
 *
 * Setup:
 *   1. Create a Google Sheet.
 *   2. Extensions -> Apps Script, and replace everything with this file.
 *   3. Deploy -> New deployment -> Web app.
 *        Execute as:     Me
 *        Who has access: Anyone
 *   4. Copy the /exec URL. That is what the website posts to.
 *
 * Re-deploying after an edit: Deploy -> Manage deployments -> edit the existing
 * one -> Version: New version. A *new* deployment issues a different URL, and
 * the website would keep posting to the old one.
 *
 * The page sends Content-Type: text/plain on purpose. That keeps the request
 * "simple" in CORS terms, so the browser sends no preflight OPTIONS request,
 * which Apps Script cannot answer.
 *
 * Columns are addressed by their header text, never by position, so you can
 * reorder or hide them, or insert your own (a "Decision" column, say), without
 * answers landing in the wrong place.
 */

var TABS = {
  participant: 'Participants',
  mentor: 'Mentors'
};

var ID_COLUMN = 'Submission ID';
var RECEIVED_COLUMN = 'Received';

function doPost(e) {
  var lock = LockService.getScriptLock();
  try {
    // Two people submitting at the same instant would otherwise race for the
    // same row. Serialise the whole read-modify-write.
    lock.waitLock(20000);

    if (!e || !e.postData || !e.postData.contents) {
      return json({ ok: false, error: 'empty request' });
    }

    var body = JSON.parse(e.postData.contents);

    // Honeypot: a hidden field no human ever fills in. Answer as if it worked,
    // so the bot does not retry, but write nothing.
    if (body.website) return json({ ok: true });

    var tabName = TABS[body.type];
    if (!tabName) return json({ ok: false, error: 'unknown form type' });

    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(tabName);
    if (!sheet) sheet = ss.insertSheet(tabName);

    var fields = body.fields || {};
    var record = { };
    record[RECEIVED_COLUMN] = new Date();
    record[ID_COLUMN] = body.submissionId || '';
    Object.keys(fields).forEach(function (k) { record[k] = fields[k]; });

    var header = readHeader(sheet);

    // A brand new tab gets its columns in the order the form sends them.
    if (header.length === 0) {
      header = Object.keys(record);
      sheet.getRange(1, 1, 1, header.length)
           .setNumberFormat('@')
           .setValues([header])
           .setFontWeight('bold');
      sheet.setFrozenRows(1);
    }

    // Anything the form sends that has no column yet gets one appended, rather
    // than being silently dropped. This is also what repairs a tab created by
    // an older version of this script.
    Object.keys(record).forEach(function (key) {
      if (header.indexOf(key) === -1) {
        sheet.getRange(1, header.length + 1)
             .setNumberFormat('@')
             .setValue(key)
             .setFontWeight('bold');
        header.push(key);
      }
    });

    // Submission IDs are plumbing. Keep the column, hide it from view.
    var idIndex = header.indexOf(ID_COLUMN);
    if (idIndex !== -1) sheet.hideColumns(idIndex + 1);

    // If a reply was lost in transit and the visitor pressed send again, the
    // same id arrives twice. Update that row instead of filing them twice.
    var targetRow = 0;
    if (body.submissionId && idIndex !== -1 && sheet.getLastRow() > 1) {
      var ids = sheet.getRange(2, idIndex + 1, sheet.getLastRow() - 1, 1).getValues();
      for (var i = 0; i < ids.length; i++) {
        if (ids[i][0] === body.submissionId) { targetRow = i + 2; break; }
      }
    }

    var row = header.map(function (name) {
      return record[name] !== undefined ? record[name] : '';
    });

    if (targetRow) {
      sheet.getRange(targetRow, 1, 1, row.length).setValues([row]);
    } else {
      sheet.appendRow(row);
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
  var values = sheet.getRange(1, 1, 1, sheet.getLastColumn())
                    .getValues()[0]
                    .map(function (v) { return String(v).trim(); });
  // Drop only TRAILING blanks. Removing a blank from the middle would shift
  // every later column, and the row is written by array position.
  while (values.length && values[values.length - 1] === '') values.pop();
  return values;
}

/** Opening the /exec URL in a browser should show this. Handy sanity check. */
function doGet() {
  return json({ ok: true, service: 'hackathon application receiver' });
}

function json(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
