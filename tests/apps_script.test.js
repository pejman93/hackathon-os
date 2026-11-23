// Tests for the Google Apps Script backend, with a small fake of Google's services.
//
//     node tests/apps_script.test.js
//
// Run it from the repository root. It also runs in JavaScriptCore (jsc).
var read = typeof readFile === 'function' ? readFile : function (p) { return require('fs').readFileSync(p, 'utf8'); };
var log = typeof print === 'function' ? print : console.log;

// ------------------------------------------------------------------ fake services
function FakeRange(sheet, row, col, rows, cols) { this.s = sheet; this.r = row; this.c = col; this.nr = rows; this.nc = cols; }
FakeRange.prototype.getValues = function () {
  var out = [];
  for (var i = 0; i < this.nr; i++) {
    var line = [], source = this.s.rows[this.r - 1 + i] || [];
    for (var j = 0; j < this.nc; j++) line.push(source[this.c - 1 + j] === undefined ? '' : source[this.c - 1 + j]);
    out.push(line);
  }
  return out;
};
FakeRange.prototype.setValues = function (values) {
  for (var i = 0; i < values.length; i++) {
    while (this.s.rows.length < this.r + i) this.s.rows.push([]);
    for (var j = 0; j < values[i].length; j++) this.s.rows[this.r - 1 + i][this.c - 1 + j] = values[i][j];
  }
  return this;
};
FakeRange.prototype.setValue = function (v) { return this.setValues([[v]]); };
FakeRange.prototype.setNumberFormat = function () { return this; };
FakeRange.prototype.setFontWeight = function () { return this; };

function FakeSheet() { this.rows = []; this.hidden = []; }
FakeSheet.prototype.getLastRow = function () { return this.rows.length; };
FakeSheet.prototype.getLastColumn = function () { return this.rows.reduce(function (m, r) { return Math.max(m, r.length); }, 0); };
FakeSheet.prototype.getRange = function (r, c, nr, nc) { return new FakeRange(this, r, c, nr || 1, nc || 1); };
FakeSheet.prototype.appendRow = function (v) { this.rows.push(v.slice()); };
FakeSheet.prototype.hideColumns = function (c) { this.hidden.push(c); };
FakeSheet.prototype.setFrozenRows = function () {};

function load(file, env, exported, edit) {
  var names = Object.keys(env);
  var source = read(file);
  if (edit) source = edit(source);
  var factory = Function.apply(null, names.concat(source + '\n;return {' + exported.join(',') + '};'));
  return factory.apply(null, names.map(function (n) { return env[n]; }));
}

function receiver(file) {
  var sheets = {}, mails = [];
  var spreadsheet = {
    getSheetByName: function (n) { return sheets[n] || null; },
    insertSheet: function (n) { sheets[n] = new FakeSheet(); return sheets[n]; },
    getUrl: function () { return 'https://example.org/sheet'; },
  };
  var api = load(file, {
    LockService: { getScriptLock: function () { return { waitLock: function () {}, releaseLock: function () {} }; } },
    SpreadsheetApp: { getActiveSpreadsheet: function () { return spreadsheet; } },
    ContentService: {
      MimeType: { JSON: 'json' },
      createTextOutput: function (text) { return { text: text, setMimeType: function () { return this; } }; },
    },
    MailApp: { sendEmail: function (m) { mails.push(m); } },
  }, ['doPost', 'doGet']);
  return {
    sheets: sheets, mails: mails, api: api,
    post: function (body) { return JSON.parse(api.doPost({ postData: { contents: JSON.stringify(body) } }).text); },
  };
}

// ------------------------------------------------------------------ a tiny test runner
var passed = 0, failed = [];
function equal(a, b, what) {
  var x = JSON.stringify(a), y = JSON.stringify(b);
  if (x !== y) throw new Error((what || 'value') + ': expected ' + y + ', got ' + x);
}
function test(name, fn) {
  try { fn(); passed++; log('ok    ' + name); }
  catch (e) { failed.push(name); log('FAIL  ' + name + ': ' + e.message); }
}
function column(sheet, title, row) { return sheet.rows[row - 1][sheet.rows[0].indexOf(title)]; }

// ------------------------------------------------------------------ applications
var APP = 'backend/applications/Code.gs';
var application = function (id, extra) {
  var fields = { 'Full name': 'Ada Lovelace', 'Email': 'ada@example.org' };
  Object.keys(extra || {}).forEach(function (k) { fields[k] = extra[k]; });
  return { type: 'participant', submissionId: id, fields: fields };
};

