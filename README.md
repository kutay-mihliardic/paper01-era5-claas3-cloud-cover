# Model error or satellite artefact? A three-way comparison of cloud cover over Northern Germany

Monthly total cloud cover over Northern Germany (52–55.5°N, 6–14.5°E), 2015–2024, from
three sources:

- **ERA5** reanalysis total cloud cover (`tcc`, model grid-box fraction, 0.25°)
- **CM SAF CLAAS-3** satellite cloud fractional cover (`cfc`, SEVIRI on Meteosat, 0.05°)
- **DWD** ground stations, monthly mean total cloud cover (`MO_N`, octas) as the referee

All three are converted to a fraction (0–1). ERA5 and CLAAS-3 are compared with each
other and with the stations at the station locations, by season. The station network
is checked as a referee: stations are grouped by how they measure cloud cover
(human observer or ceilometer), and stations that switched method during the period
are used for a separate before/after test.

## Quick start

```bash
conda env create -f environment.yml      # or: pip install -r requirements.txt  (Python 3.13)
conda activate paper01-cloud-cover
make all                                 # or: python run.py
```

`make all` reproduces every figure and table from the data committed in this
repository (about 15 s; the first run also downloads Natural Earth coastlines for
cartopy). It needs no account or API key.

| Step | Script | Output |
|---|---|---|
| Verify MD5 and extract CLAAS-3 archives | `src/extract_claas3.py` | `data/raw/claas3/*.nc` (git-ignored) |
| Figure 1 — 10-year mean maps | `src/fig_a_mean_maps.py` | `figures/fig_a_mean_maps.png` |
| Figure 2 — seasonal cycle at the stations | `src/fig_b_seasonal_cycle.py` | `figures/fig_b_seasonal_cycle.png`, `data/processed/fig_b_monthly_climatology.csv` |
| Figure 3 — station scatter by season | `src/fig_c_station_scatter.py` | `figures/fig_c_station_scatter.png`, `data/processed/fig_c_*.csv` |
| Table 1 — seasonal differences, full period and CDR/ICDR sub-periods | `src/table1_seasonal_differences.py` | `data/processed/table1_seasonal_differences.csv` |
| Figure S1 — CLAAS-3 CDR → ICDR break test | `src/break_test_2021.py` | `figures/figS1_break_test_2021.png`, `data/processed/break_test_2021.csv` |
| Figure S2 — observer → instrument switch test | `src/method_switch_test.py` | `figures/figS2_method_switch.png`, `data/processed/method_switch_test.csv` |

Shared code: `src/load_data.py` (loading, unit conversion, station selection, sampling
at stations).

### Re-downloading the inputs (optional)

```bash
make data                                # or: python run.py data
```

- **ERA5** needs a Copernicus CDS account with the licence of the dataset accepted. The
  API key is read by `cdsapi` from `~/.cdsapirc` or the `CDSAPI_URL` / `CDSAPI_KEY`
  environment variables; it is never stored in this repository.
- **DWD** data are open. DWD revises its archive, so re-downloaded files can differ
  slightly from the committed ones; the committed files were downloaded on 2026-11-08.
- `src/dwd_station_metadata.py` downloads about 75 MB of DWD hourly cloudiness files
  (cached in `data/raw/dwd/zips/`, git-ignored) to derive the measurement method of each
  station.

## Repository layout

```
data/raw/claas3/     CM SAF order archives (.tar, committed); extracted .nc git-ignored
data/raw/era5/       ERA5 monthly tcc (NetCDF, committed)
data/raw/dwd/        DWD monthly MO_N and station list (CSV, committed)
data/processed/      derived tables (committed)
figures/             figures
src/                 code
paper/skeleton.md    outline of the research note
methods_notes.md     verified facts, decisions (with reasons), open questions, sources
next_questions.md    ideas for follow-up notes
ai_log.md            working log
```

## Data

| Dataset | Variable | Unit | Location in repo | Obtained by |
|---|---|---|---|---|
| CM SAF CLAAS-3 monthly means (CDR 2015–2020, ICDR 2021–2024), 0.05° | `cfc` | % | `data/raw/claas3/*.tar` | CM SAF order; `python src/extract_claas3.py` |
| ERA5 monthly averaged data on single levels, 0.25° | `tcc` | fraction (0–1) | `data/raw/era5/` | `python src/download_era5.py` (needs a CDS account) |
| DWD station monthly climate data (kl) | `MO_N` | octas (0–8) | `data/raw/dwd/` | `python src/download_dwd.py` |

### Credits and licences

- **CLAAS-3:** © EUMETSAT. Meirink, J. F. et al. (2022): CLAAS-3: CM SAF CLoud property dAtAset using SEVIRI - Edition 3, Satellite Application Facility on Climate Monitoring.
  DOI: [10.5676/EUM_SAF_CM/CLAAS/V003](https://doi.org/10.5676/EUM_SAF_CM/CLAAS/V003). Licence: CC BY 4.0.
- **ERA5:** Copernicus Climate Change Service (2023): ERA5 monthly averaged data on single levels from 1940 to present.
  Copernicus Climate Change Service (C3S) Climate Data Store (CDS),
  DOI: [10.24381/cds.f17050d7](https://doi.org/10.24381/cds.f17050d7). Licence: CC BY 4.0.
  Key reference: Hersbach, H. et al. (2020), The ERA5 global reanalysis, QJRMS, doi:10.1002/qj.3803.
- **DWD:** Data basis: Deutscher Wetterdienst, Climate Data Center (opendata.dwd.de). Licence: CC BY 4.0.
- Coastlines in Figure 1: Natural Earth (public domain), via cartopy.

The code is released under the MIT License (`LICENSE`). The data keep their own
licences listed above.
