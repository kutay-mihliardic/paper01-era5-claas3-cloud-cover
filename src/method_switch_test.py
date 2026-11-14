"""Natural experiment: does a DWD station read higher after switching observer -> instrument?

Uses the 15 stations that changed their cloud-cover measurement method in 2015-2024
(excluded as referees by decision D2a). ERA5 (and, as a second reference, CLAAS-3) at
the station location serves as a reference that does not change when the station does.

Rules fixed before looking at the result (methods_notes.md, D5):
  * Switch month: from DWD hourly cloudiness, the month after the last month in which
    instrument hours are <= 50 % of valid hours. Months with an instrument share
    strictly between 10 % and 90 % ("mixed") are dropped from both periods.
  * A station is used only with >= 12 months of MO_N before and >= 12 after the switch.
  * Anomaly: d = station - reference at the station's nearest grid cell, minus that
    station's own calendar-month mean of d.
  * Control (difference-in-differences): the same before/after difference of the mean
    anomaly of the 36 stable instrument stations (D2a/D2b), over exactly the months used
    for the switching station. DiD = shift(switching station) - shift(control).
  * Summary: mean DiD over stations, bootstrap 95 % CI over stations (10 000 draws,
    seed 1), number of positive DiDs and a two-sided sign test.

Outputs:
  figures/figS2_method_switch.png
  data/processed/method_switch_test.csv           (one row per station and reference)
  data/processed/method_switch_monthly_share.csv  (instrument share per station-month)

Usage:
    python src/method_switch_test.py
"""

import io
import sys
import zipfile
from math import comb
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import load_data as L  # noqa: E402

OUT_FIG = L.REPO_ROOT / "figures" / "figS2_method_switch.png"
OUT_CSV = L.PROCESSED / "method_switch_test.csv"
OUT_SHARE = L.PROCESSED / "method_switch_monthly_share.csv"
ZIP_DIR = L.RAW / "dwd" / "zips"
MIN_MONTHS = 12
MIXED = (0.10, 0.90)
REFS = {"era5": ("ERA5", "#2a78d6"), "claas3": ("CLAAS-3", "#eb6834")}
INK, MUTED, GRID = "#1f2328", "#6e7781", "#e6e8eb"


def instrument_share(station_id: str) -> pd.Series:
    """Monthly share of valid hourly V_N values flagged 'I' (instrument), 2015-2024."""
    path = next(ZIP_DIR.glob(f"stundenwerte_N_{station_id}_*.zip"), None)
    if path is None:
        raise FileNotFoundError(f"hourly zip for {station_id} missing; run src/dwd_station_metadata.py")
    zf = zipfile.ZipFile(io.BytesIO(path.read_bytes()))
    name = next(n for n in zf.namelist() if n.startswith("produkt"))
    df = pd.read_csv(io.BytesIO(zf.read(name)), sep=";", skipinitialspace=True, dtype=str)
    df.columns = [c.strip() for c in df.columns]
    df["V_N"] = pd.to_numeric(df["V_N"], errors="coerce")
    df = df[df["V_N"].between(0, 8)]
    df["time"] = pd.to_datetime(df["MESS_DATUM"].str[:6], format="%Y%m")
    df = df[(df["time"].dt.year >= 2015) & (df["time"].dt.year <= 2024)]
    return (df["V_N_I"].str.strip() == "I").groupby(df["time"]).mean()


def switch_month(share: pd.Series) -> pd.Timestamp:
    low = share[share <= 0.5]
    return low.index.max() + pd.offsets.MonthBegin(1)


