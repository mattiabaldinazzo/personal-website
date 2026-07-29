/* =========================================================
   Mattia Baldinazzo - main.js
   Vanilla JS, nessuna dipendenza. Tutto progressive enhancement.
   I testi (menu, libri) arrivano dagli attributi data-* del markup,
   quindi questo file resta identico in italiano e in inglese.
   ========================================================= */
(function () {
  'use strict';

  var doc = document;
  var header = doc.querySelector('[data-header]');
  var menuToggle = doc.querySelector('[data-menu-toggle]');

  /* ---- Reveal allo scroll (per primo: il contenuto non resta mai nascosto) ---- */
  var reveals = doc.querySelectorAll('.reveal');
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
  var inAttesa = false;
  function aggiornaHeader() {
    inAttesa = false;
    if (!header) { return; }
    header.classList.toggle('is-scrolled', window.scrollY > 8);
  }
  function onScroll() {
    if (inAttesa) { return; }
    inAttesa = true;
    window.requestAnimationFrame(aggiornaHeader);
  }
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  /* ---- Menu mobile ---- */
  function closeMenu() {
    if (!header) { return; }
    header.classList.remove('menu-open');
    if (menuToggle) {
      menuToggle.setAttribute('aria-expanded', 'false');
      menuToggle.setAttribute('aria-label', menuToggle.getAttribute('data-testo-apri') || '');
    }
  }
  function openMenu() {
    if (!header) { return; }
    header.classList.add('menu-open');
    if (menuToggle) {
      menuToggle.setAttribute('aria-expanded', 'true');
      menuToggle.setAttribute('aria-label', menuToggle.getAttribute('data-testo-chiudi') || '');
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

  /* ---- Filtro progetti e "Mostra tutti i progetti" ----
     Due condizioni indipendenti decidono se una scheda si vede: la categoria
     scelta e la soglia di quante schede mostrare. Le calcolo insieme a ogni
     cambiamento, cosi' filtro ed espansione non si pestano i piedi. */
  var filterBtns = doc.querySelectorAll('[data-filter]');
  var works = doc.querySelectorAll('[data-works] .work');
  var emptyMsg = doc.querySelector('[data-works-empty]');
  var worksToggle = doc.querySelector('[data-works-toggle]');
  var limite = worksToggle ? parseInt(worksToggle.getAttribute('data-limite'), 10) : 0;
  var categoria = 'tutti';
  var espanso = false;

  function aggiornaProgetti() {
    var visibili = [];
    works.forEach(function (w) {
      var match = (categoria === 'tutti' || w.getAttribute('data-category') === categoria);
      if (match) { visibili.push(w); }
      w.classList.toggle('is-hidden', !match);
    });
    if (worksToggle && limite > 0) {
      visibili.forEach(function (w, i) {
        w.classList.toggle('is-hidden', !espanso && i >= limite);
      });
      var serve = visibili.length > limite;
      worksToggle.parentNode.hidden = !serve;
      worksToggle.setAttribute('aria-expanded', String(espanso));
      worksToggle.textContent = espanso
        ? (worksToggle.getAttribute('data-testo-meno') || '')
        : (worksToggle.getAttribute('data-testo-tutti') || '');
    }
    if (emptyMsg) { emptyMsg.hidden = (visibili.length !== 0); }
  }

  filterBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      filterBtns.forEach(function (b) {
        b.classList.remove('is-active');
        b.setAttribute('aria-pressed', 'false');
      });
      btn.classList.add('is-active');
      btn.setAttribute('aria-pressed', 'true');
      categoria = btn.getAttribute('data-filter');
      aggiornaProgetti();
    });
  });

  if (worksToggle) {
    worksToggle.addEventListener('click', function () {
      espanso = !espanso;
      aggiornaProgetti();
    });
  }
  aggiornaProgetti();

  /* ---- "Mostra tutti" di libri e progressi ----
     Stesso comportamento per due sezioni diverse: gli elementi oltre la
     soglia nascono con la classe is-hidden e il bottone la toglie. */
  function collegaMostraTutti(selettoreBottone, selettoreNascosti) {
    var bottone = doc.querySelector(selettoreBottone);
    if (!bottone) { return; }
    var nascosti = doc.querySelectorAll(selettoreNascosti);
    bottone.addEventListener('click', function () {
      var aperto = bottone.getAttribute('aria-expanded') === 'true';
      nascosti.forEach(function (el) { el.classList.toggle('is-hidden', aperto); });
      bottone.setAttribute('aria-expanded', String(!aperto));
      bottone.textContent = aperto
        ? (bottone.getAttribute('data-testo-tutti') || '')
        : (bottone.getAttribute('data-testo-meno') || '');
    });
  }
  collegaMostraTutti('[data-books-toggle]', '[data-books] .book.is-hidden');
  collegaMostraTutti('[data-progress-toggle]', '[data-progress] .progress.is-hidden');

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
