"""Break test for the CLAAS-3 CDR -> ICDR switch in January 2021 (decision D3, D3b).

Control-series logic: if CLAAS-3 - station shifts after 2021-01 but ERA5 - station does
not, the shift points to the satellite side; if both shift, the cause is common to both
(weather sampling or the station side).

Method (instrument stations only, decision D2c; matched sampling as in figure (b)):
  1. For each station-month: d = grid - station, for grid = ERA5 and CLAAS-3, and
     CLAAS-3 - ERA5 (station cancels out).
  2. Remove each station's mean seasonal cycle of d (its calendar-month mean over all
     years) -> anomalies.
  3. Average the anomalies over stations for each month -> one monthly series per
     difference.
  4. Shift = mean(2021-2024) - mean(2015-2020).
  5. Significance: exact permutation test over whole years. All C(10, 4) = 210 ways of
     choosing 4 of the 10 years as the "after" group; p = share of splits with
     |shift| >= |observed shift|. Whole years keep within-year autocorrelation intact.

Outputs:
  figures/figS1_break_test_2021.png
  data/processed/break_test_2021.csv

Usage:
    python src/break_test_2021.py
"""

import itertools
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import load_data as L  # noqa: E402

OUT_FIG = L.REPO_ROOT / "figures" / "figS1_break_test_2021.png"
OUT_CSV = L.PROCESSED / "break_test_2021.csv"
BREAK_YEAR = 2021
SERIES = {
    "claas3_minus_station": ("CLAAS-3 − station", "#eb6834"),
    "era5_minus_station": ("ERA5 − station", "#2a78d6"),
    "claas3_minus_era5": ("CLAAS-3 − ERA5 (at stations)", "#6e7781"),
}
INK, MUTED, GRID = "#1f2328", "#6e7781", "#e6e8eb"
# Platform changes from the CLAAS-3 file attributes (methods_notes.md section 2).
PLATFORM_CHANGES = ["2018-02-01", "2019-01-01", "2019-02-01", "2022-01-01", "2022-02-01", "2023-03-01"]


def anomaly_series(t: pd.DataFrame) -> pd.DataFrame:
    t = t[t["method"] == "instrument"].copy()
    t["claas3_minus_station"] = t["claas3"] - t["station"]
    t["era5_minus_station"] = t["era5"] - t["station"]
    t["claas3_minus_era5"] = t["claas3"] - t["era5"]
    t["month"] = t["time"].dt.month
    for k in SERIES:
        t[k] = t[k] - t.groupby(["station_id", "month"])[k].transform("mean")
    out = t.groupby("time")[list(SERIES)].mean()
    out["n_stations"] = t.groupby("time")["station_id"].nunique()
    return out


def permutation_test(series: pd.Series) -> tuple[float, float]:
    years = series.index.year
    all_years = sorted(set(years))
    yearly_sum = series.groupby(years).sum()
    yearly_n = series.groupby(years).size()

    def shift(after: set) -> float:
        a = [y for y in all_years if y in after]
        b = [y for y in all_years if y not in after]
        return yearly_sum[a].sum() / yearly_n[a].sum() - yearly_sum[b].sum() / yearly_n[b].sum()

    observed = shift({y for y in all_years if y >= BREAK_YEAR})
    n_after = sum(1 for y in all_years if y >= BREAK_YEAR)
    null = [shift(set(c)) for c in itertools.combinations(all_years, n_after)]
    p = float(np.mean(np.abs(null) >= abs(observed) - 1e-12))
    return observed, p


def main() -> int:
    t, _ = L.matched_station_table()
    anom = anomaly_series(t)

    rows = []
    for k, (label, _) in SERIES.items():
        shift, p = permutation_test(anom[k])
        rows.append({"series": k, "label": label,
                     "mean_2015_2020": anom.loc[anom.index.year < BREAK_YEAR, k].mean(),
                     "mean_2021_2024": anom.loc[anom.index.year >= BREAK_YEAR, k].mean(),
                     "shift": shift, "p_permutation": p, "n_permutations": 210})
    res = pd.DataFrame(rows)
    res.round(4).to_csv(OUT_CSV, index=False)

    fig, axes = plt.subplots(3, 1, figsize=(11, 7.5), sharex=True, sharey=True, constrained_layout=True)
    for ax, (k, (label, color)) in zip(axes, SERIES.items()):
        s = anom[k]
        ax.axhline(0, color=MUTED, linewidth=0.8)
        ax.plot(s.index, s, color=color, linewidth=1.2)
        ax.plot(s.index, s.rolling(12, center=True).mean(), color=INK, linewidth=2, label="12-month running mean")
        r = res[res["series"] == k].iloc[0]
        for start, end, m in ((s.index.min(), pd.Timestamp("2020-12-31"), r["mean_2015_2020"]),
                              (pd.Timestamp("2021-01-01"), s.index.max(), r["mean_2021_2024"])):
            ax.hlines(m, start, end, color=color, linewidth=2.5, linestyles="--")
        ax.axvline(pd.Timestamp("2021-01-01"), color=INK, linewidth=1.2)
        for d in PLATFORM_CHANGES:
            ax.axvline(pd.Timestamp(d), color=MUTED, linewidth=0.8, linestyle=":")
        ax.set_title(f"{label}: shift after 2021-01 = {r['shift']:+.3f}, permutation p = {r['p_permutation']:.2f}",
                     loc="left", fontsize=10, color=INK)
        ax.grid(axis="y", color=GRID, linewidth=0.6)
        ax.tick_params(colors=MUTED, labelsize=8)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.set_ylabel("Anomaly (0–1)", fontsize=9, color=INK)
    axes[0].legend(loc="upper left", fontsize=8, frameon=False)
    fig.text(0.0, -0.02,
             "Instrument stations (n=36), matched months; each station's mean seasonal cycle of the difference "
             "removed, then averaged over stations. Solid vertical line: CDR → ICDR (2021-01); dotted: platform-"
             "attribute changes; dashed: period means.\nCLAAS-3: © EUMETSAT, CM SAF, "
             "doi:10.5676/EUM_SAF_CM/CLAAS/V003.  ERA5: C3S/ECMWF, doi:10.24381/cds.f17050d7.  "
             "DWD: Deutscher Wetterdienst.",
             fontsize=7, color=MUTED, ha="left", va="top")
    fig.savefig(OUT_FIG, dpi=200, bbox_inches="tight", facecolor="white")
    print(f"Saved {OUT_FIG.relative_to(L.REPO_ROOT)} and {OUT_CSV.relative_to(L.REPO_ROOT)}")
    print(res[["label", "mean_2015_2020", "mean_2021_2024", "shift", "p_permutation"]].round(4).to_string(index=False))
    print("stations per month: min", int(anom["n_stations"].min()), "max", int(anom["n_stations"].max()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
