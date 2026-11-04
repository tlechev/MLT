# Project status

Single place that answers "where are we, what is next and why". Tables are generated from the code, tests, notebooks and decision records (`<!-- auto -->` blocks, do not edit by hand); the sections below them are maintained by hand at every sync.

<!-- BEGIN:auto:status -->
| | |
|---|---|
| **Current phase** | P1 – Research (in progress) |
| **Last synced** | 2026-11-05 |
| **Tests** | 78 passed, 0 failed |
| **Modules done** | 5 / 11 |
| **Decisions** | 2 accepted · 3 proposed · 0 rejected |
<!-- END:auto:status -->

## Current focus

Phase **P1 – Research** is in progress. The data foundation ([R-001](RESEARCH_LOG.md)) and the baselines ([R-002](RESEARCH_LOG.md)) are done: at gateway costs with funding, buy-and-hold returned +57.9 % (Sharpe 0.59, drawdown −54.6 %) and the previous linear model +92.1 % (Sharpe 0.745, drawdown −35.3 %) on 2024-02 to 2026-10, but the model's parameters were tuned on this period, so that is a reference level, not an edge. The technical path to trade through the Coinbase gateway is verified (E37–E39); the legal basis is not ([ADR 0002](decisions/0002-execution-venue.md) stays `proposed`). The evaluation protocol ([ADR 0004](decisions/0004-evaluation-protocol.md)) and the data handling ([ADR 0005](decisions/0005-data-handling.md)) are accepted and implemented; the baselines per block are in [R-003](RESEARCH_LOG.md) (validation block: buy-and-hold −34.3 %, linear model +7.2 %). The next step is the model comparison. No claim of performance on unseen data is made anywhere in this repository.

## Next steps

Each step states **why** it is needed and its **exit criterion**, so progress is checkable.

| # | Step | Why it is needed | Done when |
|---|---|---|---|
| 1 | Run checks V1–V3 with Coinbase retail support at help.coinbase.com (not the Derivatives Exchange desk, E28): derivatives available for the account, serving entity and product, API access | Coinbase is chosen, but eligibility for a Bulgarian resident and API access are unverified; trading where it is not allowed is not an option | V1–V3 results recorded in the evidence file (V2 cannot be had in writing through chat support: use a written legal opinion); ADR 0002 `accepted`; if the checks fail, V4 (Kraken, then OKX) is run before any research is finalised |
| 2 | Accept [ADR 0003](decisions/0003-instrument-and-data-source.md) for the chosen route (owner decision) | Research must use the instrument that will be traded; the 01_data result supports the Deribit series for Global Derivatives | ADR 0003 `accepted` with its evidence linked; reopened if the route changes |
| 3 | Run `03_features_model` (written and dry-run on synthetic data with a planted signal; the owner runs it: first with `QUICK = True`, then the full run, roughly 10 minutes or more) and record it as R-004 with the trial register | A model is chosen only by experiment (ADR 0001); the bars are in R-002 and R-003 and the protocol is fixed (ADR 0004) | Notebook 03 `done`; R-004 with numbers and the trial count; ADR 0001 `accepted` or `rejected` with evidence |

## Open questions and risks

| Question / risk | Impact | Owner / how we resolve it |
|---|---|---|
| Is Bulgaria among the 26 countries where Coinbase offers EEA derivatives, and is the owner's account eligible? | Hard blocker for paper/live (P3/P4) and for choosing the research instrument | Owner runs V1–V2; result in the [evidence file](evidence/venue-availability-2026-10-23.md) |
| Can the EEA "perpetual-style" future be traded through the API, or only the Global Derivatives gateway? | Decides the broker adapter and what data can be cached. If the EU-licensed product has no API, an automated strategy cannot run legally at Coinbase and Kraken/OKX become the plan | V3; Coinbase docs or support |
| Coinbase states that true perpetual futures for EEA users come from non-EEA affiliates, not under an EU licence (E15); the owner's current product is most likely served by Coinbase Bermuda Ltd (E21, E29), whose agreement caps liability, uses Bermuda arbitration and allows liquidation and auto-deleveraging; only the CySEC futures product is EU-licensed (E4). The owner's current derivatives may be served by the non-EU route | Legal basis and traded product may differ from what the research assumes | V1 names the entity; use the EU-licensed product or a fallback venue |
| The owner's Coinbase API key carries `transfer` and `export` permissions in addition to `trade` and `view` | A leaked key could move funds; a trading bot needs only `view` and `trade` | Create a separate key with `view` + `trade` for the bot before any automated run; keep it outside the repository |
| The EU-licensed Coinbase contract (index-based, daily settlement, price limits) may have a short price history and different mechanics from the Deribit-based perpetual | Research on the wrong or too short a series would not transfer to the traded product | Compare in `01_data`; if only a proxy is usable, measure its difference first (ADR 0003) |
| The contract terms for the owner's current account are one-sided: liability capped at 12 months of fees (E33), Bermuda arbitration, a pledge over the assets in the derivatives account, liquidation and auto-deleveraging at the exchange's discretion (E29, E30) | Real losses beyond the owner's control; recourse is limited | Owner decides with these terms in view; independent legal advice recommended before real money |
| Market data obtained through Coinbase Bermuda may not be stored in a standalone database (E32) | A research cache built from it could breach the terms | Deribit's Terms of Service allow personal use only (E34, 2021 version): keep the cache private and unshared, and re-read the current terms before step 3 |
| Which Coinbase route is used for paper and live trading: Global Derivatives (technically verified, not under an EU licence, E15) or the EU-licensed product (API access undocumented) | Decides the broker adapter, the traded series and the legal basis | Owner decides after the written answer from Coinbase (V2) and, preferably, independent legal advice; Kraken/OKX remain fallbacks (V4) |
| Binance status rests on secondary sources only | Low; Binance is excluded either way | Optionally confirm against Binance's own notice |
| Coinbase API for derivatives changed on 2026-10-01 (JSON-RPC 2.0 gateway, no parallel run) | Any code written against the old INTX REST endpoints must be rewritten | Execution adapter is built only after ADR 0002 is accepted |
| Model family is open (linear, NN, boosting, sequence) | Avoid anchoring on the predecessor's setup | Compared fairly in `03_features_model`; tracked in [ADR 0001](decisions/0001-model-stack.md) |

