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
  var worksAzioni = doc.querySelector('[data-works-azioni]');
  var worksAltro = worksAzioni && worksAzioni.querySelector('[data-works-altro]');
  var worksMeno = worksAzioni && worksAzioni.querySelector('[data-works-meno]');
  var schermoLargo = window.matchMedia('(min-width: 920px)');
  var passoLavori = function () {
    if (!worksAzioni) { return 0; }
    var attr = schermoLargo.matches ? 'data-passo' : 'data-passo-mobile';
    return parseInt(worksAzioni.getAttribute(attr), 10) || 0;
  };
  var categoria = 'tutti';
  var mostrati = passoLavori();

  function aggiornaProgetti() {
    var visibili = [];
    works.forEach(function (w) {
      var match = (categoria === 'tutti' || w.getAttribute('data-category') === categoria);
      if (match) { visibili.push(w); }
      w.classList.toggle('is-hidden', !match);
    });
    var passo = passoLavori();
    if (worksAzioni && passo > 0) {
      mostrati = Math.max(passo, mostrati);
      visibili.forEach(function (w, i) {
        w.classList.toggle('is-hidden', i >= mostrati);
      });
      worksAzioni.hidden = visibili.length <= passo;
      worksAltro.hidden = mostrati >= visibili.length;
      worksMeno.hidden = mostrati <= passo;
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
      mostrati = passoLavori();      // cambiando categoria si riparte dalle prime schede
      aggiornaProgetti();
    });
  });

  if (worksAzioni) {
    worksAltro.addEventListener('click', function () {
      var prima = mostrati;
      mostrati += passoLavori();
      aggiornaProgetti();
      // il focus va sulla prima scheda nuova, o sul bottone che resta
      var nuove = [].filter.call(works, function (w) { return !w.classList.contains('is-hidden'); });
      var prossima = nuove[prima] && nuove[prima].querySelector('button, a[href]');
      if (prossima) { prossima.focus(); }
      else if (worksAltro.hidden) { worksMeno.focus(); }
    });
    worksMeno.addEventListener('click', function () {
      mostrati = passoLavori();
      aggiornaProgetti();
      var sezione = doc.getElementById('lavori');
      if (sezione && sezione.getBoundingClientRect().top < 0) {
        var ridotto = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        sezione.scrollIntoView({ block: 'start', behavior: ridotto ? 'auto' : 'smooth' });
      }
      worksAltro.focus({ preventScroll: true });
    });
    // cambiando larghezza cambia il passo: si riparte dalle prime schede
    var cambioSchermo = function () { mostrati = passoLavori(); aggiornaProgetti(); };
    if (schermoLargo.addEventListener) { schermoLargo.addEventListener('change', cambioSchermo); }
    else if (schermoLargo.addListener) { schermoLargo.addListener(cambioSchermo); }
  }
  aggiornaProgetti();

  /* ---- "Mostra tutti" dei progressi ----
     Gli elementi oltre la soglia nascono con la classe is-hidden e il
     bottone la toglie. */
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
  collegaMostraTutti('[data-progress-toggle]', '[data-progress] .progress.is-hidden');

  /* ---- Libreria: righe visibili, "Mostra altro" e "Mostra meno" ----
     Le righe dipendono dalla larghezza dello schermo, quindi si contano qui
     dopo l'impaginazione. Ogni elemento di una mensola occupa uno spazio alto
     quanto la riga: gli elementi con la stessa posizione verticale formano una
     riga. Senza JavaScript i bottoni restano nascosti e si vede tutta la
     libreria. "Mostra meno" compare dal primo clic e torna subito alle righe
     iniziali. */
  var libreria = doc.querySelector('[data-libreria]');
  var libreriaAzioni = doc.querySelector('[data-libreria-azioni]');
  if (libreria && libreriaAzioni) {
    var bottoneAltro = libreriaAzioni.querySelector('[data-libreria-altro]');
    var bottoneMeno = libreriaAzioni.querySelector('[data-libreria-meno]');
    var annuncio = doc.querySelector('[data-libreria-annuncio]');
    var mensole = libreria.querySelectorAll('.mensola');
    var righeIniziali = parseInt(libreria.getAttribute('data-righe'), 10) || 3;
    var righePerClic = parseInt(libreria.getAttribute('data-righe-clic'), 10) || 3;
    var righeMostrate = righeIniziali;
    var larghezzaNota = libreria.clientWidth;
    var attesaResize = 0;

    var contaRighe = function () {
      var righe = [];
      mensole.forEach(function (mensola) {
        mensola.hidden = false;
        Array.prototype.forEach.call(mensola.children, function (el) { el.hidden = false; });
      });
      mensole.forEach(function (mensola) {
        var cima = null;
        Array.prototype.forEach.call(mensola.children, function (el) {
          if (el.offsetTop !== cima) {
            righe.push([]);
            cima = el.offsetTop;
          }
          righe[righe.length - 1].push(el);
        });
      });
      return righe;
    };

    var aggiornaLibreria = function () {
      var righe = contaRighe();
      var totale = righe.length;
      righeMostrate = Math.max(righeIniziali, Math.min(righeMostrate, totale));
      righe.forEach(function (riga, i) {
        if (i >= righeMostrate) {
          riga.forEach(function (el) { el.hidden = true; });
        }
      });
      mensole.forEach(function (mensola) {
        mensola.hidden = !Array.prototype.some.call(mensola.children, function (el) { return !el.hidden; });
      });
      libreriaAzioni.hidden = totale <= righeIniziali;
      bottoneAltro.hidden = righeMostrate >= totale;
      bottoneMeno.hidden = righeMostrate <= righeIniziali;
      return righe;
    };

    var annunciaLibri = function (quanti) {
      if (!annuncio) { return; }
      // svuotare e riscrivere fa ripetere l'annuncio anche se il testo e' uguale
      annuncio.textContent = '';
      window.setTimeout(function () {
        annuncio.textContent = (annuncio.getAttribute('data-testo') || '').replace('%s', quanti);
      }, 60);
    };

    bottoneAltro.addEventListener('click', function () {
      var prima = righeMostrate;
      righeMostrate += righePerClic;
      var righe = aggiornaLibreria();
      var libri = 0;
      var primoComando = null;
      righe.slice(prima, righeMostrate).forEach(function (riga) {
        riga.forEach(function (el) {
          libri += el.classList.contains('libro') ? 1 : el.querySelectorAll('.libro').length;
          if (!primoComando) { primoComando = el.querySelector('button, a[href]'); }
        });
      });
      // il focus va sul primo libro nuovo; se il bottone sparisce passa a "Mostra meno"
      if (primoComando) { primoComando.focus(); }
      else if (bottoneAltro.hidden) { bottoneMeno.focus(); }
      annunciaLibri(libri);
    });

    bottoneMeno.addEventListener('click', function () {
      righeMostrate = righeIniziali;
      aggiornaLibreria();
      // la pagina si e' accorciata sopra: riporta in vista l'inizio della libreria
      if (libreria.getBoundingClientRect().top < 0) {
        var ridotto = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        libreria.scrollIntoView({ block: 'start', behavior: ridotto ? 'auto' : 'smooth' });
      }
      bottoneAltro.focus({ preventScroll: true });
    });

    window.addEventListener('resize', function () {
      if (attesaResize) { return; }
      attesaResize = window.requestAnimationFrame(function () {
        attesaResize = 0;
        // Safari su iPhone genera resize anche quando la barra degli indirizzi
        // si ritira: si ricalcola solo se cambia la larghezza
        if (libreria.clientWidth === larghezzaNota) { return; }
        larghezzaNota = libreria.clientWidth;
        aggiornaLibreria();
      });
    });

    aggiornaLibreria();
  }

  /* ---- Modali (generate dal build per ogni progetto con dettaglio) ---- */
  var lastFocused = null;
  function focusables(modal) {
    return modal.querySelectorAll('a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])');
  }
  /* Le schede dei libri hanno data-hash: aprendole l'indirizzo diventa
     #libro-<nome>, cosi' il tasto indietro le chiude e il link si puo'
     condividere. daIndirizzo e' vero quando apertura o chiusura arrivano
     dall'indirizzo stesso, per non scrivere la cronologia due volte. */
  function openModal(modal, daIndirizzo) {
    lastFocused = doc.activeElement;
    modal.hidden = false;
    doc.body.classList.add('modal-open');
    var hash = modal.getAttribute('data-hash');
    if (hash && !daIndirizzo && location.hash !== '#' + hash) {
      history.pushState({ scheda: hash }, '', '#' + hash);
    }
    var closeBtn = modal.querySelector('.modal-close');
    var f = focusables(modal);
    (closeBtn || f[0] || modal).focus();
  }
  function closeModal(modal, daIndirizzo) {
    var hash = modal.getAttribute('data-hash');
    if (hash && !daIndirizzo && location.hash === '#' + hash) {
      if (history.state && history.state.scheda === hash) {
        // la scheda ha aggiunto una voce alla cronologia: tornare indietro la
        // toglie, e l'evento popstate chiude la scheda
        history.back();
        return;
      }
      // aperta da un link diretto: si toglie l'indirizzo senza cambiare pagina
      history.replaceState(null, '', location.pathname + location.search);
    }
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

  /* ---- Deep link: #libro-<nome> apre la scheda del libro ---- */
  function schedaDaIndirizzo() {
    if (location.hash.indexOf('#libro-') !== 0) { return null; }
    return doc.getElementById('modal-' + location.hash.slice(1));
  }
  window.addEventListener('popstate', function () {
    var aperta = doc.querySelector('.modal:not([hidden])');
    var hashAperta = aperta ? aperta.getAttribute('data-hash') : null;
    if (hashAperta && location.hash !== '#' + hashAperta) { closeModal(aperta, true); }
    var daAprire = schedaDaIndirizzo();
    if (daAprire && daAprire.hidden) { openModal(daAprire, true); }
  });
  var schedaIniziale = schedaDaIndirizzo();
  if (schedaIniziale) {
    // dietro la scheda porta la libreria: chiudendola ci si ritrova li'
    var libreriaDietro = doc.querySelector('[data-libreria]');
    if (libreriaDietro) { libreriaDietro.scrollIntoView({ block: 'start', behavior: 'instant' }); }
    openModal(schedaIniziale, true);
  }

  /* ---- Deep link: #progetto-<slug> apre la modale corrispondente ---- */
  if (location.hash.indexOf('#progetto-') === 0) {
    var deepModal = doc.getElementById('modal-' + location.hash.slice(10));
    if (deepModal) { openModal(deepModal); }
  }
})();
