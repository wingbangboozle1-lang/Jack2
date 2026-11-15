/*
 * Private sell-versus-hold calculator. Runs entirely in the reader's browser.
 * Nothing typed here is sent, stored, logged or shown to anyone else:
 * there is no network call, no cookie, no localStorage and no form submission.
 *
 * Rates are supplied by the page from the verified tax ledger (see the rule
 * table on calculator.html). No input has a default value: a blank input is
 * reported as missing and the comparison is not computed. No winner is chosen.
 *
 * Arithmetic only. Each tax rate is applied to the same base; no tax is
 * deducted from another (for example, state tax is not deducted from federal
 * income). Capital losses are not modelled: a gain at or below zero carries no tax.
 */
(function (root) {
  "use strict";

  var MONEY = ["price", "costs", "basis", "dep", "rent", "term"];
  var PCT = ["ttShare", "cgRate", "recRate", "caRate", "disc", "fedRate", "caRate2"];
  var YN = ["niit", "niit2"];

  var LABEL = {
    price: "sale price", costs: "selling costs", ttShare: "seller's share of transfer tax",
    basis: "adjusted tax basis", dep: "depreciation taken", cgRate: "federal rate on long-term gain",
    recRate: "federal rate on depreciation recapture", niit: "whether the 3.8% tax applies to the sale",
    caRate: "California rate on the gain", rent: "taxable rent per year", years: "years of hold",
    disc: "discount rate", fedRate: "federal rate on rent", caRate2: "California rate on rent",
    niit2: "whether the 3.8% tax applies to rent", term: "after-tax cash at the end of the hold"
  };

  function parseNumber(v) {
    if (v === null || v === undefined) return null;
    if (typeof v === "number") return isFinite(v) ? v : NaN;
    var s = String(v).trim();
    if (s === "") return null;
    if (!/^-?(\d+\.?\d*|\.\d+)$/.test(s)) return NaN;
    return Number(s);
  }

  function check(inp, key, rules, errors, missing) {
    var v = parseNumber(inp[key]);
    if (key === "niit" || key === "niit2") {
      if (inp[key] !== "yes" && inp[key] !== "no") missing.push(LABEL[key]);
      return;
    }
    if (v === null) { missing.push(LABEL[key]); return; }
    if (isNaN(v)) { errors.push(LABEL[key] + " must be a number"); return; }
    if (MONEY.indexOf(key) >= 0 && v < 0) errors.push(LABEL[key] + " cannot be negative");
    if (PCT.indexOf(key) >= 0 && (v < 0 || v > 100)) errors.push(LABEL[key] + " must be between 0 and 100 percent");
    if (key === "years" && (v < 1 || v > 50 || Math.floor(v) !== v)) errors.push("years of hold must be a whole number from 1 to 50");
  }

  function cityRate(price, R) {
    if (price <= R.threshLow) return R.cityLow;
    if (price < R.threshHigh) return R.cityMid;
    return R.cityHigh;
  }

  function money(x) {
    if (typeof Intl !== "undefined" && Intl.NumberFormat) {
      return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(Math.round(x));
    }
    return "$" + String(Math.round(x));
  }

  function compute(inp, R) {
    var missing = [], errors = [];
    var keys = ["price", "costs", "ttShare", "basis", "dep", "cgRate", "recRate", "niit", "caRate",
                "rent", "years", "disc", "fedRate", "caRate2", "niit2", "term"];
    keys.forEach(function (k) { check(inp, k, R, errors, missing); });
    var out = { ok: false, missing: missing, errors: errors, sale: null, hold: null, diff: null, verdict: "" };
    if (missing.length || errors.length) return out;

    var n = function (k) { return parseNumber(inp[k]); };

    // --- Sale now -----------------------------------------------------------
    var price = n("price"), costs = n("costs"), share = n("ttShare") / 100;
    var rate = cityRate(price, R);
    var transferTotal = price * (rate + R.county) / 100;          // city tier + county, whole price (ledger TX-006 to TX-008, TX-013)
    var sellerTransfer = transferTotal * share;
    var netRealized = price - costs - sellerTransfer;
    var gain = netRealized - n("basis");
    var taxable = Math.max(gain, 0);
    var recap = Math.min(taxable, n("dep"));                      // unrecaptured gain, straight-line depreciation assumed (TX-042)
    var capPart = taxable - recap;
    var fedGain = recap * n("recRate") / 100 + capPart * n("cgRate") / 100;
    var niitSale = inp.niit === "yes" ? taxable * R.niit / 100 : 0; // TX-043
    var caSale = taxable * n("caRate") / 100;
    var saleTaxes = fedGain + niitSale + caSale;
    var saleCash = netRealized - saleTaxes;

    out.sale = {
      cityRatePct: rate, countyRatePct: R.county, transferTotal: transferTotal, sellerTransfer: sellerTransfer,
      netRealized: netRealized, gain: gain, recap: recap, capPart: capPart,
      fedTax: fedGain, niitTax: niitSale, caTax: caSale, taxes: saleTaxes, cash: saleCash,
      aboveLowThreshold: price > R.threshLow
    };

    // --- Hold and renew: after-tax rent, discounted, plus end cash -----------
    var niitRent = inp.niit2 === "yes" ? R.niit : 0;
    var ratePct = n("fedRate") + n("caRate2") + niitRent;
    var afterRent = n("rent") * (1 - ratePct / 100);
    var years = n("years"), r = n("disc") / 100;
    var annuity = r === 0 ? years : (1 - Math.pow(1 + r, -years)) / r;
    var pvRent = afterRent * annuity;
    var pvTerm = n("term") / Math.pow(1 + r, years);
    var holdPV = pvRent + pvTerm;

    out.hold = {
      ratePct: ratePct, afterRent: afterRent, annuity: annuity,
      pvRent: pvRent, pvTerm: pvTerm, pv: holdPV
    };

    out.diff = saleCash - holdPV;
    out.ok = true;
    var d = Math.abs(out.diff);
    if (Math.round(d) === 0) out.verdict = "The two figures are equal under these inputs.";
    else if (out.diff > 0) out.verdict = "Under these inputs the sale leaves " + money(d) + " more in today's dollars than the hold path.";
    else out.verdict = "Under these inputs the hold path is worth " + money(d) + " more in today's dollars than the sale.";
    return out;
  }

  var core = { compute: compute, cityRate: cityRate, money: money, parseNumber: parseNumber };

  if (typeof module !== "undefined" && module.exports) { module.exports = core; return; }

  // ---- page wiring (browser only) ---------------------------------------
  root.CalcCore = core;
  if (typeof document === "undefined") return;

  var R = root.CALC_RULES;
  function val(id) { var el = document.getElementById(id); return el ? el.value : ""; }
  function setVal(id, v) { var el = document.getElementById(id); if (el) el.value = v; }

  function readInputs() {
    var inp = {};
    ["price", "costs", "ttShare", "basis", "dep", "cgRate", "recRate", "niit", "caRate",
     "rent", "years", "disc", "fedRate", "caRate2", "niit2", "term"].forEach(function (k) { inp[k] = val("c-" + k); });
    return inp;
  }

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;" }[c]; }); }

  function row(label, value, bold) {
    var l = esc(label), v = esc(value);
    if (bold) { l = "<strong>" + l + "</strong>"; v = "<strong>" + v + "</strong>"; }
    return "<tr><th scope=\"row\">" + l + "</th><td>" + v + "</td></tr>";
  }

  function render() {
    var res = compute(readInputs(), R);
    var box = document.getElementById("c-result");
    if (!box) return;
    if (!res.ok) {
      var parts = [];
      if (res.missing.length) parts.push("<p><strong>Still blank:</strong> " + res.missing.map(esc).join("; ") + ". Nothing is calculated until every input is entered; no value is assumed.</p>");
      if (res.errors.length) parts.push("<p><strong>Check:</strong> " + res.errors.map(esc).join("; ") + ".</p>");
      box.innerHTML = parts.join("");
      return;
    }
    var s = res.sale, h = res.hold;
    box.innerHTML =
      "<p class=\"verdict\"><strong>" + esc(res.verdict) + "</strong> Arithmetic on the inputs only: this is not a recommendation.</p>" +
      "<div class=\"calc-cols\">" +
      "<div><h3>A. Sell now</h3><table class=\"calc-t\"><tbody>" +
      row("Transfer tax (city tier " + s.cityRatePct + "% plus county " + s.countyRatePct + "%, on the whole price)", money(s.transferTotal)) +
      row("Seller's share of transfer tax", money(s.sellerTransfer)) +
      row("Amount realised after costs and seller's transfer tax", money(s.netRealized)) +
      row("Taxable gain (zero if negative)", money(Math.max(s.gain, 0))) +
      row("   of which depreciation recapture", money(s.recap)) +
      row("Federal tax on the gain", money(s.fedTax)) +
      row("Net investment income tax", money(s.niitTax)) +
      row("California tax on the gain", money(s.caTax)) +
      row("After-tax cash from the sale", money(s.cash), true) +
      "</tbody></table></div>" +
      "<div><h3>B. Hold and renew</h3><table class=\"calc-t\"><tbody>" +
      row("Combined tax rate on rent", h.ratePct.toFixed(2) + "%") +
      row("After-tax rent per year", money(h.afterRent)) +
      row("Years counted (discount factor)", h.annuity.toFixed(4)) +
      row("Present value of after-tax rent", money(h.pvRent)) +
      row("Present value of after-tax cash at the end", money(h.pvTerm)) +
      row("Present value of the hold path", money(h.pv), true) +
      "</tbody></table></div></div>" +
      "<p><strong>Difference (sell minus hold):</strong> " + money(res.diff) + " in today's dollars.</p>" +
      (s.aboveLowThreshold ? "<p class=\"note\">The price is above the lower Measure ULA threshold, so the higher city rate applies to the whole price (rule TX-004 and TX-007 on this page).</p>" : "") +
      "<p class=\"note\">Left out on purpose: loss of rent during a vacancy, repairs, tenant default, the timing of a sale, selling costs not entered, loan payoff, any capital loss, and the state tax rate you enter in place of an official schedule. Enter only figures you have verified.</p>";
  }

  function upperBound() {
    setVal("c-cgRate", String(R.cg));
    setVal("c-recRate", String(R.rec));
    setVal("c-niit", "yes");
    setVal("c-caRate", String(R.caTop));
    render();
  }

  function clearAll() {
    ["price", "costs", "ttShare", "basis", "dep", "cgRate", "recRate", "niit", "caRate",
     "rent", "years", "disc", "fedRate", "caRate2", "niit2", "term"].forEach(function (k) { setVal("c-" + k, ""); });
    render();
  }

  var form = document.getElementById("c-form");
  if (form) {
    form.addEventListener("input", render);
    form.addEventListener("change", render);
    form.addEventListener("submit", function (ev) { ev.preventDefault(); render(); });
  }
  var ub = document.getElementById("c-upper");
  if (ub) ub.addEventListener("click", upperBound);
  var cl = document.getElementById("c-clear");
  if (cl) cl.addEventListener("click", clearAll);
  var pr = document.getElementById("c-print");
  if (pr) pr.addEventListener("click", function () { window.print(); });
  render();
})(typeof window !== "undefined" ? window : this);
