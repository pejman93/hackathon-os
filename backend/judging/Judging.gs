/**
 * Judging form and live results sheet.
 *
 * Paste this under HandIn.gs in the same Apps Script project (it uses publish_()),
 * then run setupJudging() ONCE. It creates a folder with:
 *   - a form with one response per judge per team
 *   - a results sheet: the responses, each judge's score out of 100, and the ranking
 * Nothing is shared. Judges only get the form link.
 *
 * Scoring: each criterion is scored 1 to 5 and has a weight in percent. A score s on
 * a criterion of weight w gives s / 5 * w points, so a judge's total is out of 100.
 * A team's result is the average of its judges' totals.
 */

const JUDGES = ['Charles Babbage', 'Emmy Noether', 'John McCarthy', 'Katherine Johnson', 'Dorothy Vaughan'];
// "Other" is added for anyone else
const JUDGING_TEAMS = ['Team 1', 'Team 2', 'Team 3', 'Team 4'];
const CRITERIA = [   // title, weight in %, what it means. The weights must add up to 100.
  ['Working product', 30, 'It works live, with real AI inside.'],
  ['Real problem, real user', 20, 'A specific person or role with a real problem.'],
  ['Business case', 20, 'Who pays, how much, and why they would switch.'],
  ['Sustainability', 15, 'Monthly running cost, and what it depends on.'],
  ['Demo and pitch', 15, 'A clear story, on time.'],
];
const JUDGING_FOLDER = 'AI Entrepreneurship Hackathon – Judging';
const JUDGING_TITLE = 'Judging – AI Entrepreneurship Hackathon';
const FIRST_CRITERION_COLUMN = 4;   // Responses: A time, B judge, C team, D onwards the criteria


/** The column letter for a 1-based column number (A to Z is enough here). */
function columnLetter_(n) {
  return String.fromCharCode(64 + n);
}


/** The weighted total for one response, over whole columns of the Responses tab. */
function scoreExpression_() {
  return CRITERIA.map(function (c, i) {
    const col = columnLetter_(FIRST_CRITERION_COLUMN + i);
    return 'Responses!' + col + ':' + col + '*' + (c[1] / 5);
  }).join('+');
}


/**
 * The three formulas of the Scores tab, placed in row 1.
 *
 * Google Forms inserts each new answer as a new row, which shifts any reference that starts at
 * row 2 and leaves the tab empty. Whole-column references cannot shift, so these keep working.
 */
function scoreFormulas_() {
  const header = function (text, value) {
    return '=ARRAYFORMULA(IF(ROW(Responses!C:C)=1,"' + text + '",IF(Responses!C:C="",,' + value + ')))';
  };
  return [
    header('Judge', 'Responses!B:B'),
    header('Team', 'Responses!C:C'),
    header('Score (out of 100)', 'ROUND(' + scoreExpression_() + ',1)'),
  ];
}


