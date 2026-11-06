(function () {
  "use strict";

  function initTableFilters() {
    var wrappers = document.querySelectorAll("[data-table-block]");
    wrappers.forEach(function (block) {
      var input = block.querySelector("[data-table-search]");
      var pills = block.querySelectorAll("[data-status-filter]");
      var exportBtn = block.querySelector("[data-csv-export]");
      var table = block.querySelector("table.data-table");
      if (!table) return;
      var rows = Array.prototype.slice.call(table.querySelectorAll("tbody tr"));
      var activeStatus = "all";

      function applyFilter() {
        var q = input ? input.value.trim().toLowerCase() : "";
        rows.forEach(function (tr) {
          var rowStatus = tr.getAttribute("data-status") || "";
          var text = tr.textContent.toLowerCase();
          var matchStatus = activeStatus === "all" || rowStatus === activeStatus;
          var matchText = !q || text.indexOf(q) !== -1;
          tr.style.display = matchStatus && matchText ? "" : "none";
        });
      }

      if (input) {
        input.addEventListener("input", applyFilter);
      }

      pills.forEach(function (btn) {
        btn.addEventListener("click", function () {
          pills.forEach(function (b) { b.classList.remove("active"); });
          btn.classList.add("active");
          activeStatus = btn.getAttribute("data-status-filter") || "all";
          applyFilter();
        });
      });

      if (exportBtn) {
        exportBtn.addEventListener("click", function () {
          var csvLines = [];
          var trs = table.querySelectorAll("tr");
          trs.forEach(function (tr) {
            if (tr.style.display === "none") return;
            var cells = Array.prototype.slice.call(tr.querySelectorAll("th, td")).map(function (c) {
              var link = c.querySelector("a.src-link");
              var raw = link ? (c.textContent.trim() + " (" + link.getAttribute("href") + ")") : c.textContent.trim();
              return '"' + raw.replace(/"/g, '""').replace(/\s+/g, " ") + '"';
            });
            csvLines.push(cells.join(","));
          });
          var blob = new Blob([csvLines.join("\n")], { type: "text/csv;charset=utf-8;" });
          var url = URL.createObjectURL(blob);
          var a = document.createElement("a");
          a.href = url;
          a.download = (table.getAttribute("id") || "verified_table") + ".csv";
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          URL.revokeObjectURL(url);
        });
      }
    });
  }

  function fmtUSD(n) {
    return "$" + Math.round(n).toLocaleString("en-US");
  }

  function capForTerm(remYears) {
    if (remYears >= 12) return 0.0585;
    if (remYears >= 8) return 0.0620;
    if (remYears >= 6) return 0.0655;
    if (remYears >= 4) return 0.0705;
    if (remYears >= 2) return 0.0765;
    return 0.0825;
  }

  function initSimulator() {
    var root = document.getElementById("private-decision-simulator");
    if (!root) return;

    var elRent = document.getElementById("sim-rent");
    var elExp = document.getElementById("sim-expiry");
    var elBasis = document.getElementById("sim-basis");
    var elProp13 = document.getElementById("sim-prop13");
    var elUla = document.getElementById("sim-ula");
    var elExtend = document.getElementById("sim-extend");

    function updateSim() {
      var rent = Math.max(25000, parseFloat(elRent.value) || 200000);
      var expYear = parseInt(elExp.value, 10) || 2032;
      var basis = Math.max(0, parseFloat(elBasis.value) || 850000);
      var prop13Base = Math.max(0, parseFloat(elProp13.value) || 950000);
      var inLaCity = elUla.value === "city_la";
      var canExtend = elExtend.value === "yes";

      var remYears = Math.max(1, expYear - 2026);
      var capNow = capForTerm(remYears);
      var grossSaleNow = rent / capNow;

      var blendedRent = rent * 0.96;
      var grossSaleExtended = blendedRent / capForTerm(12);
      var chosenGrossSale = canExtend ? grossSaleExtended : grossSaleNow;

      // City of LA Measure ULA transfer tax (post-June 30, 2026 official thresholds)
      var transferTaxPct = 0.0011; // County 0.11%
      var ulaNote = "Outside City of LA (0.11% County only)";
      if (inLaCity) {
        if (chosenGrossSale >= 10900000) {
          transferTaxPct = 0.0595 + 0.0011;
          ulaNote = "ALERT: >= $10.9M triggers 5.95% City ULA+Base!";
        } else if (chosenGrossSale > 5400000) {
          transferTaxPct = 0.0445 + 0.0011;
          ulaNote = "ALERT: > $5.4M triggers 4.45% City ULA+Base!";
        } else {
          transferTaxPct = 0.0045 + 0.0011;
          ulaNote = "Below $5.4M ULA cliff (0.45% City + 0.11% County)";
        }
      }

      var brokerPct = 0.04;
      var netProceeds1031 = chosenGrossSale * (1 - brokerPct - transferTaxPct);

      // Taxable sale drag (~35.5% combined Fed 20% LTCG + 3.8% NIIT + 25% 1250 + CA up to 13.3%)
      var capGain = Math.max(0, netProceeds1031 - basis);
      var estTaxDrag = capGain * 0.355;
      var afterTaxCashProceeds = netProceeds1031 - estTaxDrag;

      // Prop 13 reassessment shock passed to NNN tenant upon sale (~1.18% effective LA tax rate)
      var prop13AnnualJump = Math.max(0, chosenGrossSale - prop13Base) * 0.0118;

      // 10-Yr wealth scaling from Monte Carlo ratios per $100k NOI
      var scale = rent / 100000.0;
      var w1031 = netProceeds1031 * 2.02; // 7.1% initial diversified NNN yield + 1.75% bumps over 10 yrs
      var wHold = (2581030 * scale) * (remYears >= 7 ? 1.04 : (remYears <= 4 ? 0.93 : 1.0));
      var wTaxable = afterTaxCashProceeds * Math.pow(1.052, 10);

      document.getElementById("out-val-now").textContent = fmtUSD(grossSaleNow) + " (" + (capNow * 100).toFixed(2) + "% cap)";
      document.getElementById("out-val-ext").textContent = fmtUSD(grossSaleExtended) + " (5.85% cap)";
      document.getElementById("out-ula").textContent = fmtUSD(chosenGrossSale * transferTaxPct);
      document.getElementById("out-ula-hint").textContent = ulaNote;
      document.getElementById("out-tax-saved").textContent = fmtUSD(estTaxDrag);
      document.getElementById("out-prop13-shock").textContent = "+" + fmtUSD(prop13AnnualJump) + " / yr";
      document.getElementById("out-w-1031").textContent = fmtUSD(w1031);
      document.getElementById("out-w-hold").textContent = fmtUSD(wHold);
      document.getElementById("out-w-cash").textContent = fmtUSD(wTaxable);

      var verdictEl = document.getElementById("sim-dynamic-verdict");
      var ulaWarn = (inLaCity && chosenGrossSale > 5400000 && chosenGrossSale < 5750000)
        ? " CRITICAL ULA PRICING ALERT: Your estimated sale price sits just above the $5,400,000 Measure ULA cliff — pricing at $5,395,000 instead would save >$200,000 in gross transfer tax!"
        : "";

      if (remYears <= 5 && !canExtend) {
        verdictEl.textContent =
          "URGENT PRE-CLIFF ACTION (" + remYears + " yrs left): Because remaining term is already <=5 years and early extension is unavailable, waiting further risks severe cap-rate expansion (7.65%–8.25%). Execute a Pre-Cliff Sale + IRC §1031 Diversified Exchange in 2027 to preserve " +
          fmtUSD(estTaxDrag) + " in deferred taxes and outperform passive hold by ~" + fmtUSD(w1031 - wHold) + " over 10 years." + ulaWarn;
      } else if (canExtend) {
        verdictEl.textContent =
          "OPTIMAL TWO-STAGE EXECUTION: Negotiating an early 12-year Blend-and-Extend lifts gross value from " +
          fmtUSD(grossSaleNow) + " to " + fmtUSD(grossSaleExtended) + ", and completing an IRC §1031 Exchange into 2–3 diversified assets defers " +
          fmtUSD(estTaxDrag) + " in Fed+CA taxes, generating ~" + fmtUSD(w1031) + " in expected 10-yr wealth while eliminating single-parcel Central LA seismic & JACK closure concentration." + ulaWarn;
      } else {
        verdictEl.textContent =
          "RECOMMENDED PRE-CLIFF §1031 EXCHANGE (" + remYears + " yrs left): Sell while >5 years of financeable term remain (2027–2028) and redeploy via IRC §1031 into 2–3 diversified net-lease assets, outperforming passive hold by ~" +
          fmtUSD(w1031 - wHold) + " and outperforming a taxable cash sale by ~" + fmtUSD(w1031 - wTaxable) + " over 10 years." + ulaWarn;
      }
    }

    [elRent, elExp, elBasis, elProp13, elUla, elExtend].forEach(function (el) {
      if (el) {
        el.addEventListener("input", updateSim);
        el.addEventListener("change", updateSim);
      }
    });
    updateSim();
  }

  document.addEventListener("DOMContentLoaded", function () {
    initTableFilters();
    initSimulator();
  });
})();
