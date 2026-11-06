/* Jack2 dashboard — minimal, dependency-free interactions */
(function () {
  "use strict";

  // Mobile sidebar toggle
  var burger = document.getElementById("burger");
  var sidebar = document.getElementById("sidebar");
  var overlay = document.getElementById("overlay");
  function closeNav() {
    if (sidebar) sidebar.classList.remove("open");
    if (overlay) overlay.classList.remove("show");
  }
  if (burger && sidebar && overlay) {
    burger.addEventListener("click", function () {
      sidebar.classList.toggle("open");
      overlay.classList.toggle("show");
    });
    overlay.addEventListener("click", closeNav);
  }

  // Mark current page in nav (fallback if not hard-coded)
  var path = (location.pathname.split("/").pop() || "index.html").toLowerCase();
  document.querySelectorAll(".nav a[href]").forEach(function (a) {
    var href = (a.getAttribute("href") || "").toLowerCase();
    if (href === path) a.classList.add("active");
  });

  // Client-side table filter: <input data-filter-target="#tableId">
  document.querySelectorAll("input[data-filter-target]").forEach(function (input) {
    var table = document.querySelector(input.getAttribute("data-filter-target"));
    if (!table) return;
    input.addEventListener("input", function () {
      var q = input.value.trim().toLowerCase();
      table.querySelectorAll("tbody tr").forEach(function (row) {
        row.style.display = !q || row.textContent.toLowerCase().indexOf(q) !== -1 ? "" : "none";
      });
    });
  });

  // Footer year
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
