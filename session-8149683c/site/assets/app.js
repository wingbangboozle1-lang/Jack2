/* Jack2 — tiny vanilla dashboard helpers.
   Loads data/*.json with RELATIVE paths so the site works from a GitHub Pages
   project subpath (https://user.github.io/repo/) as well as from a file:// read. */
(function () {
  "use strict";

  const ROOT = (function () {
    // If this page sits in a subdirectory, data lives one level up.
    return document.documentElement.getAttribute("data-root") || ".";
  })();

  async function getJSON(rel) {
    const res = await fetch(ROOT + "/data/" + rel, { cache: "no-store" });
    if (!res.ok) throw new Error("HTTP " + res.status + " for " + rel);
    return res.json();
  }

  const fmtInt = (n) =>
    n === null || n === undefined || n === "" ? "" : Number(n).toLocaleString("en-US");

  function fmtMoney(n, dp) {
    if (n === null || n === undefined || n === "") return "";
    const v = Number(n);
    const sign = v < 0 ? "-" : "";
    const a = Math.abs(v);
    if (a >= 1e9) return sign + "$" + (a / 1e9).toFixed(dp === undefined ? 2 : dp) + "B";
    if (a >= 1e6) return sign + "$" + (a / 1e6).toFixed(dp === undefined ? 2 : dp) + "M";
    return sign + "$" + a.toLocaleString("en-US", { maximumFractionDigits: 0 });
  }

  function fmtPct(n, dp) {
    if (n === null || n === undefined || n === "") return "";
    return (Number(n) * 100).toFixed(dp === undefined ? 2 : dp) + "%";
  }

  function esc(s) {
    return String(s === null || s === undefined ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function pill(status, label) {
    const txt = label || status;
    return '<span class="pill ' + esc(status) + '">' + esc(txt) + "</span>";
  }

  // Render one category's rows into a table body.
  function rowsTable(rows, opts) {
    opts = opts || {};
    let h = '<div class="tablewrap"><table><thead><tr>' +
      "<th>ID</th><th>Metric</th><th>Value</th><th>Unit</th><th>As of</th>" +
      "<th>Scope</th><th>Status</th><th>Source</th><th>Note</th>" +
      "</tr></thead><tbody>";
    rows.forEach(function (r) {
      const srcLabel = r.url
        ? '<a href="' + esc(r.url) + '" target="_blank" rel="noopener noreferrer">' + esc(r.source) + " \u2197</a>"
        : '<span class="small">' + esc(r.source) + " (not supplied)</span>";
      const val = r.value === "" || r.value === null || r.value === undefined
        ? '<span class="blank">blank</span>'
        : esc(r.value);
      h += "<tr>" +
        "<td class=\"nowrap\"><code>" + esc(r.id) + "</code></td>" +
        "<td>" + esc(r.metric) + "</td>" +
        "<td class=\"num\">" + val + "</td>" +
        "<td class=\"small\">" + esc(r.unit) + "</td>" +
        "<td class=\"small nowrap\">" + esc(r.as_of) + "</td>" +
        "<td class=\"small\">" + esc(r.geo) + "</td>" +
        "<td>" + pill(r.status) + "</td>" +
        "<td class=\"small\">" + srcLabel + "</td>" +
        "<td class=\"small\">" + esc(r.note) + "</td>" +
        "</tr>";
    });
    return h + "</tbody></table></div>";
  }

  function countBy(rows) {
    const c = { VERIFIED: 0, DERIVED: 0, FLAGGED: 0, UNVERIFIED: 0 };
    rows.forEach(function (r) { if (c[r.status] !== undefined) c[r.status]++; });
    return c;
  }

  window.Jack2 = {
    ROOT: ROOT, getJSON: getJSON, fmtInt: fmtInt, fmtMoney: fmtMoney,
    fmtPct: fmtPct, esc: esc, pill: pill, rowsTable: rowsTable, countBy: countBy,
  };
})();
