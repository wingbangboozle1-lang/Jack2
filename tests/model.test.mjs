import test from 'node:test';
import assert from 'node:assert/strict';
import { project, reference, propertyInputs, saleDecision, buildScenarioSuite, validateAssumptions } from '../scripts/model.mjs';
const close = (a,b,tol=1e-8) => assert.ok(Math.abs(a-b)<tol,`${a} != ${b}`);

test('missing real property inputs remain null, never zero or fabricated', () => {
  assert.ok(Object.values(propertyInputs).every(v => v === null));
});
test('flat monthly annuity agrees with closed-form present value', () => {
  const a={...reference,leaseYears:10,escalation:0,landlordLeakage:0,exitCapRate:0.08,releasingCostMonths:0};
  const r=project(a), i=(1+a.discountRate)**(1/12)-1;
  const expected=100/12*(1-(1+i)**-120)/i + (100/0.08)*0.98/(1.09**10);
  close(r.pv,expected);
});
test('lease expiry, downtime and releasing cost land in the correct periods', () => {
  const r=project({...reference,leaseYears:4,escalation:0,landlordLeakage:0,downtimeMonths:12,releasingCostMonths:12});
  close(r.annual[3].rent,100); close(r.annual[3].releasingCost,100);
  close(r.annual[4].rent,0); close(r.annual[5].rent,100);
  close(r.releasingCostPV,100/(1.09**4));
});
test('six-month downtime produces six months of rent in the first post-vacancy year', () => {
  const r=project({...reference,leaseYears:4,escalation:0,landlordLeakage:0,downtimeMonths:6,releasingCostMonths:0});
  close(r.annual[4].rent,50); close(r.annual[5].rent,100);
});
test('rent reset is relative to initial rent, not the last escalated rent', () => {
  const r=project({...reference,leaseYears:4,escalation:0.1,rentReset:-0.2,downtimeMonths:0,releasingCostMonths:0,landlordLeakage:0});
  close(r.annual[4].rent,80);
});
test('vacant path has no post-expiry rent and uses only explicit residual hypothesis', () => {
  const r=project({...reference,leaseYears:4,outcome:'vacant',residualRentMultiple:3,downtimeMonths:0,releasingCostMonths:0});
  assert.ok(r.annual.slice(4).every(x=>x.rent===0));
  close(r.annual[9].terminal,294); close(r.postExpiryPV,0); close(r.pv,r.contractPV+r.terminalPV);
});
test('zero landlord leakage means rent is not silently reduced', () => {
  const r=project({...reference,landlordLeakage:0});
  close(r.annual[0].rent,100); close(r.annual[0].net,100);
});
test('scaling rent scales all value outputs linearly', () => {
  const a=project(), b=project({...reference,initialAnnualRent:200});
  close(a.pv*2,b.pv); close(a.presentValuePerUnitRent,b.presentValuePerUnitRent);
});
test('higher discount rate and exit cap reduce value; longer downtime reduces value', () => {
  assert.ok(project({discountRate:0.11}).pv<project({discountRate:0.07}).pv);
  assert.ok(project({exitCapRate:0.09}).pv<project({exitCapRate:0.065}).pv);
  assert.ok(project({downtimeMonths:24}).pv<project({downtimeMonths:6}).pv);
  assert.ok(project({rentReset:0.1}).pv>project({rentReset:-0.2}).pv);
});
test('annual present values reconcile to total including terminal and costs', () => {
  const r=project(); close(r.annual.reduce((s,x)=>s+x.presentValue,0),r.pv);
  close(r.contractPV+r.postExpiryPV+r.terminalPV,r.pv);
  close(r.annual.reduce((s,x)=>s+x.net,0),r.undiscountedNet);
});
test('invalid, nonfinite and inconsistent controls fail closed', () => {
  for (const a of [{discountRate:NaN},{discountRate:Infinity},{initialAnnualRent:0},{exitCapRate:0},{leaseYears:11},{leaseYears:4.5},{downtimeMonths:-1},{outcome:'unknown'},{outcome:'renew',downtimeMonths:1}]) assert.throws(()=>project(a));
});
test('no invented property value can produce a sell/hold recommendation', () => {
  assert.equal(saleDecision({netSaleValueBeforeDebtAndOwnerTax:null,holdPV:800}).recommendation,null);
  assert.equal(saleDecision({netSaleValueBeforeDebtAndOwnerTax:NaN,holdPV:800}).status,'insufficient-evidence');
});
test('same-basis comparison respects explicit buffer and equality boundary', () => {
  assert.equal(saleDecision({netSaleValueBeforeDebtAndOwnerTax:850,holdPV:800,riskAndLiquidityBuffer:50}).recommendation,'lean-sell');
  assert.equal(saleDecision({netSaleValueBeforeDebtAndOwnerTax:849,holdPV:800,riskAndLiquidityBuffer:50}).recommendation,'lean-hold');
  assert.throws(()=>saleDecision({netSaleValueBeforeDebtAndOwnerTax:900,holdPV:800,riskAndLiquidityBuffer:-1}));
});
test('scenario suite covers both expiry endpoints, paths, tail tests and sensitivities', () => {
  const s=buildScenarioSuite(); assert.equal(s.rows.length,16); assert.equal(s.sensitivities.length,15);
  assert.ok(s.rows.some(r=>r.leaseYears===4)); assert.ok(s.rows.some(r=>r.leaseYears===9));
  assert.ok(s.rows.every(r=>Number.isFinite(r.pv)));
  assert.ok(s.renewalPremiums.every(r=>r.value>0));
});
test('validation does not mutate the reference assumptions', () => {
  const before=JSON.stringify(reference); validateAssumptions({leaseYears:9}); assert.equal(JSON.stringify(reference),before);
});
