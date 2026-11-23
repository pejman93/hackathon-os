/**
 * Hand-in setup. Run setup() ONCE. It creates, in your Drive:
 *   - a parent folder with one folder per team, each editable only by that team
 *   - the hand-in Google Form and its responses Sheet, inside that folder
 *   - a timer that OPENS the form at OPENS_AT
 *
 * The deadline can be announced only (the default), with late hand-ins visible
 * from the timestamp in the Sheet, or enforced by setting AUTO_CLOSE to true.
 * It is safe to run again: it reuses the folders, form and sheet it already made.
 * openHandIn() and closeHandIn() can also be run by hand at any time.
 */

// ===== 1. FILL IN THE EMAILS: in quotes, a comma after each =====
const TEAM_EMAILS = {
  'Team 1': [
    // 'name@example.org',
  ],
  'Team 2': [],
  'Team 3': [],
  'Team 4': [],
};

// Mentors and judges can VIEW everything: all four team folders and the responses.
const MENTORS_AND_JUDGES = [
  // 'name@example.org',
];

// ===== 2. THE HAND-IN WINDOW (write the UTC offset that applies on that date) =====
const OPENS_AT = new Date('2026-10-25T16:00:00+01:00');
const CLOSES_AT = new Date('2026-10-25T23:59:00+01:00');
const AUTO_CLOSE = false;                // false: the form never closes by itself
const LOCK_FOLDERS_AT_CLOSE = false;     // true: when closed, each team becomes Viewer of its folder

const PARENT_NAME = 'AI Entrepreneurship Hackathon – Hand-in';
const FORM_TITLE = 'Hand-in – AI Entrepreneurship Hackathon';
const NOT_OPEN_YET = 'The hand-in opens on Sunday 25 October at 16:00. Deadline: 23:59.';
const CLOSED = 'The hand-in is closed. Thank you!';


function setup() {
  // ---- Folders (reused if an earlier run made them) ----
  const parent = folderIn_(null, PARENT_NAME);
  share_(parent, MENTORS_AND_JUDGES, 'viewer');          // viewers here can see the team folders too

  const teamFolders = {};
  Object.keys(TEAM_EMAILS).forEach(function (team) {
    const folder = folderIn_(parent, team);
    share_(folder, TEAM_EMAILS[team], 'editor');         // each team edits only its own folder
    teamFolders[team] = folder;
  });

  // ---- Form (reused if an earlier run made it; its questions are only added once) ----
  const old = DriveApp.getFilesByName(FORM_TITLE);
  let form = null;
  while (old.hasNext() && !form) {
    const file = old.next();
    if (file.getMimeType() === MimeType.GOOGLE_FORMS && !file.isTrashed()) form = FormApp.openById(file.getId());
  }
  const fresh = !form || form.getItems().length === 0;
  if (!form) form = FormApp.create(FORM_TITLE);
  form.setDescription('One person per team fills this in. Open from Sunday 25 October, 16:00. Deadline: 23:59. ' +
      'Put your slides and your 1-minute demo recording in your team folder first, then paste the links here.');
  form.setRequireLogin(false);                            // people without a Workspace account can submit
  form.setCollectEmail(false);

  const isUrl = FormApp.createTextValidation()
      .requireTextIsUrl()
      .setHelpText('Please paste a full link, starting with https://')
      .build();
  const SHARE_HINT = 'Set sharing to "Anyone with the link can view", so the judges can open it.';

  if (fresh) {
  form.addListItem().setTitle('Team').setChoiceValues(Object.keys(TEAM_EMAILS)).setRequired(true);
  form.addTextItem().setTitle('Product name').setRequired(true);
  form.addParagraphTextItem().setTitle("One sentence: who it's for and what it does").setRequired(true);
  form.addTextItem().setTitle('GitHub link').setValidation(isUrl).setRequired(true);
  form.addTextItem().setTitle('Live link').setValidation(isUrl).setRequired(false);
  form.addTextItem().setTitle('Slides link').setHelpText(SHARE_HINT).setValidation(isUrl).setRequired(true);
  form.addTextItem().setTitle('Demo recording link, 1 minute').setHelpText(SHARE_HINT)
      .setValidation(isUrl).setRequired(true);
  form.addParagraphTextItem().setTitle('How to open or run it').setRequired(true);
  form.addParagraphTextItem().setTitle('AI tools used to build it');
  form.addParagraphTextItem().setTitle('Anything not working yet?');
  }

  // Closed until OPENS_AT; people who open the link early see when it opens.
  // New Google Forms must be published before their response setting can change.
  publish_(form);
  if (new Date() < OPENS_AT) {
    // Some Google accounts refuse these two settings on new forms; then the form simply stays open,
    // and the link is shared at opening time instead.
    try { form.setAcceptingResponses(false); } catch (e) { Logger.log('Could not close the form: ' + e.message); }
    try { form.setCustomClosedFormMessage(NOT_OPEN_YET); } catch (e) { Logger.log('No closed message: ' + e.message); }
  }
  Logger.log('Form accepting responses now: ' + form.isAcceptingResponses() +
      (typeof form.isPublished === 'function' ? ', published: ' + form.isPublished() : ''));

  // ---- Responses Sheet, linked to the form ----
  let sheet = null;
  try { sheet = SpreadsheetApp.openById(form.getDestinationId()); } catch (e) { /* no sheet yet */ }
  if (!sheet) {
    sheet = SpreadsheetApp.create('Hand-in – responses');
    form.setDestination(FormApp.DestinationType.SPREADSHEET, sheet.getId());
  }

  // The form and the sheet start in My Drive; move them into the hand-in folder.
  DriveApp.getFileById(form.getId()).moveTo(parent);
  DriveApp.getFileById(sheet.getId()).moveTo(parent);

  // ---- Remember the IDs for the timers ----
  const ids = {form: form.getId()};
  Object.keys(teamFolders).forEach(function (team) { ids[team] = teamFolders[team].getId(); });
  PropertiesService.getScriptProperties().setProperty('IDS', JSON.stringify(ids));

  // ---- Timers: open at OPENS_AT (and close at CLOSES_AT only if AUTO_CLOSE) ----
  ScriptApp.getProjectTriggers().forEach(function (t) { ScriptApp.deleteTrigger(t); });   // only this script's
  if (new Date() < OPENS_AT) ScriptApp.newTrigger('openHandIn').timeBased().at(OPENS_AT).create();
  if (AUTO_CLOSE) ScriptApp.newTrigger('closeHandIn').timeBased().at(CLOSES_AT).create();

  // ---- Links ----
  let formLink = form.getPublishedUrl();
  try { formLink = form.shortenFormUrl(formLink); } catch (e) { /* the long link works too */ }

  Logger.log('PARENT FOLDER:   ' + parent.getUrl());
  Object.keys(teamFolders).forEach(function (team) {
    Logger.log(team + ' folder:   ' + teamFolders[team].getUrl());
  });
  Logger.log('FORM (share this): ' + formLink);
  Logger.log('Form editor (only for you): ' + form.getEditUrl());
  Logger.log('RESPONSES SHEET: ' + sheet.getUrl());
  Logger.log('Form opens ' + OPENS_AT + (AUTO_CLOSE ? ' and closes ' + CLOSES_AT : ' and stays open'));
}


