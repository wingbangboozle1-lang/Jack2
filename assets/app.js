/* Progressive enhancement only: filtering and search on the metrics tables.
   The site is fully readable with JavaScript disabled. No analytics, no network calls. */
(function () {
  document.body.classList.add('js');

  var q = document.getElementById('q');
  var fcat = document.getElementById('fcat');
  var count = document.getElementById('count');
  if (!q && !fcat) return;

  var sections = Array.prototype.slice.call(document.querySelectorAll('h2[id]'));
  var tables = Array.prototype.slice.call(document.querySelectorAll('.tablewrap'));

  function rowsOf(tbl) {
    return Array.prototype.slice.call(tbl.querySelectorAll('tbody tr'));
  }

  function apply() {
    var term = (q && q.value || '').trim().toLowerCase();
    var cat = (fcat && fcat.value || '').toLowerCase();
    var shown = 0;

    tables.forEach(function (tbl) {
      var section = tbl.previousElementSibling;
      // find the owning section heading (walk back)
      var head = null;
      var node = tbl.previousElementSibling;
      while (node && !head) {
        if (node.tagName === 'H2') head = node;
        node = node.previousElementSibling;
      }
      var headText = head ? head.textContent.toLowerCase() : '';
      var sectionMatch = !cat || headText === cat;

      var any = 0;
      rowsOf(tbl).forEach(function (tr) {
        var text = tr.textContent.toLowerCase();
        var ok = sectionMatch && (!term || text.indexOf(term) !== -1);
        tr.hidden = !ok;
        if (ok) any++;
      });
      shown += any;
      var wrap = tbl;
      wrap.style.display = any === 0 ? 'none' : '';
      if (head) head.style.display = any === 0 ? 'none' : '';
    });

    if (count) count.textContent = shown + ' row' + (shown === 1 ? '' : 's');
  }

  if (q) q.addEventListener('input', apply);
  if (fcat) fcat.addEventListener('change', apply);
  // Only auto-apply when the user has actually typed/selected.
  apply();
})();
