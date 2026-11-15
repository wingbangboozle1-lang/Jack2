// Hand-checked cases for assets/calculator.js. Run: node canonical/tests/calculator_test.js
"use strict";
const assert = require("assert");
const path = require("path");
const C = require(path.join(__dirname, "..", "..", "assets", "calculator.js"));

// Rules exactly as the page supplies them from the verified ledger.
const R = { cityLow: 0.45, cityMid: 4.45, cityHigh: 5.95, threshLow: 5400000, threshHigh: 10900000,
            county: 0.11, cg: 20, rec: 25, niit: 3.8, caTop: 13.3 };

const blank = { price: "", costs: "", ttShare: "", basis: "", dep: "", cgRate: "", recRate: "", niit: "", caRate: "",
                rent: "", years: "", disc: "", fedRate: "", caRate2: "", niit2: "", term: "" };
const full = Object.assign({}, blank, { price: "3000000", costs: "150000", ttShare: "100", basis: "1000000", dep: "500000",
  cgRate: "20", recRate: "25", niit: "yes", caRate: "13.3", rent: "100000", years: "5", disc: "5",
  fedRate: "30", caRate2: "9.3", niit2: "no", term: "0" });
const near = (a, b, eps = 0.01) => assert.ok(Math.abs(a - b) < eps, `expected ${b}, got ${a}`);

// 1. Blank inputs: nothing is computed, nothing is assumed.
let r = C.compute(blank, R);
assert.strictEqual(r.ok, false);
assert.strictEqual(r.sale, null);
assert.strictEqual(r.missing.length, 16, "every input is reported missing");

// 2. Hand-computed full case.
r = C.compute(full, R);
assert.strictEqual(r.ok, true, JSON.stringify(r.errors) + JSON.stringify(r.missing));
near(r.sale.transferTotal, 16800);            // 3,000,000 x (0.45 + 0.11)%
near(r.sale.netRealized, 2833200);            // less 150,000 costs and 16,800 transfer tax
near(r.sale.gain, 1833200);
near(r.sale.recap, 500000);                   // limited by depreciation taken
near(r.sale.fedTax, 391640);                  // 500,000 x 25% + 1,333,200 x 20%
near(r.sale.niitTax, 69661.6);                // 1,833,200 x 3.8%
near(r.sale.caTax, 243815.6);                 // 1,833,200 x 13.3%
near(r.sale.cash, 2128082.8, 0.05);
near(r.hold.ratePct, 39.3);
near(r.hold.afterRent, 60700);
near(r.hold.annuity, 4.3294767, 0.0001);
near(r.hold.pv, 262799.2, 0.5);
near(r.diff, 2128082.8 - 262799.2, 0.5);
assert.ok(/sale leaves/.test(r.verdict));

// 3. City tier boundaries (ledger TX-006, TX-007, TX-008) and the cliff at 5.4 million.
assert.strictEqual(C.cityRate(5400000, R), 0.45);
assert.strictEqual(C.cityRate(5400001, R), 4.45);
assert.strictEqual(C.cityRate(10899999, R), 4.45);
assert.strictEqual(C.cityRate(10900000, R), 5.95);
near(C.compute(Object.assign({}, full, { price: "5400000" }), R).sale.transferTotal, 30240);      // 0.56%
near(C.compute(Object.assign({}, full, { price: "5400001" }), R).sale.transferTotal, 246240.05, 0.1); // 4.56%
near(C.compute(Object.assign({}, full, { price: "10900000" }), R).sale.transferTotal, 660540);    // 6.06%

// 4. No gain means no tax; a gain is never taxed below zero.
r = C.compute(Object.assign({}, full, { basis: "9000000" }), R);
assert.strictEqual(r.sale.taxes, 0);
assert.strictEqual(r.sale.gain < 0, true);

// 5. Recapture cannot exceed the gain.
r = C.compute(Object.assign({}, full, { dep: "9999999" }), R);
near(r.sale.recap, r.sale.gain);
near(r.sale.capPart, 0);

// 6. Zero discount rate: the annuity factor is the number of years.
r = C.compute(Object.assign({}, full, { disc: "0" }), R);
near(r.hold.annuity, 5);

// 7. Validation: out-of-range percent, negative money, fractional years, non-numeric text.
assert.ok(C.compute(Object.assign({}, full, { ttShare: "150" }), R).errors.length === 1);
assert.ok(C.compute(Object.assign({}, full, { price: "-5" }), R).errors.length === 1);
assert.ok(C.compute(Object.assign({}, full, { years: "2.5" }), R).errors.length === 1);
assert.ok(C.compute(Object.assign({}, full, { years: "0" }), R).errors.length === 1);
assert.ok(C.compute(Object.assign({}, full, { costs: "abc" }), R).errors.length === 1);
assert.strictEqual(C.compute(Object.assign({}, full, { niit: "" }), R).ok, false);

// 8. Money formatting.
assert.strictEqual(C.money(1234.4), "$1,234");

console.log("calculator tests: all assertions passed");
