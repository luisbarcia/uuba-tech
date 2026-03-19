/* ============================================
   UUBA Tech — Main JS
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {
  initNavScroll();
  initRevealAnimations();
  initParallax();
  initCounters();
  initSmoothScroll();
  initLogoAnimation();
});

/* --- Nav scroll effect --- */
function initNavScroll() {
  const nav = document.querySelector('.nav');
  if (!nav) return;

  const onScroll = () => {
    nav.classList.toggle('scrolled', window.scrollY > 80);
  };

  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
}

/* --- Reveal on scroll (Intersection Observer) --- */
function initRevealAnimations() {
  const reveals = document.querySelectorAll('.reveal, .reveal-left, .reveal-right');
  if (!reveals.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.15,
    rootMargin: '0px 0px -60px 0px'
  });

  reveals.forEach(el => observer.observe(el));
}

/* --- Parallax on scroll --- */
function initParallax() {
  const elements = document.querySelectorAll('.parallax-element');
  if (!elements.length) return;

  let ticking = false;

  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(() => {
        const scrollY = window.scrollY;
        elements.forEach(el => {
          const speed = parseFloat(el.dataset.speed) || 0.3;
          const rect = el.getBoundingClientRect();
          const offset = (rect.top + scrollY) - scrollY;
          el.style.transform = `translateY(${offset * speed * -0.1}px)`;
        });
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });
}

/* --- Animated counters --- */
function initCounters() {
  const counters = document.querySelectorAll('[data-counter]');
  if (!counters.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });

  counters.forEach(el => observer.observe(el));
}

function animateCounter(el) {
  const target = parseInt(el.dataset.counter, 10);
  const duration = 2000;
  const start = performance.now();

  function update(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 4);
    const current = Math.floor(eased * target);

    el.textContent = current;

    if (progress < 1) {
      requestAnimationFrame(update);
    } else {
      el.textContent = target;
    }
  }

  requestAnimationFrame(update);
}

/* --- Smooth scroll for anchor links --- */
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', (e) => {
      e.preventDefault();
      const target = document.querySelector(anchor.getAttribute('href'));
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });
}

/* --- Logo SVG draw animation --- */
function initLogoAnimation() {
  const logoPaths = document.querySelectorAll('.hero-logo path');
  if (!logoPaths.length) return;

  logoPaths.forEach(path => {
    const length = path.getTotalLength ? path.getTotalLength() : 1000;
    path.style.strokeDasharray = length;
    path.style.strokeDashoffset = length;
    path.style.fill = 'transparent';
    path.style.stroke = '#F4F4F4';
    path.style.strokeWidth = '1';
    path.style.transition = 'none';

    requestAnimationFrame(() => {
      path.style.transition = 'stroke-dashoffset 2.5s cubic-bezier(0.16, 1, 0.3, 1), fill 1s ease 1.5s';
      path.style.strokeDashoffset = '0';
      path.style.fill = '#F4F4F4';
    });
  });
}
