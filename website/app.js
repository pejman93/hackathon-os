'use strict';
(() => {
 const journey=document.querySelector('.photo-journey');
 const reduceMotion=window.matchMedia('(prefers-reduced-motion: reduce)');
 let queued=false;
 const clamp=(v,min,max)=>v<min?min:v>max?max:v;
 function updateScroll(){
  queued=false;
  if(!journey)return;
  const box=journey.getBoundingClientRect();
  // The journey is one screen tall now (the story only), so the photo is not
  // pinned; it drifts slowly from the moment the section enters at the bottom
  // until it leaves at the top.
  const progress=clamp((innerHeight-box.top)/(innerHeight+box.height),0,1);
  if(!isFinite(progress))return;
  journey.style.setProperty('--photo-shift',reduceMotion.matches?'0px':`${(progress*55).toFixed(1)}px`);
 }
 // The stage has to cover the whole visible screen. Viewport units cannot be
 // trusted for that here: on the live site every vh unit resolved ~190px
 // shorter than the actual viewport, leaving a bare strip at the bottom.
 // innerHeight is the honest number. It only ever grows within an orientation,
 // so a mobile address bar sliding away never reflows the stage mid-scroll.
 let tallestSeen=0;
 function sizeStage(){
  if(innerHeight>tallestSeen){
   tallestSeen=innerHeight;
   // On the root, so the hero (outside the journey) can size itself too.
   document.documentElement.style.setProperty('--stage-h',tallestSeen+'px');
  }
 }
 sizeStage();
 // One update per frame at most, so flinging the page cannot queue up work.
 const request=()=>{if(!queued){queued=true;requestAnimationFrame(()=>{sizeStage();updateScroll();});}};
 // Resizing and zooming move the scroll maths in one jump. The crossfade
 // transition would animate that jump, which reads as a flash. Suppress it
 // while the viewport is changing and restore it once it settles.
 let settle=0;
 const reflow=()=>{
  if(journey)journey.classList.add('viewport-changing');
  clearTimeout(settle);
  settle=setTimeout(()=>{if(journey)journey.classList.remove('viewport-changing');},250);
  request();
 };
 addEventListener('scroll',request,{passive:true});
 addEventListener('resize',reflow,{passive:true});
 addEventListener('orientationchange',()=>{tallestSeen=0;sizeStage();reflow();},{passive:true});
 addEventListener('pageshow',request,{passive:true});
 // Frames stop while the tab is hidden; re-sync on the way back.
 document.addEventListener('visibilitychange',request);
 // Pinch-zoom resizes the visual viewport without firing a window resize.
 if(window.visualViewport){visualViewport.addEventListener('resize',reflow,{passive:true});visualViewport.addEventListener('scroll',request,{passive:true});}
 if(reduceMotion.addEventListener)reduceMotion.addEventListener('change',request);
 // Backdrops change the stage height as they decode; re-measure when they land.
 // Decode both photographs up front rather than on first paint: the second and third
 // are transparent until scrolled to, so the browser is in no hurry to
 // rasterise them, and an undecoded image pops in late during a fast scroll.
 document.querySelectorAll('img.backdrop').forEach(img=>{
  const ready=()=>{if(img.decode)img.decode().catch(()=>{});request();};
  if(img.complete)ready();else img.addEventListener('load',ready,{once:true});
 });
 addEventListener('load',request,{once:true});
 updateScroll();

 const config=window.HACKATHON_CONFIG||{};
 if(config.endpoint)document.querySelector('.preview-banner')?.remove();
 const escape=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const arrow='<svg class="icon-arrow" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M5 19 19 5M5 5h14v14"/></svg>';

 // ---- People ------------------------------------------------------------
 // Someone without a LinkedIn link is a plain card, someone without a photo
 // gets their initial in the display face. The last entry is the invitation
 // to mentor the next hackathon, which opens the mentor dialog.
 function personCard(p){
  if(p.unannounced)return `<button type="button" class="person person-more" data-mentor-open aria-label="Apply to mentor the next hackathon"><span class="portrait-slot"><span class="more-plus" aria-hidden="true">+</span><span class="more-label">YOUR EXPERIENCE.<br>THEIR NEXT STEP.</span></span><span class="person-caption"><strong><span class="label-full">Mentor the next one</span><span class="label-tight">Be a mentor</span></strong><span class="person-role">Support a team</span><span class="person-title">Share what you know. Help an idea take shape.</span><span class="person-link-label">Apply to mentor <span aria-hidden="true">${arrow}</span></span></span></button>`;
  const portrait=p.image?`<img src="${escape(p.image)}" alt="${escape(p.name+', '+p.role)}" width="400" height="400" loading="lazy">`:`<span class="portrait-index" aria-hidden="true">${escape(p.name.charAt(0))}</span>`;
  const slot=`<span class="portrait-slot${p.stagePortrait?' portrait-stage':''}">${portrait}</span>`;
  const caption=`<strong>${escape(p.name)}</strong><span class="person-role">${escape(p.role)}</span>${p.title?`<span class="person-title">${escape(p.title)}</span>`:''}`;
  if(!p.linkedin)return `<div class="person person-profile person-static">${slot}<span class="person-caption">${caption}</span></div>`;
  return `<a class="person person-profile" href="${escape(p.linkedin)}" target="_blank" rel="noopener noreferrer" aria-label="${escape(p.name)} on LinkedIn (opens in a new tab)">${slot}<span class="person-caption">${caption}<span class="person-link-label">LinkedIn <span aria-hidden="true">${arrow}</span></span></span></a>`;
 }
 const peopleGrid=document.getElementById('people-grid');
 if(peopleGrid&&Array.isArray(window.HACKATHON_TEAM))peopleGrid.innerHTML=window.HACKATHON_TEAM.map(personCard).join('');
 // The mentor invitation fills whatever is left of the final row, so adding or
 // removing a person never strands a card alone in a column. The column count
 // is read from the grid itself rather than assumed, so this follows the
 // responsive breakpoints without duplicating them here.
 function fitMentorCard(){
  if(!peopleGrid)return;
  const card=peopleGrid.querySelector('.person-more');
  if(!card)return;
  // Release our own span before measuring. A card left spanning more tracks
  // than the template defines creates an IMPLICIT extra column, and counting
  // that back as a real one feeds the wrong number straight into the next
  // calculation — the card then keeps its oversized span forever and bursts
  // out of the grid. Measuring from a neutral state breaks that loop.
  card.style.gridColumn='auto';
  card.classList.remove('person-more-wide');
  const cols=getComputedStyle(peopleGrid).gridTemplateColumns.split(' ').filter(Boolean).length;
  if(!cols)return;
  const remainder=peopleGrid.querySelectorAll('.person-profile').length%cols;
  const span=remainder===0?cols:cols-remainder;
  card.style.gridColumn='span '+span;
  // Decide the side-by-side layout from the width the card actually ended up
  // with, not from the span it was asked for. Dragging a window edge moves
  // through many intermediate widths, and a span read a frame late would
  // otherwise lay the card out horizontally inside a narrow column.
  card.classList.toggle('person-more-wide',card.getBoundingClientRect().width>=420);
 }
 fitMentorCard();
 addEventListener('resize',()=>{
  fitMentorCard();
  // Re-measure once the reflow has settled, so a mid-drag frame cannot leave
  // the card in a layout that does not match its final width.
  requestAnimationFrame(fitMentorCard);
 },{passive:true});

 // ---- The background video ---------------------------------------------
 // A silent loop of short cuts from the four days, behind the hero only (see
 // the note on backdrops in styles.css for why it is not pinned). Portrait
 // screens get the 2x2 cut, others the three columns; the choice is made once,
 // here, so a phone never falls back to the wide file. It plays only while the
 // hero is on screen and never under reduced motion: the first-frame image
 // behind it stays instead.
 const video=document.querySelector('.hero-video');
 const hero=document.querySelector('.hero');
 if(video&&video.dataset.wide&&hero&&!reduceMotion.matches){
  video.src=window.matchMedia('(orientation: portrait)').matches?video.dataset.tall:video.dataset.wide;
  video.preload='auto';
  let visible=true;
  const sync=()=>{
   const play=visible&&!document.hidden;
   if(play&&video.paused)video.play().catch(()=>{});
   else if(!play&&!video.paused)video.pause();
  };
  document.addEventListener('visibilitychange',sync);
  if('IntersectionObserver' in window)new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;sync();},{threshold:.05}).observe(hero);
  sync();
 }
 // ---- Sign-ups for the next hackathon ------------------------------------
 // "Notify me" and "Partner with us" post to their own sheet (signupEndpoint
 // in config.js). As with the applications, success is only shown once the
 // row is written; on failure the answers stay where they are.
 const signupLive=Boolean(config.signupEndpoint);
 const validEmail=value=>/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
 async function signup(type,fields,button,error){
  if(button.disabled)return false;                 // a double tap must not file twice
  const label=button.innerHTML;
  button.disabled=true;button.textContent='Sending…';error.textContent='';
  try{
   const result=await window.HACKATHON_SUBMIT(type,fields);
   if(!result||!result.ok)throw new Error((result&&result.error)||'save failed');
   return true;
  }catch(err){
   error.textContent=`That didn’t go through. Please try again, or email ${config.contactEmail}.`;
   return false;
  }finally{button.disabled=false;button.innerHTML=label;}
 }
 const previewNote=signupLive?'':'<p class="signup-preview">Preview only: nothing was sent or saved.</p>';

 const notifyForm=document.getElementById('notify-form');
 if(notifyForm){
  const email=document.getElementById('notify-email');
  const error=document.getElementById('notify-error');
  const done=document.getElementById('notify-success');
  notifyForm.addEventListener('submit',async event=>{
   event.preventDefault();
   const value=email.value.trim();
   if(!validEmail(value)||!email.checkValidity()){error.textContent='Enter a valid email address.';email.setAttribute('aria-describedby','notify-error');email.focus();return;}
   if(!await signup('notify',{'Email':value},notifyForm.querySelector('button[type=submit]'),error))return;
   notifyForm.hidden=true;done.hidden=false;
   done.innerHTML=`<strong>You’re on the list.</strong> We’ll email ${escape(value)} as soon as applications for the next hackathon open.${previewNote}`;
  });
 }

 const partner=document.getElementById('partner-dialog');
 if(partner){
  const form=document.getElementById('partner-form');
  const done=document.getElementById('partner-success');
  const error=document.getElementById('partner-error');
  const note=document.getElementById('partner-note');
  if(signupLive&&note)note.innerHTML=`We use your details only to reply to you. See our <a href="${config.privacyUrl}" target="_blank" rel="noopener noreferrer">privacy policy</a>.`;
  let opener=null;
  const close=()=>{partner.close();};
  partner.addEventListener('close',()=>{document.body.classList.remove('dialog-open');opener?.focus({preventScroll:true});});
  document.addEventListener('click',event=>{const button=event.target.closest('[data-partner-open]');if(!button)return;event.preventDefault();opener=button;partner.showModal();document.body.classList.add('dialog-open');document.getElementById(form.hidden?'partner-close':'partner-name').focus({preventScroll:true});});
  document.getElementById('partner-close').addEventListener('click',close);
  // A click on the backdrop lands on the dialog element itself.
  partner.addEventListener('click',event=>{if(event.target!==partner)return;const b=partner.getBoundingClientRect();if(event.clientX<b.left||event.clientX>b.right||event.clientY<b.top||event.clientY>b.bottom)close();});
  form.addEventListener('submit',async event=>{
   event.preventDefault();error.textContent='';
   const field=id=>document.getElementById(id);
   const fail=(message,el)=>{error.textContent=message;el.setAttribute('aria-describedby','partner-error');el.focus();};
   const name=field('partner-name'),email=field('partner-email'),org=field('partner-org'),message=field('partner-message');
   if(!name.value.trim())return fail('Tell us your name.',name);
   if(!validEmail(email.value.trim())||!email.checkValidity())return fail('Enter a valid email address.',email);
   if(!org.value.trim())return fail('Tell us which organisation you’re with.',org);
   if(!message.value.trim())return fail('Tell us briefly how you’d like to be involved.',message);
   const sent=await signup('partner',{'Name':name.value.trim(),'Email':email.value.trim(),'Organisation':org.value.trim(),'Message':message.value.trim()},form.querySelector('button[type=submit]'),error);
   if(!sent)return;
   form.hidden=true;done.hidden=false;
   done.innerHTML=`<div class="mentor-success-mark" aria-hidden="true">THANK YOU.</div><h3>Thanks, ${escape(name.value.trim())}.</h3><p>We’ll reply to <strong>${escape(email.value.trim())}</strong> soon.</p>${previewNote}<button type="button" class="button button-dark" id="partner-done">Close <span aria-hidden="true">${arrow}</span></button>`;
   document.getElementById('partner-done').addEventListener('click',close);
   partner.scrollTop=0;document.getElementById('partner-done').focus({preventScroll:true});
  });
 }
})();
