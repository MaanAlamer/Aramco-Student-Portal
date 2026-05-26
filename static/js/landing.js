// ===============================
// Advantage Academy Landing JS
// File: static/js/landing.js
// ===============================

// Form Submission – استشارة مجانية
const consultationForm = document.getElementById('consultationForm');
if (consultationForm) {
    consultationForm.addEventListener('submit', function (e) {
        e.preventDefault();
        alert('تم تقديم طلب الاستشارة بنجاح! سنتواصل معك قريبًا 🌟');
        this.reset();
    });
}

// Form Submission – تواصل معنا
const contactForm = document.getElementById('contactForm');
if (contactForm) {
    contactForm.addEventListener('submit', function (e) {
        e.preventDefault();
        alert('تم إرسال رسالتك بنجاح! سنرد عليك في أقرب وقت ممكن ✅');
        this.reset();
    });
}

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;

        const targetElement = document.querySelector(targetId);
        if (!targetElement) return;

        e.preventDefault();
        window.scrollTo({
            top: targetElement.offsetTop - 90,
            behavior: 'smooth'
        });
    });
});

// ===============================
// Advantage Academy Landing JS
// File: static/js/landing.js
// ===============================

// Form Submission – استشارة مجانية
const consultationForm = document.getElementById('consultationForm');
if (consultationForm) {
    consultationForm.addEventListener('submit', function (e) {
        e.preventDefault();
        alert('تم تقديم طلب الاستشارة بنجاح! سنتواصل معك قريبًا 🌟');
        this.reset();
    });
}

// Form Submission – تواصل معنا
const contactForm = document.getElementById('contactForm');
if (contactForm) {
    contactForm.addEventListener('submit', function (e) {
        e.preventDefault();
        alert('تم إرسال رسالتك بنجاح! سنرد عليك في أقرب وقت ممكن ✅');
        this.reset();
    });
}

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;

        const targetElement = document.querySelector(targetId);
        if (!targetElement) return;

        e.preventDefault();
        window.scrollTo({
            top: targetElement.offsetTop - 90,
            behavior: 'smooth'
        });
    });
});
