/* =========================================================
   Mattia Baldinazzo - main.js
   Vanilla JS, nessuna dipendenza. Tutto progressive enhancement.
   ========================================================= */
(function () {
  'use strict';

  var doc = document;
  var header = doc.querySelector('[data-header]');
  var menuToggle = doc.querySelector('[data-menu-toggle]');

  /* ---- Reveal allo scroll (per primo: il contenuto non resta mai nascosto) ---- */
  var reveals = doc.querySelectorAll('.reveal');
  var heroReveals = doc.querySelectorAll('.hero .reveal');
  for (var i = 0; i < heroReveals.length; i++) {
    heroReveals[i].style.setProperty('--d', (i * 0.07).toFixed(2) + 's');
  }
  if (!('IntersectionObserver' in window)) {
    reveals.forEach(function (el) { el.classList.add('is-visible'); });
  } else {
    var io = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          obs.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    reveals.forEach(function (el) { io.observe(el); });
  }

  /* ---- Bordo header allo scroll ---- */
  function onScroll() {
    if (!header) { return; }
    header.classList.toggle('is-scrolled', window.scrollY > 8);
  }
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  /* ---- Menu mobile ---- */
  function closeMenu() {
    if (!header) { return; }
    header.classList.remove('menu-open');
    if (menuToggle) {
      menuToggle.setAttribute('aria-expanded', 'false');
      menuToggle.setAttribute('aria-label', 'Apri il menu');
    }
  }
  function openMenu() {
    if (!header) { return; }
    header.classList.add('menu-open');
    if (menuToggle) {
      menuToggle.setAttribute('aria-expanded', 'true');
      menuToggle.setAttribute('aria-label', 'Chiudi il menu');
    }
  }
  if (menuToggle && header) {
    menuToggle.addEventListener('click', function () {
      if (header.classList.contains('menu-open')) { closeMenu(); }
      else { openMenu(); }
    });
    doc.querySelectorAll('#mobile-menu a').forEach(function (a) {
      a.addEventListener('click', closeMenu);
    });
    doc.addEventListener('click', function (e) {
      if (!header.classList.contains('menu-open')) { return; }
      if (header.contains(e.target)) { return; }
      closeMenu();
    });
  }

  /* ---- Filtro progetti ---- */
  var filterBtns = doc.querySelectorAll('[data-filter]');
  var works = doc.querySelectorAll('[data-works] .work');
  var emptyMsg = doc.querySelector('[data-works-empty]');
  function applyFilter(cat) {
    var visible = 0;
    works.forEach(function (w) {
      var show = (cat === 'tutti' || w.getAttribute('data-category') === cat);
      w.classList.toggle('is-hidden', !show);
      if (show) { visible++; }
    });
    if (emptyMsg) { emptyMsg.hidden = (visible !== 0); }
  }
  filterBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      filterBtns.forEach(function (b) {
        b.classList.remove('is-active');
        b.setAttribute('aria-pressed', 'false');
      });
      btn.classList.add('is-active');
      btn.setAttribute('aria-pressed', 'true');
      applyFilter(btn.getAttribute('data-filter'));
    });
  });

  /* ---- Mostra tutti i libri ---- */
  var booksToggle = doc.querySelector('[data-books-toggle]');
  if (booksToggle) {
    var hiddenBooks = doc.querySelectorAll('[data-books] .book.is-hidden');
    booksToggle.addEventListener('click', function () {
      var expanded = booksToggle.getAttribute('aria-expanded') === 'true';
      hiddenBooks.forEach(function (b) { b.classList.toggle('is-hidden', expanded); });
      booksToggle.setAttribute('aria-expanded', String(!expanded));
      booksToggle.textContent = expanded ? 'Mostra tutti i libri' : 'Mostra meno';
    });
  }

  /* ---- Modali (generate dal build per ogni progetto con dettaglio) ---- */
  var lastFocused = null;
  function focusables(modal) {
    return modal.querySelectorAll('a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])');
  }
  function openModal(modal) {
    lastFocused = doc.activeElement;
    modal.hidden = false;
    doc.body.classList.add('modal-open');
    var closeBtn = modal.querySelector('.modal-close');
    var f = focusables(modal);
    (closeBtn || f[0] || modal).focus();
  }
  function closeModal(modal) {
    modal.hidden = true;
    doc.body.classList.remove('modal-open');
    if (lastFocused && typeof lastFocused.focus === 'function') { lastFocused.focus(); }
    lastFocused = null;
  }
  doc.querySelectorAll('[data-modal]').forEach(function (trigger) {
    trigger.addEventListener('click', function () {
      var modal = doc.getElementById('modal-' + trigger.getAttribute('data-modal'));
      if (modal) { openModal(modal); }
    });
  });
  doc.querySelectorAll('.modal [data-close]').forEach(function (el) {
    el.addEventListener('click', function () {
      var modal = el.closest('.modal');
      if (modal) { closeModal(modal); }
    });
  });
  doc.addEventListener('keydown', function (e) {
    var openEl = doc.querySelector('.modal:not([hidden])');
    if (e.key === 'Escape') {
      if (openEl) { closeModal(openEl); return; }
      if (header && header.classList.contains('menu-open')) {
        closeMenu();
        if (menuToggle) { menuToggle.focus(); }
      }
      return;
    }
    if (e.key === 'Tab' && openEl) {
      var f = focusables(openEl);
      if (!f.length) { return; }
      var first = f[0];
      var last = f[f.length - 1];
      if (e.shiftKey && doc.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && doc.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });

  /* ---- Deep link: #progetto-<slug> apre la modale corrispondente ---- */
  if (location.hash.indexOf('#progetto-') === 0) {
    var deepModal = doc.getElementById('modal-' + location.hash.slice(10));
    if (deepModal) { openModal(deepModal); }
  }
})();
