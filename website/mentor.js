'use strict';
(() => {
 const dialog=document.getElementById('mentor-dialog');
 const form=document.getElementById('mentor-form');
 const success=document.getElementById('mentor-success');
 const error=document.getElementById('mentor-error');
 let opener=null;
 // Same rule as the participant form: live copy follows the endpoint setting.
 (()=>{const c=window.HACKATHON_CONFIG||{};if(!c.endpoint)return;
  const note=document.querySelector('#mentor-form .mentor-preview-note');
  if(note)note.innerHTML=`We use your details only to consider you as a mentor. See our <a href="${c.privacyUrl}" target="_blank" rel="noopener noreferrer">privacy policy</a>.`;
  const submit=document.querySelector('#mentor-form button[type=submit]');
  if(submit)submit.innerHTML=submit.innerHTML.replace('Preview mentor application','Send my application');
 })();
 function close(){dialog.close();document.body.classList.remove('dialog-open');opener?.focus({preventScroll:true});}
 function open(button){opener=button;dialog.showModal();document.body.classList.add('dialog-open');document.getElementById(form.hidden?'mentor-close':'mentor-name').focus({preventScroll:true});}
 document.addEventListener('click',event=>{const button=event.target.closest('[data-mentor-open]');if(button){event.preventDefault();open(button);}});
 document.getElementById('mentor-close').addEventListener('click',close);
 dialog.addEventListener('cancel',event=>{event.preventDefault();close();});
 dialog.addEventListener('click',event=>{if(event.target===dialog){const b=dialog.getBoundingClientRect();if(event.clientX<b.left||event.clientX>b.right||event.clientY<b.top||event.clientY>b.bottom)close();}});
 const safe=value=>String(value).replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
 form.addEventListener('submit',async event=>{
  event.preventDefault();error.textContent='';
  const name=document.getElementById('mentor-name'),email=document.getElementById('mentor-email'),linkedin=document.getElementById('mentor-linkedin'),why=document.getElementById('mentor-why');
  const fail=(message,field)=>{error.textContent=message;field.setAttribute('aria-describedby','mentor-error');field.focus();};
  if(!name.value.trim())return fail('Tell us your name.',name);
  if(!email.value.trim()||!email.checkValidity())return fail('Enter a valid email address.',email);
  let linkedinURL;try{linkedinURL=new URL(linkedin.value.trim().startsWith('http')?linkedin.value.trim():'https://'+linkedin.value.trim());}catch{}
  if(!linkedinURL||!['https:','http:'].includes(linkedinURL.protocol)||!(linkedinURL.hostname==='linkedin.com'||linkedinURL.hostname.endsWith('.linkedin.com'))||!/^\/in\/[^/]+/.test(linkedinURL.pathname))return fail('Add your LinkedIn profile, for example linkedin.com/in/your-name.',linkedin);
  if(!why.value.trim())return fail('Tell us briefly why you’d like to support a team.',why);
  const config=window.HACKATHON_CONFIG||{},live=Boolean(config.endpoint);
  const submit=form.querySelector('button[type=submit]');
  if(live){
   if(submit.disabled)return;                // a double tap must not file twice
   const label=submit.innerHTML;
   submit.disabled=true;submit.textContent='Sending…';
   try{
    const result=await window.HACKATHON_SUBMIT('mentor',{
     'Name':name.value.trim(),'Email':email.value.trim(),
     'LinkedIn':linkedinURL.href,'Why':why.value.trim()
    });
    if(!result||!result.ok)throw new Error((result&&result.error)||'save failed');
   }catch(err){
    submit.disabled=false;submit.innerHTML=label;
    error.textContent=`We couldn’t send your application just now. Your details are still here — try again, or email them to ${config.contactEmail}.`;
    return;
   }
  }
  form.hidden=true;success.hidden=false;
  success.innerHTML=`<div class="mentor-success-mark" aria-hidden="true">LET’S HELP<br>GOOD IDEAS HAPPEN.</div><h3>Thanks, ${safe(name.value.trim())}.</h3><p>${live?'We’ll':'In the live application, we’ll'} review your experience and contact you at <strong>${safe(email.value.trim())}</strong> about mentoring a team.</p><dl class="mentor-summary"><dt>LinkedIn</dt><dd>${safe(linkedinURL.href)}</dd><dt>Your motivation</dt><dd>${safe(why.value.trim())}</dd></dl><p class="cv-reminder"><strong>One thing left to do.</strong> Send your CV to <a href="mailto:hackathon@example.org">hackathon@example.org</a>. A few lines about what draws you to this are welcome alongside it, though not required.</p>${live?'':`<p class="mentor-preview-note"><strong>Preview complete.</strong> Nothing has been saved or emailed.</p>`}<button class="button button-dark" type="button" id="mentor-edit">Review my details <span aria-hidden="true"><svg class="icon-arrow" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M20 12H4m7-7-7 7 7 7"/></svg></span></button>`;
  document.getElementById('mentor-edit').addEventListener('click',()=>{success.hidden=true;form.hidden=false;name.focus();});
  dialog.scrollTop=0;success.querySelector('button').focus({preventScroll:true});
 });
})();
