"""Figure (c): ERA5 and CLAAS-3 at the station locations vs the station values, by season.

Each point is one station's seasonal mean: the mean of its three calendar-month
climatologies (same matched sampling as figure (b), load_data.matched_station_table).
Rows: ERA5, CLAAS-3. Columns: DJF, MAM, JJA, SON. Circles: instrument stations,
open squares: observer stations (shown, but statistics use instrument stations only,
decision D2c). Dashed line: 1:1.

Statistics per panel (instrument stations, across stations):
  bias = mean(grid - station), RMSE, Pearson r.

Outputs:
  figures/fig_c_station_scatter.png
  data/processed/fig_c_station_seasonal_means.csv   (one row per station and season)
  data/processed/fig_c_stats.csv                    (bias, RMSE, r per dataset/season/group)

Usage:
    python src/fig_c_station_scatter.py
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import load_data as L  # noqa: E402

OUT_FIG = L.REPO_ROOT / "figures" / "fig_c_station_scatter.png"
OUT_MEANS = L.PROCESSED / "fig_c_station_seasonal_means.csv"
OUT_STATS = L.PROCESSED / "fig_c_stats.csv"

COLORS = {"era5": "#2a78d6", "claas3": "#eb6834"}
LABELS = {"era5": "ERA5", "claas3": "CLAAS-3"}
SEASON_ORDER = ["DJF", "MAM", "JJA", "SON"]
INK, MUTED, GRID = "#1f2328", "#6e7781", "#e6e8eb"
LIM = (0.50, 0.92)


def stats(x: pd.Series, y: pd.Series) -> dict:
    d = y - x
    return {"n": len(x), "bias": d.mean(), "rmse": float(np.sqrt((d ** 2).mean())),
            "r": float(np.corrcoef(x, y)[0, 1]) if len(x) > 2 else np.nan}


def main() -> int:
    t, stations = L.matched_station_table()
    clim = L.station_climatology(t)
    clim["season"] = clim["month"].map(L.SEASONS)
    seas = clim.groupby(["method", "station_id", "season"])[["station", "era5", "claas3"]].mean().reset_index()
    seas.round(4).to_csv(OUT_MEANS, index=False)

    rows = []
    for (method, season), g in seas.groupby(["method", "season"]):
        for k in ("era5", "claas3"):
            rows.append({"dataset": k, "method": method, "season": season, **stats(g["station"], g[k])})
    st = pd.DataFrame(rows)
    st.round(4).to_csv(OUT_STATS, index=False)

    fig, axes = plt.subplots(2, 4, figsize=(13, 6.8), sharex=True, sharey=True, constrained_layout=True)
    for i, k in enumerate(("era5", "claas3")):
        for j, season in enumerate(SEASON_ORDER):
            ax = axes[i, j]
            ax.plot(LIM, LIM, color=MUTED, linestyle="--", linewidth=1, zorder=1)
            g = seas[seas["season"] == season]
            ins, obs = g[g["method"] == "instrument"], g[g["method"] == "observer"]
            ax.scatter(ins["station"], ins[k], s=36, color=COLORS[k], edgecolors="white", linewidths=0.8,
                       zorder=3, label="instrument station")
            ax.scatter(obs["station"], obs[k], s=40, marker="s", facecolors="white", edgecolors=INK,
                       linewidths=1.0, zorder=4, label="observer station")
            s = st[(st["dataset"] == k) & (st["method"] == "instrument") & (st["season"] == season)].iloc[0]
            ax.text(0.04, 0.96, f"bias {s['bias']:+.3f}\nRMSE {s['rmse']:.3f}\nr {s['r']:.2f}  (n={int(s['n'])})",
                    transform=ax.transAxes, va="top", ha="left", fontsize=8, color=INK)
            ax.set_xlim(LIM)
            ax.set_ylim(LIM)
            ax.set_aspect("equal")
            ax.grid(color=GRID, linewidth=0.6)
            ax.tick_params(colors=MUTED, labelsize=8)
            for side in ("top", "right"):
                ax.spines[side].set_visible(False)
            for side in ("left", "bottom"):
                ax.spines[side].set_color(MUTED)
            if i == 0:
                ax.set_title(season, fontsize=10, color=INK)
            if j == 0:
                ax.set_ylabel(f"{LABELS[k]} at station (0–1)", fontsize=9, color=INK)
            if i == 1:
                ax.set_xlabel("DWD station (0–1)", fontsize=9, color=INK)
    axes[1, 3].legend(loc="lower right", fontsize=7, frameon=False)
    axes[0, 3].legend(loc="lower right", fontsize=7, frameon=False)
    fig.text(0.0, -0.02,
             "Each point: one station's 2015–2024 seasonal mean (matched months). Statistics: instrument "
             "stations only; bias = grid − station. Dashed: 1:1.\n"
             "CLAAS-3: © EUMETSAT, CM SAF, doi:10.5676/EUM_SAF_CM/CLAAS/V003 (% / 100).  "
             "ERA5: C3S/ECMWF, doi:10.24381/cds.f17050d7.  DWD: Deutscher Wetterdienst (octas / 8).",
             fontsize=7, color=MUTED, ha="left", va="top")

    fig.savefig(OUT_FIG, dpi=200, bbox_inches="tight", facecolor="white")
    print(f"Saved {OUT_FIG.relative_to(L.REPO_ROOT)}, {OUT_MEANS.name}, {OUT_STATS.name}")
    print(st.pivot_table(index=["method", "season"], columns="dataset", values=["bias", "rmse", "r"])
          .reindex(SEASON_ORDER, level=1).round(3).to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
