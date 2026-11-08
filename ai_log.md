# AI log

## 2026-11-08 — Phase 3 (Data), session 1: CLAAS-3 archives

**Asked:** Move the two CM SAF order archives into `data/raw/claas3/`, verify their
MD5 checksums, write `src/extract_claas3.py`, report file count / naming / metadata of
the CLAAS-3 files (no plots), test network access to the CDS API and opendata.dwd.de,
create `ai_log.md` and `next_questions.md`, commit.

**Done:**
- `git mv` of `ORD71208.tar` and `ORD71209.tar` into `data/raw/claas3/`.
- MD5 of both archives matches the CM SAF values.
- `src/extract_claas3.py` re-checks the MD5s, refuses archive members that are not plain
  `.nc` files, and extracts with `tarfile` `filter="data"`. The extracted `.nc` files are
  git-ignored (`data/raw/claas3/*.nc`).
- 120 files (72 + 48), 2015-01 .. 2024-12, no missing months.
- Checked in all 120 files: grid identical (90 lat x 190 lon, 0.05°, cell centres
  51.525–55.975°N, 5.525–14.975°E); `cfc` stored as int32 in `%`, range 23–98, no fill
  values (-999) present; `record_status` = 0 (ok) everywhere; `nobs` (daily means per
  month) never below the number of days in the month.
- Connectivity: both cds.climate.copernicus.eu and opendata.dwd.de are blocked by this
  environment's network proxy (HTTP 403 on CONNECT). Nothing was downloaded.

**Where I went wrong / was uncertain:**
- The global attributes `geospatial_lat/lon_min/max` say -90..90 (full-disk values copied
  from the original product), not the cut region. I did not use them; extent was taken
  from the `lat`/`lon` coordinates and their bounds instead. Flagging it so nobody relies
  on those attributes later.
- The `platform` attribute changes during the record (Meteosat-10 → 11 in 2018-02,
  Meteosat-9 in 2019-01 only, empty in 2022-01, Meteosat-10 from 2023-03). I only report
  it; I have not checked whether it matters. It is a second candidate discontinuity
  besides the CDR → ICDR switch in 2021-01.
- CLAUDE.md calls the archives "CDR v004" / "ICDR v004i1"; the files themselves report
  `product_version = 3.0` (CLAAS edition 3). The "004" appears only in the file names.
  Not resolved; left for the user to confirm.
- First attempt at a small cleanup in the script used `sed` with a `\n` pattern, which
  silently did nothing; caught when I grepped the file afterwards, fixed with a proper edit.
- `xarray` / `netCDF4` were not installed in the container; installed with pip for the
  inspection only. No environment file yet (that is phase 6).
