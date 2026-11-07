// Progressive enhancement: client-side table filtering & 100% browser-local NNN / §1031 simulator
// Zero network requests, zero cookies, zero external storage.
(function () {
  // 1. Table search / status filter
  var searchInputs = document.querySelectorAll("[data-table-search]");
  searchInputs.forEach(function (inp) {
    var targetId = inp.getAttribute("data-table-search");
    var tbl = document.getElementById(targetId);
    if (!tbl) return;
    var statusSel = document.querySelector('[data-table-status="' + targetId + '"]');
    function filterRows() {
      var q = (inp.value || "").toLowerCase().trim();
      var st = statusSel ? (statusSel.value || "").toLowerCase() : "";
      var rows = tbl.querySelectorAll("tbody tr");
      rows.forEach(function (r) {
        var txt = r.textContent.toLowerCase();
        var rowSt = (r.getAttribute("data-status") || "").toLowerCase();
        var matchQ = !q || txt.indexOf(q) !== -1;
        var matchSt = !st || rowSt === st;
        r.style.display = matchQ && matchSt ? "" : "none";
      });
    }
    inp.addEventListener("input", filterRows);
    if (statusSel) statusSel.addEventListener("change", filterRows);
  });

  // 2. Browser-local private NNN / §1031 / Measure ULA / Prop 13 Simulator
  var simForm = document.getElementById("local-nnn-simulator");
  if (!simForm) return;

  function fmtMoney(n) {
    var s = n < 0 ? "-" : "";
    return s + "$" + Math.round(Math.abs(n)).toLocaleString("en-US");
  }

  function capForTerm(rem) {
    if (rem >= 14) return 0.064;
    if (rem >= 10) return 0.064 + (14 - rem) * (0.002 / 4);
    if (rem >= 6) return 0.066 + (10 - rem) * (0.0035 / 4);
    if (rem >= 3) return 0.0695 + (6 - rem) * (0.0075 / 3);
    return 0.077 + Math.max(0, 3 - rem) * (0.0065 / 3);
  }

  function runSim() {
    var noi = parseFloat(document.getElementById("sim-noi").value) || 150000;
    var expYear = parseInt(document.getElementById("sim-expiry").value, 10) || 2032;
    var storeSales = parseFloat(document.getElementById("sim-sales").value) || 1874000;
    var prop13Basis = parseFloat(document.getElementById("sim-prop13").value) || 950000;
    var taxBasis = parseFloat(document.getElementById("sim-taxbasis").value) || 600000;
    var inCityLA = document.getElementById("sim-cityla").value === "yes";
    var reinvestY = (parseFloat(document.getElementById("sim-reinvest").value) || 7.1) / 100.0;

    var rem = Math.max(1, expYear - 2026);
    var capNow = capForTerm(rem);
    var grossNow = noi / capNow;
    var capExt = 0.064;
    var grossExt = (noi * 1.045) / capExt;

    // Transfer tax + Measure ULA check
    var ulaRateNow = inCityLA && grossNow > 5400000 ? (grossNow >= 10900000 ? 0.055 : 0.04) : 0.0;
    var ulaRateExt = inCityLA && grossExt > 5400000 ? (grossExt >= 10900000 ? 0.055 : 0.04) : 0.0;
    var frictionNow = 0.0456 + ulaRateNow;
    var frictionExt = 0.0456 + ulaRateExt;

    var net1031Now = grossNow * (1 - frictionNow);
    var net1031Ext = grossExt * (1 - frictionExt);
    var capGain = Math.max(0, grossNow * (1 - frictionNow) - taxBasis);
    var taxBill = capGain * 0.355;
    var netCashSale = net1031Now - taxBill;

    // Prop 13 NNN tax reassessment shock to tenant upon sale
    var oldPropTax = prop13Basis * 0.0115;
    var newPropTax = grossNow * 0.0115;
    var propTaxJump = Math.max(0, newPropTax - oldPropTax);
    var rentToSalesNow = ((noi + oldPropTax + 18000) / storeSales) * 100.0;
    var rentToSalesPostSale = ((noi + newPropTax + 18000) / storeSales) * 100.0;

    var w2040_S2 = net1031Ext * Math.pow(1 + reinvestY * 0.78 + 0.018, 12) + noi * 2.1;
    var w2040_S1 = net1031Now * Math.pow(1 + reinvestY * 0.78 + 0.018, 14);
    var w2040_S5 = netCashSale * Math.pow(1 + reinvestY * 0.55 + 0.014, 14);

    document.getElementById("out-val-now").textContent = fmtMoney(grossNow) + " (" + (capNow * 100).toFixed(2) + "% cap)";
    document.getElementById("out-val-ext").textContent = fmtMoney(grossExt) + " (6.40% cap)";
    document.getElementById("out-net-1031").textContent = fmtMoney(net1031Now);
    document.getElementById("out-tax-saved").textContent = fmtMoney(taxBill);
    document.getElementById("out-prop13-jump").textContent = "+" + fmtMoney(propTaxJump) + "/yr to NNN tenant";
    document.getElementById("out-rts").textContent = rentToSalesNow.toFixed(1) + "% now -> " + rentToSalesPostSale.toFixed(1) + "% post-sale";
    document.getElementById("out-w2040-s2").textContent = fmtMoney(w2040_S2);
    document.getElementById("out-w2040-s1").textContent = fmtMoney(w2040_S1);
    document.getElementById("out-w2040-s5").textContent = fmtMoney(w2040_S5);

    var recEl = document.getElementById("out-sim-verdict");
    if (rem <= 5 || rentToSalesNow >= 10.5) {
      recEl.textContent = "URGENT ACTION: Remaining term is <=5 yrs or store rent-to-sales is elevated (" + rentToSalesNow.toFixed(1) + "%). Execute Stage 1 Blend-and-Extend inquiry immediately with a hard 90-day cutoff to sell via IRC §1031 before lender WALT curtailment.";
    } else if (inCityLA && grossExt > 5400000 && grossExt < 5700000) {
      recEl.textContent = "MEASURE ULA CLIFF ALERT: Extended value (" + fmtMoney(grossExt) + ") crosses the $5.40M City of LA ULA cliff (+4.0% = " + fmtMoney(grossExt * 0.04) + " surtax). Cap sale price at $5,390,000 or exchange before crossing $5.40M.";
    } else {
      recEl.textContent = "OPTIMAL SEQUENCE: Pursue Early 15-Year Blend-and-Extend (unlocking " + fmtMoney(grossExt - grossNow) + " of cap-compression value) and rotate 100% tax-deferred via IRC §1031 (saving " + fmtMoney(taxBill) + " in taxes).";
    }
  }

  var inputs = simForm.querySelectorAll("input, select");
  inputs.forEach(function (el) { el.addEventListener("input", runSim); el.addEventListener("change", runSim); });
  runSim();
})();
