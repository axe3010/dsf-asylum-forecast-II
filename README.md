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

The notebooks follow one pattern: `01` prepares the data, `02` produces backtest forecasts, `03` evaluates them and chooses the model, `04` tests the chosen model once. A letter marks each extra data block or model family (`01b`/`02c` for the Frontex routes, `01c`/`02d` for the extra data).

**Added after the test.** The group chose the model (`03`, section 8, commit `c6a3976`) and then used the test period once (`04`, commit `4f284f5`). Everything marked † below was added afterwards. It is judged on the backtest only, labelled as added after the test in each notebook, and does not change the chosen model or its test result.

1. `01_preprocess.ipynb`: load and check the monthly series, split the months by time (first training window, backtest, test), explore the months before the test period, save `data/processed/asylum_clean.csv`.
1b. `01b_preprocess_indicators.ipynb`: load and check the Frontex detections by route, build the indicator (sum of the Central Mediterranean, Eastern Mediterranean and Western Balkan routes), state what is known at the cutoff, explore it before the test period, save `data/processed/routes_clean.csv`.
1c. † `01c_preprocess_extra_data.ipynb`: load and check four extra sources (applications in Germany, Austria, France and Italy; monthly arrivals in Italy, Greece and Spain from UNHCR; Swiss applications by citizenship; conflict deaths from UCDP), state what is known at the cutoff, explore them before the test period. UNHCR's arrivals are the Frontex route numbers, published one month earlier, so we use the Frontex history at the UNHCR timing. Saves `extra_indicators_clean.csv`, `nationality_shares_clean.csv` and `conflict_intensity_clean.csv` in `data/processed/`.
2. `02_estimate.ipynb`: seasonal naive, 12-month average and three (S)ARIMA models in an expanding-window backtest (141 origins, h = 1, 2, 3), plus † the random walk (last known month); saves `data/processed/backtest_forecasts.csv`. Runs in about 30 seconds.
2b. `02b_estimate_regression.ipynb`: linear regression, Ridge and Lasso on the series' own past (one model per horizon), same backtest; the penalty is chosen inside each training window. Saves `data/processed/backtest_forecasts_regression.csv`. Runs in about 60 seconds.
2c. `02c_estimate_indicator.ipynb`: the same three regressions plus two route features (changes of the indicator, using only months known at the cutoff), same backtest and same rules. Saves `data/processed/backtest_forecasts_indicator.csv`. Runs in about 60 seconds.
2d. † `02d_estimate_extra.ipynb`: the three regressions of `02b` plus one extra block at a time (neighbours, Mediterranean routes, a conflict index weighted by the nationalities of the last 12 months) and all three together, same backtest and same rules. Saves `data/processed/backtest_forecasts_extra.csv`. Runs in about four minutes.
2e. † `02e_estimate_lag_choice.ipynb`: would an older month work better? The lag (0 to 12 months) is chosen together with `alpha` inside each training window, so that the choice is tested out of sample. Saves `data/processed/backtest_forecasts_lag_choice.csv` and `output/tables/02e_chosen_lags.csv`. Runs in about ten minutes.
2f. † `02f_estimate_one_year.ipynb`: a second horizon for annual planning, the total of the next 12 months (94 origins), with and without the extra blocks. Saves `data/processed/backtest_forecasts_one_year.csv`.
3. `03_evaluate.ipynb`: **Part A** (sections 1 to 8, before the test): backtest errors of all eleven planned models (MAE in persons, RMSE in logs) per model and horizon; main comparison at h = 2; results without 2015-16 and 2020 and from 2022; year-by-year comparison; does the route indicator help? Section 8 writes down the final model before the test: the linear regression. **Part B** † (sections 9 to 17): the random walk as a third simple rule, each extra block against the same model without it (year by year, without the crisis periods, success rule), the one-year horizon, and whether any of this would change the choice (it does not). Saves tables in `output/tables/` and figures in `output/figures/`. The test period is not used.
4. `04_test.ipynb`: the chosen linear regression and the 12-month average on the test period (2024-10 to 2026-09), used once; forecasts made as in the backtest (refit at each origin on the months known then). Saves `data/processed/test_forecasts.csv`, `output/tables/04_test_errors.csv` and `output/figures/04_test_forecasts_h2.png`. † Section 8 adds, for information only, the random walk, Ridge and Ridge + Med routes on the same test months (`output/tables/04_test_errors_added_after.csv`); they are not used to choose.
5. † `05_ranges_and_forecast.ipynb`: 80% and 90% ranges from the past forecast errors of the chosen model, how often the actual number falls inside them (backtest and test), and the forecast from the newest data (origin September 2026). Saves `05_range_coverage.csv`, `05_forecast_from_2026_09.csv` and one figure.

`main.ipynb` runs all notebooks in this order (about 20 minutes, mostly `02d` and `02e`). Rerunning it from the raw data reproduces the same outputs (no random steps; seed fixed at 42).

## Main result

Forecasting two months ahead, the linear regression on the series' own past misses by 188 applications per month on average in the test period (2024-10 to 2026-09), against 331 for the 12-month average (43% lower MAE). In the backtest (2013 to 2024-09) the gain was 32% (358 against 528). The route indicator (Frontex) did not improve the forecasts, because it is published too late.

### Added after the test (†)

- **Random walk:** the simplest rule, "next months like the last known month", misses by 379 applications per month in the backtest ($h = 2$) and 269 in the test period. It was not among our planned baselines. Our linear regression is 5.4% better in the backtest (better in 7 of 12 years, so against this rule the 10% success rule would not be met) and 30% better in the test period.
- **Extra data:** no source meets the success rule. Applications in the neighbouring countries move at the same time as Swiss applications and make the forecasts worse; the conflict index changes little; the Mediterranean routes at the UNHCR timing help a little (Ridge −4.8%, better in 8 of 12 years, but small against the spread across years). Choosing the lag inside each window or combining the sources does not change this. On the test months (information only, `04` section 8), Ridge + Med routes is 9% worse than Ridge without them (209 against 192 at $h = 2$): the small backtest gain does not hold.
- **One year ahead:** "next 12 months = last 12 months" is the best rule (error about 31%); no model or block beats it.
- **Ranges:** the 80% range from past errors contains 80% of the actual numbers in the backtest (about ±30% at $h = 2$), but is too wide in calm periods and too narrow at the start of a crisis.

## Data

- `data/raw/frontex_detections_by_route_monthly.csv`: Frontex detections of illegal border-crossings by route, 2009-01 to 2026-09 (file dated 4 November 2026).
- `data/raw/eurostat_asylum_ch_monthly.csv`: Eurostat `migr_asyappctzm`, Switzerland, all citizenships, 2008-01 to 2026-09. Source, download date and checks against SEM's figures in `data/raw/SOURCES.md`.
- Extra data (†, read in `01c`): `estat_migr_asyappctzm_neighbours_en.csv`, `estat_migr_asyappctzm_ch_by_citizenship_en.csv` (Eurostat), `unhcr_italy_sea_arrivals_by_month.json`, `unhcr_greece_sea_land_arrivals_by_month.csv`, `unhcr_spain_sea_land_arrivals_by_month.csv` (UNHCR) and `ucdp_ged261_country_month_deaths.csv` (UCDP GED 26.1, summed by country and month). Sources, download dates and checks in `data/raw/SOURCES.md`.
