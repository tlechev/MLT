# Changelog

Dated history of what changed and why. Groups: Added, Changed, Fixed, Removed, Docs.

<!-- changelog:start -->

## 2026-10-29

### Added
- R-002 in the research log (baselines on the owner's run: flat, buy-and-hold and the previous linear model with costs and funding; cost, funding and calendar-year sensitivity; shifted-timing test)
- ADR 0004 (evaluation protocol: fixed data window and time blocks), proposed
- mlt.protocol (frozen data window, development / validation / test blocks, a guard on the test block, purge for batch training) with 6 unit tests; ADR 0004 accepted with that evidence
- R-003 in the research log (baselines per block under the protocol: development and validation; sensitivity to the 23-bar change of the window start; timing test)
- ADR 0005 (data handling: zero-volume candles kept and flagged, missing funding counted as zero), accepted with tests as evidence; protocol.require_window (fails if the cache does not cover the frozen window)

### Changed
- notebook 02_baselines is done with its findings filled from the printed numbers; STATUS next steps now start with the protocol decision and the data-handling decisions
- notebook 02_baselines reads only the frozen window and adds the development / validation baseline table (status in progress until re-run); ADR 0004 clarified so that test-block baselines are produced in notebook 04
- DATA_START set to the first candle of the owner's cache (2023-10-30 22:00); notebook 01 uses the frozen window constants, notebook 02 checks coverage and prints the dates of the data exceptions; STATUS step 3 is now the model comparison
- ADR 0001 now holds the experiment plan for the model comparison (reference bars, four families, live-only features, walk-forward training, trial register, acceptance rule); awaiting the owner's approval

### Docs
- ARCHITECTURE contract for the protocol; STATUS next steps

## 2026-10-28

### Added
- evidence E41 (Coinbase support e-mail is disabled; requests go through the web form); V2 updated
- mlt.evaluation (simulate, metrics: causal position-to-PnL accounting with costs and funding), mlt.models.linear (OnlineLinear, the predecessor's SGD model as a baseline), mlt.models.online (run_online: causal walk-forward training), FrameCache.read (cache without network)
- notebook 02_baselines (flat, buy-and-hold, previous linear model, cost and funding sensitivity, calendar years, shifted-timing test); status in progress, to be run by the owner
- 13 unit tests for the accounting, the online model and the causal protocol

### Docs
- ARCHITECTURE contracts and principle for helpers built during research; STATUS step 3

## 2026-10-27

### Added
- evidence E38 (smoke test stage 1: authentication with the uri-claim JWT and read-only private calls succeed for the owner's key)
- evidence E39 (smoke test stage 2: a minimum-size post-only order was accepted, queried and cancelled on the Global Derivatives gateway)
- R-001 in the research log (01_data run by the owner: 26,280 clean hourly candles, 26,244 funding observations, specification identical to the Coinbase gateway); evidence E40

### Changed
- V3 now shows stages 0-1 done, stage 2 (order lifecycle) pending; STATUS step 1a narrowed to stage 2
- V3 closed technically for Global Derivatives, still open for the EU-licensed product; ADR 0002 stays proposed; STATUS step 1a removed and the route decision added to open questions
- notebook 01_data is done (comparison table and findings filled with the printed numbers); ADR 0003 result recorded; V2 recorded as not obtainable in writing through chat support; STATUS steps updated


## 2026-10-26

### Added
- evidence E37 (smoke test stage 0: public gateway reachable from the owner's location; contract specification and fee fields read)

### Changed
- ADR 0003 records the gateway's contract specification; STATUS step 1a narrowed to stages 1-2
- smoke test validates the key file (clear errors for a wrong format or an Ed25519 key, never echoing secrets); runbook gets a Windows example

### Fixed
- removed the shebang from tools/coinbase_smoke_test.py (ruff EXE001 failed CI because git stores the file as non-executable); the script is run with python tools/coinbase_smoke_test.py

## 2026-10-25

### Added
- tools/coinbase_smoke_test.py (read-only stages plus one post-only order that is cancelled; refuses to place orders without a confirmation phrase) with 10 unit tests against a fake gateway, and docs/RUNBOOK_API_SMOKE_TEST.md
- evidence E35 (help-center chat) and E36 (gateway technical guide); V2 and V3 results updated

### Changed
- lint and CI now cover tools/; live/dev extras include PyJWT and cryptography

### Docs
- STATUS next step 1a (smoke test) and README documentation map


## 2026-10-24

### Added
- evidence E28 - the Derivatives Exchange desk does not handle retail questions; V2 to be retried through retail support
- evidence E29 - key terms of the Coinbase Bermuda User Agreement (Part A) that apply to the owner's Global Derivatives account
- evidence E30-E33 (Coinbase Bermuda agreement Parts B, D and Appendix 4: EEA clients are CBBM clients with a Luxembourg pledge, orders execute only on Deribit, market-data storage restriction, version differences)
- Deribit public provider (candles, funding, instrument spec) with retries, pagination and canonical close-time index; parquet cache with incremental download and atomic writes; find_gaps in the schema module
- 18 unit tests for the provider, the cache and gap detection (fake HTTP session, no network)
- notebooks/01_data with working cells for spec check, candles, quality checks and funding (status in progress; to be run by the owner)
- evidence E34 (Deribit Terms of Service: personal use only)

### Docs
- STATUS next step 1 names the correct channel
- STATUS risks on contract terms and on market-data licensing
- STATUS next step 3 and data-licensing risk updated

### Changed
- V1 now asks the owner to confirm the entity from the onboarding screen or e-mail and to read Part D (country-specific terms)
- V1 now names Coinbase Bermuda Ltd with Luxembourg custody as the serving entity, pending the owner's confirmation; ADR 0002 and 0003 updated

## 2026-10-23

### Added
- docs/evidence/venue-availability-2026-10-23.md - sourced review of Binance, Coinbase and Deribit availability for a Bulgarian resident, with verification checklist V1-V3
- ADR 0003 (traded instrument and research data source), proposed
- evidence E14-E19 and a comparison of EU-authorised derivatives routes (Coinbase, Kraken, OKX) in docs/evidence
- evidence E20 (owner's Coinbase account shows BTC_USDC-PERPETUAL on the Global Derivatives portfolio); V1 partly done
- evidence E21-E24 (Coinbase help: Global Derivatives served by Coinbase Bermuda Ltd for unlisted jurisdictions; EU-licensed product is the US derivatives offering via CBFSE; developer-docs answers)
- evidence E25-E27 (Coinbase Derivatives rulebook: BIP contract specification; EEA user agreement scope)

### Changed
- ADR 0002 renamed to 'Execution venue'; owner chose Coinbase on 2026-10-23, kept proposed until eligibility for Bulgaria is verified
- ADR 0002 now has an explicit decision rule and Kraken/OKX as ranked fallbacks; verification checklist gets V4
- evidence E15 verified from Coinbase's own page - true perpetuals for EEA users are served by non-EEA affiliates, not under an EU licence
- ADR 0002/0003 now require the EU-licensed Coinbase product to pass V1-V3 (incl. API); Global Derivatives perpetual demoted to an option needing the owner's own legal check
- ADR 0003 notes the hypothesis that Deribit public candles of the same contract are the traded series, to be verified in 01_data
- V1 narrowed to confirming the entity in the owner's agreement; V2 not answered by the docs assistant; V3 partly answered
- ADR 0003 option 1 records the contract mechanics; V1 points to the derivatives agreement, not the EEA user agreement

### Docs
- STATUS next steps and open questions rewritten around checks V1-V3; README constraints updated
- STATUS open questions note that the current Coinbase derivatives may be served by a non-EU entity
- STATUS risks updated (legal path and API path at Coinbase may not coincide)
- STATUS risk about over-broad API key permissions
- ADR 0002 and 0003 describe the two Coinbase routes by entity
- STATUS risk about the history and mechanics of the EU-licensed contract


## 2026-10-22

### Added
- project skeleton (config, canonical candle schema, Forecaster contract) with 19 unit tests, CI and pre-commit
- research notebooks 00-05 as outlines with explicit status lines
- decision records 0001 (model stack, proposed) and 0002 (traded instrument and venue, proposed)

### Docs
- documentation system - README, STATUS, ARCHITECTURE, RESEARCH_LOG, CHANGELOG, decisions with an evidence rule

### Fixed
- removed two stray empty directories from the first skeleton archive

