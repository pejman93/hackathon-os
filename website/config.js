/**
 * Site configuration.
 *
 * endpoint — the Google Apps Script web app URL (ends in /exec) that receives
 * applications. Leave it EMPTY to run the site in preview mode: the forms work
 * and show a confirmation, but nothing is sent or stored, and the page says so
 * in the banner and on every confirmation screen.
 *
 * Setting it flips the whole page to live copy automatically. That coupling is
 * deliberate: it is not possible to publish a page that promises "nothing is
 * stored" while it is quietly storing applications.
 *
 * signupEndpoint — the separate web app (backend/signups/Signups.gs) that takes
 * the "Notify me" and "Partner with us" forms of the recap page into their
 * own sheet. Same rule: empty means preview, and the page says so.
 */
window.HACKATHON_CONFIG = {
  endpoint: '',
  signupEndpoint: '',
  privacyUrl: 'https://example.org/privacy-policy/',
  contactEmail: 'hackathon@example.org'
};

/**
 * Posts one application and resolves with the receiver's answer.
 *
 * Content-Type is text/plain on purpose: that keeps this a "simple" CORS
 * request, so the browser sends no preflight OPTIONS — which Apps Script has
 * no way to answer.
 *
 * Each send carries a random id. If a reply is lost in transit and the visitor
 * retries, the receiver recognises the id and updates that row instead of
 * filing the person twice.
 */
window.HACKATHON_SUBMIT = function (type, fields) {
  var config = window.HACKATHON_CONFIG || {};
  // Sign-ups for the next edition go to their own sheet, applications to theirs.
  var endpoint = (type === 'notify' || type === 'partner') ? config.signupEndpoint : config.endpoint;
  if (!endpoint) return Promise.resolve({ ok: true, preview: true });
  window.HACKATHON_SUBMIT.ids = window.HACKATHON_SUBMIT.ids || {};
  if (!window.HACKATHON_SUBMIT.ids[type]) {
    window.HACKATHON_SUBMIT.ids[type] =
      Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 10);
  }
  return fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'text/plain;charset=utf-8' },
    body: JSON.stringify({
      type: type,
      submissionId: window.HACKATHON_SUBMIT.ids[type],
      website: (document.getElementById(type + '-website') || {}).value || '',
      fields: fields
    })
  }).then(function (response) {
    if (!response.ok) throw new Error('HTTP ' + response.status);
    return response.json();
  });
};
