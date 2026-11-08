# Methods notes — Note #1 (ERA5 vs CLAAS-3 vs DWD cloud cover)

Running record of verified facts, decisions and open questions, kept so nothing has to be
remembered. Every fact points to where it was checked. This is a notebook, not the paper:
the user writes the paper (phases 7–9).

Status tags: **[verified]** checked in the data/files · **[doc]** from documentation, not
checked in data · **[to verify]** my (Claude's) statement, still needs a source ·
**[decided]** · **[open]**

---

## 0. Big picture — where we are

**Question:** In which season does ERA5 total cloud cover deviate most from CLAAS-3 over
Northern Germany, and — with DWD stations as referee — how much of the deviation is
ERA5's and how much the satellite's?

**Logic of the study:** two "players" (ERA5 model, CLAAS-3 satellite) and one "referee"
(DWD stations). If ERA5 and CLAAS-3 disagree, the station tells which one is closer.
That only works if the referee is trustworthy → hence the DWD checks in §2 and the
station rules in §4.

| Phase | Owner | Status |
|---|---|---|
| 1 Question | user | done (CLAUDE.md) |
| 2 Physics: what each dataset measures | user | partly done (§3, §5); continues alongside phase 4 |
| 3 Data: download, units, ranges, referee check, station rules | Claude | **done 2026-11-08** |
| 4 Analysis: figures | Claude | **in progress** (steps below) |
| 5 Interpretation | user | — (analysis frozen afterwards) |
| 6 Code packaging | Claude | — |
| 7–9 Writing, preprint, Substack | user | — |

**Phase 4 steps**

| # | Step | Status |
|---|---|---|
| 4.1 | One loader, all data in fraction 0–1, station rules D1/D2 in code (`src/load_data.py`) | done |
| 4.2 | Fig (a): 10-year mean maps (`src/fig_a_mean_maps.py`) | draft done |
| 4.3 | Fig (b): seasonal cycle of all three | next |
| 4.4 | Fig (c): ERA5 and CLAAS-3 at station locations vs station values, by season, instrument/observer separate | — |
| 4.5 | Break test (D3): CLAAS−station vs ERA5−station before/after 2021 | needs user's "what if a jump is found" |
| 4.6 | Table of seasonal differences — the numbers that answer the question | — |

**How the notes map onto the paper:** Introduction ← question (§0) · Data ← §1–2 ·
Methods ← §3–4 · Results ← §8 + figures · Discussion ← user's hypotheses (§5) and
phase 5 · Limitations ← open items in §4 and §6.

## 1. Data sources

| | CLAAS-3 | ERA5 | DWD |
|---|---|---|---|
| Product | CM SAF CLAAS ed. 3, monthly means; CDR 2015-01..2020-12, ICDR 2021-01..2024-12 | ERA5 monthly averaged data on single levels (`reanalysis-era5-single-levels-monthly-means`), product type monthly_averaged_reanalysis | DWD CDC monthly kl (climate_summary), via wetterdienst 0.185.0 |
| Variable | `cfc` | `tcc` | `MO_N` (`cloud_cover_total_mean`) |
| Unit as stored | % (int32) | fraction, "(0 - 1)" (float32) | octas, 1/8 |
| Grid / sites | 0.05°, 90 lat × 190 lon, centres 51.525–55.975°N, 5.525–14.975°E | 0.25°, 19 × 39, 51.5–56°N, 5.5–15°E, lat stored N→S | 76 stations with data in 52–55.5°N, 6–14.5°E |
| Licence / credit | CC BY 4.0, © EUMETSAT, DOI 10.5676/EUM_SAF_CM/CLAAS/V003 | CC BY 4.0, C3S/CDS, DOI 10.24381/cds.f17050d7 | CC BY 4.0, "Data basis: Deutscher Wetterdienst" |
| Script | `src/extract_claas3.py` | `src/download_era5.py` | `src/download_dwd.py`, `src/dwd_station_metadata.py` |

## 2. Verified facts (data checks, phase 3)

### CLAAS-3
- 120 files, no missing month; MD5 of both order archives match CM SAF. **[verified]**
- Grid identical in all 120 files. **[verified]**
- `cfc` range 23–98 %, no fill values (-999) present, `record_status` = 0 (ok) in all
  files, `nobs` (daily means per month) = number of days in every month. **[verified]**
- Global attributes `geospatial_lat/lon_min/max` say −90..90: full-disk values, NOT the
  cut region. Use the coordinates. **[verified]**
- `platform` attribute changes: Meteosat-10 (2015-01) → Meteosat-11 (2018-02) →
  Meteosat-9 (2019-01 only) → Meteosat-11 (2019-02) → empty (2022-01) → Meteosat-11
  (2022-02) → Meteosat-10 (2023-03..2024-12). **[verified]**
- Files report `product_version = 3.0`; "004" appears only in file names (CLAUDE.md says
  "v004"). **[open]** — which is the correct version label for citation?

### ERA5
- 120 monthly steps 2015-01..2024-12, `tcc` range 0.271–0.924, no NaN. **[verified]**
- `expver` = 0001 for all months → final ERA5, no preliminary ERA5T. **[verified]**

### DWD
- 146 stations in the box, 76 with ≥ 1 MO_N value in 2015–2024; 6924 station-months.
  Only 1 station complete (120 months), 19 with ≥ 108. Fewest stations: 2018-09 (28). **[verified]**
- wetterdienst run with `convert_units=False` (default True!) and plausibility `soft`
  (default nulls values). Output identical to the raw DWD zip for Hamburg-Fuhlsbüttel
  (01975), 120/120 months. **[verified]**
- **MO_N is a 24-hour mean**: over 6854 station-months, |MO_N − mean of all valid hourly
  V_N| has median 0.007 octa (instrument) / 0.010 (observer); vs mean of 06/12/18 UTC
  only: 0.12–0.16. The metadata text ("3 Termine 06, 12, 18 UTC und Tageswerte aus
  stündlichen Werten…") is ambiguous; the data decide. **[verified]**
- Measurement method per station-year (hourly `V_N_I`, P = person, I = instrument),
  table in `data/processed/dwd_cloud_method_by_station*.csv`: **[verified]**
  - 48 stations instrument-only (median 102 months of MO_N)
  - 12 observer-only (median 40 months; 10 % of observer station-years < 16 valid h/day)
  - 15 switch observer → instrument during 2016–2023 (median 113 months), e.g.
    Hamburg 2022, Bremen 2022, Hannover 2022, Potsdam 03987 2020, Lindenberg 2020
- Night hours (21–03 UTC) are ≈ 7/24 of valid hours in both groups. **[verified]**
- Code `V_N = -1` appears in 17,105 hours, more in observer years; NOT defined in DWD's
  hourly description. **[open]**
- Potsdam Säkularstation (03988): 9 months with MO_N > 8 (max 8.94), QN = 1; built from
  3 terms (~07, 14, 21 local); series ends 2019-12. DWD docs do not explain values > 8. **[verified]**
- wetterdienst warns: stations 01018, 02996, 05047 have data files but are not in DWD's
  station list, so they are not requested. **[open]** (location not checked)

## 3. Definitions — what each number is (phase 2 material)

- **ERA5 `tcc`**: model-diagnosed fraction of the grid box covered by cloud; cloud layers
  at different model levels combined with an overlap assumption into one number, 0–1.
  Cloud fraction observations are not assimilated directly. User's wording: "Katmanlar
  bir örtüşme varsayımıyla üst üste konup tek sayıya indiriliyor: yukarıdan bakınca
  kutunun ne kadarı bulutla kapalı?" **[doc]** (check ECMWF ERA5 documentation for the
  exact definition and citation)
- **CLAAS-3 `cfc`**: each SEVIRI pixel classified binary cloudy/clear per slot; monthly
  `cfc` = share of cloudy observations in the 0.05° box (mean of daily means). At 0.05°
  roughly one SEVIRI pixel per box → effectively a frequency of cloud occurrence.
  **[to verify]** in the CLAAS-3 Product User Manual.
- **DWD `MO_N`**: observer = estimate of the whole sky dome; ceilometer = vertical beam
  over the site, cloud cover derived from the time series. Both aggregated to a 24-h
  daily mean, then monthly mean (verified above). **[doc]** for the ceilometer algorithm.
- **Viewing geometry**: SEVIRI at 0° longitude views Northern Germany at a satellite
  zenith angle of roughly 60°. **[to verify]** compute the exact angle for the box.

### Sampling

| | Values per day | Night | Monthly value |
|---|---|---|---|
| CLAAS-3 | 96 slots (15 min) | yes, IR-only algorithm | mean of daily means **[to verify]** |
| ERA5 | 24 (hourly) | yes | mean of hourly fields **[doc]** |
| DWD MO_N | ~24 (hourly) | yes | mean of daily means of hourly values **[verified]** |

### Unit conversion (to be applied in phase 4, not yet done)
- CLAAS-3 % → fraction: ÷ 100. ERA5: already fraction. DWD octas → fraction: ÷ 8.

## 4. Decisions

| # | Date | Decision | Justification (a priori) | Status |
|---|---|---|---|---|
| D1 | 2026-11-08 | Use Potsdam 03987, drop 03988 | Two series at the same site would double-count it; 03987 is the regular operational station, longer record (114 vs 60 months); 03988 ends 2019 and its months have QN = 1 | **[decided]** |
| D2a | 2026-11-08 | DWD stations: keep only stations whose measurement method does not change in 2015–2024 (48 instrument-only + 12 observer-only; the 15 switching stations are excluded) | A method change is a non-climatic break in the referee; a referee must be homogeneous in time. The paper should state why the 15 were excluded (user's request) | **[decided]** |
| D2b | 2026-11-08 | Completeness: every season (DJF, MAM, JJA, SON) must have ≥ 21 of its 30 months of MO_N (70 %). Leaves 39 stations: 36 instrument, 3 observer (Berlin-Dahlem 00403, Nordholz-Wanhöden 03639, Berlin Brandenburg 00427). Rejected alternative: ≥ 84 months in total (47 stations), because it allowed stations with only 16/30 DJF or SON months | User: "the research question is seasonal", so completeness must hold per season, not only in total | **[decided]** |
| D2c | 2026-11-08 | Report instrument and observer stations separately | User: they measure conceptually different quantities (frequency at a point vs sky-area fraction, §3). Consequence to state: the observer group has n = 3 (two in Berlin) → main result rests on the 36 instrument stations; observer group is a small side comparison | **[decided]** |
| D3 | 2026-11-08 | CLAAS-3 2021 break (and platform changes): test whether a jump in CLAAS−station after 2021-01 also appears in ERA5−station (control series). Same jump in both → common cause (weather/station side); jump only in CLAAS−station → evidence for a satellite-side break | User: "check whether the other sources also jump, to see if it is weather-related" | **[decided: test]** · what to do if a CLAAS-only jump is found: **[open]** |

Selected stations (D2a + D2b), 39 ids: 00298 00342 00403 00427 00591 00596 00662 00704
00963 01200 01503 01544 01694 01759 01869 02115 02794 02907 03032 03086 03093 03196 03639
03897 04024 04039 04371 04625 04745 05109 05142 05158 05349 05516 05839 05930 06163 07351
07374. Extent: 52.08–55.01°N, 6.94–14.07°E. **[verified]** (to be implemented in phase-4
code, not hand-copied)
| D4 | — | Treatment of `V_N = -1` (affects only hourly-based checks; MO_N is DWD's own) | — | **[open]** |

## 5. User's hypotheses (phase 2, in the user's words)

- H1: The slanted satellite view may cause CLAAS-3 to overestimate cloud cover.
  Still needed: mechanism, which cloud types, and a test with the available data.

### Conceptual pairing (discussed 2026-11-08)
- User: ceilometer is close to CLAAS and ERA5 ("same point"); observer looks at the whole sky.
- Refinement given: by *kind of quantity*, ceilometer (yes/no over a point, averaged in
  time → frequency) pairs with CLAAS-3 (binary pixel, averaged in time → frequency);
  observer (fraction of a sky area) pairs with ERA5 (fraction of a grid-box area).
  Spatial footprints still differ (point / ~4–6 km pixel / sky dome / ~25 km box).
  **[to verify]** against literature before it goes into the paper.

## 6. Open questions for the user

1. Two breaks (CLAAS 2021, DWD method switches 2016–2023) can overlap in time — how does
   the design separate them? D2a removes the DWD side; D3 still open (see the
   "control series" idea taught on 2026-11-08: compare CLAAS−station and ERA5−station
   before/after 2021).
2. ERA5 is an area fraction, CLAAS a frequency — when do their monthly means converge?
3. Observers also look at slant angles toward the horizon — does that connect to H1?

## 7. Points the paper will need to state (methods)

- Units of the three datasets and the conversion used.
- That MO_N was verified to be a 24-h mean (numbers in §2).
- wetterdienst settings (no unit conversion, soft plausibility) and the raw-file cross-check.
- Station selection rule (D2) stated before results; Potsdam choice (D1).
- Why the 15 observer → instrument stations were excluded, with their switch years
  (table: `data/processed/dwd_cloud_method_by_station.csv`).
- CLAAS-3 CDR/ICDR split and platform changes; how D3 was handled.
- DWD observer → instrument transitions in the study period and how they were handled.
- ERA5 version: final ERA5 only (expver 0001).
- Credits: © EUMETSAT + CLAAS-3 DOI, C3S ERA5 DOI, DWD.

## 8. Results log (descriptive only — interpretation is phase 5, by the user)

### Fig (a) `figures/fig_a_mean_maps.png` — 10-year mean (mean of 12 monthly climatologies)
- Study-box mean, cos-lat weighted: CLAAS-3 0.682, ERA5 0.674. **[verified]**
- Grid range of the 10-year mean: CLAAS-3 0.616–0.819, ERA5 0.630–0.701. **[verified]**
- Stations: instrument (n = 36) mean 0.714, range 0.632–0.773; observer (n = 3) mean
  0.676, range 0.656–0.712. **[verified]**
- Visible in the maps: CLAAS-3 values are higher over sea and along coastlines than
  over land; ERA5 field is smoother with a smaller range. **[verified, visual]**
- Caveat: grid means use all 120 months, station means only the months available.
