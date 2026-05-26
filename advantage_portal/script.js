// script.js - site behavior: sticky navbar, mobile toggle, accordions, smooth scroll

document.addEventListener('DOMContentLoaded', function(){
  // Sticky navbar background change on scroll
  const navbar = document.querySelector('.navbar');
  if(navbar){
    const onScroll = ()=>{
      if(window.scrollY > 24) navbar.classList.add('scrolled');
      else navbar.classList.remove('scrolled');
    }
    window.addEventListener('scroll', onScroll);
    onScroll();
  }

  // Mobile menu toggle
  const hamburger = document.querySelector('.hamburger');
  const mobileNav = document.querySelector('.mobile-nav');
  if(hamburger && mobileNav){
    hamburger.addEventListener('click', ()=>{
      mobileNav.classList.toggle('open');
      const expanded = mobileNav.classList.contains('open');
      hamburger.setAttribute('aria-expanded', expanded);
    });
  }

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(a=>{
    a.addEventListener('click', function(e){
      const href = this.getAttribute('href');
      if(href.length>1){
        e.preventDefault();
        document.querySelector(href)?.scrollIntoView({behavior:'smooth'});
      }
    });
  });

  // Accordion behavior (FAQ & courses) - allow only one open at a time per group
  document.querySelectorAll('.accordion').forEach(group=>{
    group.addEventListener('click', (e)=>{
      const head = e.target.closest('.head');
      if(!head) return;
      const item = head.closest('.item');
      if(!item) return;
      const currentlyOpen = group.querySelector('.item.open');
      if(currentlyOpen && currentlyOpen!==item) currentlyOpen.classList.remove('open');
      item.classList.toggle('open');
    });
  });

  // Course expand buttons (alternate way if we use expand buttons)
  document.querySelectorAll('[data-expand]').forEach(btn=>{
    btn.addEventListener('click', ()=>{
      const target = document.querySelector(btn.dataset.expand);
      if(target) target.classList.toggle('open');
    });
  });
});
