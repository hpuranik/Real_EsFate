/**
 * Investment simulator math. Pure functions, no network calls, no platform
 * "forecast" -- every appreciation/rent assumption here is something the
 * USER types in or picks from a labeled scenario preset. That distinction
 * matters: this file computes honest financial math on assumptions you
 * supply, it does not claim to have predicted the future. See the
 * conversation history (methodology honesty fixes) for why that line
 * matters for this project specifically.
 */

export interface SimulatorInputs {
  purchasePrice: number;
  downPaymentPct: number; // 0-100
  annualMortgageRatePct: number; // e.g. 6.5
  loanTermYears: number; // 30 for typical residential mortgage, 5-15 for land loans
  holdPeriodYears: number;
  monthlyRentalIncome: number; // 0 if not modeling rental income
  monthlyExpenses: number; // taxes/insurance/maintenance/HOA, 0 if not modeling
  annualAppreciationPct: number; // the user's assumption, not a forecast
  isCashPurchase: boolean; // true = no loan at all (common for land)
}

export interface SimulatorResult {
  loanAmount: number;
  monthlyMortgagePayment: number;
  projectedSaleValue: number;
  remainingLoanBalance: number;
  equityAtExit: number;
  totalCashInvested: number;
  totalProfit: number;
  cashOnCashAnnualizedPct: number | null;
  annualizedIRRPct: number | null;
  monthlyNetCashFlow: number;
}

/** Standard amortization formula. */
export function monthlyMortgagePayment(
  principal: number,
  annualRatePct: number,
  termYears: number
): number {
  const r = annualRatePct / 100 / 12;
  const n = termYears * 12;
  if (r === 0) return principal / n;
  const factor = Math.pow(1 + r, n);
  return (principal * r * factor) / (factor - 1);
}

/** Remaining loan balance after `monthsElapsed` payments. */
export function remainingBalance(
  principal: number,
  annualRatePct: number,
  termYears: number,
  monthsElapsed: number
): number {
  const r = annualRatePct / 100 / 12;
  const n = termYears * 12;
  const payment = monthlyMortgagePayment(principal, annualRatePct, termYears);
  if (r === 0) return Math.max(principal - payment * monthsElapsed, 0);
  const factor = Math.pow(1 + r, monthsElapsed);
  const balance = principal * factor - payment * ((factor - 1) / r);
  return Math.max(balance, 0);
}

/**
 * Monthly IRR via bisection on NPV(r) = 0, then annualized.
 * cashFlows[0] is the initial outlay (negative), last entry includes exit proceeds.
 */
export function computeIRR(cashFlows: number[]): number | null {
  const npv = (monthlyRate: number) =>
    cashFlows.reduce((sum, cf, t) => sum + cf / Math.pow(1 + monthlyRate, t), 0);

  let lo = -0.99; // can't lose more than 100%/month
  let hi = 1.0; // 100%/month ceiling, generous
  const npvLo = npv(lo);
  const npvHi = npv(hi);

  // No sign change across the bracket -> no solvable IRR (e.g. all positive
  // or all negative cash flows). Don't fabricate a number.
  if ((npvLo > 0 && npvHi > 0) || (npvLo < 0 && npvHi < 0)) {
    return null;
  }

  let mid = 0;
  for (let i = 0; i < 100; i++) {
    mid = (lo + hi) / 2;
    const v = npv(mid);
    if (Math.abs(v) < 1e-6) break;
    if ((v > 0) === (npvLo > 0)) {
      lo = mid;
    } else {
      hi = mid;
    }
  }

  const annualRate = Math.pow(1 + mid, 12) - 1;
  return annualRate * 100;
}

export function simulateInvestment(inputs: SimulatorInputs): SimulatorResult {
  const {
    purchasePrice,
    downPaymentPct,
    annualMortgageRatePct,
    loanTermYears,
    holdPeriodYears,
    monthlyRentalIncome,
    monthlyExpenses,
    annualAppreciationPct,
    isCashPurchase,
  } = inputs;

  const downPayment = isCashPurchase ? purchasePrice : purchasePrice * (downPaymentPct / 100);
  const loanAmount = isCashPurchase ? 0 : purchasePrice - downPayment;
  const payment = isCashPurchase ? 0 : monthlyMortgagePayment(loanAmount, annualMortgageRatePct, loanTermYears);
  const monthsHeld = Math.round(holdPeriodYears * 12);

  const projectedSaleValue =
    purchasePrice * Math.pow(1 + annualAppreciationPct / 100, holdPeriodYears);
  const balanceAtExit = isCashPurchase
    ? 0
    : remainingBalance(loanAmount, annualMortgageRatePct, loanTermYears, monthsHeld);
  const equityAtExit = projectedSaleValue - balanceAtExit;

  const monthlyNetCashFlow = monthlyRentalIncome - payment - monthlyExpenses;
  const totalCashInvested = downPayment;
  const totalCashFlowDuringHold = monthlyNetCashFlow * monthsHeld;
  const totalProfit = equityAtExit - totalCashInvested + totalCashFlowDuringHold;

  const cashOnCashAnnualizedPct =
    totalCashInvested > 0 && holdPeriodYears > 0
      ? (Math.pow(
          (equityAtExit + totalCashFlowDuringHold) / totalCashInvested,
          1 / holdPeriodYears
        ) -
          1) *
        100
      : null;

  // Monthly cash flow series for IRR: -downPayment at t=0, net monthly
  // cash flow each month, plus exit equity added to the final month.
  const cashFlows: number[] = [-totalCashInvested];
  for (let m = 1; m <= monthsHeld; m++) {
    cashFlows.push(m === monthsHeld ? monthlyNetCashFlow + equityAtExit : monthlyNetCashFlow);
  }
  const annualizedIRRPct = computeIRR(cashFlows);

  return {
    loanAmount,
    monthlyMortgagePayment: payment,
    projectedSaleValue,
    remainingLoanBalance: balanceAtExit,
    equityAtExit,
    totalCashInvested,
    totalProfit,
    cashOnCashAnnualizedPct,
    annualizedIRRPct,
    monthlyNetCashFlow,
  };
}

/** Labeled scenarios, not a platform forecast -- the user picks one (or
 * types a custom rate). These are round, conservative-leaning numbers, not
 * derived from this project's mock signals. */
export const APPRECIATION_SCENARIOS = {
  conservative: { label: "Conservative", annualPct: 2.0 },
  moderate: { label: "Moderate", annualPct: 4.0 },
  optimistic: { label: "Optimistic", annualPct: 7.0 },
} as const;
