# paper01-era5-claas3-cloud-cover
Model error or satellite artefact? A three-way comparison of cloud cover over Northern Germany

## Data

| Dataset | Variable | Unit | Location in repo | Obtained by |
|---|---|---|---|---|
| CM SAF CLAAS-3 monthly means (CDR 2015–2020, ICDR 2021–2024), 0.05° | `cfc` | % | `data/raw/claas3/*.tar` | CM SAF order; `python src/extract_claas3.py` |
| ERA5 monthly averaged data on single levels, 0.25° | `tcc` | fraction (0–1) | `data/raw/era5/` | `python src/download_era5.py` (needs a CDS account) |
| DWD station monthly climate data (kl) | `MO_N` | octas (0–8) | `data/raw/dwd/` | `python src/download_dwd.py` |

### Credits and licences

- **CLAAS-3:** © EUMETSAT. CM SAF CLoud property dAtAset using SEVIRI, edition 3.
  DOI: [10.5676/EUM_SAF_CM/CLAAS/V003](https://doi.org/10.5676/EUM_SAF_CM/CLAAS/V003). Licence: CC BY 4.0.
- **ERA5:** Hersbach et al. (2023), ERA5 monthly averaged data on single levels from 1940 to present,
  Copernicus Climate Change Service (C3S) Climate Data Store (CDS),
  DOI: [10.24381/cds.f17050d7](https://doi.org/10.24381/cds.f17050d7). Licence: CC BY 4.0.
- **DWD:** Data basis: Deutscher Wetterdienst, Climate Data Center (opendata.dwd.de). Licence: CC BY 4.0.
