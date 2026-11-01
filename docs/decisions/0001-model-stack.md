# 0001 – Model stack (NumPy core vs PyTorch)
- Status: proposed (hypothesis, NOT yet tested)

## Question
Which model families and training schemes should the production path support?

## Hypothesis
Small models can run on NumPy, keeping live inference light and identical to research.
Heavier models (sequence nets, GPU) may be trained in Colab and exported (NumPy/ONNX) for live.

## Experiment (plan, awaiting the owner's approval)
Notebook `03_features_model`, under the protocol of [ADR 0004](0004-evaluation-protocol.md), the data handling of [ADR 0005](0005-data-handling.md) and the cost model of R-002 / R-003 (taker 3.5 bp from the gateway, funding included). The test block is not read.

- **Reference bars:** flat, buy-and-hold, the previous linear model (R-003) and a no-ML trend rule (sign of the 24 h or 72 h return), to show whether machine learning adds anything over a rule.
- **Candidate families**, all behind the same `Forecaster` contract, with the same features and the same cost model: (1) online linear (SGD), retuned on development only; (2) ridge regression with batch rolling retraining; (3) gradient boosting (scikit-learn `HistGradientBoostingRegressor`); (4) a small neural network (scikit-learn `MLPRegressor` first; PyTorch only if an experiment justifies it).
- **Features** (gate G3: they must exist live): log returns over several windows, realised volatility, volume relative to its recent average, candle range, and the hourly funding rate known at the decision bar (lagged one bar). Nothing venue-specific beyond OHLCV and funding.
- **Target:** forward log return over a horizon H, with H taken from a small grid (for example 12, 24, 48 hours) chosen on development.
- **Training:** walk-forward with an expanding window, retraining every 168 bars, `purge_mask` before every fit; the online model learns from matured samples only.
- **Positions:** the sign of the prediction beyond a cost-based threshold; the threshold multiplier comes from a small grid chosen on development.
- **Selection:** configurations are ranked on development (walk-forward) and confirmed on validation. Every configuration tried is written to a trial register and its count is reported with the result, because the more are tried the more likely a lucky winner is.
- **Acceptance of a family:** net Sharpe on validation above the previous linear model and above the trend rule, with a paired block-bootstrap interval of the difference reported. The exact rule is fixed in notebook 04 before the test block is touched.
- **Out of scope for now:** sizing and leverage, bars shorter than one hour, other instruments.
