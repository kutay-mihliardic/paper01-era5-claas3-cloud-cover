"""Figure (b): seasonal cycle of cloud fraction at the DWD stations.

ERA5 and CLAAS-3 are sampled at each selected station (nearest grid cell) and only in
the months in which that station has MO_N, so all three share the same sampling
(load_data.matched_station_table). For every station a 12-month climatology is formed
from the available years; the lines are the mean of those climatologies over stations.
Instrument and observer stations are shown separately (decision D2c).

Top row: cloud fraction. Bottom row: differences to the station (ERA5 - station,
CLAAS-3 - station); the band is the 25-75 % range across stations (instrument only).

Outputs:
  figures/fig_b_seasonal_cycle.png
  data/processed/fig_b_monthly_climatology.csv   (the numbers behind the figure)

Usage:
    python src/fig_b_seasonal_cycle.py
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import load_data as L  # noqa: E402

OUT_FIG = L.REPO_ROOT / "figures" / "fig_b_seasonal_cycle.png"
OUT_CSV = L.PROCESSED / "fig_b_monthly_climatology.csv"

COLORS = {"station": "#1f2328", "era5": "#2a78d6", "claas3": "#eb6834"}
LABELS = {"station": "DWD station", "era5": "ERA5", "claas3": "CLAAS-3"}
MARKERS = {"station": "s", "era5": "o", "claas3": "^"}
INK, MUTED, GRID = "#1f2328", "#6e7781", "#e6e8eb"
MONTHS = list("JFMAMJJASOND")


def style(ax):
    ax.set_xticks(range(1, 13), MONTHS)
    ax.set_xlim(0.6, 12.4)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.tick_params(colors=MUTED, labelsize=8)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)


def main() -> int:
    t, stations = L.matched_station_table()
    clim = L.station_climatology(t)
    agg = clim.groupby(["method", "month"]).agg(
        n_stations=("station_id", "nunique"),
        station=("station", "mean"), era5=("era5", "mean"), claas3=("claas3", "mean"),
        d_era5=("d_era5", "mean"), d_claas3=("d_claas3", "mean"),
        d_era5_q25=("d_era5", lambda x: x.quantile(0.25)), d_era5_q75=("d_era5", lambda x: x.quantile(0.75)),
        d_claas3_q25=("d_claas3", lambda x: x.quantile(0.25)), d_claas3_q75=("d_claas3", lambda x: x.quantile(0.75)),
    ).reset_index()
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    agg.round(4).to_csv(OUT_CSV, index=False)

    fig, axes = plt.subplots(2, 2, figsize=(11, 7), sharex=True, sharey="row",
                             gridspec_kw={"height_ratios": [1.2, 1]}, constrained_layout=True)
    for col, method in enumerate(("instrument", "observer")):
        a = agg[agg["method"] == method].sort_values("month")
        n = int(a["n_stations"].max())
        ax = axes[0, col]
        for k in ("station", "era5", "claas3"):
            ax.plot(a["month"], a[k], color=COLORS[k], linewidth=2, marker=MARKERS[k], markersize=5,
                    label=LABELS[k], zorder=3 if k == "station" else 2)
        if col == 0:  # direct labels at December, pushed apart so they do not overlap
            ends = sorted(((a[k].iloc[-1], k) for k in ("station", "era5", "claas3")), reverse=True)
            ys, prev = [], None
            for y, k in ends:
                y = y if prev is None else min(y, prev - 0.014)
                ys.append((y, k))
                prev = y
            for y, k in ys:
                ax.annotate(LABELS[k], (12, y), xytext=(8, 0), textcoords="offset points",
                            va="center", fontsize=8, color=INK)
        ax.set_title(f"{'(a)' if col == 0 else '(b)'} {method} stations (n={n})", loc="left",
                     fontsize=10, color=INK)
        style(ax)

        ax = axes[1, col]
        ax.axhline(0, color=MUTED, linewidth=1)
        for k in ("era5", "claas3"):
            ax.plot(a["month"], a[f"d_{k}"], color=COLORS[k], linewidth=2, marker=MARKERS[k], markersize=5,
                    label=f"{LABELS[k]} − station")
            if method == "instrument":
                ax.fill_between(a["month"], a[f"d_{k}_q25"], a[f"d_{k}_q75"], color=COLORS[k], alpha=0.15,
                                linewidth=0)
        ax.set_title(f"{'(c)' if col == 0 else '(d)'} difference to station"
                     + (" (band: 25–75 % of stations)" if method == "instrument" else ""),
                     loc="left", fontsize=10, color=INK)
        style(ax)

    axes[0, 0].set_ylabel("Cloud fraction (0–1)", fontsize=9, color=INK)
    axes[1, 0].set_ylabel("Difference (0–1)", fontsize=9, color=INK)
    axes[0, 1].legend(loc="lower left", fontsize=8, frameon=False)
    axes[1, 1].legend(loc="lower left", fontsize=8, frameon=False)
    fig.text(0.0, -0.03,
             "2015–2024 monthly means. ERA5 and CLAAS-3 sampled at each station (nearest cell) in the months "
             "the station has data; station climatologies averaged over stations.\n"
             "CLAAS-3: © EUMETSAT, CM SAF, doi:10.5676/EUM_SAF_CM/CLAAS/V003 (% / 100).  "
             "ERA5: C3S/ECMWF, doi:10.24381/cds.f17050d7.  DWD: Deutscher Wetterdienst (octas / 8).",
             fontsize=7, color=MUTED, ha="left", va="top")

    OUT_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_FIG, dpi=200, bbox_inches="tight", facecolor="white")
    print(f"Saved {OUT_FIG.relative_to(L.REPO_ROOT)} and {OUT_CSV.relative_to(L.REPO_ROOT)}")

    # Descriptive numbers for the report (no interpretation).
    seasons = agg.assign(season=agg["month"].map(L.SEASONS))
    table = seasons.groupby(["method", "season"])[["station", "era5", "claas3", "d_era5", "d_claas3"]].mean()
    table = table.reindex(["DJF", "MAM", "JJA", "SON"], level=1)
    print(table.round(3).to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
