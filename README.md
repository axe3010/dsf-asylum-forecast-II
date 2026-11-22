# Predicting monthly asylum applications in Switzerland

Projet de groupe - Data Science Fundamentals (HSG)

**Collaborators:** Louis Bitar, Thibaud Marti, Axel Walther, Fedor Kleymenov (Group 11)

**This repository** is a copy of the group repository [fedorkleymenov-sketch/dsf-projet-groupe](https://github.com/fedorkleymenov-sketch/dsf-projet-groupe) (full history kept, up to commit `a116e8d`), extended with a second model family (indicators), a third simple rule, a lag test, a one-year horizon and ranges for planners, all in one pipeline.

**Goal:** Forecast the number of asylum applications in Switzerland one to three months ahead, to support the capacity planning of federal reception places.

## Run

Goal: reproduce all outputs (figures and tables) from the raw data.

- Install the packages in `requirements.txt` (`python -m pip install -r requirements.txt` from the project root).
- Open `code/main.ipynb`, restart the kernel and run all cells.
- Optional: `python 00_download_target.py` (from `code/`) downloads the target again from Eurostat. Recent months may differ slightly from the stored vintage, because Eurostat revises them.
- Use `code/` as the working directory. If you start at the project root, run `%cd code` in a notebook cell first.

## Workflow

`01` prepares the data, `02` produces backtest forecasts, `03` evaluates them and chooses the model, `04` tests all candidates once, `05` gives the planner ranges and the newest forecast. There are **two model families**, each with a linear regression, Ridge and Lasso:

1. **The series' own past** (`02b`).
2. **Own past + indicators** (`02c`): the Frontex routes towards Switzerland, the asylum applications in Germany, Austria, France and Italy (both known up to month $t-1$ at the cutoff) and a conflict index for the countries of origin (share of violent events in the news coded by GDELT, weighted by the nationalities of recent applicants, with its lag of 0 to 12 months chosen inside each training window); each alone, each pair and all three. GDELT is coded every day and never revised, so it is known at the cutoff in every month, up to October 2026. UNHCR's monthly arrivals (start only in 2014 to 2018) and UCDP's conflict deaths (revised final numbers, ending in December 2025) are not used.

**Timeline.** The group fixed the choice rule and chose the linear regression on 17 November 2026 (commit `c6a3976`), then ran the test once (commit `4f284f5`). The random walk, the neighbouring countries, the conflict index, the lag test (`02d`) and the one-year horizon (`02e`) were added afterwards, on the backtest only. The rule was not changed and still chooses the linear regression, so the test result of the chosen model is the same as in the first run.

1. `01_preprocess.ipynb`: load and check the monthly series, split the months by time (first training window, backtest, test), explore the months before the test period, save `data/processed/asylum_clean.csv`.
1b. `01b_preprocess_indicators.ipynb`: the three indicators: Frontex detections on the Central Mediterranean, Eastern Mediterranean and Western Balkan routes; applications in DE + AT + FR + IT (Eurostat, the same dataset as the target); and the inputs of the conflict index (shares of the nationalities in Swiss applications, GDELT share of violent events). Checks, what is known at the cutoff, exploration before the test period; saves `routes_clean.csv`, `neighbours_clean.csv`, `nationality_shares_clean.csv` and `conflict_intensity_clean.csv`.
2. `02_estimate.ipynb`: seasonal naive, 12-month average, random walk and three (S)ARIMA models in an expanding-window backtest (141 origins, h = 1, 2, 3); saves `backtest_forecasts.csv`. About 30 seconds.
2b. `02b_estimate_regression.ipynb`: **family 1**, linear regression, Ridge and Lasso on the series' own past (one model per horizon); scaling inside the pipeline; the penalty is chosen on two validation blocks inside each training window. Saves `backtest_forecasts_regression.csv`. About 60 seconds.
2c. `02c_estimate_indicator.ipynb`: **family 2**, the same regressions with each indicator, each pair and all three; same backtest and rules; the conflict lag chosen inside each window; which indicators Lasso keeps. Saves `backtest_forecasts_indicator.csv`, `output/tables/02c_lasso_kept.csv` and `02c_conflict_lags.csv`. About ten minutes.
2d. `02d_estimate_lag_choice.ipynb`: would an older indicator month work better? The lag (1 to 12 months) is chosen together with `alpha` inside each training window. Saves `backtest_forecasts_lag_choice.csv` and `output/tables/02d_chosen_lags.csv`. About four minutes.
2e. `02e_estimate_one_year.ipynb`: a second horizon for annual planning, the total of the next 12 months (94 origins). Saves `backtest_forecasts_one_year.csv`.
3. `03_evaluate.ipynb`: backtest errors of all 32 models (MAE in persons, MSE and RMSE in logs); main comparison at h = 2; without the crisis periods; year by year; errors by horizon; do the indicators help (family 2 against family 1, year by year, success rule) and which data lower the error the most; the two families side by side; the one-year horizon; the choice before the test (section 10): the linear regression. The test period is not used.
4. `04_test.ipynb`: all candidates on the test period (2024-10 to 2026-09) in one table, the forecasts made as in the backtest (refit at each origin on the months known then); main comparison of the chosen model with the 12-month average; test against backtest; month by month; which data help on the test months. Saves `test_forecasts.csv`, `output/tables/04_test_errors.csv` and a figure.
5. `05_ranges_and_forecast.ipynb`: 80% and 90% ranges from the past errors of the chosen model, how often the actual number falls inside them, and the forecast from the newest data (origin September 2026).

`main.ipynb` runs all notebooks in this order (about 20 minutes). Rerunning it from the raw data reproduces the same outputs (no random steps; seed fixed at 42).

## Main result

Forecasting two months ahead, the linear regression on the series' own past misses by **188 applications per month** on average in the test period (2024-10 to 2026-09), against 331 for the 12-month average (43% lower MAE) and 269 for the random walk (30% lower). In the backtest (2013 to 2024-09) the gain was 32% against the 12-month average (358 against 528), but only 5% against the random walk (379).

- **Indicators (family 2):** the routes, the neighbouring countries and the conflict index (at its lag chosen in each window), alone or together, give no regression a lower backtest MAE at h = 2 (+0.9% to +9.3%), and none meets the success rule. On the test months, model 2 (Ridge with all three indicators) misses by 190, practically the same as our model (188); the models with indicators range from 182 to 213, a spread of a few persons per month over 23 months.
- **Which data help:** removing any indicator from the models with all three mostly lowers the error; Lasso keeps only the newest route month at most origins (81%).
- **Lags:** the chosen lag jumps around for every indicator (the conflict lag between all lags from 0 to 12) and never beats a fixed lag: there is no stable delay the data can pick up.
- **One year ahead:** "next 12 months = last 12 months" is the best rule (error about 31%); no model or indicator beats it.
- **Ranges:** the 80% range from past errors contains 80% of the actual numbers in the backtest (about ±30% at h = 2), but is too wide in calm periods and too narrow at the start of a crisis.

## Data

- `data/raw/eurostat_asylum_ch_monthly.csv`: Eurostat `migr_asyappctzm`, Switzerland, all citizenships, 2008-01 to 2026-09 (target).
- `data/raw/frontex_detections_by_route_monthly.csv`: Frontex detections of illegal border-crossings by route, 2009-01 to 2026-09 (file dated 4 November 2026).
- `data/raw/estat_migr_asyappctzm_neighbours_en.csv`: the same Eurostat dataset for Germany, Austria, France and Italy (and Switzerland as a check), 2008-01 to 2026-09.
- `data/raw/estat_migr_asyappctzm_ch_by_citizenship_en.csv`: the same dataset for Switzerland by citizenship (weights of the conflict index).
- `data/raw/gdelt_events_by_country_month.csv`: GDELT 1.0 events by country and month (all events and violent events, CAMEO root codes 18 to 20), 2006-01 to 2026-10, exported from Google BigQuery.

Sources, download dates and checks in `data/raw/SOURCES.md`.
