"""Describe HOW each DWD station measured cloud cover in 2015-2024 (data QC, no analysis).

For every station that has at least one MO_N value in data/raw/dwd/, this script reads
two DWD open-data products for the same station:

1. Hourly cloudiness (hourly/cloudiness/historical): column V_N_I says per hour whether
   total cloud cover V_N was observed by a person ("P") or an instrument ("I").
   Per station and year we count valid hours (V_N in 0..8), hours by P and by I,
   hours with V_N = -1 (a code not defined in DWD's dataset description) and the
   share of valid hours that fall in the night window 21-03 UTC.
2. Monthly kl (monthly/kl/historical): the MO_N entries of Metadaten_Parameter (how the
   monthly value is built) and Metadaten_Geraete_Bedeckungsgrad (cloud instruments),
   restricted to entries that overlap 2015-2024.

Zip files are cached in data/raw/dwd/zips/ (git-ignored) and only read in memory.

Outputs (data/processed/):
  dwd_cloud_method_by_station_year.csv   one row per station and year
  dwd_cloud_method_by_station.csv        one row per station (summary + metadata text)

Usage:
    python src/dwd_station_metadata.py
"""

import io
import re
import sys
import urllib.request
import zipfile
from pathlib import Path

import polars as pl

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DWD = REPO_ROOT / "data" / "raw" / "dwd"
ZIP_DIR = RAW_DWD / "zips"
OUT_DIR = REPO_ROOT / "data" / "processed"

BASE = "https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/"
HOURLY_URL = BASE + "hourly/cloudiness/historical/"
MONTHLY_URL = BASE + "monthly/kl/historical/"

YEAR_MIN, YEAR_MAX = 2015, 2024
NIGHT_HOURS_UTC = {21, 22, 23, 0, 1, 2, 3}


def fetch(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=120) as r:
        return r.read()


def listing(url: str) -> list[str]:
    html = fetch(url).decode("latin1")
    return re.findall(r'href="([^"]+\.zip)"', html)


def cached_zip(base_url: str, name: str) -> zipfile.ZipFile:
    ZIP_DIR.mkdir(parents=True, exist_ok=True)
    path = ZIP_DIR / name
    if not path.exists():
        path.write_bytes(fetch(base_url + name))
    return zipfile.ZipFile(io.BytesIO(path.read_bytes()))


def read_member(zf: zipfile.ZipFile, prefix: str) -> str | None:
    names = [n for n in zf.namelist() if n.startswith(prefix) and n.endswith(".txt")]
    return zf.read(names[0]).decode("latin1") if names else None


def overlapping_rows(text: str | None, keep=lambda cols: True) -> list[dict]:
    """Rows of a DWD ';'-separated metadata table overlapping YEAR_MIN..YEAR_MAX."""
    if not text:
        return []
    lines = [ln for ln in text.splitlines() if ";" in ln]
    header = [h.strip() for h in lines[0].split(";")]
    out = []
    for ln in lines[1:]:
        cols = dict(zip(header, (c.strip() for c in ln.split(";"))))
        start = cols.get("Von_Datum", "")
        end = cols.get("Bis_Datum", "") or "99991231"
        if not (start[:4].isdigit() and end[:4].isdigit()):
            continue
        if int(start[:4]) <= YEAR_MAX and int(end[:4]) >= YEAR_MIN and keep(cols):
            out.append(cols)
    return out


def hourly_by_year(zf: zipfile.ZipFile, station_id: str) -> list[dict]:
    text = read_member(zf, "produkt_n_stunde")
    stats: dict[int, dict] = {}
    for ln in text.splitlines()[1:]:
        cols = [c.strip() for c in ln.split(";")]
        if len(cols) < 5:
            continue
        stamp, method, value = cols[1], cols[3], int(cols[4])
        year = int(stamp[:4])
        if not YEAR_MIN <= year <= YEAR_MAX:
            continue
        s = stats.setdefault(
            year,
            {"n_valid": 0, "n_person": 0, "n_instrument": 0, "n_minus1": 0, "n_missing": 0, "n_night": 0},
        )
        if value == -999:
            s["n_missing"] += 1
        elif value == -1:
            s["n_minus1"] += 1
        elif 0 <= value <= 8:
            s["n_valid"] += 1
            s["n_person"] += method == "P"
            s["n_instrument"] += method == "I"
            s["n_night"] += int(stamp[8:10]) in NIGHT_HOURS_UTC
    return [{"station_id": station_id, "year": y, **v} for y, v in sorted(stats.items())]


