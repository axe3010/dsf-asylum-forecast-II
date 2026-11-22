# Predicting monthly asylum applications in Switzerland

Projet de groupe - Data Science Fundamentals (HSG)

**Collaborators:** Louis Bitar, Thibaud Marti, Axel Walther, Fedor Kleymenov (Group 11)

**This repository** is a copy of the group repository [fedorkleymenov-sketch/dsf-projet-groupe](https://github.com/fedorkleymenov-sketch/dsf-projet-groupe) (full history kept, up to commit `a116e8d`), with the analyses added after the test integrated into the notebook pipeline (marked † below).

**Goal:** Forecast the number of asylum applications in Switzerland one to three months ahead, to support the capacity planning of federal reception places.

## Run

Goal: reproduce all outputs (figures and tables) from the raw data.

- Install the packages in `requirements.txt` (`python -m pip install -r requirements.txt` from the project root).
- Open `code/main.ipynb`, restart the kernel and run all cells.
- Use `code/` as the working directory. If you start at the project root, run `%cd code` in a notebook cell first.

## Workflow

The notebooks follow one pattern: `01` prepares the data, `02` produces backtest forecasts, `03` evaluates them and chooses the model, `04` tests the chosen model once. There are **two model families**, each with a linear regression, Ridge and Lasso:

1. **The series' own past** (`02b`): the family of our chosen model.
2. **Own past + indicators** (`02c`): the Frontex routes (our plan); after the test, the applications in the neighbouring countries, the Mediterranean routes at the UNHCR timing and a conflict index, each alone, all together, and all but one, to see which data lower the error the most. The Frontex routes are not in "all indicators": the Mediterranean routes carry the same numbers one month earlier, and did better in the backtest.

**Added after the test.** The group chose the model (`03`, section 8, commit `c6a3976`) and then used the test period once (`04`, commit `4f284f5`). Everything marked † was added afterwards: it is labelled as such in each notebook, judged on the backtest only, and does not change the chosen model or its test result.

1. `01_preprocess.ipynb`: load and check the monthly series, split the months by time (first training window, backtest, test), explore the months before the test period, save `data/processed/asylum_clean.csv`.
1b. `01b_preprocess_indicators.ipynb`: all indicators. Part A: the Frontex detections by route, summed over the Central Mediterranean, Eastern Mediterranean and Western Balkan routes; saves `routes_clean.csv`. † Part B: applications in Germany, Austria, France and Italy (Eurostat), monthly arrivals in Italy, Greece and Spain (UNHCR, the Frontex numbers one month earlier), Swiss applications by citizenship (Eurostat) and conflict deaths (UCDP); saves `extra_indicators_clean.csv`, `nationality_shares_clean.csv` and `conflict_intensity_clean.csv`. For every source: checks, what is known at the cutoff, exploration before the test period; logs (log(1 + x) where a month can be 0) and changes, never levels.
2. `02_estimate.ipynb`: seasonal naive, 12-month average and three (S)ARIMA models in an expanding-window backtest (141 origins, h = 1, 2, 3), plus † the random walk (last known month); saves `data/processed/backtest_forecasts.csv`. About 30 seconds.
2b. `02b_estimate_regression.ipynb`: **family 1**, linear regression, Ridge and Lasso on the series' own past (one model per horizon); the penalty is chosen on two validation blocks inside each training window; scaling inside the pipeline. Saves `backtest_forecasts_regression.csv`. About 60 seconds.
2c. `02c_estimate_indicator.ipynb`: **family 2**, the same three regressions with indicators, same backtest and rules. Part A: + the Frontex routes (`backtest_forecasts_indicator.csv`). † Part B: the neighbours, the Mediterranean routes and the conflict index, each alone, all together, and all but one block (`backtest_forecasts_extra.csv`), and which indicators Lasso keeps (`output/tables/02c_lasso_kept.csv`). About nine minutes.
2d. † `02d_estimate_lag_choice.ipynb`: would an older month work better? The lag (0 to 12 months) is chosen together with `alpha` inside each training window. Saves `backtest_forecasts_lag_choice.csv` and `output/tables/02d_chosen_lags.csv`. About five minutes.
2e. † `02e_estimate_one_year.ipynb`: a second horizon for annual planning, the total of the next 12 months (94 origins), with and without indicators. Saves `backtest_forecasts_one_year.csv`.
3. `03_evaluate.ipynb`: **Part A** (sections 1 to 8, before the test): backtest errors of the eleven planned models (MAE in persons, RMSE in logs), main comparison at h = 2, without the crisis periods, year by year, does the route indicator help? Section 8 chooses the final model: the linear regression. **† Part B** (sections 9 to 19): the random walk as a third simple rule; each indicator alone; **which data lower the MSE the most** (all indicators, minus one block at a time, and Lasso's choice); year by year and the success rule; the two families side by side (model 2 = the best regression with all indicators, chosen by code); the one-year horizon; would any of this change the choice (no). The test period is not used.
4. `04_test.ipynb`: the chosen linear regression and the 12-month average on the test period (2024-10 to 2026-09), used once; refit at each origin on the months known then. Saves `test_forecasts.csv`, `output/tables/04_test_errors.csv` and a figure. † Section 8, information only: the random walk, and both model families on the same test months, including which indicators help there (`output/tables/04_test_errors_added_after.csv`).
5. † `05_ranges_and_forecast.ipynb`: 80% and 90% ranges from the past errors of the chosen model, how often the actual number falls inside them, and the forecast from the newest data (origin September 2026).

`main.ipynb` runs all notebooks in this order (about 25 minutes). Rerunning it from the raw data reproduces the same outputs (no random steps; seed fixed at 42).

## Main result

Forecasting two months ahead, the linear regression on the series' own past misses by 188 applications per month on average in the test period (2024-10 to 2026-09), against 331 for the 12-month average (43% lower MAE). In the backtest (2013 to 2024-09) the gain was 32% (358 against 528). The route indicator (Frontex) did not improve the forecasts, because it is published too late.

### Added after the test (†)

- **Random walk:** the simplest rule, "next months like the last known month", misses by 379 applications per month in the backtest ($h = 2$) and 269 in the test period. It was not among our planned baselines. Our linear regression is 5.4% better in the backtest (better in 7 of 12 years, so against this rule the 10% success rule would not be met) and 30% better in the test period.
- **Two model families:** the best model with all indicators (Ridge with the neighbours, the Mediterranean routes and the conflict index) misses by 342 applications per month in the backtest ($h = 2$) against 358 for our linear regression (−4.4%, better in 9 of 12 years): below the 10% of our success rule.
- **Which data help:** in the backtest, the Mediterranean routes at the UNHCR timing lower the error the most (removing them raises Ridge's MSE by 9%); the neighbouring countries make it worse. On the test months (information only, `04` section 8), the model with all indicators misses by 249 against 208 for our model, and the ranking flips: the small backtest gain does not hold.
- **Lags:** the route data lead Swiss applications by one month only; letting the model choose the lag (0 to 12 months) inside each window never beats the newest month.
- **One year ahead:** "next 12 months = last 12 months" is the best rule (error about 31%); no model or block beats it.
- **Ranges:** the 80% range from past errors contains 80% of the actual numbers in the backtest (about ±30% at $h = 2$), but is too wide in calm periods and too narrow at the start of a crisis.

## Data

- `data/raw/frontex_detections_by_route_monthly.csv`: Frontex detections of illegal border-crossings by route, 2009-01 to 2026-09 (file dated 4 November 2026).
- `data/raw/eurostat_asylum_ch_monthly.csv`: Eurostat `migr_asyappctzm`, Switzerland, all citizenships, 2008-01 to 2026-09. Source, download date and checks against SEM's figures in `data/raw/SOURCES.md`.
- Extra indicators (†, read in `01b` Part B): `estat_migr_asyappctzm_neighbours_en.csv`, `estat_migr_asyappctzm_ch_by_citizenship_en.csv` (Eurostat), `unhcr_italy_sea_arrivals_by_month.json`, `unhcr_greece_sea_land_arrivals_by_month.csv`, `unhcr_spain_sea_land_arrivals_by_month.csv` (UNHCR) and `ucdp_ged261_country_month_deaths.csv` (UCDP GED 26.1, summed by country and month). Sources, download dates and checks in `data/raw/SOURCES.md`.
