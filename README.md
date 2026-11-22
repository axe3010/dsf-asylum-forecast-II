# Predicting monthly asylum applications in Switzerland

Projet de groupe - Data Science Fundamentals (HSG)

**Collaborators:** Louis Bitar, Thibaud Marti, Axel Walther, Fedor Kleymenov (Group 11)

**This repository** is a copy of the group repository [fedorkleymenov-sketch/dsf-projet-groupe](https://github.com/fedorkleymenov-sketch/dsf-projet-groupe) (full history kept, up to commit `a116e8d`), extended with a second model family (indicators), a third simple rule and ranges for planners, all in one pipeline. The code follows the group's notebooks and the course notebooks as closely as possible.

**Goal:** Forecast the number of asylum applications in Switzerland one to three months ahead, to support the capacity planning of federal reception places.

## Run

Goal: reproduce all outputs (figures and tables) from the raw data.

- Install the packages in `requirements.txt` (`python -m pip install -r requirements.txt` from the project root).
- Open `code/main.ipynb`, restart the kernel and run all cells.
- Optional: `python 00_download_target.py` (from `code/`) downloads the target again from Eurostat. Recent months may differ slightly from the stored vintage, because Eurostat revises them.
- Use `code/` as the working directory. If you start at the project root, run `%cd code` in a notebook cell first.

## Workflow

`01` prepares the data, `02` produces backtest forecasts, `03` evaluates them and chooses the model, `04` tests the chosen model once, next to the best model with indicators, `05` gives the planner ranges and the newest forecast. There are **two model families**, each with a linear regression, Ridge and Lasso:

1. **The series' own past** (`02b`).
2. **Own past + indicators** (`02c`): the Frontex routes towards Switzerland, the asylum applications in Germany, Austria, France and Italy (both known up to month $t-1$ at the cutoff) and a conflict index for the countries of origin (share of violent events in the news coded by GDELT, weighted by the nationalities of recent applicants); every indicator enters with its change over the last month and over three months, the conflict changes ending at a lag of 0 to 12 months chosen inside each training window; each indicator alone and all three. GDELT is coded every day and never revised, so it is known at the cutoff in every month, up to October 2026. UNHCR's monthly arrivals (start only in 2014 to 2018) and UCDP's conflict deaths (revised final numbers, ending in December 2025) are not used.

**Timeline.** The group fixed the choice rule and chose the linear regression on 17 November 2026 (commit `c6a3976`), then ran the test once (commit `4f284f5`). The random walk, the neighbouring countries and the conflict index were added afterwards, on the backtest only. The rule was not changed and still chooses the linear regression, so the test result of the chosen model is the same as in the first run. Model 2 and the other extensions were built after that first test, so their test results are for information only. A one-year horizon (total of the next 12 months) was also tried and left out to keep the project simple; "next 12 months = last 12 months" was best there (see the git history).

1. `01_preprocess.ipynb`: load and check the monthly series, split the months by time (first training window, backtest, test), explore the months before the test period, save `data/processed/asylum_clean.csv`.
1b. `01b_preprocess_indicators.ipynb`: the three indicators: Frontex detections on the Central Mediterranean, Eastern Mediterranean and Western Balkan routes; applications in DE + AT + FR + IT (Eurostat, the same dataset as the target); and the conflict index (GDELT share of violent events in the 10 largest nationalities of the last 12 months, weighted by their shares). Checks, what is known at the cutoff, exploration before the test period; saves `routes_clean.csv`, `neighbours_clean.csv` and `conflict_clean.csv`.
2. `02_estimate.ipynb`: seasonal naive, 12-month average, random walk and SARIMA(0,1,1)(0,1,1)12 in an expanding-window backtest (141 origins, h = 1, 2, 3); saves `backtest_forecasts.csv`. About 30 seconds.
2b. `02b_estimate_regression.ipynb`: **family 1**, linear regression, Ridge and Lasso on the series' own past (one model per horizon); scaling inside the pipeline; the penalty is chosen on two validation blocks inside each training window. Saves `backtest_forecasts_regression.csv`. About 60 seconds.
2c. `02c_estimate_indicator.ipynb`: **family 2**, the same regressions with each indicator and with all three; same backtest and rules; the conflict lag chosen inside each window; which indicators Lasso keeps. Saves `backtest_forecasts_indicator.csv`, `output/tables/02c_lasso_kept.csv` and `02c_conflict_lags.csv`. About ten minutes.
3. `03_evaluate.ipynb`: backtest errors of all 19 models (MAE in persons, MSE and RMSE in logs); main comparison at h = 2; without the crisis periods; year by year; errors by horizon; do the indicators help (family 2 against family 1, year by year, success rule) and which data lower the error the most; the two families side by side; the choice before the test (section 9): the linear regression. The test period is not used.
4. `04_test.ipynb`: the chosen linear regression and model 2 (Ridge with all indicators), both chosen in `03`, with the 12-month average and the random walk, on the test period (2024-10 to 2026-09); the forecasts made as in the backtest (refit at each origin on the months known then); main comparison of the chosen model with the 12-month average; test against backtest; month by month. Saves `test_forecasts.csv`, `output/tables/04_test_errors.csv` and a figure.
5. `05_ranges_and_forecast.ipynb`: 80% and 90% ranges from the past errors of the chosen model, how often the actual number falls inside them, and the forecast from the newest data (origin September 2026).

`main.ipynb` runs all notebooks in this order (about 10 minutes). Rerunning it from the raw data reproduces the same outputs (no random steps; seed fixed at 42).

## Main result

Forecasting two months ahead, the linear regression on the series' own past misses by **188 applications per month** on average in the test period (2024-10 to 2026-09), against 331 for the 12-month average (43% lower MAE) and 269 for the random walk (30% lower). In the backtest (2013 to 2024-09) the gain was 32% against the 12-month average (358 against 528), but only 5% against the random walk (379).

- **Indicators (family 2):** the routes, the neighbouring countries and the conflict index (at its lag chosen in each window), alone or together, change the backtest MAE at h = 2 by −0.2% (Ridge with the conflict index, less than one person) to +11.9%, and none meets the success rule. Model 2 (Ridge with all three indicators) is 4% worse than our model in the backtest (372 against 358) and 3% better on the test (183 against 188): 5 persons per month over 23 calm months.
- **Which data help:** ranked by the change in MSE (log) when added alone at h = 2, the routes hurt the least (+2.4%), then the conflict index (+4.3%) and the neighbours (+4.4%); Lasso keeps only the newest route month at most origins (80%).
- **Lags:** the conflict lag chosen in each window jumps between lags from 0 to 12: there is no stable delay the data can pick up.
- **Ranges:** the 80% range from past errors contains 80% of the actual numbers in the backtest (about ±30% at h = 2), but is too wide in calm periods and too narrow at the start of a crisis.

## Data

- `data/raw/eurostat_asylum_ch_monthly.csv`: Eurostat `migr_asyappctzm`, Switzerland, all citizenships, 2008-01 to 2026-09 (target).
- `data/raw/frontex_detections_by_route_monthly.csv`: Frontex detections of illegal border-crossings by route, 2009-01 to 2026-09 (file dated 4 November 2026).
- `data/raw/estat_migr_asyappctzm_neighbours_en.csv`: the same Eurostat dataset for Germany, Austria, France and Italy (and Switzerland as a check), 2008-01 to 2026-09.
- `data/raw/estat_migr_asyappctzm_ch_by_citizenship_en.csv`: the same dataset for Switzerland by citizenship (weights of the conflict index).
- `data/raw/gdelt_events_by_country_month.csv`: GDELT 1.0 events by country and month (all events and violent events, CAMEO root codes 18 to 20), 2006-01 to 2026-10, exported from Google BigQuery.

Sources, download dates and checks in `data/raw/SOURCES.md`.
