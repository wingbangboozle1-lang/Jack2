/**
 * Conditional, normalized NNN cash-flow laboratory. NOT an appraisal.
 * All money is divided by initial annual contractual base rent (R0).
 * No actual property input is supplied or inferred. Missing facts stay null.
 * Monthly end-of-period cash flows; annual effective discount/escalation.
 * Unlevered and before owner income taxes. Terminal selling costs are included.
 */
export const propertyInputs = Object.freeze({
  annualBaseRent: null, exactLeaseExpiry: null, marketRent: null,
  netSaleValue: null, debtPayoff: null, ownerTax: null, marketCapRate: null,
  landlordCosts: null, tenantRentCoverage: null, insuranceRecovery: null,
});

export const reference = Object.freeze({
  horizonYears: 10, leaseYears: 4, initialAnnualRent: 100,
  discountRate: 0.09, escalation: 0.015, landlordLeakage: 0.02,
  rentReset: 0, downtimeMonths: 12, releasingCostMonths: 12,
  exitCapRate: 0.075, sellingCost: 0.02, outcome: 'relet',
  residualRentMultiple: 0,
});

export function validateAssumptions(input) {
  const a = { ...reference, ...input };
  const ranges = {
    horizonYears: [1, 30], leaseYears: [0, 30], initialAnnualRent: [0.000001, 1e12],
    discountRate: [0.000001, 1], escalation: [-0.5, 1], landlordLeakage: [0, 1],
    rentReset: [-0.99, 5], downtimeMonths: [0, 360], releasingCostMonths: [0, 360],
    exitCapRate: [0.005, 1], sellingCost: [0, 1], residualRentMultiple: [0, 100],
  };
  for (const [key, [min, max]] of Object.entries(ranges)) {
    if (!Number.isFinite(a[key]) || a[key] < min || a[key] > max) {
      throw new RangeError(`${key} must be finite and between ${min} and ${max}`);
    }
  }
  for (const key of ['horizonYears', 'leaseYears', 'downtimeMonths', 'releasingCostMonths']) {
    if (!Number.isInteger(a[key])) throw new RangeError(`${key} must be an integer`);
  }
  if (a.leaseYears > a.horizonYears) throw new RangeError('Lease term cannot exceed horizon');
  if (!['renew', 'relet', 'vacant'].includes(a.outcome)) throw new RangeError('Unknown post-expiry outcome');
  if (a.outcome === 'renew' && (a.downtimeMonths !== 0 || a.releasingCostMonths !== 0)) {
    throw new RangeError('Renewal path assumes no downtime or releasing cost; use relet for concessions');
  }
  return a;
}

export function project(input = {}) {
  const a = validateAssumptions(input);
  const months = a.horizonYears * 12;
  const expiry = a.leaseYears * 12;
  const downtime = a.outcome === 'vacant' ? 0 : a.downtimeMonths;
  const monthlyBase = a.initialAnnualRent / 12;
  const annual = Array.from({ length: a.horizonYears }, (_, i) => ({
    year: i + 1, rent: 0, landlordCost: 0, releasingCost: 0, terminal: 0, net: 0, presentValue: 0,
  }));
  let contractPV = 0, postExpiryPV = 0;
  for (let m = 1; m <= months; m++) {
    const row = annual[Math.floor((m - 1) / 12)];
    let rent = 0;
    if (m <= expiry) {
      rent = monthlyBase * (1 + a.escalation) ** Math.floor((m - 1) / 12);
    } else if (a.outcome !== 'vacant' && m > expiry + downtime) {
      // Reset is relative to INITIAL rent, not the last escalated rent.
      const completedYearsAfterRelet = Math.floor((m - expiry - downtime - 1) / 12);
      rent = monthlyBase * (1 + a.rentReset) * (1 + a.escalation) ** completedYearsAfterRelet;
    }
    const cost = rent * a.landlordLeakage;
    const releasing = m === expiry && a.outcome === 'relet'
      ? monthlyBase * a.releasingCostMonths : 0;
    const df = (1 + a.discountRate) ** (-m / 12);
    const net = rent - cost - releasing;
    row.rent += rent; row.landlordCost += cost; row.releasingCost += releasing; row.net += net;
    row.presentValue += net * df;
    if (m <= expiry) contractPV += net * df; // includes any cost paid at expiry
    else postExpiryPV += net * df;
  }
  const last = annual.at(-1);
  const residual = a.outcome === 'vacant'
    ? a.initialAnnualRent * a.residualRentMultiple
    : Math.max(0, last.rent - last.landlordCost) / a.exitCapRate;
  last.terminal = residual * (1 - a.sellingCost);
  last.net += last.terminal;
  const terminalPV = last.terminal * (1 + a.discountRate) ** -a.horizonYears;
  last.presentValue += terminalPV;
  const pv = contractPV + postExpiryPV + terminalPV;
  const costPV = annual.reduce((s, r) => s + r.releasingCost, 0) *
    (expiry === 0 ? 1 : (1 + a.discountRate) ** -a.leaseYears);
  return {
    assumptions: a, annual, pv, presentValuePerUnitRent: pv / a.initialAnnualRent,
    contractPV, postExpiryPV, terminalPV, releasingCostPV: costPV,
    terminalShare: pv === 0 ? 0 : terminalPV / pv,
    undiscountedNet: annual.reduce((s, r) => s + r.net, 0),
  };
}

