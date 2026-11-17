# Predicting monthly asylum applications in Switzerland

Projet de groupe - Data Science Fundamentals (HSG)

**Collaborators:** Louis Bitar, Thibaud Marti, Axel Walther, Fedor Kleymenov (Group 11)

**Goal:** Forecast the number of asylum applications in Switzerland one to three months ahead, to support the capacity planning of federal reception places.

## Run

Goal: reproduce all outputs (figures and tables) from the raw data.

- Install the packages in `requirements.txt` (`python -m pip install -r requirements.txt` from the project root).
- Open `code/main.ipynb`, restart the kernel and run all cells.
- Use `code/` as the working directory. If you start at the project root, run `%cd code` in a notebook cell first.

## Workflow

1. `01_preprocess.ipynb`: load and check the monthly series, split the months by time (first training window, backtest, test), explore the months before the test period, save `data/processed/asylum_clean.csv`.
2. `02_estimate.ipynb`: seasonal naive, 12-month average and three (S)ARIMA models in an expanding-window backtest (141 origins, h = 1, 2, 3); saves `data/processed/backtest_forecasts.csv`. Runs in about 30 seconds.
2b. `02b_estimate_regression.ipynb`: linear regression, Ridge and Lasso on the series' own past (one model per horizon), same backtest; the penalty is chosen inside each training window. Saves `data/processed/backtest_forecasts_regression.csv`. Runs in about 75 seconds.
3. `03_evaluate.ipynb`: backtest errors of all eight models (MAE in persons, RMSE in logs) per model and horizon; main comparison at h = 2; results without 2015-16 and 2020 and from 2022; year-by-year comparison. Saves tables in `output/tables/` and figures in `output/figures/`. The test period is not used yet.

`main.ipynb` runs the four notebooks in order (about two minutes). Rerunning it from the raw data reproduces the same outputs (no random steps; seed fixed at 42).

## Data

- `data/raw/eurostat_asylum_ch_monthly.csv`: Eurostat `migr_asyappctzm`, Switzerland, all citizenships, 2008-01 to 2026-09. Source, download date and checks against SEM's figures in `data/raw/SOURCES.md`.
