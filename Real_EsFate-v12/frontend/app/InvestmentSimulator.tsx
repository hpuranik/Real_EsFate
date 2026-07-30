'use client';

import React, { useMemo, useState } from 'react';
import styles from './InvestmentSimulator.module.css';
import {
  simulateInvestment,
  APPRECIATION_SCENARIOS,
  SimulatorInputs,
} from '../lib/mortgage';

interface Props {
  tractName: string;
}

type ScenarioKey = keyof typeof APPRECIATION_SCENARIOS | 'custom';
type Mode = 'land' | 'property';

// Mode-specific defaults. Land loans typically carry shorter terms, higher
// rates, and higher down payment requirements than residential mortgages --
// these aren't arbitrary, they reflect how land financing actually differs
// from improved-property financing. Still fully editable by the user.
const MODE_DEFAULTS: Record<Mode, { downPaymentPct: number; rate: number; termYears: number }> = {
  land: { downPaymentPct: 35, rate: 8.0, termYears: 10 },
  property: { downPaymentPct: 20, rate: 6.5, termYears: 30 },
};

function formatMoney(n: number): string {
  return n.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
}

function formatPct(n: number | null): string {
  if (n === null) return 'N/A';
  return `${n.toFixed(1)}%`;
}

export default function InvestmentSimulator({ tractName }: Props) {
  const [open, setOpen] = useState(false);
  const [mode, setMode] = useState<Mode>('land');
  const [purchasePrice, setPurchasePrice] = useState(120000);
  const [downPaymentPct, setDownPaymentPct] = useState(MODE_DEFAULTS.land.downPaymentPct);
  const [mortgageRate, setMortgageRate] = useState(MODE_DEFAULTS.land.rate);
  const [loanTermYears, setLoanTermYears] = useState(MODE_DEFAULTS.land.termYears);
  const [isCashPurchase, setIsCashPurchase] = useState(false);
  const [holdYears, setHoldYears] = useState(10);
  const [monthlyIncome, setMonthlyIncome] = useState(0);
  const [monthlyCosts, setMonthlyCosts] = useState(150); // property tax / carrying cost starting point
  const [scenario, setScenario] = useState<ScenarioKey>('moderate');
  const [customAppreciation, setCustomAppreciation] = useState(4.0);

  // Switching modes resets financing assumptions to that mode's realistic
  // defaults -- a land-loan rate left over from "land" mode would silently
  // mislead a property calculation, and vice versa.
  function handleModeChange(newMode: Mode) {
    setMode(newMode);
    setDownPaymentPct(MODE_DEFAULTS[newMode].downPaymentPct);
    setMortgageRate(MODE_DEFAULTS[newMode].rate);
    setLoanTermYears(MODE_DEFAULTS[newMode].termYears);
    if (newMode === 'property') {
      setPurchasePrice(250000);
      setMonthlyCosts(0);
    } else {
      setPurchasePrice(120000);
      setMonthlyIncome(0);
      setMonthlyCosts(150);
    }
  }

  const appreciationPct =
    scenario === 'custom' ? customAppreciation : APPRECIATION_SCENARIOS[scenario].annualPct;

  const result = useMemo(() => {
    const inputs: SimulatorInputs = {
      purchasePrice,
      downPaymentPct,
      annualMortgageRatePct: mortgageRate,
      loanTermYears,
      holdPeriodYears: holdYears,
      monthlyRentalIncome: monthlyIncome,
      monthlyExpenses: monthlyCosts,
      annualAppreciationPct: appreciationPct,
      isCashPurchase,
    };
    return simulateInvestment(inputs);
  }, [
    purchasePrice,
    downPaymentPct,
    mortgageRate,
    loanTermYears,
    holdYears,
    monthlyIncome,
    monthlyCosts,
    appreciationPct,
    isCashPurchase,
  ]);

  if (!open) {
    return (
      <button className={styles.openBtn} onClick={() => setOpen(true)}>
        Simulate an investment in {tractName}
      </button>
    );
  }

  return (
    <div className={styles.simulator}>
      <div className={styles.simHeader}>
        <h3>Investment Simulator</h3>
        <button className={styles.collapseBtn} onClick={() => setOpen(false)}>
          Hide
        </button>
      </div>

      <p className={styles.disclaimer}>
        The appreciation rate below is your own assumption, not a platform forecast -- pick a
        scenario or type a custom rate. The math (amortization, ROI, IRR) is deterministic.
      </p>

      <div className={styles.modeRow}>
        <button
          className={`${styles.modeBtn} ${mode === 'land' ? styles.modeActive : ''}`}
          onClick={() => handleModeChange('land')}
        >
          Land / Lot
        </button>
        <button
          className={`${styles.modeBtn} ${mode === 'property' ? styles.modeActive : ''}`}
          onClick={() => handleModeChange('property')}
        >
          Income Property
        </button>
      </div>
      <p className={styles.modeNote}>
        {mode === 'land'
          ? "Land financing differs from a residential mortgage: shorter loan terms, higher down payments, higher rates, and almost never any rental income. Defaults below reflect that -- profit here comes from appreciation, not cash flow."
          : 'Models a financed purchase that may generate rental income during the hold, with profit from both cash flow and appreciation at exit.'}
      </p>

      <label className={styles.checkboxRow}>
        <input
          type="checkbox"
          checked={isCashPurchase}
          onChange={(e) => setIsCashPurchase(e.target.checked)}
        />
        Cash purchase (no loan){mode === 'land' ? ' -- common for raw land' : ''}
      </label>

      <div className={styles.inputGrid}>
        <label>
          Purchase price
          <input
            type="number"
            value={purchasePrice}
            onChange={(e) => setPurchasePrice(Number(e.target.value))}
          />
        </label>

        {!isCashPurchase && (
          <>
            <label>
              Down payment (%)
              <input
                type="number"
                value={downPaymentPct}
                onChange={(e) => setDownPaymentPct(Number(e.target.value))}
              />
            </label>
            <label>
              Loan rate (%/yr)
              <input
                type="number"
                step="0.1"
                value={mortgageRate}
                onChange={(e) => setMortgageRate(Number(e.target.value))}
              />
            </label>
            <label>
              Loan term (years)
              <input
                type="number"
                value={loanTermYears}
                onChange={(e) => setLoanTermYears(Number(e.target.value))}
              />
            </label>
          </>
        )}

        <label>
          Hold period (years)
          <input
            type="number"
            value={holdYears}
            onChange={(e) => setHoldYears(Number(e.target.value))}
          />
        </label>
        <label>
          {mode === 'land' ? 'Monthly income (optional -- lease, parking, etc.)' : 'Monthly rental income'}
          <input
            type="number"
            value={monthlyIncome}
            onChange={(e) => setMonthlyIncome(Number(e.target.value))}
          />
        </label>
        <label>
          {mode === 'land' ? 'Monthly carrying costs (tax, insurance)' : 'Monthly expenses (tax, insurance, maintenance)'}
          <input
            type="number"
            value={monthlyCosts}
            onChange={(e) => setMonthlyCosts(Number(e.target.value))}
          />
        </label>
      </div>

      <div className={styles.scenarioRow}>
        {(Object.keys(APPRECIATION_SCENARIOS) as (keyof typeof APPRECIATION_SCENARIOS)[]).map((key) => (
          <button
            key={key}
            className={`${styles.scenarioBtn} ${scenario === key ? styles.scenarioActive : ''}`}
            onClick={() => setScenario(key)}
          >
            {APPRECIATION_SCENARIOS[key].label}
            <span className={styles.scenarioPct}>{APPRECIATION_SCENARIOS[key].annualPct}%/yr</span>
          </button>
        ))}
        <button
          className={`${styles.scenarioBtn} ${scenario === 'custom' ? styles.scenarioActive : ''}`}
          onClick={() => setScenario('custom')}
        >
          Custom
          <input
            type="number"
            step="0.1"
            className={styles.customInput}
            value={customAppreciation}
            onClick={(e) => e.stopPropagation()}
            onChange={(e) => {
              setScenario('custom');
              setCustomAppreciation(Number(e.target.value));
            }}
          />
        </button>
      </div>

      <div className={styles.resultsGrid}>
        {!isCashPurchase && (
          <div className={styles.resultCard}>
            <div className={styles.resultValue}>{formatMoney(result.monthlyMortgagePayment)}</div>
            <div className={styles.resultLabel}>Monthly loan payment</div>
          </div>
        )}
        <div className={styles.resultCard}>
          <div className={styles.resultValue}>{formatMoney(result.projectedSaleValue)}</div>
          <div className={styles.resultLabel}>Projected sale value (yr {holdYears})</div>
        </div>
        <div className={styles.resultCard}>
          <div className={styles.resultValue}>{formatMoney(result.equityAtExit)}</div>
          <div className={styles.resultLabel}>Equity at exit</div>
        </div>
        <div className={`${styles.resultCard} ${result.totalProfit >= 0 ? styles.positive : styles.negative}`}>
          <div className={styles.resultValue}>{formatMoney(result.totalProfit)}</div>
          <div className={styles.resultLabel}>Total profit</div>
        </div>
        <div className={styles.resultCard}>
          <div className={styles.resultValue}>{formatPct(result.cashOnCashAnnualizedPct)}</div>
          <div className={styles.resultLabel}>Annualized cash-on-cash return</div>
        </div>
        <div className={styles.resultCard}>
          <div className={styles.resultValue}>{formatPct(result.annualizedIRRPct)}</div>
          <div className={styles.resultLabel}>Annualized IRR</div>
        </div>
      </div>

      {result.monthlyNetCashFlow < 0 && (
        <p className={styles.negativeCashFlowNote}>
          Note: monthly cash flow during the hold is {formatMoney(result.monthlyNetCashFlow)}
          {' '}(negative) at these inputs -- you'd be funding the difference out of pocket each month.
          {mode === 'land' && ' This is normal for land -- carrying costs with no income is the typical case.'}
        </p>
      )}
    </div>
  );
}
