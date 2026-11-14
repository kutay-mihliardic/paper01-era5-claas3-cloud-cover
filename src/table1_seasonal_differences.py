"""Table 1: seasonal mean cloud fraction and differences at the DWD stations.

Main result: 2015-2024. Sensitivity (decision D3c): CDR period 2015-2020 and ICDR
period 2021-2024 separately. Same matched sampling and averaging as figure (b):
per station a calendar-month climatology from the years available in the period,
then mean over stations, then mean of the three months of a season.

Output: data/processed/table1_seasonal_differences.csv

Usage:
    python src/table1_seasonal_differences.py
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import load_data as L  # noqa: E402
from fig_b_seasonal_cycle import station_climatology  # noqa: E402

OUT = L.PROCESSED / "table1_seasonal_differences.csv"
PERIODS = {"2015-2024": (2015, 2024), "2015-2020 (CDR)": (2015, 2020), "2021-2024 (ICDR)": (2021, 2024)}
SEASON_ORDER = ["DJF", "MAM", "JJA", "SON"]


def main() -> int:
    t, _ = L.matched_station_table()
    rows = []
    for period, (y0, y1) in PERIODS.items():
        sub = t[(t["time"].dt.year >= y0) & (t["time"].dt.year <= y1)]
        clim = station_climatology(sub)
        monthly = clim.groupby(["method", "month"]).agg(
            n_stations=("station_id", "nunique"), station=("station", "mean"),
            era5=("era5", "mean"), claas3=("claas3", "mean")).reset_index()
        monthly["season"] = monthly["month"].map(L.SEASONS)
        seas = monthly.groupby(["method", "season"]).agg(
            n_stations_min=("n_stations", "min"), n_stations_max=("n_stations", "max"),
            station=("station", "mean"), era5=("era5", "mean"), claas3=("claas3", "mean")).reset_index()
        seas["era5_minus_station"] = seas["era5"] - seas["station"]
        seas["claas3_minus_station"] = seas["claas3"] - seas["station"]
        seas["era5_minus_claas3"] = seas["era5"] - seas["claas3"]
        seas.insert(0, "period", period)
        rows.append(seas)
    table = pd.concat(rows)
    table["season"] = pd.Categorical(table["season"], SEASON_ORDER, ordered=True)
    table = table.sort_values(["method", "period", "season"])
    table.round(3).to_csv(OUT, index=False)
    print(f"Saved {OUT.relative_to(L.REPO_ROOT)}")
    cols = ["period", "season", "n_stations_min", "n_stations_max", "station", "era5", "claas3",
            "era5_minus_station", "claas3_minus_station", "era5_minus_claas3"]
    for method in ("instrument", "observer"):
        print(f"\n{method}")
        print(table.loc[table["method"] == method, cols].round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
