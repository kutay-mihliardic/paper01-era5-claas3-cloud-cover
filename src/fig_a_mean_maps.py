"""Figure (a): 10-year (2015-2024) mean cloud fraction, side by side.

Panels: CLAAS-3 cfc, ERA5 tcc, DWD MO_N at the selected stations. All in fraction
(0-1) on one shared colour scale. The mean is the mean of the 12 calendar-month
climatologies (see load_data.climatological_mean_*), so stations with missing months
are not biased toward the seasons that happen to be present.

Output: figures/fig_a_mean_maps.png

Usage:
    python src/fig_a_mean_maps.py
"""

import sys
from pathlib import Path

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import BoundaryNorm, LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parent))
import load_data as L  # noqa: E402

OUT = L.REPO_ROOT / "figures" / "fig_a_mean_maps.png"

# Single-hue sequential ramp (light -> dark blue).
CMAP = LinearSegmentedColormap.from_list(
    "seq_blue", ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
)
LEVELS = np.round(np.arange(0.60, 0.8201, 0.02), 2)  # data range 0.62-0.82, checked
EXTENT = [5.5, 15.0, 51.5, 56.0]
INK, MUTED = "#1f2328", "#6e7781"


def add_base(ax):
    ax.set_extent(EXTENT, crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE.with_scale("10m"), linewidth=0.6, edgecolor=INK)
    ax.add_feature(cfeature.BORDERS.with_scale("10m"), linewidth=0.4, edgecolor=MUTED, linestyle=":")
    b = L.STUDY_BOX
    ax.add_patch(Rectangle((b["lon_min"], b["lat_min"]), b["lon_max"] - b["lon_min"],
                           b["lat_max"] - b["lat_min"], fill=False, edgecolor=INK,
                           linewidth=1.0, linestyle="--", transform=ccrs.PlateCarree(), zorder=10))
    gl = ax.gridlines(draw_labels=True, linewidth=0.3, color="#d0d7de", x_inline=False, y_inline=False)
    gl.top_labels = gl.right_labels = False
    gl.xlabel_style = gl.ylabel_style = {"size": 7, "color": MUTED}


def main() -> int:
    claas = L.climatological_mean_grid(L.load_claas3())
    era5 = L.climatological_mean_grid(L.load_era5())
    vals, stations = L.load_dwd()
    stations = stations.merge(
        L.climatological_mean_stations(vals).rename("mean").reset_index(), on="station_id"
    )

    norm = BoundaryNorm(LEVELS, CMAP.N, extend="both")
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4), subplot_kw={"projection": ccrs.PlateCarree()},
                             constrained_layout=True)

    panels = [
        (claas, "CLAAS-3 cfc (0.05°)", "a"),
        (era5, "ERA5 tcc (0.25°)", "b"),
    ]
    for ax, (da, title, tag) in zip(axes[:2], panels):
        add_base(ax)
        ax.pcolormesh(da["lon"], da["lat"], da, cmap=CMAP, norm=norm, shading="nearest",
                      transform=ccrs.PlateCarree())
        ax.set_title(f"({tag}) {title}", loc="left", fontsize=10, color=INK)

    ax = axes[2]
    add_base(ax)
    markers = {"instrument": "o", "observer": "s"}
    for method, mk in markers.items():
        sub = stations[stations["method"] == method]
        ax.scatter(sub["longitude"], sub["latitude"], c=sub["mean"], cmap=CMAP, norm=norm,
                   marker=mk, s=70, edgecolors=INK, linewidths=0.8, transform=ccrs.PlateCarree(),
                   zorder=5)
    n_i = (stations["method"] == "instrument").sum()
    n_o = (stations["method"] == "observer").sum()
    ax.set_title(f"(c) DWD MO_N, {len(stations)} stations", loc="left", fontsize=10, color=INK)
    handles = [
        Line2D([], [], marker="o", linestyle="", markerfacecolor="white", markeredgecolor=INK,
               markersize=7, label=f"instrument (n={n_i})"),
        Line2D([], [], marker="s", linestyle="", markerfacecolor="white", markeredgecolor=INK,
               markersize=7, label=f"observer (n={n_o})"),
        Line2D([], [], color=INK, linestyle="--", linewidth=1.0, label="study region"),
    ]
    ax.legend(handles=handles, loc="upper right", fontsize=7, frameon=True, framealpha=0.9)

    sm = plt.cm.ScalarMappable(norm=norm, cmap=CMAP)
    cb = fig.colorbar(sm, ax=axes, orientation="horizontal", shrink=0.45, aspect=40, pad=0.02,
                      ticks=LEVELS[::2])
    cb.set_label("Mean cloud fraction 2015–2024 (0–1)", fontsize=9, color=INK)
    cb.ax.tick_params(labelsize=8, colors=MUTED)

    fig.text(0.01, -0.04,
             "CLAAS-3: © EUMETSAT, CM SAF, doi:10.5676/EUM_SAF_CM/CLAAS/V003 (% / 100).  "
             "ERA5: C3S/ECMWF, doi:10.24381/cds.f17050d7.  DWD: Deutscher Wetterdienst (octas / 8).  "
             "Mean = mean of 12 monthly climatologies.",
             fontsize=7, color=MUTED, ha="left", va="top")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=200, bbox_inches="tight", facecolor="white")
    print(f"Saved {OUT.relative_to(L.REPO_ROOT)}")

    # Descriptive numbers for the report (no interpretation).
    print("study-box mean (cos-lat weighted): CLAAS-3 %.3f, ERA5 %.3f" %
          (float(L.box_mean(claas)), float(L.box_mean(era5))))
    for m in ("instrument", "observer"):
        s = stations.loc[stations["method"] == m, "mean"]
        print(f"stations {m}: n={len(s)} mean {s.mean():.3f} min {s.min():.3f} max {s.max():.3f}")
    print("grid min/max: CLAAS-3 %.3f/%.3f, ERA5 %.3f/%.3f" %
          (float(claas.min()), float(claas.max()), float(era5.min()), float(era5.max())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
