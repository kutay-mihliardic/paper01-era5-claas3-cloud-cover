"""Load the three cloud-cover datasets and convert them to one unit: fraction (0-1).

Unit conversions (see methods_notes.md, section 3):
    CLAAS-3 cfc   [%]       -> / 100
    ERA5 tcc      [0-1]     -> unchanged
    DWD MO_N      [octas]   -> / 8

Station selection implements the decisions in methods_notes.md, section 4:
    D1   drop Potsdam Saekularstation 03988 (03987 is used)
    D2a  keep only stations whose measurement method (person / instrument) does not
         change in 2015-2024
    D2b  keep only stations with >= 21 of 30 months in every season (DJF, MAM, JJA, SON)
    D2c  the method group ("instrument" / "observer") is kept as a column so the two
         groups can be reported separately
"""

from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "data" / "raw"
PROCESSED = REPO_ROOT / "data" / "processed"

STUDY_BOX = {"lat_min": 52.0, "lat_max": 55.5, "lon_min": 6.0, "lon_max": 14.5}
SEASONS = {12: "DJF", 1: "DJF", 2: "DJF", 3: "MAM", 4: "MAM", 5: "MAM",
           6: "JJA", 7: "JJA", 8: "JJA", 9: "SON", 10: "SON", 11: "SON"}
MIN_MONTHS_PER_SEASON = 21  # D2b, out of 30
EXCLUDED_STATIONS = {"03988"}  # D1


def load_claas3() -> xr.DataArray:
    """CLAAS-3 monthly cfc as fraction, dims (time, lat, lon), lat ascending."""
    files = sorted((RAW / "claas3").glob("CFCmm*.nc"))
    if len(files) != 120:
        raise RuntimeError(f"expected 120 CLAAS-3 files, found {len(files)}; run src/extract_claas3.py")
    arrays = []
    for f in files:
        with xr.open_dataset(f) as ds:
            arrays.append(ds["cfc"].load())
    cfc = xr.concat(arrays, dim="time")
    cfc = cfc.where(cfc != -999) / 100.0  # fill values were checked to be absent; mask anyway
    cfc.attrs = {"long_name": "CLAAS-3 cloud fractional cover", "units": "1", "source_units": "%"}
    return cfc.sortby("lat")


def load_era5() -> xr.DataArray:
    """ERA5 monthly tcc as fraction, dims (time, lat, lon), lat ascending."""
    with xr.open_dataset(RAW / "era5" / "era5_tcc_monthly_2015_2024.nc") as ds:
        tcc = ds["tcc"].load()
    tcc = tcc.rename({"valid_time": "time", "latitude": "lat", "longitude": "lon"})
    tcc = tcc.drop_vars([c for c in ("number", "expver") if c in tcc.coords])
    tcc.attrs = {"long_name": "ERA5 total cloud cover", "units": "1", "source_units": "(0 - 1)"}
    return tcc.sortby("lat")


def load_dwd(select: bool = True) -> tuple[pd.DataFrame, pd.DataFrame]:
    """DWD monthly MO_N as fraction.

    Returns (values, stations):
      values   columns station_id, time, cloud_fraction (rows with missing MO_N dropped)
      stations columns station_id, name, latitude, longitude, method, n_months,
               months_DJF/MAM/JJA/SON
    With select=True only the stations passing D1, D2a and D2b are returned.
    """
    vals = pd.read_csv(
        RAW / "dwd" / "dwd_mo_n_monthly_2015_2024.csv",
        dtype={"station_id": str, "value": float, "quality_flags": str},
    )
    vals = vals.dropna(subset=["value"])
    vals["time"] = pd.to_datetime(vals["timestamp"])
    vals["cloud_fraction"] = vals["value"] / 8.0
    vals = vals[["station_id", "time", "cloud_fraction"]]

    meta = pd.read_csv(PROCESSED / "dwd_cloud_method_by_station.csv", dtype={"station_id": str})
    methods = meta["majority_method_by_year"].fillna("").map(
        lambda s: {m.split(":")[1] for m in s.split()} if s else set()
    )
    meta["method"] = methods.map(
        lambda m: "instrument" if m == {"I"} else "observer" if m == {"P"} else "changes" if m else "unknown"
    )

    season = vals["time"].dt.month.map(SEASONS)
    counts = vals.groupby([vals["station_id"], season]).size().unstack(fill_value=0)
    counts = counts.reindex(columns=["DJF", "MAM", "JJA", "SON"], fill_value=0).add_prefix("months_")

    stations = meta[["station_id", "name", "latitude", "longitude", "method", "n_months_mo_n"]].rename(
        columns={"n_months_mo_n": "n_months"}
    )
    stations = stations.merge(counts, left_on="station_id", right_index=True, how="left").fillna(
        {c: 0 for c in counts.columns}
    )

    if select:
        ok = (
            ~stations["station_id"].isin(EXCLUDED_STATIONS)
            & stations["method"].isin(["instrument", "observer"])
            & (stations[[f"months_{s}" for s in ("DJF", "MAM", "JJA", "SON")]].min(axis=1)
               >= MIN_MONTHS_PER_SEASON)
        )
        stations = stations[ok].reset_index(drop=True)
        vals = vals[vals["station_id"].isin(stations["station_id"])].reset_index(drop=True)
    return vals, stations