test('applications: first answer creates the tab, its columns and one row', function () {
  var h = receiver(APP);
  equal(h.post(application('a1')), { ok: true, duplicate: false });
  var s = h.sheets.Participants;
  equal(s.rows[0], ['Received', 'Submission ID', 'Full name', 'Email']);
  equal(s.rows.length, 2);
  equal(column(s, 'Email', 2), 'ada@example.org');
  equal(s.hidden.indexOf(2) !== -1, true, 'id column hidden');
});
test('applications: honeypot answers ok and writes nothing', function () {
  var h = receiver(APP), body = application('a1');
  body.website = 'https://spam.example.org';
  equal(h.post(body), { ok: true });
  equal(Object.keys(h.sheets).length, 0);
});
test('applications: an unknown form type is refused', function () {
  var h = receiver(APP), body = application('a1');
  body.type = 'nonsense';
  equal(h.post(body).ok, false);
});
test('applications: an empty request is refused', function () {
  var h = receiver(APP);
  equal(JSON.parse(h.api.doPost({}).text).ok, false);
});
test('applications: a resend with the same id updates the row', function () {
  var h = receiver(APP);
  h.post(application('a1'));
  equal(h.post(application('a1', { 'Email': 'new@example.org' })).duplicate, true);
  var s = h.sheets.Participants;
  equal(s.rows.length, 2);
  equal(column(s, 'Email', 2), 'new@example.org');
});
test('applications: a new field gets its own column, older rows stay put', function () {
  var h = receiver(APP);
  h.post(application('a1'));
  h.post(application('a2', { 'LinkedIn': 'linkedin.com/in/your-name' }));
  var s = h.sheets.Participants;
  equal(s.rows[0][4], 'LinkedIn');
  equal(column(s, 'Email', 2), 'ada@example.org');
  equal(column(s, 'LinkedIn', 3), 'linkedin.com/in/your-name');
});
test('applications: answers follow the header text after columns are reordered', function () {
  var h = receiver(APP);
  h.post(application('a1'));
  var s = h.sheets.Participants;
  s.rows = s.rows.map(function (r) { return [r[3], r[2], r[1], r[0]]; });
  h.post(application('a2', { 'Email': 'grace@example.org', 'Full name': 'Grace Hopper' }));
  equal(column(s, 'Email', 3), 'grace@example.org');
  equal(column(s, 'Full name', 3), 'Grace Hopper');
});

// ------------------------------------------------------------------ sign-ups
var SIGNUPS = 'backend/signups/Signups.gs';
var partner = { type: 'partner', submissionId: 'p1', fields: { 'Name': 'Emmy Noether', 'Email': 'emmy@example.org', 'Organisation': 'Example Labs' } };

test('sign-ups: a partner request emails the inbox once, even when resent', function () {
  var h = receiver(SIGNUPS);
  h.post(partner);
  equal(h.post(partner).duplicate, true);
  equal(h.mails.length, 1);
  equal(h.mails[0].replyTo, 'emmy@example.org');
  equal(h.sheets.Partners.rows.length, 2);
});
test('sign-ups: "notify me" is saved and emails nobody', function () {
  var h = receiver(SIGNUPS);
  h.post({ type: 'notify', submissionId: 'n1', fields: { 'Email': 'alan@example.org' } });
  equal(h.mails.length, 0);
  equal(h.sheets['Notify me'].rows.length, 2);
});
test('sign-ups: very long answers are cut to 2000 characters', function () {
  var h = receiver(SIGNUPS), long = new Array(5001).join('x');
  h.post({ type: 'partner', submissionId: 'p2', fields: { 'Message': long } });
  var s = h.sheets.Partners;
  equal(column(s, 'Message', 2).length, 2000);
});

// ------------------------------------------------------------------ judging
var JUDGING = 'backend/judging/Judging.gs';
var judging = function (edit, drive) {
  return load(JUDGING, { DriveApp: drive || {}, FormApp: {}, SpreadsheetApp: {}, Utilities: {}, Logger: {}, MimeType: {} },
              ['CRITERIA', 'scoreExpression_', 'scoreFormulas_', 'setupJudging'], edit);
};
function scoreFor(expression, scores) {             // evaluates "Responses!D:D*6+Responses!E:E*4+..."
  return expression.split('+').reduce(function (sum, term, i) { return sum + scores[i] * Number(term.split('*')[1]); }, 0);
}

test('judging: the weights add up to 100', function () {
  equal(judging().CRITERIA.reduce(function (s, c) { return s + c[1]; }, 0), 100);
});
test('judging: top marks give 100, lowest marks give 20, and weights count', function () {
  var e = judging().scoreExpression_();
  equal(Math.round(scoreFor(e, [5, 5, 5, 5, 5])), 100);
  equal(Math.round(scoreFor(e, [1, 1, 1, 1, 1])), 20);
  equal(Math.round(scoreFor(e, [5, 1, 1, 1, 1])), 44);
});
test('judging: score formulas use whole columns, so new form rows cannot shift them', function () {
  judging().scoreFormulas_().forEach(function (f) {
    equal(/Responses![A-Z]+\d/.test(f), false, 'row number in ' + f);
    equal(f.indexOf('ARRAYFORMULA') !== -1, true);
  });
});
test('judging: wrong weights stop the setup before anything is created', function () {
  var touched = 0;
  var drive = { getFoldersByName: function () { touched++; return { hasNext: function () { return false; } }; }, createFolder: function () { touched++; } };
  var j = judging(function (s) { return s.replace("['Working product', 30,", "['Working product', 40,"); }, drive);
  var message = '';
  try { j.setupJudging(); } catch (e) { message = e.message; }
  equal(message.indexOf('110') !== -1, true, 'error names the total');
  equal(touched, 0, 'Drive calls');
});

log('\n' + passed + ' passed, ' + failed.length + ' failed');
if (failed.length) {
  if (typeof process !== 'undefined') process.exit(1);
  throw new Error('tests failed');
}
