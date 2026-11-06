/* PARCEL-01 — tiny, dependency-free progressive enhancement.
   1) mobile nav toggle  2) table filter for long data tables  3) copy link on heading click */
(function () {
  "use strict";

  // ---- mobile navigation
  var btn = document.querySelector(".menu-btn");
  var nav = document.getElementById("nav");
  if (btn && nav) {
    btn.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    nav.addEventListener("click", function (e) {
      if (e.target.tagName === "A") {
        nav.classList.remove("open");
        btn.setAttribute("aria-expanded", "false");
      }
    });
  }

  // ---- add a filter box above any table with more than 12 rows
  document.querySelectorAll("section.panel").forEach(function (panel) {
    var table = panel.querySelector("table.data");
    if (!table) return;
    var rows = table.querySelectorAll("tbody tr");
    if (rows.length < 12) return;

    var wrap = document.createElement("div");
    wrap.className = "filter";
    var input = document.createElement("input");
    input.type = "search";
    input.placeholder = "Filter these " + rows.length + " rows…";
    input.setAttribute("aria-label", "Filter table rows");
    var status = document.createElement("span");
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    wrap.appendChild(input);
    wrap.appendChild(status);

    var target = panel.querySelector(".tw") || table;
    target.parentNode.insertBefore(wrap, target);

    function apply() {
      var q = input.value.trim().toLowerCase();
      var shown = 0;
      rows.forEach(function (tr) {
        var hit = !q || tr.textContent.toLowerCase().indexOf(q) !== -1;
        tr.style.display = hit ? "" : "none";
        if (hit) shown++;
      });
      // hide topic headings whose whole group is filtered out
      panel.querySelectorAll("h3.grp").forEach(function (h) {
        var el = h.nextElementSibling;
        var any = false;
        while (el && el.tagName === "DIV") {
          if (el.style.display !== "none" && el.querySelector("tbody tr:not([style*='display: none'])")) any = true;
          el = el.nextElementSibling;
          if (el && el.tagName === "H3") break;
        }
        h.style.display = (q && !any) ? "none" : "";
      });
      status.textContent = q ? shown + " of " + rows.length + " shown" : "";
    }
    input.addEventListener("input", apply);
  });

  // ---- make section headings linkable
  document.querySelectorAll(".prose h2").forEach(function (h) {
    var text = h.textContent.trim();
    if (!text) return;
    var id = text.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
    if (!id) return;
    h.id = id;
    var a = document.createElement("a");
    a.href = "#" + id;
    a.className = "anchor";
    a.setAttribute("aria-label", "Link to this section");
    a.textContent = "#";
    a.style.cssText = "margin-left:8px;opacity:.35;font-weight:400;text-decoration:none;font-size:.8em";
    h.appendChild(a);
  });
})();
