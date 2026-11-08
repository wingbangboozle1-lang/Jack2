/* Progressive enhancement only: the site is fully readable with JavaScript disabled. */
(function () {
  "use strict";
  var inputs = document.querySelectorAll(".filter input[type=search]");
  Array.prototype.forEach.call(inputs, function (input) {
    var wrap = input.closest(".filter");
    var table = wrap && wrap.nextElementSibling && wrap.nextElementSibling.querySelector("table");
    if (!table) return;
    var count = wrap.querySelector(".count");
    var rows = table.querySelectorAll("tbody tr");
    input.addEventListener("input", function () {
      var q = input.value.trim().toLowerCase();
      var shown = 0;
      Array.prototype.forEach.call(rows, function (tr) {
        var hit = !q || tr.textContent.toLowerCase().indexOf(q) !== -1;
        tr.style.display = hit ? "" : "none";
        if (hit) shown++;
      });
      if (count) count.textContent = shown + " of " + rows.length + " rows";
    });
  });

  var riskSearch = document.getElementById("risk-search");
  var riskType = document.getElementById("risk-type");
  var riskTable = document.getElementById("risk-table");
  if (riskSearch && riskTable) {
    var rows = riskTable.querySelectorAll("tbody tr");
    var apply = function () {
      var q = (riskSearch.value || "").toLowerCase();
      var t = riskType ? riskType.value : "";
      Array.prototype.forEach.call(rows, function (tr) {
        var ok = (!q || tr.textContent.toLowerCase().indexOf(q) !== -1) &&
                 (!t || tr.getAttribute("data-type") === t);
        tr.style.display = ok ? "" : "none";
      });
    };
    riskSearch.addEventListener("input", apply);
    if (riskType) riskType.addEventListener("change", apply);
  }

  /* Click a table header to sort — useful on the long registers. */
  Array.prototype.forEach.call(document.querySelectorAll("table[data-filterable], #risk-table"), function (table) {
    var ths = table.querySelectorAll("thead th");
    Array.prototype.forEach.call(ths, function (th, i) {
      th.style.cursor = "pointer";
      th.title = "Sort by this column";
      th.addEventListener("click", function () {
        var body = table.tBodies[0];
        var rows = Array.prototype.slice.call(body.rows);
        var asc = th.getAttribute("data-asc") !== "true";
        th.setAttribute("data-asc", asc ? "true" : "false");
        rows.sort(function (a, b) {
          var x = a.cells[i] ? a.cells[i].textContent.trim() : "";
          var y = b.cells[i] ? b.cells[i].textContent.trim() : "";
          var nx = parseFloat(x.replace(/[^0-9.\-]/g, ""));
          var ny = parseFloat(y.replace(/[^0-9.\-]/g, ""));
          if (!isNaN(nx) && !isNaN(ny) && /[0-9]/.test(x) && /[0-9]/.test(y)) {
            return asc ? nx - ny : ny - nx;
          }
          return asc ? x.localeCompare(y) : y.localeCompare(x);
        });
        rows.forEach(function (r) { body.appendChild(r); });
      });
    });
  });
})();