// Runs at OPENS_AT (also works by hand): the form starts accepting hand-ins.
function openHandIn() {
  const ids = JSON.parse(PropertiesService.getScriptProperties().getProperty('IDS'));
  const form = FormApp.openById(ids.form);
  publish_(form);
  try { form.setAcceptingResponses(true); } catch (e) { Logger.log('Could not open the form: ' + e.message); }
  Logger.log('Hand-in is OPEN.');
}


// Runs at CLOSES_AT if AUTO_CLOSE (also works by hand): the form closes and, if set, the team folders become view-only.
function closeHandIn() {
  const ids = JSON.parse(PropertiesService.getScriptProperties().getProperty('IDS'));
  const form = FormApp.openById(ids.form);
  try { form.setAcceptingResponses(false); } catch (e) { Logger.log('Could not close the form: ' + e.message); }
  try { form.setCustomClosedFormMessage(CLOSED); } catch (e) { /* some accounts refuse a custom message */ }
  if (LOCK_FOLDERS_AT_CLOSE) {
    const me = Session.getEffectiveUser().getEmail();
    Object.keys(TEAM_EMAILS).forEach(function (team) {
      const folder = DriveApp.getFolderById(ids[team]);
      folder.getEditors().forEach(function (user) {
        const email = user.getEmail();
        if (!email || email === me) return;              // never touch your own access
        try {
          folder.removeEditor(email);
          folder.addViewer(email);
        } catch (e) {
          Logger.log('Could not lock ' + team + ' for ' + email + ': ' + e.message);
        }
      });
    });
  }
  Logger.log('Hand-in is CLOSED.');
}


// Shares a folder with each email; if one fails (e.g. outside sharing is blocked), it logs it and goes on.
function share_(folder, emails, role) {
  emails.forEach(function (email) {
    try {
      if (role === 'editor') folder.addEditor(email);
      else folder.addViewer(email);
    } catch (e) {
      Logger.log('Could not share "' + folder.getName() + '" with ' + email + ': ' + e.message);
    }
  });
}


// The folder with this name inside `parent` (or in My Drive when parent is null); made if missing.
function folderIn_(parent, name) {
  const found = parent ? parent.getFoldersByName(name) : DriveApp.getFoldersByName(name);
  while (found.hasNext()) {
    const folder = found.next();
    if (!folder.isTrashed()) return folder;
  }
  return parent ? parent.createFolder(name) : DriveApp.createFolder(name);
}


// Publishes the form if this Google account uses the newer "publish" step for Forms.
function publish_(form) {
  try {
    if (typeof form.isPublished === 'function' && !form.isPublished()) form.setPublished(true);
  } catch (e) {
    Logger.log('Could not publish the form automatically: ' + e.message);
  }
}
