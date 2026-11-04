"""Research helpers: causal position -> PnL accounting and performance metrics.

Conventions (the backtest module must reproduce them):
- ``target[t]`` is the position decided at the CLOSE of bar ``t`` using data up to ``t`` and
  executed at that close. It is held over bar ``t+1`` (the move from close ``t`` to close ``t+1``).
  The function shifts ``target`` itself, so a caller cannot introduce look-ahead by mistake.
- Position is a fraction of equity: +1 = fully long, -1 = fully short, 0 = flat (1x leverage).
- Costs are ``(fee_rate + slippage_rate) * |change in held position|``, charged on the bar in
  which the new position is first held; entering from flat at the start counts as a trade.
- Funding: a long pays ``interest_1h`` per hour while the rate is positive and a short receives
  it (ASSUMED sign and timing, not verified against the venue; see ``funding_lag`` and run the
  sensitivity before trusting a result). Missing funding observations are reported in
  ``result.attrs["n_missing_funding"]`` and replaced by ``missing_funding`` explicitly.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

HOURS_PER_YEAR = 8760


def simulate(
    close: pd.Series,
    target: pd.Series,
    fee_rate: float = 0.0,
    slippage_rate: float = 0.0,
    funding_1h: pd.Series | None = None,
    funding_lag: int = 0,
    missing_funding: float = 0.0,
) -> pd.DataFrame:
    """Per-bar accounting of a position series. Columns: ret, held, gross, cost, funding, net, equity."""
    if not close.index.equals(target.index):
        raise ValueError("close and target must share the same index")
    if (close <= 0).any() or close.isna().any():
        raise ValueError("close must be finite and positive")
    ret = close.pct_change().fillna(0.0)
    held = target.shift(1).fillna(0.0)
    gross = held * ret
    turnover = held.diff().abs()
    turnover.iloc[0] = abs(held.iloc[0])
    cost = (fee_rate + slippage_rate) * turnover
    n_missing = 0
    if funding_1h is None:
        fund = pd.Series(0.0, index=close.index)
    else:
        rate = funding_1h.reindex(close.index)
        if funding_lag:
            rate = rate.shift(funding_lag)
        n_missing = int(rate.isna().sum())
        fund = held * rate.fillna(missing_funding)
    net = gross - cost - fund
    out = pd.DataFrame(
        {"ret": ret, "held": held, "gross": gross, "cost": cost, "funding": fund,
         "net": net, "equity": (1.0 + net).cumprod()}
    )
    out.attrs["n_missing_funding"] = n_missing
    return out


def metrics(net: pd.Series, held: pd.Series | None = None,
            periods_per_year: int = HOURS_PER_YEAR) -> dict:
    """Headline numbers of a net-return series (all net of whatever costs the series contains)."""
    n = len(net)
    equity = (1.0 + net).cumprod()
    final = float(equity.iloc[-1])
    years = n / periods_per_year
    vol = float(net.std(ddof=1)) * np.sqrt(periods_per_year) if n > 1 else float("nan")
    mean_ann = float(net.mean()) * periods_per_year
    out = {
        "bars": n,
        "total_return": final - 1.0,
        "cagr": final ** (1.0 / years) - 1.0 if final > 0 and years > 0 else -1.0,
        "ann_vol": vol,
        "sharpe": mean_ann / vol if vol and vol > 0 else float("nan"),
        "max_drawdown": float((equity / equity.cummax() - 1.0).min()),
    }
    if held is not None:
        change = held.diff().abs()
        change.iloc[0] = abs(held.iloc[0])
        out["exposure"] = float((held != 0).mean())
        out["trades"] = int((change > 0).sum())
        out["turnover_per_year"] = float(change.sum()) / years if years > 0 else float("nan")
    return out


def sharpe(net: np.ndarray | pd.Series, periods_per_year: int = HOURS_PER_YEAR) -> float:
    """Annualised Sharpe ratio of a net-return series (no risk-free rate)."""
    a = np.asarray(net, dtype=float)
    sd = a.std(ddof=1) if len(a) > 1 else 0.0
    return float(a.mean() / sd * np.sqrt(periods_per_year)) if sd > 0 else float("nan")


def bootstrap_sharpe_diff(
    net_a: pd.Series,
    net_b: pd.Series,
    block: int = 168,
    n_boot: int = 1000,
    seed: int = 0,
    periods_per_year: int = HOURS_PER_YEAR,
) -> dict:
    """Paired circular block bootstrap of ``sharpe(a) - sharpe(b)`` on the same bars.

    Both series are resampled with the SAME blocks, so their correlation is preserved. Returns the
    observed difference, a 95 % percentile interval and the share of resamples with a difference
    not above zero. It captures sampling noise, not selection bias from trying many candidates.
    """
    a = np.asarray(net_a, dtype=float)
    b = np.asarray(net_b, dtype=float)
    if len(a) != len(b) or len(a) < 2 * block:
        raise ValueError("series must have the same length and at least two blocks")
    n = len(a)
    rng = np.random.default_rng(seed)
    n_blocks = -(-n // block)
    starts = rng.integers(0, n, size=(n_boot, n_blocks))
    idx = ((starts[:, :, None] + np.arange(block)[None, None, :]) % n).reshape(n_boot, -1)[:, :n]
    ra, rb = a[idx], b[idx]

    def sh(x: np.ndarray) -> np.ndarray:
        sd = x.std(axis=1, ddof=1)
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.where(sd > 0, x.mean(axis=1) / sd * np.sqrt(periods_per_year), np.nan)

    diffs = sh(ra) - sh(rb)
    lo, hi = np.nanpercentile(diffs, [2.5, 97.5])
    return {"diff": sharpe(a, periods_per_year) - sharpe(b, periods_per_year),
            "lo": float(lo), "hi": float(hi), "p_not_above_zero": float(np.nanmean(diffs <= 0))}