## Modules

<!-- BEGIN:auto:modules -->
| Module | What it does | Status | Tests |
|---|---|---|---|
| `config` | Typed settings from environment; dry-run is the default, live needs an explicit confirmation phrase. | done | 4 |
| `data` | Candle providers (Deribit, Coinbase), one canonical OHLCV schema, validation, parquet cache. | done | 33 |
| `features` | Pure feature functions, identical in research, backtest and live (no look-ahead). | stub | 0 |
| `models` | Model-agnostic Forecaster contract plus the models that won experiments. | done | 11 |
| `evaluation` | Research helpers: causal position-to-PnL accounting with costs and funding, performance metrics. The backtest module must reproduce its conventions. | done | 11 |
| `protocol` | Evaluation protocol (ADR 0004): frozen data window, development / validation / test blocks, a guard on the test block. | done | 7 |
| `strategy` | Turns predictions into target positions (thresholds, cost filter). | stub | 0 |
| `risk` | Position limits, daily loss halt, liquidation distance. | stub | 0 |
| `backtest` | Walk-forward simulation with fees, slippage and funding; must reproduce notebook results. | stub | 0 |
| `execution` | Broker contract with a paper broker and the venue adapter; dry-run by default. | stub | 0 |
| `engine` | Wires data -> features -> model -> strategy -> risk -> execution into one live loop. | stub | 0 |
<!-- END:auto:modules -->

## Notebooks

<!-- BEGIN:auto:notebooks -->
| Notebook | Purpose | Status |
|---|---|---|
| [00_colab_bootstrap.ipynb](../notebooks/00_colab_bootstrap.ipynb) | 00 – Colab bootstrap: Run this first in Google Colab (needed only for experiments that require PyTorch/GPU). | not started |
| [01_data.ipynb](../notebooks/01_data.ipynb) | 01 – Data: Goal: load the perpetual we will actually trade, validate it, cache it. Checks: gaps, duplicates, closed candles only, UTC. Add funding rates. | done |
| [02_baselines.ipynb](../notebooks/02_baselines.ipynb) | 02 – Baselines: Buy-and-hold, flat, and the previous linear model on the NEW data, with costs. | in progress |
| [03_features_model.ipynb](../notebooks/03_features_model.ipynb) | 03 – Features and models: Only features that exist live. Compare model families fairly (same data, costs, splits). | in progress |
| [04_validation.ipynb](../notebooks/04_validation.ipynb) | 04 – Validation: Tune on an early window; test ONCE on a held-out later window. Costs and funding included. | not started |
| [05_decision.ipynb](../notebooks/05_decision.ipynb) | 05 – Decision: Does the candidate pass the research gate? Summarise evidence and update docs/decisions. | not started |
<!-- END:auto:notebooks -->

## Decisions

<!-- BEGIN:auto:decisions -->
| ID | Decision | Status | Evidence |
|---|---|---|---|
| [0001](decisions/0001-model-stack.md) | Model stack (NumPy core vs PyTorch) | proposed | – |
| [0002](decisions/0002-execution-venue.md) | Execution venue | proposed | [docs/evidence/venue-availability-2026-10-23.md](../docs/evidence/venue-availability-2026-10-23.md) |
| [0003](decisions/0003-instrument-and-data-source.md) | Traded instrument and research data source | proposed | [docs/evidence/venue-availability-2026-10-23.md](../docs/evidence/venue-availability-2026-10-23.md) |
| [0004](decisions/0004-evaluation-protocol.md) | Evaluation protocol: fixed data window and time split | accepted | [tests/test_protocol.py](../tests/test_protocol.py) |
| [0005](decisions/0005-data-handling.md) | Data handling: zero-volume candles and missing funding | accepted | [tests/data/test_schema.py](../tests/data/test_schema.py) |
<!-- END:auto:decisions -->
