import numpy as np
import pandas as pd
import pytest

from mlt.evaluation import bootstrap_sharpe_diff, metrics, sharpe, simulate

IDX = pd.date_range("2024-01-01", periods=6, freq="1h", tz="UTC")


def px(values):
    return pd.Series(values, index=IDX, dtype=float)


def test_flat_earns_nothing_and_costs_nothing():
    out = simulate(px([100, 101, 99, 100, 102, 103]), px([0] * 6), fee_rate=0.001)
    assert (out["net"] == 0).all()


def test_long_and_hold_pays_one_entry_cost_and_earns_the_move():
    close = px([100, 110, 121, 121, 121, 121])
    out = simulate(close, px([1] * 6), fee_rate=0.001)
    # decided at close of bar 0, held from bar 1: earns +10% and +10%, pays one entry cost on bar 1
    assert out["held"].iloc[0] == 0 and out["held"].iloc[1] == 1
    assert out["net"].iloc[1] == pytest.approx(0.10 - 0.001)
    assert out["net"].iloc[2] == pytest.approx(0.10)
    assert out["cost"].sum() == pytest.approx(0.001)


def test_decision_at_t_cannot_earn_the_move_ending_at_t():
    close = px([100, 100, 200, 200, 200, 200])
    a = simulate(close, px([0, 1, 0, 0, 0, 0]))   # long decided at bar 1, held over bar 2: earns +100%
    b = simulate(close, px([0, 0, 1, 0, 0, 0]))   # long decided at bar 2: misses the jump
    assert a["net"].iloc[2] == pytest.approx(1.0)
    assert b["net"].sum() == pytest.approx(0.0)


def test_reversal_charges_two_units_of_turnover():
    out = simulate(px([100] * 6), px([1, 1, -1, -1, 0, 0]), fee_rate=0.001)
    # entries: 0->1 (1 unit), 1->-1 (2 units), -1->0 (1 unit)
    assert out["cost"].sum() == pytest.approx(0.004)


def test_funding_long_pays_short_receives_and_missing_is_counted():
    close = px([100] * 6)
    rate = pd.Series([0.001] * 4, index=IDX[:4])   # bars 4 and 5 have no observation
    long = simulate(close, px([1] * 6), funding_1h=rate)
    short = simulate(close, px([-1] * 6), funding_1h=rate)
    assert long["funding"].sum() == pytest.approx(0.001 * 3)    # held on bars 1..3 with a rate
    assert short["funding"].sum() == pytest.approx(-0.001 * 3)
    assert long.attrs["n_missing_funding"] == 2
    lagged = simulate(close, px([1] * 6), funding_1h=rate, funding_lag=1)
    # lag 1: the rate stamped at bar k applies to bar k+1, so bars 1..4 each pay 0.001; bar 0 and 5 have none
    assert lagged["funding"].sum() == pytest.approx(0.001 * 4)
    assert lagged.attrs["n_missing_funding"] == 2


def test_index_mismatch_rejected():
    with pytest.raises(ValueError):
        simulate(px([100] * 6), pd.Series([1.0] * 6))


def test_metrics_known_values():
    net = pd.Series([0.10, -0.10] + [0.0] * 8)
    m = metrics(net, held=pd.Series([0, 1, 1, 0, 0, 0, 0, 0, 0, 0], dtype=float))
    assert m["total_return"] == pytest.approx(1.1 * 0.9 - 1)
    assert m["max_drawdown"] == pytest.approx(0.9 - 1)
    assert m["trades"] == 2 and m["exposure"] == pytest.approx(0.2)
    assert np.isfinite(m["sharpe"])


def test_sharpe_matches_the_metrics_function():
    net = pd.Series(np.random.default_rng(0).normal(0.0002, 0.004, 3000))
    assert sharpe(net) == pytest.approx(metrics(net)["sharpe"])


def test_bootstrap_identical_series_has_zero_difference():
    net = pd.Series(np.random.default_rng(1).normal(0.0001, 0.004, 2000))
    out = bootstrap_sharpe_diff(net, net, block=100, n_boot=200)
    assert out["diff"] == 0 and out["lo"] == 0 and out["hi"] == 0


def test_bootstrap_detects_a_clear_difference_and_keeps_pairing():
    rng = np.random.default_rng(2)
    noise = rng.normal(0, 0.004, 4000)
    a = pd.Series(noise + 0.002)           # same noise, higher mean: the difference is certain
    b = pd.Series(noise)
    out = bootstrap_sharpe_diff(a, b, block=100, n_boot=300)
    assert out["lo"] > 0 and out["p_not_above_zero"] == 0.0
    c = pd.Series(rng.permutation(noise))          # same mean and std, different timing: the observed difference is 0
    wide = bootstrap_sharpe_diff(b, c, block=100, n_boot=300)
    assert wide["diff"] == pytest.approx(0.0, abs=1e-9)
    assert wide["lo"] < 0 < wide["hi"]


def test_bootstrap_rejects_short_or_mismatched_series():
    with pytest.raises(ValueError):
        bootstrap_sharpe_diff(pd.Series([0.0] * 50), pd.Series([0.0] * 50), block=100)
