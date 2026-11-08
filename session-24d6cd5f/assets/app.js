(function () {
  "use strict";

  // 1. Live table search & status filtering across data pages
  function initTableFilters() {
    document.querySelectorAll("[data-filter-table]").forEach(function (bar) {
      var targetId = bar.getAttribute("data-filter-table");
      var tbl = document.getElementById(targetId);
      if (!tbl) return;
      var qInput = bar.querySelector("input[type='search']");
      var sel = bar.querySelector("select");

      function apply() {
        var q = qInput ? qInput.value.trim().toLowerCase() : "";
        var st = sel ? sel.value : "all";
        var rows = tbl.querySelectorAll("tbody tr");
        var shown = 0;
        rows.forEach(function (tr) {
          var txt = tr.textContent.toLowerCase();
          var rowStatus = tr.getAttribute("data-status") || "";
          var rowCat = tr.getAttribute("data-cat") || "";
          var matchText = !q || txt.indexOf(q) !== -1;
          var matchSel =
            st === "all" ||
            rowStatus === st ||
            rowCat === st;
          var vis = matchText && matchSel;
          tr.style.display = vis ? "" : "none";
          if (vis) shown++;
        });
        var counter = bar.querySelector(".filter-count");
        if (counter) counter.textContent = shown + " rows shown";
      }

      if (qInput) qInput.addEventListener("input", apply);
      if (sel) sel.addEventListener("change", apply);
      apply();
    });
  }

  // 2. 100% Browser-Local Private Calculator & Sensitivity Analyzer (Zero Network Calls)
  function capForTerm(remYears, spreadBps) {
    var base;
    if (remYears >= 14) base = 6.45;
    else if (remYears >= 10) base = 6.45 + (14 - remYears) * (0.15 / 4);
    else if (remYears >= 6) base = 6.60 + (10 - remYears) * (0.35 / 4);
    else if (remYears >= 3) base = 6.95 + (6 - remYears) * (0.65 / 3);
    else base = 7.60 + Math.max(0, 3 - remYears) * 0.35;
    return Math.max(5.25, Math.min(11.0, base + spreadBps / 100));
  }

  function fmtUSD(v) {
    var neg = v < 0 ? "-" : "";
    return neg + "$" + Math.round(Math.abs(v)).toLocaleString("en-US");
  }

  function initSimulator() {
    var panel = document.getElementById("private-sim");
    if (!panel) return;

    var inputs = {
      noi: document.getElementById("sim-noi"),
      expiry: document.getElementById("sim-expiry"),
      guarantor: document.getElementById("sim-guarantor"),
      basis: document.getElementById("sim-basis"),
      debt: document.getElementById("sim-debt"),
      jurisdiction: document.getElementById("sim-jurisdiction"),
      esc: document.getElementById("sim-esc"),
      reitYield: document.getElementById("sim-reit-yield"),
      rateRegime: document.getElementById("sim-rate-regime"),
      storeSales: document.getElementById("sim-store-sales")
    };

    var outBody = document.getElementById("sim-output-body");
    var summaryEl = document.getElementById("sim-summary");

    function compute() {
      var noi = Math.max(10000, parseFloat(inputs.noi.value) || 100000);
      var expYr = parseInt(inputs.expiry.value, 10) || 2032;
      var remYrs = Math.max(1, expYr - 2026);
      var guar = inputs.guarantor.value;
      var basis = Math.max(0, parseFloat(inputs.basis.value) || 0);
      var debt = Math.max(0, parseFloat(inputs.debt.value) || 0);
      var juris = inputs.jurisdiction.value;
      var escPct = Math.max(0, parseFloat(inputs.esc.value) || 1.5) / 100;
      var reitYield = Math.max(4.0, parseFloat(inputs.reitYield.value) || 7.2) / 100;
      var regimeBps = parseFloat(inputs.rateRegime.value) || 0;
      var storeSales = parseFloat(inputs.storeSales.value) || 1874000;

      var guarBps = guar === "franchisee" ? 45 : 0;
      var capNow = capForTerm(remYrs, guarBps + regimeBps * 0.5);
      var grossVal = noi / (capNow / 100);

      // Transfer tax rules (verified July 1, 2026 City of LA Office of Finance + County DTT)
      var transferTaxRate = 0.0011; // County 0.11%
      if (juris === "lacity") {
        transferTaxRate += 0.0045; // City base 0.45%
        if (grossVal >= 10900000) transferTaxRate += 0.055;
        else if (grossVal > 5400000) transferTaxRate += 0.040;
      }
      var brokerageCloseRate = 0.040;
      var sellFriction = grossVal * (brokerageCloseRate + transferTaxRate);

      var netEquityBeforeTax = Math.max(0, grossVal - sellFriction - debt);
      var totalGain = Math.max(0, grossVal - sellFriction - basis);
      // Blended LTCG/NIIT (23.8%) + CA 13.30% (permanent post-Prop 3) + partial §1250 slice -> ~38.6% effective
      var taxOnCashSale = totalGain * 0.386;
      var afterTaxCashSaleEquity = Math.max(0, netEquityBeforeTax - taxOnCashSale);

      var rentToSales = (noi / Math.max(100000, storeSales)) * 100;
      var healthLabel =
        rentToSales <= 8.0
          ? "Healthy (<=8.0% rent/sales)"
          : rentToSales <= 10.5
          ? "Watch Zone (8%–10.5%)"
          : "Elevated Closure Risk (>10.5%)";

      // 14-Year Horizon to 2040 projection (deterministic expected values scaled to private equity)
      var horizon = 14;
      var cashReinv = 0.0475 * 0.70; // ~3.325% after tax on cash accumulations

      // Strategy S4: Immediate Sale + 1031
      var s4Equity = Math.max(0, grossVal - sellFriction);
      var s4Debt = debt;
      var s4NetEq = Math.max(0, s4Equity - s4Debt);
      var s4Noi = s4Equity * reitYield;
      var s4DebtCost = s4Debt * 0.055; // assumed replacement debt service parity
      var s4Cash = 0;
      for (var y = 1; y <= horizon; y++) {
        s4Cash = s4Cash * (1 + cashReinv) + (s4Noi - s4DebtCost);
        s4Noi *= 1.020;
      }
      var s4Term = (s4Noi / 0.067) * (1 - 0.025) - s4Debt;
      var s4Total = s4Cash + s4Term;

      // Strategy S3: Blend & Extend 10yr (-3% rent reset) then 1031 at Yr 1
      var extCap = capForTerm(remYrs + 9, guarBps + regimeBps * 0.5);
      var extGross = (noi * 0.97) / (extCap / 100);
      var extFrictionRate = brokerageCloseRate + 0.0011 + (juris === "lacity" ? 0.0045 + (extGross >= 10900000 ? 0.055 : extGross > 5400000 ? 0.040 : 0) : 0);
      var s3Proceeds = Math.max(0, extGross * (1 - extFrictionRate));
      var s3Noi = s3Proceeds * reitYield;
      var s3Cash = (noi - s4DebtCost) * (1 + cashReinv);
      for (var y3 = 2; y3 <= horizon; y3++) {
        s3Cash = s3Cash * (1 + cashReinv) + (s3Noi - s4DebtCost);
        s3Noi *= 1.020;
      }
      var s3Term = (s3Noi / 0.067) * (1 - 0.025) - s4Debt;
      var s3TotalIfGranted = s3Cash + s3Term;

      // Strategy S1: Hold Passive through Expiry
      var s1Cash = 0;
      var s1Noi = noi;
      var nonRenewProb = (guar === "franchisee" ? 0.37 : 0.28) + (rentToSales > 10.5 ? 0.20 : 0.0);
      nonRenewProb = Math.min(0.75, nonRenewProb);
      for (var y1 = 1; y1 <= horizon; y1++) {
        if (y1 === remYrs + 1) {
          // Expected downtime + TI/LC drag weighted by non-renewal probability
          s1Cash -= nonRenewProb * (noi * 1.15 + noi * 1.85);
          s1Noi = s1Noi * (1 - nonRenewProb * 0.12);
        }
        s1Cash = s1Cash * (1 + cashReinv) + (s1Noi * 0.96 - s4DebtCost);
        s1Noi *= 1 + escPct;
      }
      var s1TermCap = capForTerm(4, guarBps + regimeBps * 0.6);
      var s1Term = (s1Noi / (s1TermCap / 100)) * (1 - brokerageCloseRate - transferTaxRate) - s4Debt;
      var s1Total = s1Cash + s1Term;

      // Strategy S5: Immediate Taxable Cash Sale -> Treasury/IG Bonds
      var bondNetRate = (0.0486 + regimeBps / 10000 * 0.6) * (1 - 0.35);
      var s5Total = afterTaxCashSaleEquity * Math.pow(1 + bondNetRate, horizon);

      var rows = [
        { name: "Blend & Extend (If Granted 100%) + §1031 Yr 1", gross: extGross, fric: extGross * extFrictionRate, tax: 0, net2040: s3TotalIfGranted, note: "Conditional on tenant signing 10-yr extension" },
        { name: "Immediate Sale + §1031 Exchange Now (Recommended Base)", gross: grossVal, fric: sellFriction, tax: 0, net2040: s4Total, note: "Unconditional execution; exits May 2031 ARD" },
        { name: "Hold Passive Through " + expYr + " Expiry", gross: grossVal, fric: 0, tax: 0, net2040: s1Total, note: "Carries " + Math.round(nonRenewProb * 100) + "% non-renewal/downtime risk" },
        { name: "Immediate Taxable Cash Sale -> Treasury/IG Ladder", gross: grossVal, fric: sellFriction, tax: taxOnCashSale, net2040: s5Total, note: "Post-Prop 3 38.6% effective gain/§1250 tax drag" }
      ];

      if (summaryEl) {
        summaryEl.innerHTML =
          "<strong>Local Valuation Snapshot:</strong> Implied Cap Rate <code>" +
          capNow.toFixed(2) +
          "%</code> | Estimated Gross Value <code>" +
          fmtUSD(grossVal) +
          "</code> | Measure ULA Triggered? <code>" +
          (juris === "lacity" && grossVal > 5400000 ? "YES (" + (transferTaxRate * 100).toFixed(2) + "% total DTT)" : "NO (" + (transferTaxRate * 100).toFixed(2) + "% base DTT)") +
          "</code> | Store Coverage: <code>" +
          rentToSales.toFixed(1) +
          "% (" +
          healthLabel +
          ")</code>";
      }

      if (outBody) {
        outBody.innerHTML = rows
          .map(function (r) {
            return (
              "<tr><td><strong>" +
              r.name +
              "</strong><br><span class='muted'>" +
              r.note +
              "</span></td><td class='num'>" +
              fmtUSD(r.gross) +
              "</td><td class='num'>" +
              fmtUSD(r.fric) +
              "</td><td class='num'>" +
              fmtUSD(r.tax) +
              "</td><td class='num'><strong>" +
              fmtUSD(r.net2040) +
              "</strong></td></tr>"
            );
          })
          .join("");
      }
    }

    Object.keys(inputs).forEach(function (k) {
      if (inputs[k]) {
        inputs[k].addEventListener("input", compute);
        inputs[k].addEventListener("change", compute);
      }
    });

    var resetBtn = document.getElementById("sim-reset");
    if (resetBtn) {
      resetBtn.addEventListener("click", function () {
        inputs.noi.value = "100000";
        inputs.expiry.value = "2032";
        inputs.guarantor.value = "corporate";
        inputs.basis.value = "500000";
        inputs.debt.value = "0";
        inputs.jurisdiction.value = "lacity";
        inputs.esc.value = "1.5";
        inputs.reitYield.value = "7.2";
        inputs.rateRegime.value = "0";
        inputs.storeSales.value = "1874000";
        compute();
      });
    }

    var exportBtn = document.getElementById("sim-export-csv");
    if (exportBtn) {
      exportBtn.addEventListener("click", function () {
        var trs = Array.from(document.querySelectorAll("#sim-output-table tr"));
        var csv = trs
          .map(function (tr) {
            return Array.from(tr.children)
              .map(function (td) {
                return '"' + td.textContent.replace(/\s+/g, " ").trim().replace(/"/g, '""') + '"';
              })
              .join(",");
          })
          .join("\n");
        var blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
        var url = URL.createObjectURL(blob);
        var a = document.createElement("a");
        a.href = url;
        a.download = "local-private-nnn-decision-analysis.csv";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      });
    }

    compute();
  }

  document.addEventListener("DOMContentLoaded", function () {
    initTableFilters();
    initSimulator();
  });
})();
