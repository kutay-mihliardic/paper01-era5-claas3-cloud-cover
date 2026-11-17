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
| 4 Analysis: figures | Claude | **done 2026-11-14** (user approved figures as final) |
| 5 Interpretation | user (+ Claude at user's request, §5b) | closed 2026-11-14 when the user moved to phase 6; **analysis frozen** |
| 6 Code packaging | Claude | merged to main 2026-11-17 (PR #1, bc03028); `make all` re-verified on main; tag `v1.0.0` → user creates it as a GitHub release (tag push blocked here) |
| 7–9 Writing, preprint, Substack | user | skeleton: `paper/skeleton.md` |

**Phase 4 steps**

| # | Step | Status |
|---|---|---|
| 4.1 | One loader, all data in fraction 0–1, station rules D1/D2 in code (`src/load_data.py`) | done |
| 4.2 | Fig (a): 10-year mean maps (`src/fig_a_mean_maps.py`) | draft done |
| 4.3 | Fig (b): seasonal cycle at the stations, matched sampling (`src/fig_b_seasonal_cycle.py`) | draft done |
| 4.4 | Fig (c): station seasonal means, grid vs station (`src/fig_c_station_scatter.py`) | draft done |
| 4.5 | Break test (`src/break_test_2021.py`, fig S1) | done; handled by D3c |
| 4.6 | Table 1: seasonal differences, full period + CDR/ICDR sensitivity (`src/table1_seasonal_differences.py`) | done |
| 4.7 | Method-switch natural experiment (D5, `src/method_switch_test.py`, fig S2) | done |

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
| Licence / credit | CC BY 4.0, © EUMETSAT; cite Meirink et al. (2022), DOI 10.5676/EUM_SAF_CM/CLAAS/V003 (S1) | CC BY 4.0; cite Copernicus Climate Change Service (2023), DOI 10.24381/cds.f17050d7 (S2), key paper Hersbach et al. (2020) | CC BY 4.0, "Data basis: Deutscher Wetterdienst" |
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

- **ERA5 `tcc`**: verbatim (CDS variable table, S2): "This parameter is the proportion of
  a grid box covered by cloud. Total cloud cover is a single level field calculated from
  the cloud occurring at different model levels through the atmosphere. Assumptions are
  made about the degree of overlap/randomness between clouds at different heights. Cloud
  fractions vary from 0 to 1." **[verified, source S2]** User's wording matches: "Katmanlar
  bir örtüşme varsayımıyla üst üste konup tek sayıya indiriliyor: yukarıdan bakınca
  kutunun ne kadarı bulutla kapalı?" — Claim "cloud fraction observations are not
  assimilated directly" **[to verify]** (not found in S2).
- **CLAAS-3 `cfc`**: verbatim (PUM, S3, §4.1): "The cloud fractional cover L3 product
  (monthly and daily mean, as well as monthly mean diurnal cycle) is defined as the
  fraction of cloudy pixels per grid box compared to the total number of analyzed pixels in
  the grid box. Pixels are counted as cloudy if the corresponding cloud probability is
  higher than 50%." L2 pixels: 3 × 3 km² at the sub-satellite point, 15-min resolution
  (S3 §3). Day = SZA < 75°, night = SZA > 95°, twilight excluded from day/night splits (S3).
  **[verified, source S3]** The file attribute of `nobs` reads "number of daily means"
  → monthly = mean of daily means. **[verified, file attribute]** "Roughly one pixel per
  0.05° box → effectively a frequency" remains Claude's inference **[to verify]**.
- **DWD `MO_N`**: observer = estimate of the whole sky dome; ceilometer = vertical beam
  over the site, cloud cover derived from the time series. Both aggregated to a 24-h
  daily mean, then monthly mean (verified above). **[doc]** for the ceilometer algorithm.
- **Viewing geometry**: satellite viewing zenith angle over the study box (corners) is
  59.7–64.6° for a sub-satellite point at 0°E (59.5–64.0° at 3.5°E, 59.6–63.4° at 9.5°E);
  computed from spherical geometry (R = 6371 km, orbit radius 42164 km). **[verified, computed]**

### Sampling

| | Values per day | Night | Monthly value |
|---|---|---|---|
| CLAAS-3 | 96 slots (15 min) | yes; day/night split at SZA 75°/95° | mean of daily means **[verified]** |
| ERA5 | 24 (hourly) | yes | mean of hourly fields **[doc]** |
| DWD MO_N | ~24 (hourly) | yes | mean of daily means of hourly values **[verified]** |

### Unit conversion (implemented in `src/load_data.py`)
- CLAAS-3 % → fraction: ÷ 100. ERA5: already fraction. DWD octas → fraction: ÷ 8.

## 4. Decisions

| # | Date | Decision | Justification (a priori) | Status |
|---|---|---|---|---|
| D1 | 2026-11-08 | Use Potsdam 03987, drop 03988 | Two series at the same site would double-count it; 03987 is the regular operational station, longer record (114 vs 60 months); 03988 ends 2019 and its months have QN = 1 | **[decided]** |
| D2a | 2026-11-08 | DWD stations: keep only stations whose measurement method does not change in 2015–2024 (48 instrument-only + 12 observer-only; the 15 switching stations are excluded) | A method change is a non-climatic break in the referee; a referee must be homogeneous in time. The paper should state why the 15 were excluded (user's request) | **[decided]** |
| D2b | 2026-11-08 | Completeness: every season (DJF, MAM, JJA, SON) must have ≥ 21 of its 30 months of MO_N (70 %). Leaves 39 stations: 36 instrument, 3 observer (Berlin-Dahlem 00403, Nordholz-Wanhöden 03639, Berlin Brandenburg 00427). Rejected alternative: ≥ 84 months in total (47 stations), because it allowed stations with only 16/30 DJF or SON months | User: "the research question is seasonal", so completeness must hold per season, not only in total | **[decided]** |
| D2c | 2026-11-08 | Report instrument and observer stations separately | User: they measure conceptually different quantities (frequency at a point vs sky-area fraction, §3). Consequence to state: the observer group has n = 3 (two in Berlin) → main result rests on the 36 instrument stations; observer group is a small side comparison | **[decided]** |
| D3 | 2026-11-08 | CLAAS-3 2021 break (and platform changes): test whether a jump in CLAAS−station after 2021-01 also appears in ERA5−station (control series). Same jump in both → common cause (weather/station side); jump only in CLAAS−station → evidence for a satellite-side break | User: "check whether the other sources also jump, to see if it is weather-related" | **[decided]** |
| D3b | 2026-11-14 | If the D3 test finds a jump only in CLAAS−station: report the CDR period (2015–2020) and the ICDR period (2021–2024) separately | User's choice (option a of: separate periods / CDR only / whole period + limitation), made before seeing the test result | **[decided]** |
| D3c | 2026-11-14 | No threshold for "jump" had been fixed before the test; the result is borderline (CLAAS−station p = 0.09, CLAAS−ERA5 p = 0.02). Main results use 2015–2024; CDR (2015–2020) and ICDR (2021–2024) are shown as a sensitivity analysis regardless of the test; test results reported as they are. Supersedes D3b | Choosing a threshold after seeing the result would be outcome-driven; showing both views lets the reader judge. Decided by Claude at the user's request ("decide what a peer-reviewed journal expects") | **[decided]** |
| D5 | 2026-11-14 | Method-switch test (user chose to do it now, option a): 15 observer→instrument stations; switch month = month after the last month with ≤ 50 % instrument hours (DWD hourly V_N_I); months with 10–90 % instrument share dropped; station used only with ≥ 12 months before and after; anomaly of station − reference (ERA5; CLAAS-3 as second reference) minus the station's calendar-month mean; difference-in-differences against the 36 stable instrument stations over the same months; mean over stations, bootstrap 95 % CI (10 000, seed 1), sign test | Tests H2's premise that instrument stations read higher than observers at the same site. Rules fixed and committed before running (`src/method_switch_test.py`) | **[decided, pre-registered]** |
| D6 | 2026-11-14 | Main message (option a): we cannot say definitively which dataset is right, because the referee itself depends on the measurement method; we show that ERA5 and CLAAS-3 diverge most in summer (independent of the referee and of the CDR/ICDR period), and that the attribution to ERA5 vs satellite is sensitive to the choice of referee | User's choice | **[decided]** |
| D4 | — | Treatment of `V_N = -1` (affects only hourly-based checks; MO_N is DWD's own) | — | **[open]** |

Selected stations (D2a + D2b), 39 ids: 00298 00342 00403 00427 00591 00596 00662 00704
00963 01200 01503 01544 01694 01759 01869 02115 02794 02907 03032 03086 03093 03196 03639
03897 04024 04039 04371 04625 04745 05109 05142 05158 05349 05516 05839 05930 06163 07351
07374. Extent: 52.08–55.01°N, 6.94–14.07°E. **[verified]** (to be implemented in phase-4
code, not hand-copied)

## 5. User's hypotheses (phase 2, in the user's words)

- H1: The slanted satellite view may cause CLAAS-3 to overestimate cloud cover.
  Still needed: mechanism, which cloud types, and a test with the available data.

- H2 (2026-11-14), on why the 36 instrument stations read higher than both ERA5 and
  CLAAS-3 in every month: "ceilometre sadece tepesine baktığı için fazla okuyor olabilir,
  yani gökyüzünün çok küçük bir kısmını gözledikleri için hassasiyetin bozulma riski
  önemli diyebiliriz" (based on S4).
  Supervisor feedback: S4 talks about *precision* (random error); the observed offset is
  a *bias* (same sign in all 12 months and across stations). Random error from a small
  sky sample averages out over 10 years × 36 stations, so H2 as stated predicts noise,
  not a systematic excess. Still needed: a mechanism that makes a point/ceilometer value
  systematically higher, and a test. Test done (D5, §8): user chose to run it now.

- H3 (2026-11-14), after the D5 test: "evet destekliyor bence, cihaz daha yüksek okuyor.
  İnsanlarda scenery ile ilgili sorun var, geceleri (ve yazın konvektif bulutlar)."
  Supervisor feedback: (1) given the caveat in §8 (gradual rise, changing composition),
  "consistent with" is the defensible wording, not "shows". (2) The two cited S4
  mechanisms point in opposite directions: night → observers report *less* cloud
  (would make instrument > observer); summer scenery effect → observers report *more*
  convective cloud (would make instrument < observer in summer). The hypothesis must say
  which dominates and predicts a direction per season. (3) H3 moves the question from
  "ceilometers read too high" to "observers read too low (at night)": which referee is
  closer to the truth is not known from our data, and the attribution (ERA5 vs CLAAS-3
  share) depends on it. **[open: user's Discussion point]**

## 5b. Claude's interpretation (at the user's request, 2026-11-14)

The user asked Claude to develop the interpretation. Everything in this subsection is
Claude's reading of our results plus sources S3/S4 only. The user will be examined on
these points before submission. Evidence strength is given for each point.

- **I1 — The referee offset is at least partly a property of the referee.**
  Facts: the 36 instrument stations read 0.03–0.05 above both ERA5 and CLAAS-3 in every
  season (Table 1); the 3 observer stations are within about ±0.03 of both; at the 11
  switching stations the instrument period reads about +0.024 higher relative to ERA5
  than the observer period (D5). Reading: these three facts point the same way — the
  constant offset to instrument stations is, to a large part, tied to the measurement
  method, so it should not be presented as an ERA5 or CLAAS-3 error. S4 documents one
  mechanism on the observer side (night-time underestimation); our data cannot tell
  whether observers read too low or instruments too high.
  Strength: moderate (n = 3 observer stations, n = 11 switch stations, gradual-rise caveat).
- **I2 — The summer divergence is the referee-independent result.**
  Facts: ERA5 − CLAAS-3 at the stations is largest in JJA (+0.022; CDR +0.012, ICDR
  +0.035) and within ±0.01 in other seasons. In JJA, CLAAS − station is more negative than
  ERA5 − station for BOTH referee types (instrument −0.049 vs −0.027; observer −0.027 vs
  −0.003). Reading: the direction "in summer CLAAS-3 is lower than ERA5, and further from
  the stations" holds for both kinds of referee, so it does not depend on the referee
  question in I1 — only its size does. Strength: good for the direction (both referee
  types, both periods); weak for the size (observer n = 3).
  Physical mechanism for the summer difference: **not proposed** — Claude has no checked
  source; any mechanism (e.g. how small broken convective clouds are treated by a binary
  pixel mask vs a model grid-box fraction) would be speculation and needs literature
  before it enters the paper.
- **I3 — H1 (viewing angle) is not visible as a general overestimate at land stations.**
  Facts: S3/S4 document CLAAS-3 overestimation at high viewing angles; our VZA is 60–65°.
  But at land stations CLAAS-3 is about equal to ERA5 outside summer and lower in summer.
  Reading: in our data a viewing-angle overestimate is not visible at land stations
  relative to ERA5; it may exist and be offset by something else — we cannot separate
  this. The higher CLAAS-3 values over sea and at Baltic coast/island stations (Fig 1,
  Fig 3) are a separate pattern that we did not analyse (surface type) → next_questions.
  Strength: weak either way; state as an open point.
- **I4 — The CLAAS-3 change around 2020/21 looks like a satellite-side drift, not a
  break in our main result.** Facts: CLAAS − station shifts −0.017 after 2021 (p = 0.09),
  ERA5 − station does not (p = 0.96); the decline is gradual from about 2020; S3 reports
  "slight anomalies [...] after 2018, which originate from nighttime observations"; S4
  found ICDR and TCDR highly consistent in their 2020 overlap. Reading: consistent with
  a slow satellite-side drift rather than a step caused by the ICDR switch itself; the
  summer maximum of ERA5 − CLAAS holds in both periods. Strength: moderate.

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

### Fig (b) `figures/fig_b_seasonal_cycle.png` — seasonal cycle at the stations
Method: ERA5 and CLAAS-3 sampled at each selected station (nearest cell; max distance
14.1 km ERA5, 3.1 km CLAAS-3) only in months with MO_N → identical sampling for all
three (4052 station-months: 3742 instrument, 310 observer). Per-station 12-month
climatology, then mean over stations. Numbers: `data/processed/fig_b_monthly_climatology.csv`.
This replaces the sampling caveat of fig (a) for station comparisons. **[verified]**

Seasonal means (fraction), instrument stations, n = 36:

| Season | Station | ERA5 | CLAAS-3 | ERA5−station | CLAAS−station | ERA5−CLAAS |
|---|---|---|---|---|---|---|
| DJF | 0.818 | 0.783 | 0.789 | −0.035 | −0.029 | −0.006 |
| MAM | 0.659 | 0.622 | 0.622 | −0.036 | −0.037 | 0.000 |
| JJA | 0.639 | 0.611 | 0.590 | −0.027 | −0.049 | +0.021 |
| SON | 0.741 | 0.709 | 0.701 | −0.032 | −0.040 | +0.008 |

Observer stations, n = 3: ERA5−station −0.009/−0.009/−0.003/+0.009 and
CLAAS−station −0.002/−0.008/−0.027/+0.014 (DJF/MAM/JJA/SON).

Descriptive observations **[verified]**:
- Instrument stations: both ERA5−station and CLAAS−station are negative in all 12
  months (ERA5 −0.046…−0.013, CLAAS −0.053…−0.019).
- Observer stations: differences lie between −0.039 and +0.027; positive in Oct–Dec.
- ERA5−CLAAS at instrument stations is largest in Jun (+0.035), Aug (+0.029), Sep (+0.022);
  within ±0.01 in all other months.
- Inter-station spread (25–75 %) of the differences is 0.02–0.06 wide, i.e. comparable
  to or larger than the mean differences.

### Fig (c) `figures/fig_c_station_scatter.png` — station seasonal means, grid vs station
Numbers: `data/processed/fig_c_station_seasonal_means.csv`, `fig_c_stats.csv`. Statistics
across the 36 instrument stations (bias = grid − station): **[verified]**

| Season | ERA5 bias | ERA5 RMSE | ERA5 r | CLAAS bias | CLAAS RMSE | CLAAS r |
|---|---|---|---|---|---|---|
| DJF | −0.035 | 0.039 | 0.64 | −0.029 | 0.041 | 0.20 |
| MAM | −0.036 | 0.047 | 0.50 | −0.037 | 0.053 | 0.22 |
| JJA | −0.027 | 0.041 | 0.58 | −0.049 | 0.065 | 0.33 |
| SON | −0.032 | 0.040 | 0.57 | −0.040 | 0.055 | 0.14 |

- Across stations, ERA5 tracks the station-to-station differences more closely
  (r 0.50–0.64) than CLAAS-3 (r 0.14–0.33) in every season. **[verified]**
- Largest positive CLAAS−station (mean of seasons): Schönhagen (Ostseebad) +0.057,
  Greifswalder Oie (island) +0.047, Boltenhagen +0.027 — Baltic coast/island sites.
  Most negative: Quickborn −0.086, Schwerin −0.085, Marnitz −0.083. **[verified]**
- Observer stations (n = 3): |bias| ≤ 0.027 in all seasons (r not meaningful with n = 3).

### Break test (D3) `figures/figS1_break_test_2021.png`, `data/processed/break_test_2021.csv`
Instrument stations, matched months, station seasonal cycle of each difference
removed, averaged over stations (10–35 stations per month). Shift = mean(2021–2024) −
mean(2015–2020); exact permutation test over whole years (210 splits). **[verified]**

| Series | Shift | p |
|---|---|---|
| CLAAS-3 − station | −0.017 | 0.09 |
| ERA5 − station (control) | −0.001 | 0.96 |
| CLAAS-3 − ERA5 (at stations) | −0.016 | 0.02 |

- Visual: the CLAAS-3 − station running mean declines gradually from about 2020 and
  is most negative in 2024; it does not look like a single step at 2021-01. **[verified, visual]**
- D3 had not fixed in advance what counts as "a jump"; resolved by D3c (sensitivity
  analysis for both periods, no threshold).

### Table 1 `data/processed/table1_seasonal_differences.csv` (instrument stations, n = 36)
ERA5−CLAAS at stations by period (DJF/MAM/JJA/SON): 2015–2024 −0.006/+0.001/+0.022/+0.007;
CDR 2015–2020 −0.012/−0.001/+0.012/−0.005; ICDR 2021–2024 +0.004/+0.003/+0.035/+0.021.
ERA5−station: CDR −0.039…−0.028, ICDR −0.045…−0.026. CLAAS−station: CDR −0.040…−0.027,
ICDR −0.061…−0.033. All 36 stations have every calendar month in both sub-periods. **[verified]**
- JJA has the largest ERA5−CLAAS difference in all three periods. **[verified]**
- CLAAS−station is more negative in the ICDR period in every season; ERA5−station
  changes by ≤ 0.014 between periods. **[verified]**

## 9. Sources (read 2026-11-14) and documented statements

Statements below are quoted from the sources. They are literature for the user's
phase-5 interpretation; Claude has not linked them to our results.

- **S1** CLAAS-3 DOI landing page, https://doi.org/10.5676/EUM_SAF_CM/CLAAS/V003 →
  wui.cmsaf.eu. Citation: Meirink, J. F.; Karlsson, K.-G.; Solodovnik, I.; Hüser, I.;
  Benas, N.; Johansson, E.; Håkansson, N.; Stengel, M.; Selbach, N.; Schröder, M.;
  Hollmann, R. (2022): CLAAS-3: CM SAF CLoud property dAtAset using SEVIRI - Edition 3,
  Satellite Application Facility on Climate Monitoring, DOI:10.5676/EUM_SAF_CM/CLAAS/V003.
- **S2** CDS catalogue entry `reanalysis-era5-single-levels-monthly-means` (layout JSON on
  object-store.os-api.cci2.ecmwf.int). Required citation: "Copernicus Climate Change
  Service (2023): ERA5 monthly averaged data on single levels from 1940 to present.
  Copernicus Climate Change Service (C3S) Climate Data Store (CDS). DOI:
  10.24381/cds.f17050d7 (Accessed on DD-MMM-YYYY)". Key reference listed there:
  Hersbach et al. (2020), The ERA5 global reanalysis, doi:10.1002/qj.3803.
  How monthly means of instantaneous fields (tcc) are formed: **not found** in S2.
- **S3** CM SAF Product User Manual, SEVIRI cloud products, CLAAS Edition 3,
  SAF/CM/KNMI/PUM/SEV/CLD, Issue 3.1, 08.08.2022.
  https://www.cmsaf.eu/SharedDocs/Literatur/document/2022/saf_cm_knmi_pum_sev_cld_3_1_final_pdf.pdf
  - "users should keep in mind that CFC is overestimated at high viewing angles, i.e.
    towards the edge of the SEVIRI disk." (§4.1, Recommended applications)
  - "Near the SEVIRI sub-satellite point MODIS CFC tends to be higher than CLAAS-3, while
    the opposite is true towards the edge of the disk. This feature was also found in the
    comparisons with SYNOP data, and is consistent with the expectation that retrieved
    cloud cover increases with viewing angle." (§4.1, Validation)
  - "CLAAS-3 CFC is stable over time [...] although it does feature slight anomalies in
    the years 2010-2013 and after 2018, which originate from nighttime observations and
    are most likely related to the calibration of some of the SEVIRI infrared channels"
    (§4.1, Validation)
  - CLAAS-3 vs SYNOP: "very good agreement with a small and stable bias of 0.2% in average"
    (§4.1)
- **S4** CM SAF Validation Report, SEVIRI cloud products, CLAAS Edition 3,
  SAF/CM/KNMI/VAL/SEV/CLD, Issue 3.1, 08.08.2022.
  https://www.cmsaf.eu/SharedDocs/Literatur/document/2022/saf_cm_knmi_val_sev_cld_3_1_final_pdf.pdf
  - ICDR: "produced with the same algorithms as the TCDR"; a 2020 backwards-extension
    showed "a very high consistency between the ICDR and the TCDR with differences much
    smaller than the deviations of the TCDR to the reference observations."
  - SYNOP reference used only "SYNOP reports provided by manned airport stations"; "At
    manned stations the total cloud cover is visually estimated by human observers. In
    contrast, ceilometers are used for that purpose at automatic stations."
  - Observer errors listed: subjectivity; eye detection limit (cloud optical thickness
    ~0.5–1.0); at night "the overall effect is normally a negative bias"; "scenery effect,
    i.e. overestimation of convective cloud towers at a slanted view (Karlsson, 2003). This
    effect is most pronounced in the summer season and for low to moderate cloud amounts
    when the overestimation easily can reach values of 20-30 % (1-2 octas)."
  - Ceilometers: "considerable risk that the precision figures degrade, mainly because
    ceilometers only observe a very small fraction of the sky."
  - "a known tendency of CLAAS-3 to overestimate cloud cover at large viewing angles"
    (cloud-mask validation vs CALIOP).
- Not downloaded/committed: the PDFs themselves (EUMETSAT documents); URLs above.

### Method-switch test (D5) `figures/figS2_method_switch.png`, `data/processed/method_switch_test.csv`
Pre-registered in commit 1371c3e before running. **[verified]**
- 15 switching stations; 11 used (≥ 12 months before and after). Excluded by the rule:
  Arkona (0 months before), Magdeburg (0 before), Sankt Peter-Ording (5 before),
  Seehausen (5 after; hourly instrument share fluctuated until 2024-05).
- Difference-in-differences shift of station − reference after the switch:
  - vs ERA5: mean +0.024 (+0.20 octa), bootstrap 95 % CI [+0.014, +0.034], 10 of 11 positive,
    sign test p = 0.012
  - vs CLAAS-3: mean +0.023 (+0.18 octa), 95 % CI [+0.010, +0.033], 9 of 11 positive, p = 0.065
- Only negative station: Rostock-Warnemünde (−0.017 vs ERA5, −0.025 vs CLAAS-3).
- For scale: at the 36 stable instrument stations ERA5 − station is −0.027 … −0.036
  by season (Table 1).
- Caveat (visual, panel a): the aligned composite rises gradually from about 40 months
  before the switch rather than as a single step at month 0. The set of stations
  contributing changes along the axis (early switchers only contribute after, late
  switchers only before). A before/after mean does not distinguish a step from a trend.
  **[verified, visual]** — not tested further (would be post hoc).
