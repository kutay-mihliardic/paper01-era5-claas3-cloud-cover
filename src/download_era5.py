"""Download ERA5 monthly mean total cloud cover (tcc) for the study region.

Dataset: "ERA5 monthly averaged data on single levels from 1940 to present"
(CDS id: reanalysis-era5-single-levels-monthly-means), licence CC BY 4.0.

Credentials are NOT stored here. cdsapi reads them from the environment
(CDSAPI_URL / CDSAPI_KEY) or from ~/.cdsapirc.

Usage:
    python src/download_era5.py            # skips if the file already exists
    python src/download_era5.py --force    # re-download
"""

import argparse
import sys
from pathlib import Path

import cdsapi

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "data" / "raw" / "era5"
OUT_FILE = OUT_DIR / "era5_tcc_monthly_2015_2024.nc"

DATASET = "reanalysis-era5-single-levels-monthly-means"
YEARS = [str(y) for y in range(2015, 2025)]
MONTHS = [f"{m:02d}" for m in range(1, 13)]
# Same box as the CLAAS-3 order (51.5-56N, 5.5-15E); order is N, W, S, E.
AREA = [56.0, 5.5, 51.5, 15.0]

REQUEST = {
    "product_type": ["monthly_averaged_reanalysis"],
    "variable": ["total_cloud_cover"],
    "year": YEARS,
    "month": MONTHS,
    "time": ["00:00"],
    "area": AREA,
    "data_format": "netcdf",
    "download_format": "unarchived",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--force", action="store_true", help="re-download even if the file exists")
    args = parser.parse_args()

    if OUT_FILE.exists() and not args.force:
        print(f"{OUT_FILE.relative_to(REPO_ROOT)} already exists; use --force to re-download")
        return 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    client = cdsapi.Client()
    client.retrieve(DATASET, REQUEST).download(str(OUT_FILE))
    print(f"Saved {OUT_FILE.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