function setupJudging() {
  const totalWeight = CRITERIA.reduce(function (sum, c) { return sum + c[1]; }, 0);
  if (totalWeight !== 100) throw new Error('The criteria weights add up to ' + totalWeight + ', not 100.');
  if (DriveApp.getFoldersByName(JUDGING_FOLDER).hasNext()) {
    throw new Error('"' + JUDGING_FOLDER + '" already exists. Nothing was changed.');
  }
  const folder = DriveApp.createFolder(JUDGING_FOLDER);

  // ---- Form ----
  const form = FormApp.create(JUDGING_TITLE);
  form.setDescription('Please fill this in once for each team, right after its demo. ' +
      'Score each criterion from 1 (weak) to 5 (excellent). ' +
      'After submitting you can still change your answers with the edit link.');
  form.setRequireLogin(false);                   // judges without a Workspace account can use it
  form.setCollectEmail(false);
  form.setAllowResponseEdits(true);              // a judge corrects a score instead of sending it twice
  try { form.setConfirmationMessage('Thank you. Your scores are saved.'); } catch (e) { /* optional */ }

  form.addMultipleChoiceItem().setTitle('Your name')
      .setChoiceValues(JUDGES).showOtherOption(true).setRequired(true);
  form.addListItem().setTitle('Team').setChoiceValues(JUDGING_TEAMS).setRequired(true);
  CRITERIA.forEach(function (c) {
    form.addScaleItem().setTitle(c[0] + ' (' + c[1] + '%)').setHelpText(c[2])
        .setBounds(1, 5).setLabels('Weak', 'Excellent').setRequired(true);
  });
  form.addParagraphTextItem().setTitle('Comments (optional)');

  publish_(form);                                // newer Google Forms must be published to take answers
  try { form.setAcceptingResponses(true); } catch (e) { Logger.log('Accepting responses: ' + e.message); }

  // ---- Results sheet ----
  let ss = SpreadsheetApp.create('Judging – results');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());
  SpreadsheetApp.flush();
  Utilities.sleep(3000);                         // give Google a moment to add the responses tab
  ss = SpreadsheetApp.openById(ss.getId());

  const responses = ss.getSheets().filter(function (s) { return s.getFormUrl(); })[0];
  responses.setName('Responses');
  const results = ss.getSheets().filter(function (s) { return !s.getFormUrl(); })[0];
  results.setName('Results');
  const scores = ss.insertSheet('Scores');

  // Scores: one row per response, the judge's total out of 100.
  scoreFormulas_().forEach(function (formula, i) { scores.getRange(1, i + 1).setFormula(formula); });
  styleHeader_(scores.getRange('A1:C1'));
  scores.setColumnWidths(1, 3, 170);
  scores.setFrozenRows(1);

  // Results: average per team and the ranking, then a judge-by-team table.
  results.getRange('A1').setValue('Results').setFontSize(16).setFontWeight('bold');
  results.getRange('A2').setValue('Each team\'s score is the average of its judges\' scores, out of 100. ' +
      'This page updates by itself.').setFontColor('#5d6068');
  results.getRange('A4:D4').setValues([['Team', 'Judges who scored', 'Average score', 'Rank']]);
  styleHeader_(results.getRange('A4:D4'));
  const firstTeam = 5;
  const lastTeam = firstTeam + JUDGING_TEAMS.length - 1;
  JUDGING_TEAMS.forEach(function (team, i) {
    const r = firstTeam + i;
    results.getRange(r, 1).setValue(team);
    results.getRange(r, 2).setFormula('=COUNTIF(Scores!$B:$B,A' + r + ')');
    results.getRange(r, 3).setFormula('=IF(B' + r + '=0,"",ROUND(AVERAGEIF(Scores!$B:$B,A' + r + ',Scores!$C:$C),1))');
    results.getRange(r, 4).setFormula('=IF(C' + r + '="","",RANK(C' + r + ',$C$' + firstTeam + ':$C$' + lastTeam + '))');
  });
  results.getRange('C' + firstTeam + ':C' + lastTeam).setNumberFormat('0.0');

  const titleRow = lastTeam + 3;
  const headRow = titleRow + 1;
  const firstJudge = headRow + 1;
  const lastJudge = firstJudge + 7;
  const teamColumns = JUDGING_TEAMS.length;
  results.getRange(titleRow, 1).setValue('Scores by judge').setFontSize(13).setFontWeight('bold');
  results.getRange(headRow, 1, 1, teamColumns + 1).setValues([['Judge'].concat(JUDGING_TEAMS)]);
  styleHeader_(results.getRange(headRow, 1, 1, teamColumns + 1));
  results.getRange(firstJudge, 1).setFormula('=IFERROR(UNIQUE(FILTER(Scores!A2:A,Scores!A2:A<>"")),"")');
  for (let r = firstJudge; r <= lastJudge; r++) {
    for (let c = 2; c <= teamColumns + 1; c++) {
      const col = columnLetter_(c);
      results.getRange(r, c).setFormula('=IF($A' + r + '="","",IFERROR(AVERAGEIFS(Scores!$C:$C,Scores!$A:$A,$A' +
          r + ',Scores!$B:$B,' + col + '$' + headRow + '),""))');
    }
  }
  results.getRange(firstJudge, 2, lastJudge - firstJudge + 1, teamColumns).setNumberFormat('0.0');
  results.setColumnWidth(1, 170);
  results.setColumnWidths(2, teamColumns, 140);

  ss.setActiveSheet(results);
  ss.moveActiveSheet(1);

  // ---- Into the judging folder ----
  DriveApp.getFileById(form.getId()).moveTo(folder);
  DriveApp.getFileById(ss.getId()).moveTo(folder);

  let link = form.getPublishedUrl();
  try { link = form.shortenFormUrl(link); } catch (e) { /* the long link works too */ }
  Logger.log('JUDGING FORM (for the judges): ' + link);
  Logger.log('Form editor (only for you): ' + form.getEditUrl());
  Logger.log('RESULTS SHEET (only for you): ' + ss.getUrl());
  Logger.log('Folder: ' + folder.getUrl());
}


function styleHeader_(range) {
  range.setFontWeight('bold').setBackground('#eef0ff');
}


/** Puts the current JUDGES list on the existing form, for a late change of judges. */
function updateJudgeNames() {
  const files = DriveApp.getFilesByName(JUDGING_TITLE);
  while (files.hasNext()) {
    const file = files.next();
    if (file.getMimeType() !== MimeType.GOOGLE_FORMS || file.isTrashed()) continue;
    const form = FormApp.openById(file.getId());
    const item = form.getItems(FormApp.ItemType.MULTIPLE_CHOICE)
        .filter(function (i) { return i.getTitle() === 'Your name'; })[0];
    item.asMultipleChoiceItem().setChoiceValues(JUDGES).showOtherOption(true);
    Logger.log('Judges on the form: ' + JUDGES.join(', ') + ', Other');
  }
}