def main() -> int:
    vals_all, st_all = L.load_dwd(select=False)
    _, stable = L.load_dwd(select=True)
    stable = stable[stable["method"] == "instrument"]
    switching = st_all[st_all["method"] == "changes"].reset_index(drop=True)

    grids = {"era5": L.load_era5(), "claas3": L.load_claas3()}
    both = pd.concat([switching, stable], ignore_index=True)
    t = vals_all[vals_all["station_id"].isin(both["station_id"])].rename(columns={"cloud_fraction": "station"})
    for k, da in grids.items():
        t = t.merge(L.sample_at_stations(da, both, k)[["station_id", "time", k]], on=["station_id", "time"])
    t["month"] = t["time"].dt.month
    for k in grids:
        d = t["station"] - t[k]
        t[f"anom_{k}"] = d - d.groupby([t["station_id"], t["month"]]).transform("mean")

    control = t[t["station_id"].isin(stable["station_id"])].groupby("time")[[f"anom_{k}" for k in grids]].mean()

    rows, shares, events = [], [], []
    for _, s in switching.iterrows():
        sid = s["station_id"]
        share = instrument_share(sid)
        shares.append(pd.DataFrame({"station_id": sid, "time": share.index, "instrument_share": share.values}))
        sw = switch_month(share)
        mixed = share[(share > MIXED[0]) & (share < MIXED[1])].index
        ts = t[(t["station_id"] == sid) & ~t["time"].isin(mixed)].set_index("time")
        before, after = ts[ts.index < sw], ts[ts.index >= sw]
        used = len(before) >= MIN_MONTHS and len(after) >= MIN_MONTHS
        for k in grids:
            a = f"anom_{k}"
            shift = after[a].mean() - before[a].mean() if used else np.nan
            ctrl = (control.loc[after.index, a].mean() - control.loc[before.index, a].mean()) if used else np.nan
            rows.append({"station_id": sid, "name": s["name"], "reference": k, "switch_month": sw.date(),
                         "n_before": len(before), "n_after": len(after), "n_mixed_dropped": len(mixed),
                         "used": used, "shift": shift, "control_shift": ctrl, "did": shift - ctrl})
            if used:
                rel = ((ts.index.year - sw.year) * 12 + ts.index.month - sw.month)
                events.append(pd.DataFrame({"reference": k, "rel_month": rel,
                                            "value": ts[a].values - control.loc[ts.index, a].values}))
    res = pd.DataFrame(rows)
    res.round(4).to_csv(OUT_CSV, index=False)
    pd.concat(shares).round(3).to_csv(OUT_SHARE, index=False)

    rng = np.random.default_rng(1)
    summary = {}
    for k in grids:
        d = res[(res["reference"] == k) & res["used"]]["did"].to_numpy()
        boots = rng.choice(d, size=(10000, len(d)), replace=True).mean(axis=1)
        n_pos = int((d > 0).sum())
        n = len(d)
        p_sign = min(1.0, 2 * sum(comb(n, i) for i in range(max(n_pos, n - n_pos), n + 1)) / 2 ** n)
        summary[k] = {"n": n, "mean": d.mean(), "ci": np.percentile(boots, [2.5, 97.5]), "n_pos": n_pos,
                      "p_sign": p_sign}

    ev = pd.concat(events)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), constrained_layout=True,
                             gridspec_kw={"width_ratios": [1.5, 1]})
    ax = axes[0]
    ax.axhline(0, color=MUTED, linewidth=0.8)
    ax.axvline(0, color=INK, linewidth=1.2)
    for k, (label, color) in REFS.items():
        e = ev[(ev["reference"] == k) & ev["rel_month"].between(-48, 48)]
        g = e.groupby("rel_month")["value"].mean()
        ax.plot(g.index, g.rolling(6, center=True, min_periods=3).mean(), color=color, linewidth=2,
                label=f"station − {label} (6-month running mean)")
    ax.set_title("(a) Switching stations, aligned on switch month, minus stable-station control",
                 loc="left", fontsize=10, color=INK)
    ax.set_xlabel("Months relative to observer → instrument switch", fontsize=9, color=INK)
    ax.set_ylabel("Anomaly (0–1)", fontsize=9, color=INK)
    ax.legend(loc="upper left", fontsize=8, frameon=False)

    ax = axes[1]
    used = res[res["used"]]
    order = used[used["reference"] == "era5"].sort_values("did")["station_id"].tolist()
    y = {sid: i for i, sid in enumerate(order)}
    names = used.drop_duplicates("station_id").set_index("station_id")["name"]
    ax.axvline(0, color=MUTED, linewidth=0.8)
    for k, (label, color) in REFS.items():
        u = used[used["reference"] == k]
        off = -0.15 if k == "era5" else 0.15
        ax.scatter(u["did"], [y[s] + off for s in u["station_id"]], color=color, s=28, zorder=3,
                   edgecolors="white", linewidths=0.6, label=f"vs {label}: mean {summary[k]['mean']:+.3f}")
        ax.axvline(summary[k]["mean"], color=color, linewidth=1.2, linestyle="--")
    ax.set_yticks(range(len(order)), [names[s] for s in order], fontsize=7)
    ax.set_xlabel("Difference-in-differences shift (0–1)", fontsize=9, color=INK)
    ax.set_title("(b) Per station", loc="left", fontsize=10, color=INK)
    ax.legend(loc="lower right", fontsize=7, frameon=False)
    for a in axes:
        a.grid(axis="x" if a is axes[1] else "y", color=GRID, linewidth=0.6)
        a.tick_params(colors=MUTED, labelsize=8)
        for side in ("top", "right"):
            a.spines[side].set_visible(False)
    fig.text(0.0, -0.03,
             "DWD stations that switched cloud-cover measurement from observer to instrument in 2015–2024; "
             "≥12 months before and after; mixed months dropped; control = 36 stable instrument stations.\n"
             "CLAAS-3: © EUMETSAT, CM SAF, doi:10.5676/EUM_SAF_CM/CLAAS/V003.  ERA5: C3S/ECMWF, "
             "doi:10.24381/cds.f17050d7.  DWD: Deutscher Wetterdienst.",
             fontsize=7, color=MUTED, ha="left", va="top")
    fig.savefig(OUT_FIG, dpi=200, bbox_inches="tight", facecolor="white")

    print(f"Saved {OUT_FIG.relative_to(L.REPO_ROOT)}, {OUT_CSV.name}, {OUT_SHARE.name}")
    print(res[res["reference"] == "era5"][["station_id", "name", "switch_month", "n_before", "n_after",
                                           "n_mixed_dropped", "used"]].to_string(index=False))
    for k, sm in summary.items():
        print(f"{k}: n={sm['n']} mean DiD {sm['mean']:+.4f} ({sm['mean']*8:+.2f} octa) "
              f"95% CI [{sm['ci'][0]:+.4f}, {sm['ci'][1]:+.4f}] positive {sm['n_pos']}/{sm['n']} "
              f"sign-test p={sm['p_sign']:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
