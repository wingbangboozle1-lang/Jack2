/* Jack2 — tiny progressive enhancement. No dependencies. */
(function () {
  "use strict";

  // 1. Add a client-side row filter to any table longer than 12 rows.
  document.querySelectorAll(".table-wrap table").forEach(function (table) {
    var body = table.tBodies[0];
    if (!body || body.rows.length <= 12) return;

    var box = document.createElement("input");
    box.type = "search";
    box.placeholder = "Filter " + body.rows.length + " rows\u2026";
    box.setAttribute("aria-label", "Filter table rows");
    box.style.cssText =
      "width:100%;margin:0 0 8px;padding:9px 12px;border:1px solid #e2e6ec;border-radius:9px;" +
      "font:inherit;font-size:14px;background:#fff;color:#12161c;outline:none";

    var wrap = table.parentNode;
    wrap.parentNode.insertBefore(box, wrap);

    var count = document.createElement("p");
    count.className = "tbl-note";
    wrap.parentNode.insertBefore(count, wrap.nextSibling);

    function apply() {
      var q = box.value.trim().toLowerCase();
      var shown = 0;
      for (var i = 0; i < body.rows.length; i++) {
        var row = body.rows[i];
        var hit = !q || row.textContent.toLowerCase().indexOf(q) !== -1;
        row.style.display = hit ? "" : "none";
        if (hit) shown++;
      }
      count.textContent =
        q ? shown + " of " + body.rows.length + " rows match \u201c" + box.value.trim() + "\u201d"
          : body.rows.length + " rows \u00b7 each with a source link";
    }
    box.addEventListener("input", apply);
    apply();
  });

  // 2. Mark any external link that fails to declare rel=noopener.
  document.querySelectorAll('a[target="_blank"]').forEach(function (a) {
    if (!/noopener/.test(a.rel)) a.rel = "noopener";
  });
})();
