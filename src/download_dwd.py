"""Download DWD station monthly mean total cloud cover (MO_N) for the study region.

Source: DWD Climate Data Center, opendata.dwd.de, monthly "kl" (climate_summary)
files, accessed through the `wetterdienst` package.

Values are kept exactly as DWD publishes them:
  * unit conversion is OFF, so MO_N stays in octas (0-8);
  * wetterdienst's plausibility checks run in "soft" mode, so no value is
    removed -- a value outside the expected range is only flagged in
    `quality_flags` (e.g. "suspect:range");
  * months DWD reports as missing (-999) are kept as empty values, with the
    DWD quality level (QN_4) and "raw:-999" in `quality_flags`.
No station selection is done here; that belongs to the analysis.

Outputs (data/raw/dwd/):
  dwd_stations.csv                 station metadata for the stations returned
  dwd_mo_n_monthly_2015_2024.csv   one row per station and month

Usage:
    python src/download_dwd.py            # skips if the outputs already exist
    python src/download_dwd.py --force    # re-download
"""

import argparse
import sys
from pathlib import Path

import polars as pl
from wetterdienst import Settings
from wetterdienst.provider.dwd.observation import DwdObservationRequest

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "data" / "raw" / "dwd"
OUT_STATIONS = OUT_DIR / "dwd_stations.csv"
OUT_VALUES = OUT_DIR / "dwd_mo_n_monthly_2015_2024.csv"

START, END = "2015-01-01", "2024-12-31"
# Study region (CLAUDE.md): 52-55.5 N, 6-14.5 E.
BBOX = {"left": 6.0, "bottom": 52.0, "right": 14.5, "top": 55.5}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--force", action="store_true", help="re-download even if the files exist")
    args = parser.parse_args()

    if OUT_STATIONS.exists() and OUT_VALUES.exists() and not args.force:
        print("DWD files already exist; use --force to re-download")
        return 0

    request = DwdObservationRequest(
        parameters=[("monthly", "climate_summary", "cloud_cover_total_mean")],
        start=START,
        end=END,
        periods=["historical", "recent"],
        # trust_env=True lets aiohttp use HTTPS_PROXY if one is set.
        settings=Settings(fsspec_client_kwargs={"trust_env": True}),
        options={"convert_units": False, "plausibility": "soft", "drop_nulls": False},
    )
    stations = request.filter_by_bbox(**BBOX)
    values = stations.values().all().df

    station_ids = values["station_id"].unique().implode()
    meta = stations.df.filter(pl.col("station_id").is_in(station_ids))

    # Fixed, readable timestamp format for the CSV.
    values = values.with_columns(pl.col("timestamp").dt.strftime("%Y-%m-%d")).sort(
        ["station_id", "timestamp"]
    )
    meta = meta.with_columns(
        pl.col("start_timestamp").dt.strftime("%Y-%m-%d"),
        pl.col("end_timestamp").dt.strftime("%Y-%m-%d"),
    ).sort("station_id")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    meta.write_csv(OUT_STATIONS)
    values.write_csv(OUT_VALUES)
    print(f"Saved {OUT_STATIONS.relative_to(REPO_ROOT)} ({meta.height} stations)")
    print(f"Saved {OUT_VALUES.relative_to(REPO_ROOT)} ({values.height} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
