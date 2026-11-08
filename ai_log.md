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

## 2026-11-08 — Phase 3 (Data), session 1 (continued): ERA5 and DWD downloads

**Asked:** Get network access sorted out, then download ERA5 and DWD data via scripts
(no manual downloads). Also asked me to explain the CLAAS-3 variables in plain terms.

**Done:**
- Push to GitHub first failed (403, no GitHub App access); the user reconnected GitHub and
  the push then worked.
- Created a personal cloud environment for this repo allowing `cds.climate.copernicus.eu`,
  `opendata.dwd.de` and (added later, see below) `object-store.os-api.cci2.ecmwf.int`. The CDS
  token is stored as an environment network secret and injected by the proxy; it is not in
  any file, variable or commit. Scripts run with `CDSAPI_KEY=proxy-injected` as a placeholder.
- `src/download_era5.py`: ERA5 monthly means, `tcc`, 2015-01..2024-12, box 51.5–56°N,
  5.5–15°E. Checked: 120 time steps, 19 x 39 grid at 0.25° (lat 56.0 → 51.5 descending),
  units "(0 - 1)", range 0.271–0.924, no NaN, `expver` = 0001 for all months (no ERA5T).
  Licence of this CDS dataset is CC BY 4.0 (read from the CDS catalogue API).
- `src/download_dwd.py`: DWD monthly kl, `cloud_cover_total_mean` (= `MO_N`), via
  wetterdienst 0.185.0 with `convert_units=False` (default is True!) and plausibility
  `soft` (default would null implausible values). 146 stations returned in the box, 76 of
  them have at least one non-missing month in 2015–2024; 6924 non-missing station-months.
  Only 1 station has all 120 months; 19 have ≥ 108. Fewest stations: 2018-09 (28).
- Cross-checked wetterdienst output against the raw DWD zip for Hamburg-Fuhlsbüttel
  (01975): 120/120 months identical, so no unit conversion or filtering happened.

**Where I went wrong / was uncertain:**
- I first told the user only two hosts were needed. The CDS serves the result files from
  a third host (`object-store.os-api.cci2.ecmwf.int`); the first download hung on a 0-byte
  file. Caught by checking the file size, confirmed with a curl test (403 from proxy).
- wetterdienst uses aiohttp, which ignores HTTPS_PROXY unless `trust_env=True`; the first
  DWD attempt failed with a DNS error. Fixed via `Settings(fsspec_client_kwargs=...)`.
- I misused the wetterdienst API once (`.values` vs `.values()`), and my first raw-file
  cross-check silently compared nothing (wrong string filter); noticed because it printed
  no rows, fixed and re-run.
- **Open data issue, not resolved:** Potsdam (Säkularstation, 03988) has 9 months with
  MO_N > 8 (max 8.94), which is outside the 0–8 octa scale. wetterdienst flags them
  `suspect:range`; DWD quality level QN_4 = 1 for these rows. Kept as-is in raw data;
  how to treat them is the user's decision.
- wetterdienst warns that 3 stations (01018, 02996, 05047) have data files but are not in
  DWD's station list, so they cannot be requested. I did not check where they are.
- The CLAAS-3 variable explanation: `cfc_std` as "day-to-day std within the month" and the
  low/mid/high split by cloud-top pressure are from my general knowledge, not checked
  against the CLAAS-3 product user manual. Told the user so.
