# mlt — research-first ML trading framework for crypto perpetuals

> **mlt** is a framework for designing, *proving* and only then running a machine-learning trading strategy on a crypto perpetual. Every component is first justified in a research notebook and then built as a unit-tested module. Nothing is trusted because it "seems reasonable"; it is trusted because evidence is linked in this repository.

## Current status

<!-- BEGIN:auto:status -->
| | |
|---|---|
| **Current phase** | P1 – Research (in progress) |
| **Last synced** | 2026-11-05 |
| **Tests** | 78 passed, 0 failed |
| **Modules done** | 5 / 11 |
| **Decisions** | 2 accepted · 3 proposed · 0 rejected |
<!-- END:auto:status -->

**Focus now / next step:** see [docs/STATUS.md](docs/STATUS.md#current-focus) (kept in sync with every change).

## 1. Goals, non-goals and constraints

**Goals**
- Establish, with honest out-of-sample evidence, whether an ML model has a net-of-cost edge on the instrument we actually trade.
- Run *the same code* in research, backtest and live (parity), so a result in a notebook means something in production.
- Keep models, data venues and brokers swappable behind small contracts, so a better idea or a legal change never forces a rewrite.

**Non-goals**
- Guaranteed profit, high-frequency trading, or trading on any venue that is not legally accessible to the operator.

**Constraints and why they exist**

| Constraint | Why |
|---|---|
| Venue must be legally accessible from the operator's jurisdiction (Bulgaria / EU) | Binance withdrew its MiCA application and suspended EU derivatives from 2026-07-01 (secondary sources). Coinbase is the chosen venue ([ADR 0002](docs/decisions/0002-execution-venue.md), `proposed` until eligibility for Bulgaria is verified). Evidence: [docs/evidence](docs/evidence/venue-availability-2026-10-23.md). |
| Research instrument = traded instrument | In the predecessor project research used Binance spot BTCUSDT while the live bot traded a different perpetual; fees, funding and price series differ, so results did not transfer. |
| Only features that exist live | The predecessor's neural network used Binance-only fields that the live feed does not provide. |
| `DRY_RUN=true` by default | A mistake in configuration must never be able to place a real order. |

## 2. How we work (research-first)

1. **Stage 1 – Research (`notebooks/`)**: data → baselines → features/models → honest validation → decision.
   *Why:* an idea is cheap to test in a notebook and expensive to unwind from production code.
2. **Research gate** (all must hold): **G1** beats the baselines on a held-out period after costs and funding; **G2** is not sensitive to one lucky parameter set; **G3** uses only features available live; **G4** is reproducible from cached data and fixed seeds.
   *Why:* the predecessor's results were tuned and tested on the same period; the gate prevents that.
3. **Stage 2 – Build (`src/`)**: module by module in dependency order, each with unit tests, merged only when tests are green.
4. **Parity test**: the same input window must give the same prediction in the notebook, the backtest and the live engine.
5. **Decisions are evidence-based**: every non-trivial choice (model family, features, instrument, training scheme) is an ADR in [docs/decisions](docs/decisions/README.md) and is `accepted` only with a link to the experiment. Any model family may compete: linear, NN, gradient boosting, sequence models.

## 3. Roadmap

<!-- BEGIN:auto:phases -->
| Phase | Goal | Gate (exit criteria) | Status |
|---|---|---|---|
| P0 – Foundation | Repository skeleton, CI, config, candle schema, model contract. | Skeleton installs, lint is clean, unit tests pass in CI. | done |
| P1 – Research | Show with out-of-sample evidence whether a model has a net-of-cost edge on the traded instrument. | G1 beats baselines on a held-out period after costs and funding; G2 stable to parameter changes; G3 uses only features available live; G4 reproducible from cached data and fixed seeds. | in progress |
| P2 – Build | Implement the validated design module by module, each with unit tests. | All modules done; parity test (notebook = backtest = live engine) green; backtest reproduces notebook 04. | not started |
| P3 – Paper trading | Run the full engine on live data without orders. | Signals and PnL match the backtest within a tolerance defined in an ADR before the run starts. | not started |
| P4 – Live, minimal size | Trade real money with the smallest meaningful size and all risk limits on. | Defined in an ADR before go-live; requires written venue eligibility check. | not started |
<!-- END:auto:phases -->

## 4. Project structure

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

Module contracts and data flow: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## 5. Notebooks

<!-- BEGIN:auto:notebooks -->
| Notebook | Purpose | Status |
|---|---|---|
| [00_colab_bootstrap.ipynb](notebooks/00_colab_bootstrap.ipynb) | 00 – Colab bootstrap: Run this first in Google Colab (needed only for experiments that require PyTorch/GPU). | not started |
| [01_data.ipynb](notebooks/01_data.ipynb) | 01 – Data: Goal: load the perpetual we will actually trade, validate it, cache it. Checks: gaps, duplicates, closed candles only, UTC. Add funding rates. | done |
| [02_baselines.ipynb](notebooks/02_baselines.ipynb) | 02 – Baselines: Buy-and-hold, flat, and the previous linear model on the NEW data, with costs. | in progress |
| [03_features_model.ipynb](notebooks/03_features_model.ipynb) | 03 – Features and models: Only features that exist live. Compare model families fairly (same data, costs, splits). | in progress |
| [04_validation.ipynb](notebooks/04_validation.ipynb) | 04 – Validation: Tune on an early window; test ONCE on a held-out later window. Costs and funding included. | not started |
| [05_decision.ipynb](notebooks/05_decision.ipynb) | 05 – Decision: Does the candidate pass the research gate? Summarise evidence and update docs/decisions. | not started |
<!-- END:auto:notebooks -->

Experiment results with numbers, data period and costs: [docs/RESEARCH_LOG.md](docs/RESEARCH_LOG.md).

## 6. Decisions and evidence

<!-- BEGIN:auto:decisions -->
| ID | Decision | Status | Evidence |
|---|---|---|---|
| [0001](docs/decisions/0001-model-stack.md) | Model stack (NumPy core vs PyTorch) | proposed | – |
| [0002](docs/decisions/0002-execution-venue.md) | Execution venue | proposed | [docs/evidence/venue-availability-2026-10-23.md](docs/evidence/venue-availability-2026-10-23.md) |
| [0003](docs/decisions/0003-instrument-and-data-source.md) | Traded instrument and research data source | proposed | [docs/evidence/venue-availability-2026-10-23.md](docs/evidence/venue-availability-2026-10-23.md) |
| [0004](docs/decisions/0004-evaluation-protocol.md) | Evaluation protocol: fixed data window and time split | accepted | [tests/test_protocol.py](tests/test_protocol.py) |
| [0005](docs/decisions/0005-data-handling.md) | Data handling: zero-volume candles and missing funding | accepted | [tests/data/test_schema.py](tests/data/test_schema.py) |
<!-- END:auto:decisions -->

## 7. Recent changes

<!-- BEGIN:auto:changes -->
**2026-11-05**
- **Added:** notebook 03_features_model (reference bars incl. two no-ML trend rules; online linear, ridge, gradient boosting and small neural network; live-only features with a causality check; walk-forward training; trial register; selection on development, confirmation on validation; paired block bootstrap); status in progress, to be run by the owner
- **Added:** mlt.models.walkforward (causal batch retraining), mlt.models.sklearn_wrap (scikit-learn adapter for Forecaster), evaluation.sharpe and evaluation.bootstrap_sharpe_diff, with 8 unit tests; scikit-learn in the dev and research extras
- **Docs:** ARCHITECTURE contracts for the new helpers; ADR 0001 plan marked as approved; STATUS step 3

**2026-10-29**
- **Added:** R-002 in the research log (baselines on the owner's run: flat, buy-and-hold and the previous linear model with costs and funding; cost, funding and calendar-year sensitivity; shifted-timing test)
- **Added:** ADR 0004 (evaluation protocol: fixed data window and time blocks), proposed
- **Added:** mlt.protocol (frozen data window, development / validation / test blocks, a guard on the test block, purge for batch training) with 6 unit tests; ADR 0004 accepted with that evidence
- **Added:** R-003 in the research log (baselines per block under the protocol: development and validation; sensitivity to the 23-bar change of the window start; timing test)
- **Added:** ADR 0005 (data handling: zero-volume candles kept and flagged, missing funding counted as zero), accepted with tests as evidence; protocol.require_window (fails if the cache does not cover the frozen window)
- **Changed:** notebook 02_baselines is done with its findings filled from the printed numbers; STATUS next steps now start with the protocol decision and the data-handling decisions
- **Changed:** notebook 02_baselines reads only the frozen window and adds the development / validation baseline table (status in progress until re-run); ADR 0004 clarified so that test-block baselines are produced in notebook 04
- **Changed:** DATA_START set to the first candle of the owner's cache (2023-10-30 22:00); notebook 01 uses the frozen window constants, notebook 02 checks coverage and prints the dates of the data exceptions; STATUS step 3 is now the model comparison
- **Changed:** ADR 0001 now holds the experiment plan for the model comparison (reference bars, four families, live-only features, walk-forward training, trial register, acceptance rule); awaiting the owner's approval
- **Docs:** ARCHITECTURE contract for the protocol; STATUS next steps

**2026-10-28**
- **Added:** evidence E41 (Coinbase support e-mail is disabled; requests go through the web form); V2 updated
- **Added:** mlt.evaluation (simulate, metrics: causal position-to-PnL accounting with costs and funding), mlt.models.linear (OnlineLinear, the predecessor's SGD model as a baseline), mlt.models.online (run_online: causal walk-forward training), FrameCache.read (cache without network)
- **Added:** notebook 02_baselines (flat, buy-and-hold, previous linear model, cost and funding sensitivity, calendar years, shifted-timing test); status in progress, to be run by the owner
- **Added:** 13 unit tests for the accounting, the online model and the causal protocol
- **Docs:** ARCHITECTURE contracts and principle for helpers built during research; STATUS step 3

Full history: [docs/CHANGELOG.md](docs/CHANGELOG.md).
<!-- END:auto:changes -->

## 8. Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"      # core + tooling
pip install -e ".[torch]"    # only if an experiment needs it (see docs/decisions)
pre-commit install
make test                    # unit tests
make notebook                # JupyterLab
```
Heavy experiments (PyTorch/GPU) run in Google Colab via `notebooks/00_colab_bootstrap.ipynb`; the package is installed from this repository so Colab and local runs use the same code.

## 9. Safety, legal and disclaimers

- Live orders require **both** `DRY_RUN=false` **and** `LIVE_TRADING_CONFIRM=YES_I_UNDERSTAND`.
- Never commit credentials; key files live outside the repository.
- Venue availability and licensing differ per jurisdiction: verify eligibility yourself before trading. Nothing here is financial advice; trading can lose all invested capital.

## 10. Documentation map

| Document | Purpose |
|---|---|
| [docs/STATUS.md](docs/STATUS.md) | Current state, focus, next steps with reasons, open questions |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Modules, contracts, data flow, parity principle |
| [docs/RESEARCH_LOG.md](docs/RESEARCH_LOG.md) | Every experiment: setup, numbers, conclusion, link to notebook |
| [docs/decisions/README.md](docs/decisions/README.md) | Decision records (ADRs) and their evidence |
| [docs/evidence/](docs/evidence/venue-availability-2026-10-23.md) | Sources and verification checklist behind the venue decision |
| [docs/RUNBOOK_API_SMOKE_TEST.md](docs/RUNBOOK_API_SMOKE_TEST.md) | How to verify API trading safely (stages, safeguards, what to record) |
| [docs/CHANGELOG.md](docs/CHANGELOG.md) | Dated history of changes |
