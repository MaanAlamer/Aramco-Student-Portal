// main.js - small behavior for navbar and mobile toggle
document.addEventListener('DOMContentLoaded', function(){
  const nav = document.getElementById('topNav');
  const toggle = document.getElementById('navToggle');
  const mobile = document.getElementById('mobilePanel');

  // add scrolled class
  function onScroll(){
    if(window.scrollY > 24) nav.classList.add('scrolled');
    else nav.classList.remove('scrolled');
  }
  window.addEventListener('scroll', onScroll);
  onScroll();

  if(toggle && mobile){
    toggle.addEventListener('click', ()=>{
      const open = mobile.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      mobile.setAttribute('aria-hidden', open ? 'false' : 'true');
    });
  }

  // close mobile on link click
  mobile?.addEventListener('click', (e)=>{
    if(e.target.tagName === 'A'){
      mobile.classList.remove('open');
      toggle?.setAttribute('aria-expanded','false');
      mobile?.setAttribute('aria-hidden','true');
    }
  });
});