/** Same-basis sale benchmark: price minus selling costs, BEFORE debt and owner tax. */
export function saleDecision({ netSaleValueBeforeDebtAndOwnerTax, holdPV, riskAndLiquidityBuffer = 0 }) {
  if (![netSaleValueBeforeDebtAndOwnerTax, holdPV, riskAndLiquidityBuffer].every(Number.isFinite)) {
    return { status: 'insufficient-evidence', recommendation: null };
  }
  if (riskAndLiquidityBuffer < 0) throw new RangeError('Buffer cannot be negative');
  const threshold = holdPV + riskAndLiquidityBuffer;
  return {
    status: 'conditional-model-result', threshold,
    recommendation: netSaleValueBeforeDebtAndOwnerTax >= threshold ? 'lean-sell' : 'lean-hold',
    surplus: netSaleValueBeforeDebtAndOwnerTax - threshold,
  };
}

export function buildScenarioSuite() {
  const cases = {
    downside: { escalation: 0, landlordLeakage: 0.05, discountRate: 0.11, rentReset: -0.20, downtimeMonths: 24, releasingCostMonths: 24, exitCapRate: 0.09 },
    reference: {},
    upside: { escalation: 0.02, landlordLeakage: 0, discountRate: 0.07, rentReset: 0.10, downtimeMonths: 6, releasingCostMonths: 6, exitCapRate: 0.065 },
  };
  const rows = [];
  for (const [name, assumptions] of Object.entries(cases)) {
    for (const leaseYears of [4, 9]) {
      for (const outcome of ['relet', 'renew']) {
        const a = { ...reference, ...assumptions, leaseYears, outcome,
          ...(outcome === 'renew' ? { downtimeMonths: 0, releasingCostMonths: 0 } : {}) };
        rows.push({ id: `${name}-${leaseYears}-${outcome}`, family: 'expiry', name, leaseYears, outcome, ...project(a) });
      }
    }
  }
  for (const leaseYears of [2, 4, 9]) {
    const a = { ...reference, ...cases.downside, leaseYears, outcome: 'vacant', downtimeMonths: 0, releasingCostMonths: 0, residualRentMultiple: 3 };
    rows.push({ id: `vacant-${leaseYears}`, family: leaseYears === 2 ? 'early-exit stress' : 'expiry stress', name: 'No relet / residual only', leaseYears, outcome: 'vacant', ...project(a) });
  }
  const reletEarly = { ...reference, ...cases.downside, leaseYears: 2, outcome: 'relet' };
  rows.push({ id: 'early-exit-relet', family: 'early-exit stress', name: 'Downside', leaseYears: 2, outcome: 'relet', ...project(reletEarly) });
  const sensitivities = [];
  for (const [key, values] of Object.entries({
    discountRate: [0.07, 0.09, 0.11], exitCapRate: [0.065, 0.075, 0.09],
    downtimeMonths: [6, 12, 24], rentReset: [-0.20, 0, 0.10], escalation: [0, 0.015, 0.02],
  })) {
    for (const value of values) {
      const a = { ...reference, [key]: value };
      const result = project(a);
      sensitivities.push({ parameter: key, value, pv: result.pv, multiple: result.presentValuePerUnitRent, assumptions: a });
    }
  }
  return {
    disclaimer: 'Dimensionless stress tests, NOT property inputs, appraisals, market estimates, probabilities or confidence intervals. No missing factual field has been populated.',
    propertyInputs, reference, rows, sensitivities,
    renewalPremiums: [4, 9].map(term => ({
      leaseYears: term,
      value: project({ ...reference, leaseYears: term, outcome: 'renew', downtimeMonths: 0, releasingCostMonths: 0 }).pv - project({ ...reference, leaseYears: term }).pv,
    })),
  };
}