def main() -> int:
    values = pl.read_csv(
        RAW_DWD / "dwd_mo_n_monthly_2015_2024.csv", schema_overrides={"station_id": pl.Utf8}
    )
    stations = pl.read_csv(RAW_DWD / "dwd_stations.csv", schema_overrides={"station_id": pl.Utf8})
    months = (
        values.filter(pl.col("value").is_not_null())
        .group_by("station_id")
        .agg(pl.len().alias("n_months_mo_n"))
    )
    ids = sorted(months["station_id"].to_list())
    print(f"{len(ids)} stations with MO_N data")

    hourly_files = listing(HOURLY_URL)
    monthly_files = listing(MONTHLY_URL)

    year_rows, station_rows = [], []
    for sid in ids:
        h_name = next((f for f in hourly_files if f.startswith(f"stundenwerte_N_{sid}_")), None)
        m_name = next((f for f in monthly_files if f.startswith(f"monatswerte_KL_{sid}_")), None)

        rows = hourly_by_year(cached_zip(HOURLY_URL, h_name), sid) if h_name else []
        year_rows.extend(rows)

        param_txt, instr_txt = "", ""
        if m_name:
            zf = cached_zip(MONTHLY_URL, m_name)
            params = overlapping_rows(
                read_member(zf, "Metadaten_Parameter"), keep=lambda c: c.get("Parameter") == "MO_N"
            )
            param_txt = " | ".join(
                f"{p['Von_Datum']}-{p['Bis_Datum']}: {p.get('Datenquelle (Strukturversion=SV)', '')}"
                for p in params
            )
            instr = overlapping_rows(read_member(zf, "Metadaten_Geraete_Bedeckungsgrad"))
            instr_txt = " | ".join(
                f"{i['Von_Datum']}-{i['Bis_Datum']}: {i.get('Geraetetyp Name', '')}" for i in instr
            )

        valid = sum(r["n_valid"] for r in rows)
        person = sum(r["n_person"] for r in rows)
        instrument = sum(r["n_instrument"] for r in rows)
        method_by_year = {
            r["year"]: ("P" if r["n_person"] >= r["n_instrument"] else "I") for r in rows if r["n_valid"]
        }
        station_rows.append(
            {
                "station_id": sid,
                "has_hourly_cloud_file": h_name is not None,
                "hourly_valid_hours": valid,
                "share_person": round(person / valid, 3) if valid else None,
                "share_instrument": round(instrument / valid, 3) if valid else None,
                "majority_method_by_year": " ".join(f"{y}:{m}" for y, m in method_by_year.items()),
                "mo_n_metadata": param_txt,
                "cloud_instruments": instr_txt,
            }
        )
        print(f"{sid}: hourly={'yes' if h_name else 'no '} valid_hours={valid}")

    by_year = pl.DataFrame(year_rows).with_columns(
        (pl.col("n_valid") / pl.col("year").map_elements(
            lambda y: 366 if y % 4 == 0 else 365, return_dtype=pl.Int64)).round(2).alias("valid_hours_per_day"),
        (pl.col("n_night") / pl.col("n_valid")).round(3).alias("night_share"),
    )
    by_station = (
        pl.DataFrame(station_rows)
        .join(months, on="station_id")
        .join(stations.select("station_id", "name", "latitude", "longitude"), on="station_id")
        .select("station_id", "name", "latitude", "longitude", "n_months_mo_n", pl.exclude(
            "station_id", "name", "latitude", "longitude", "n_months_mo_n"))
        .sort("station_id")
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    by_year.write_csv(OUT_DIR / "dwd_cloud_method_by_station_year.csv")
    by_station.write_csv(OUT_DIR / "dwd_cloud_method_by_station.csv")
    print("Saved data/processed/dwd_cloud_method_by_station_year.csv and dwd_cloud_method_by_station.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
