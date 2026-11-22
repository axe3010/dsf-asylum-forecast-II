"""Download the target from Eurostat and save it as data/raw/eurostat_asylum_ch_monthly.csv.

Dataset migr_asyappctzm, Switzerland, all citizenships, both sexes, all ages, persons, with the three
applicant types (TOTAL, FRST = first-time, SSEQ = subsequent). Eurostat answers in JSON-stat 2.0: one flat list of
values and, for every dimension, the position of each category; this script turns it into one row per month.

Run from code/:  python 00_download_target.py
The file in the repository was downloaded on 2026-11-16 (Eurostat update of 2026-11-13). Eurostat revises recent
months, so a new download can differ slightly; the checks in data/raw/SOURCES.md show the sums of that vintage.
"""
import json
import sys
import urllib.request

import pandas as pd

URL = ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/migr_asyappctzm"
       "?geo=CH&citizen=TOTAL&sex=T&age=TOTAL&unit=PER&lang=EN")
OUT = "../data/raw/eurostat_asylum_ch_monthly.csv"
COLUMNS = {"TOTAL": "applicants_total", "FRST": "applicants_first_time", "SSEQ": "applicants_subsequent"}


def jsonstat_to_table(data):
    """One row per month, one column per applicant type (JSON-stat 2.0, as sent by Eurostat)."""
    ids, sizes = data["id"], data["size"]
    labels = {d: sorted(data["dimension"][d]["category"]["index"].items(), key=lambda kv: kv[1]) for d in ids}
    rows = []
    for flat, value in data["value"].items():          # flat position -> one position per dimension
        pos, rest = {}, int(flat)
        for d, n in zip(reversed(ids), reversed(sizes)):
            pos[d] = labels[d][rest % n][0]
            rest //= n
        rows.append({"month": pos["time"], "applicant": pos["applicant"], "value": value})
    table = pd.DataFrame(rows).pivot(index="month", columns="applicant", values="value")
    table = table.reindex(columns=list(COLUMNS)).rename(columns=COLUMNS)
    table.index.name = "month"
    return table.sort_index().astype("Int64")             # integers; months without a value stay empty


if __name__ == "__main__":
    with urllib.request.urlopen(URL, timeout=60) as response:
        data = json.load(response)
    table = jsonstat_to_table(data)
    table.to_csv(OUT)
    print(f"Saved {len(table)} months ({table.index[0]} to {table.index[-1]}) to {OUT}")
    print("Sums:", table.sum().to_dict())
    sys.exit(0)