def climatological_mean_grid(da: xr.DataArray) -> xr.DataArray:
    """Mean of the 12 calendar-month climatologies (equal weight per month)."""
    return da.groupby("time.month").mean("time").mean("month")


def climatological_mean_stations(vals: pd.DataFrame) -> pd.Series:
    """Per station: mean of the 12 calendar-month climatologies from available years.

    Using monthly climatologies first keeps a station's missing months from shifting
    its annual mean toward the seasons that happen to be present.
    """
    clim = vals.groupby([vals["station_id"], vals["time"].dt.month])["cloud_fraction"].mean()
    return clim.groupby(level=0).mean()


def box_mean(da: xr.DataArray) -> xr.DataArray:
    """Area-weighted (cos lat) mean over the study box."""
    b = STUDY_BOX
    sub = da.sel(lat=slice(b["lat_min"], b["lat_max"]), lon=slice(b["lon_min"], b["lon_max"]))
    w = np.cos(np.deg2rad(sub["lat"]))
    return sub.weighted(w).mean(("lat", "lon"))


def sample_at_stations(da: xr.DataArray, stations: pd.DataFrame, name: str) -> pd.DataFrame:
    """Value of the nearest grid cell at each station, for every month.

    Returns columns station_id, time, <name>, plus <name>_dist_km (distance from the
    station to the centre of the cell that was used).
    """
    lat = xr.DataArray(stations["latitude"].to_numpy(), dims="station")
    lon = xr.DataArray(stations["longitude"].to_numpy(), dims="station")
    picked = da.sel(lat=lat, lon=lon, method="nearest")
    out = picked.to_dataframe(name=name).reset_index()
    out["station_id"] = stations["station_id"].to_numpy()[out["station"].to_numpy()]
    dlat = np.deg2rad(picked["lat"].to_numpy() - stations["latitude"].to_numpy())
    dlon = np.deg2rad(picked["lon"].to_numpy() - stations["longitude"].to_numpy())
    km = 6371.0 * np.hypot(dlat, dlon * np.cos(np.deg2rad(stations["latitude"].to_numpy())))
    out[f"{name}_dist_km"] = km[out["station"].to_numpy()]
    return out[["station_id", "time", name, f"{name}_dist_km"]]


def matched_station_table() -> tuple[pd.DataFrame, pd.DataFrame]:
    """One row per selected station and month with MO_N: station, ERA5 and CLAAS-3 values.

    Gridded values are taken only for months in which the station has data, so all
    three columns share exactly the same sampling.
    """
    vals, stations = load_dwd()
    era5 = sample_at_stations(load_era5(), stations, "era5")
    claas = sample_at_stations(load_claas3(), stations, "claas3")
    t = vals.rename(columns={"cloud_fraction": "station"})
    t = t.merge(era5, on=["station_id", "time"], how="left").merge(claas, on=["station_id", "time"], how="left")
    t = t.merge(stations[["station_id", "method"]], on="station_id")
    if t[["era5", "claas3"]].isna().any().any():
        raise RuntimeError("missing gridded value at a station-month")
    return t, stations
