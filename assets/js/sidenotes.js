/* Sidenotes — Newy Sunsets
 *
 * Turns kramdown footnotes ([^1] in Markdown) into sidenotes placed right
 * after their reference. CSS (_sass/layout/_sidenotes.scss) floats them into
 * the notes column on wide screens; on narrower screens they stay hidden and
 * tapping the reference number opens the note inline. Posts need no changes,
 * and without JavaScript the footnotes remain at the end of the post.
 */
(function () {
  var content = document.querySelector('.page__content');
  if (!content) return;

  var refs = content.querySelectorAll('a.footnote[href^="#fn"]');
  if (!refs.length) return;

  // Keep in step with $bp-three in _sass/_themes.scss
  var wide = window.matchMedia('(min-width: 1230px)');

  Array.prototype.forEach.call(refs, function (ref) {
    var id = decodeURIComponent(ref.getAttribute('href').slice(1));
    var item = document.getElementById(id);
    if (!item) return;

    var note = document.createElement('span');
    note.className = 'sidenote';
    note.id = 'sn-' + id.replace(/[^\w-]/g, '-');
    note.setAttribute('role', 'note');

    // The note's own number links back to its place in the text
    var num = document.createElement('a');
    num.className = 'sidenote__num';
    num.href = '#' + (ref.closest('sup') || ref).id;
    num.textContent = ref.textContent;
    num.setAttribute('aria-label', 'Back to reference ' + ref.textContent + ' in the text');
    note.appendChild(num);

    // Copy the footnote's paragraphs (minus the ↩ back-links) into the note
    var paras = item.querySelectorAll('p');
    var parts = paras.length ? Array.prototype.slice.call(paras) : [item];
    parts.forEach(function (p, i) {
      var clone = p.cloneNode(true);
      Array.prototype.forEach.call(clone.querySelectorAll('.reversefootnote'), function (b) {
        b.parentNode.removeChild(b);
      });
      if (i > 0) note.appendChild(document.createElement('br'));
      while (clone.firstChild) note.appendChild(clone.firstChild);
    });

    // Insert after any punctuation hugging the reference ("planes¹." →
    // after the full stop), so an opened note never strands a full stop or
    // comma at the start of the next line.
    var at = ref.closest('sup') || ref;
    var next = at.nextSibling;
    if (next && next.nodeType === 3) {
      var m = next.nodeValue.match(/^[.,;:!?)\]\u201D\u2019"']+/);
      if (m) {
        next.splitText(m[0].length);
        at = next;
      }
    }
    at.parentNode.insertBefore(note, at.nextSibling);

    num.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopImmediatePropagation();   // keep the template's smooth-scroll out of it
      if (!wide.matches) {
        note.classList.remove('is-open');
        ref.setAttribute('aria-expanded', 'false');
      }
      backTo(ref);
    });

    ref.setAttribute('aria-controls', note.id);
    ref.setAttribute('aria-expanded', 'false');
    ref.addEventListener('click', function (e) {
      // The template's smooth-scroll (main.js) would otherwise scroll to the
      // original, now hidden, footnote, which sits at the top of the page.
      e.preventDefault();
      e.stopImmediatePropagation();
      if (wide.matches) {
        // Note is already beside the text: briefly darken it to point the eye
        note.classList.add('is-flash');
        setTimeout(function () { note.classList.remove('is-flash'); }, 50);
        return;
      }
      var open = note.classList.toggle('is-open');
      ref.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });

  content.classList.add('has-sidenotes');

  // Bring a reference into view (if it isn't already) and highlight it
  function backTo(ref) {
    var sup = ref.closest('sup') || ref;
    var r = sup.getBoundingClientRect();
    var top = 100;                                   // clear of the masthead
    if (r.top < top || r.bottom > window.innerHeight - 40) {
      var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      window.scrollTo({ top: window.scrollY + r.top - window.innerHeight * 0.35,
                        behavior: reduce ? 'auto' : 'smooth' });
    }
    sup.classList.remove('is-target');
    void sup.offsetWidth;                            // restart the highlight
    sup.classList.add('is-target');
    setTimeout(function () { sup.classList.remove('is-target'); }, 1600);
    ref.focus({ preventScroll: true });
  }
})();
