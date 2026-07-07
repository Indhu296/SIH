/**
 * Digital Farm Management Portal
 * Main JavaScript — Animations, UI Interactions & Utilities
 */

'use strict';

/* ── Auto-dismiss Flash Messages ────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', function () {

  // Auto close flash alerts after 5 seconds
  const alerts = document.querySelectorAll('.alert.alert-dismissible');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });

  /* ── Scroll Reveal Animation ──────────────────────────────────────────────── */
  const observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('fade-in');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.feature-card, .stat-card, .farm-card').forEach(function (el) {
    observer.observe(el);
  });

  /* ── Active Navbar Indicator ──────────────────────────────────────────────── */
  const currentPath = window.location.pathname;
  document.querySelectorAll('.navbar-farm .nav-link').forEach(function (link) {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
  });

  /* ── Confirm Delete Forms ─────────────────────────────────────────────────── */
  document.querySelectorAll('form[data-confirm]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      if (!confirm(form.dataset.confirm || 'Are you sure?')) {
        e.preventDefault();
      }
    });
  });

  /* ── Table Row Highlight on Click ────────────────────────────────────────── */
  document.querySelectorAll('.farm-table tbody tr').forEach(function (row) {
    row.style.cursor = 'pointer';
    row.addEventListener('click', function (e) {
      // Only highlight if not clicking action buttons
      if (!e.target.closest('button') && !e.target.closest('a')) {
        document.querySelectorAll('.farm-table tbody tr').forEach(r => r.classList.remove('table-active'));
        row.classList.add('table-active');
      }
    });
  });

  /* ── Smooth Scroll for Anchor Links ──────────────────────────────────────── */
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  /* ── Number Counters (Dashboard Stats) ───────────────────────────────────── */
  function animateCounter(el, target, duration) {
    let start = 0;
    const step = target / (duration / 16);
    const timer = setInterval(function () {
      start += step;
      if (start >= target) {
        start = target;
        clearInterval(timer);
      }
      el.textContent = Math.round(start);
    }, 16);
  }

  const counterObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        const el = entry.target;
        const target = parseInt(el.textContent, 10);
        if (!isNaN(target)) {
          el.textContent = '0';
          animateCounter(el, target, 800);
        }
        counterObserver.unobserve(el);
      }
    });
  }, { threshold: 0.5 });

  document.querySelectorAll('.stat-number').forEach(function (el) {
    counterObserver.observe(el);
  });

  /* ── Tooltip Initialisation (Bootstrap) ──────────────────────────────────── */
  const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltips.forEach(function (el) {
    new bootstrap.Tooltip(el);
  });

  /* ── Back to Top Button ───────────────────────────────────────────────────── */
  const backBtn = document.createElement('button');
  backBtn.innerHTML = '<i class="bi bi-arrow-up"></i>';
  backBtn.id = 'backToTop';
  backBtn.title = 'Back to top';
  Object.assign(backBtn.style, {
    position:   'fixed',
    bottom:     '1.5rem',
    right:      '1.5rem',
    width:      '44px',
    height:     '44px',
    background: 'var(--green-primary)',
    color:      '#fff',
    border:     'none',
    borderRadius: '50%',
    cursor:     'pointer',
    display:    'none',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize:   '1.1rem',
    boxShadow:  'var(--shadow-md)',
    zIndex:     '9999',
    transition: 'var(--transition)'
  });

  document.body.appendChild(backBtn);

  window.addEventListener('scroll', function () {
    if (window.scrollY > 300) {
      backBtn.style.display = 'flex';
    } else {
      backBtn.style.display = 'none';
    }
  });

  backBtn.addEventListener('click', function () {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  backBtn.addEventListener('mouseenter', function () {
    this.style.background = 'var(--green-dark)';
    this.style.transform  = 'scale(1.1)';
  });

  backBtn.addEventListener('mouseleave', function () {
    this.style.background = 'var(--green-primary)';
    this.style.transform  = 'scale(1)';
  });

}); // end DOMContentLoaded
