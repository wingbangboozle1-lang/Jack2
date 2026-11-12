(function () {
  "use strict";

  // 1. Generic Table Filter & Search
  function initTableFilters() {
    document.querySelectorAll("[data-filter-table]").forEach(function (ctrlBar) {
      var tableId = ctrlBar.getAttribute("data-filter-table");
      var table = document.getElementById(tableId);
      if (!table) return;
      var searchInput = ctrlBar.querySelector("[data-search]");
      var selectInput = ctrlBar.querySelector("[data-select]");
      var buttons = ctrlBar.querySelectorAll("[data-filter-btn]");
      var activeTag = "all";

      function apply() {
        var q = searchInput ? searchInput.value.trim().toLowerCase() : "";
        var sel = selectInput ? selectInput.value : "all";
        var rows = table.querySelectorAll("tbody tr");
        var visible = 0;
        rows.forEach(function (row) {
          var text = row.textContent.toLowerCase();
          var tag = row.getAttribute("data-tag") || "";
          var cat = row.getAttribute("data-cat") || "";
          var okQ = !q || text.indexOf(q) !== -1;
          var okBtn = activeTag === "all" || tag === activeTag;
          var okSel = sel === "all" || cat === sel || tag === sel;
          var show = okQ && okBtn && okSel;
          row.style.display = show ? "" : "none";
          if (show) visible += 1;
        });
        var counter = ctrlBar.querySelector("[data-count]");
        if (counter) counter.textContent = visible + " shown";
      }

      if (searchInput) searchInput.addEventListener("input", apply);
      if (selectInput) selectInput.addEventListener("change", apply);
      buttons.forEach(function (btn) {
        btn.addEventListener("click", function () {
          buttons.forEach(function (b) { b.classList.remove("active"); });
          btn.classList.add("active");
          activeTag = btn.getAttribute("data-filter-btn");
          apply();
        });
      });
      apply();
    });
  }

  // 2. Client-Side Confidential Owner Contract Calculator (projections.html & index drawer)
  function pvGrowingAnnuity(pmt1, growth, disc, n) {
    var pv = 0;
    for (var t = 1; t <= n; t++) {
      pv += (pmt1 * Math.pow(1 + growth, t - 1)) / Math.pow(1 + disc, t);
    }
    return pv;
  }

  function fmtUSD(x) {
    if (!isFinite(x)) return "-";
    return "$" + Math.round(x).toLocaleString("en-US");
  }

  function initCalculator() {
    var root = document.getElementById("owner-calc");
    if (!root) return;

    function recalc() {
      var noi = parseFloat(document.getElementById("calc-noi").value) || 250000;
      var cap = (parseFloat(document.getElementById("calc-cap").value) || 6.25) / 100.0;
      var yrs = parseInt(document.getElementById("calc-yrs").value, 10) || 6;
      var dttMode = document.getElementById("calc-ula").value;
      var gainPct = (parseFloat(document.getElementById("calc-gain").value) || 50) / 100.0;
      var debt = parseFloat(document.getElementById("calc-debt").value) || 0;
      var esc = (parseFloat(document.getElementById("calc-esc").value) || 2.0) / 100.0;
      var repYield = (parseFloat(document.getElementById("calc-rep").value) || 6.80) / 100.0;

      var gross = noi / cap;
      var dttRate = 0.0056;
      if (dttMode === "county") dttRate = 0.0011;
      else if (dttMode === "auto") {
        if (gross >= 10900000) dttRate = 0.0606;
        else if (gross > 5400000) dttRate = 0.0456;
        else dttRate = 0.0056;
      } else if (dttMode === "ula1") dttRate = 0.0456;
      else if (dttMode === "ula2") dttRate = 0.0606;

      var broker = 0.030;
      var disc = repYield;
      var grossCost = gross * (broker + dttRate);
      var netEquity1031 = Math.max(0, gross - grossCost - debt);
      var grossProceeds1031 = Math.max(0, gross - grossCost);

      // Hold NPV
      var cfHold = pvGrowingAnnuity(noi * 0.995, esc, disc, yrs);
      var termNoiHold = noi * 0.995 * Math.pow(1 + esc, yrs);
      var termValHold = Math.max(0, termNoiHold / (cap + 0.0085) - noi * 0.45);
      var npvHold = cfHold + termValHold / Math.pow(1 + disc, yrs);

      // Sell + 1031 NPV (unlevered asset basis equivalent)
      var repNoi1 = grossProceeds1031 * repYield;
      var cf1031 = pvGrowingAnnuity(repNoi1, 0.020, disc, yrs);
      var termNoi1031 = repNoi1 * Math.pow(1.020, yrs);
      var npv1031 = cf1031 + (termNoi1031 / repYield) / Math.pow(1 + disc, yrs);

      // Blend & Extend
      var cfBe = pvGrowingAnnuity(noi * 0.995, Math.max(esc, 0.0225), disc, yrs) - noi * 0.25;
      var termNoiBe = noi * 0.995 * Math.pow(1 + Math.max(esc, 0.0225), yrs);
      var npvBe = cfBe + (termNoiBe / Math.max(0.0525, cap - 0.0040)) / Math.pow(1 + disc, yrs);

      // Taxable Sale
      var gainDollars = Math.max(0, gross * gainPct);
      var incomeTax = gainDollars * 0.371;
      var atProceeds = Math.max(0, grossProceeds1031 - incomeTax);
      var npvTax = pvGrowingAnnuity(atProceeds * 0.0565, 0, disc, yrs) + atProceeds / Math.pow(1 + disc, yrs);

      document.getElementById("out-gross").textContent = fmtUSD(gross);
      document.getElementById("out-dtt").textContent = (dttRate * 100).toFixed(2) + "% (" + fmtUSD(gross * dttRate) + ")";
      document.getElementById("out-equity").textContent = fmtUSD(netEquity1031);
      document.getElementById("out-hold-npv").textContent = fmtUSD(npvHold);
      document.getElementById("out-1031-npv").textContent = fmtUSD(npv1031);
      document.getElementById("out-be-npv").textContent = fmtUSD(npvBe);
      document.getElementById("out-tax-npv").textContent = fmtUSD(npvTax);
      document.getElementById("out-y1-hold").textContent = fmtUSD(noi * 0.995);
      document.getElementById("out-y1-1031").textContent = fmtUSD(repNoi1);
      document.getElementById("out-tax-hit").textContent = fmtUSD(incomeTax);
    }

    root.querySelectorAll("input, select").forEach(function (el) {
      el.addEventListener("input", recalc);
      el.addEventListener("change", recalc);
    });
    recalc();
  }

  // 3. Interactive 5-Path Strategy Selector (suggestions.html)
  function initPathSelector() {
    var box = document.getElementById("path-selector");
    if (!box) return;

    function update() {
      var walt = document.getElementById("ps-walt").value;
      var ula = document.getElementById("ps-ula").value;
      var sales = document.getElementById("ps-sales").value;
      var gain = document.getElementById("ps-gain").value;
      var tod = document.getElementById("ps-tod").value;
      var cap = document.getElementById("ps-cap").value;

      var scores = { P1: 0, P2: 0, P3: 0, P4: 0, P5: 0 };
      var reasons = { P1: [], P2: [], P3: [], P4: [], P5: [] };

      if (walt === "short") { scores.P1 += 4; scores.P2 += 2; reasons.P1.push("WALT <= 5.5 yrs avoids liquidity cliff"); }
      else if (walt === "mid") { scores.P2 += 3; scores.P1 += 2; reasons.P2.push("6-9 yr WALT ideal for early Blend-and-Extend"); }
      else { scores.P3 += 2; scores.P2 += 2; reasons.P3.push("Longer runway gives time for re-tenant prep"); }

      if (ula === "ula") { scores.P2 += 3; scores.P3 += 2; scores.P1 -= 1; reasons.P2.push("Avoids immediate 4.56%-6.06% ULA hit unless cap <= 5.9%"); }
      else { scores.P1 += 3; reasons.P1.push("Low 0.11%-0.56% DTT favors clean §1031 rotation"); }

      if (sales === "weak") { scores.P1 += 4; scores.P4 += 2; scores.P2 -= 2; reasons.P1.push("Store below AUV increases franchisee default/non-renewal risk"); }
      else { scores.P2 += 3; scores.P3 += 2; reasons.P2.push("Healthy unit AUV supports 10-15 yr extension"); }

      if (gain === "low") { scores.P4 += 4; reasons.P4.push("Low embedded gain lets owner exit cleanly into 4.98% Treasuries"); }
      else { scores.P1 += 2; scores.P2 += 2; scores.P3 += 2; scores.P4 -= 2; reasons.P1.push("High gain makes 37.1% tax prohibitive without §1031"); }

      if (tod === "yes") { scores.P5 += 5; reasons.P5.push("Proximity to newly opened Metro D Line favors land-bank TOD pivot"); }
      if (cap === "tight") { scores.P1 += 3; reasons.P1.push("Going-in cap <= 6.25% clears 6.80% replacement hurdle"); }
      else if (cap === "wide") { scores.P2 += 2; scores.P3 += 2; scores.P1 -= 2; reasons.P3.push(">= 7.0% exit cap yields minimal spread switching to 6.80% REIT assets"); }

      var bestId = "P1";
      Object.keys(scores).forEach(function (k) {
        if (scores[k] > scores[bestId]) bestId = k;
      });

      document.querySelectorAll("[data-path-id]").forEach(function (card) {
        var pid = card.getAttribute("data-path-id");
        card.classList.remove("recommended", "caution");
        var statusEl = card.querySelector("[data-path-status]");
        var reasonEl = card.querySelector("[data-path-reason]");
        if (pid === bestId) {
          card.classList.add("recommended");
          if (statusEl) statusEl.innerHTML = '<span class="badge badge-good">Top Fit (' + scores[pid] + ' pts)</span>';
        } else if (scores[pid] >= scores[bestId] - 2) {
          card.classList.add("caution");
          if (statusEl) statusEl.innerHTML = '<span class="badge badge-warn">Viable Alternative (' + scores[pid] + ' pts)</span>';
        } else {
          if (statusEl) statusEl.innerHTML = '<span class="badge badge-slate">Secondary (' + scores[pid] + ' pts)</span>';
        }
        if (reasonEl) {
          reasonEl.textContent = reasons[pid].length ? reasons[pid].join(" · ") : "Conditional fallback based on selected profile.";
        }
      });
    }

    box.querySelectorAll("select").forEach(function (s) {
      s.addEventListener("change", update);
    });
    update();
  }

  document.addEventListener("DOMContentLoaded", function () {
    initTableFilters();
    initCalculator();
    initPathSelector();
  });
})();
