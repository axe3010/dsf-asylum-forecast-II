# Raw data sources

## eurostat_asylum_ch_monthly.csv
- Dataset: Eurostat `migr_asyappctzm` (Asylum applicants by type, citizenship, age and sex - monthly data)
- Filter: geo = CH (Switzerland), citizen = TOTAL, sex = T, age = TOTAL, unit = PER (persons)
- Columns: total applicants, first-time applicants, subsequent applicants (subsequent only reported from 2021)
- Query: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/migr_asyappctzm?geo=CH&citizen=TOTAL&sex=T&age=TOTAL&unit=PER&lang=EN
- Dataset last updated by Eurostat: 2026-11-13; downloaded 2026-11-16
- Coverage: 2008-01 to 2026-09 (225 months); 2026-10 not yet published at download
- Check at download: sum of total = 409,975; sum of first-time = 369,920; sum of subsequent = 15,565 (69 months)
- Note: Eurostat rounds values to the nearest 5.

### Check against SEM's headline figure (primary + secondary applications, without status S)
| Period | Eurostat | SEM | Source of SEM figure |
|---|---|---|---|
| Sep 2026 | 2,120 | 2,122 | SEM press release, 15 Oct 2026 |
| Sep 2025 | 2,570 | 2,571 | same release (2,122 + 449) |
| Jun 2026 | 1,775 | 1,777 | SEM via Keystone-SDA, 16 Jul 2026 |
| Jan-Jun 2026 | 9,735 | 9,734 | same |
| Year 2025 | 25,750 | 25,781 (provisional) | SEM via Keystone-SDA, 26 Jan 2026 |

The Eurostat total equals SEM's headline figure up to rounding, so we use Eurostat as the single source of the target.
Timing: SEM publishes month m around the 15th of month m+1; Eurostat publishes later (September 2026 appeared on 13 Nov 2026).
In the backtest we use SEM's timing (at the cutoff in month m, the target is known up to month m-1), because the numbers are the same.

## frontex_detections_by_route_monthly.csv
- Source: Frontex, "Detections of illegal border-crossings statistics download (updated monthly)", file `EUROSUR_data_as_of_04NOV26.xlsx`, sheet `Detections_of_IBC`, from https://www.frontex.europa.eu/what-we-do/monitoring-and-risk-analysis/migratory-map/
- Downloaded on 2026-11-17; file dated 4 November 2026; last month in the file: September 2026.
- Definition (from the file's Notes sheet): data reported monthly by Member States and Schengen Associated Countries on apprehensions of illegal border-crossing on entry between border crossing points of the external borders, aggregated by routes. The data refer to detections, not persons: the same person may cross the external border several times.
- Our processing: the file has one row per route, border type (sea / land) and nationality, and one column per month (JAN2009 to SEP2026). We summed all nationalities and both border types per route and month (inside the browser, from the original file) and saved one column per route. No other change.
- Coverage: 213 months, 2009-01 to 2026-09; 9 routes.
- Check at download (sum over all months, per route): eastern_mediterranean 1,813,218; central_mediterranean 1,326,030; western_mediterranean 282,262; western_african 183,005; western_balkan 1,379,203; eastern_borders 66,937; circular_route_from_albania_to_greece 136,066; black_sea 1,395; other 73. The saved CSV reproduces all nine sums exactly.
- Timing: the file dated 4 November 2026 already contains September 2026, so at our cutoff (around the 15th of month m) the data are known up to month m-2. Frontex revises the numbers later (notes of the file); we use the values as downloaded.

## Extra data for steps F to H (after the test)

These files are used only in `05_preprocess_extra_data.ipynb` and the notebooks after it. They were added after the test period was used (`04_test.ipynb`).

## estat_migr_asyappctzm_neighbours_en.csv
- Dataset: Eurostat `migr_asyappctzm`, the same dataset as our target
- Filter: geo = CH, DE, AT, FR, IT; citizen = TOTAL, sex = T, age = TOTAL, unit = PER, applicant = TOTAL (the same definition as `applicants_total`)
- Format: Eurostat SDMX-CSV, one row per country and month (downloaded from the Eurostat data browser with these filters)
- Query (JSON version of the same data): https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/migr_asyappctzm?geo=CH&geo=DE&geo=AT&geo=FR&geo=IT&citizen=TOTAL&sex=T&age=TOTAL&unit=PER&lang=EN
- Dataset last updated by Eurostat: 2026-11-18; downloaded 2026-11-19
- Coverage: 2008-01 to 2026-09; Germany missing 2026-09; Italy flagged `b` (break in series) in 2026-07
- Check at download: Switzerland identical to `eurostat_asylum_ch_monthly.csv` in 225 of 225 months
- Timing: about six weeks after the month, so at our cutoff known up to month m-2 (origin t-1)

## estat_migr_asyappctzm_ch_by_citizenship_en.csv
- Dataset: Eurostat `migr_asyappctzm`, geo = CH, every citizenship, sex = T, age = TOTAL, unit = PER, applicant = TOTAL (SDMX-CSV)
- Dataset last updated by Eurostat: 2026-11-18; downloaded 2026-11-19
- Read with `keep_default_na=False`: Eurostat writes Namibia as `NA`
- Check at download: the TOTAL row is identical to `eurostat_asylum_ch_monthly.csv` in 225 of 225 months
- Use: shares of the nationalities over the last 12 known months (weights of the conflict index)

## unhcr_italy_sea_arrivals_by_month.json
- Source: UNHCR Operational Data Portal, Europe Sea Arrivals, Italy, widget "Sea arrivals by month" (JSON), https://data.unhcr.org/en/situations/europe-sea-arrivals/location/24521 ; figures of the Italian Ministry of the Interior
- Downloaded 2026-11-19 (copied from the browser; the copy stops after the data, so `05` reads the monthly values with a text pattern)
- Coverage: 2014-01 to 2026-11 (November 2026 incomplete, not used)
- Check: yearly totals as published by UNHCR (e.g. 2021: 67,477; 2022: 105,131)

## unhcr_greece_sea_land_arrivals_by_month.csv, unhcr_spain_sea_land_arrivals_by_month.csv
- Source: same portal, Greece and Spain, sea and land arrivals by month (CSV, first line `sep=;`)
- Downloaded 2026-11-19; coverage Greece 2018-01 to 2026-11, Spain 2017-01 to 2026-11 (November incomplete, not used)
- Check: yearly totals, e.g. Spain 2018: 65,383; Greece 2018: 50,508
- Timing: UNHCR updates weekly, so the whole month m-1 is known at our cutoff (origin t)
- Note: the monthly changes are almost the same as those of the Frontex routes (correlation 0.99 Italy / Central Mediterranean, 0.96 Greece / Eastern Mediterranean, 0.97 Spain / Western Mediterranean + Western African), so `05` uses the longer Frontex history at the UNHCR timing

## ucdp_ged261_country_month_deaths.csv
- Source: UCDP Georeferenced Event Dataset (GED) Global version 26.1, file `GEDEvent_v26_1.csv` (274 MB, not stored here), https://ucdp.uu.se/downloads/
- Downloaded 2026-11-19; 417,968 events, 1989-01 to 2025-12
- Our processing: sum of the "best" estimate of deaths per country and month of `date_start`, all three types of violence (state-based, non-state, one-sided). `05` rebuilds the table if the raw file is put in `data/raw/`.
- Timing: the yearly versions are published after the year ends and revised; UCDP Candidate (monthly) is about one month late. We use months up to m-2 (origin t-1), with the final values: an optimistic test.
