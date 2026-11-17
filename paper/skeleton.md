# Paper skeleton — Note #1

**Working title:** Model error or satellite artefact? A three-way comparison of cloud cover
over Northern Germany

**Format:** short research note for a preprint server (ESS Open Archive / EarthArXiv).
Target ~2500–3500 words, 3 figures + 1 table in the main text, 2 supplementary figures.

**Rules for this file:** bullet points are facts, numbers and pointers, not prose. The
user writes the sentences. Every number comes from `methods_notes.md` (section given in
brackets) or from a file in `data/processed/`. Items marked ⚠ need the user's decision
or a source before writing.

**Key message (D6):** ERA5 and CLAAS-3 diverge most in summer — independent of the
ground referee and of the CLAAS-3 data-record period — while the split of "who is wrong"
depends on how the ground referee measures cloud cover.

---

## Abstract (≤ 250 words; write last)

1. Context: cloud cover from reanalysis and satellite records is widely used; they
   disagree, and ground stations are the usual referee.
2. Data: ERA5 tcc, CM SAF CLAAS-3 CFC, DWD station MO_N; Northern Germany (52–55.5°N,
   6–14.5°E); 2015–2024; monthly.
3. Method: all in fraction 0–1; grids sampled at 36 instrument + 3 observer stations in
   matched months; seasonal climatologies.
4. Results (numbers, §8 Table 1): JJA ERA5 − CLAAS-3 = +0.022 (other seasons within ±0.01);
   holds in 2015–2020 and 2021–2024; instrument stations read 0.03–0.05 above both
   datasets in all seasons; at 11 stations that switched from observer to instrument,
   the station reads ~0.2 octa (+0.024) higher after the switch relative to ERA5.
5. Implication: the summer divergence is robust; attributing it to model or satellite
   depends on the referee's measurement method.

## 1. Introduction

- Why total cloud cover matters (radiation budget, model evaluation). ⚠ needs 1–2
  references chosen by the user.
- ERA5 (Hersbach et al., 2020) and CLAAS-3 (Meirink et al., 2022) as widely used
  long-term records; geostationary view of Northern Germany at a viewing zenith angle
  of 60–65° (§3, computed).
- Ground observations as referee; known differences between observers and ceilometers
  (S4: CM SAF validation report).
- Research question (CLAUDE.md, verbatim): in which season does ERA5 deviate most from
  CLAAS-3, and how much of that comes from ERA5 vs the satellite, using DWD stations.
- One sentence on what the note adds: a referee check (method-switch test).

## 2. Data

### 2.1 ERA5 (§1, §2, §3, S2)
- Product: monthly averaged reanalysis, single levels, 0.25°, `tcc`, 2015–2024; final
  ERA5 only (expver 0001).
- Definition: verbatim CDS text (§3) — grid-box fraction with an overlap assumption.
- Citation: Copernicus Climate Change Service (2023), doi:10.24381/cds.f17050d7;
  Hersbach et al. (2020), doi:10.1002/qj.3803.

### 2.2 CLAAS-3 (§1, §2, §3, S1, S3, S4)
- CFC monthly means, 0.05°, CDR 2015–2020 + ICDR 2021–2024 (same algorithms, S4).
- Definition: fraction of cloudy pixels per grid box, cloud probability > 50 % (S3).
- Monthly = mean of daily means (`nobs` attribute); no missing months; record_status ok.
- Platform attribute changes (Meteosat-10/11/9) listed in §2.
- Credit: © EUMETSAT; Meirink et al. (2022), doi:10.5676/EUM_SAF_CM/CLAAS/V003.

### 2.3 DWD stations (§2)
- Monthly kl, MO_N in octas, via wetterdienst 0.185.0 (no unit conversion; soft
  plausibility; identical to raw file, Hamburg 120/120 months).
- MO_N verified to be a 24-h mean (median difference 0.007 octa vs hourly mean).
- Measurement method from hourly `V_N_I`: 48 instrument-only, 12 observer-only, 15
  switching stations in 2015–2024.
- Credit: Deutscher Wetterdienst.

## 3. Methods

- Unit conversion: CLAAS-3 % / 100; ERA5 as is; DWD octas / 8 (§3).
- Station selection (§4): D1 (Potsdam 03987, not 03988), D2a (no method change),
  D2b (every season ≥ 21/30 months) → 39 stations; D2c (instrument n = 36 and observer
  n = 3 reported separately). Say why the 15 switching stations are excluded (user asked).
- Matched sampling: nearest grid cell (max 14.1 km ERA5, 3.1 km CLAAS-3), only months
  with station data (§8 fig b).
- Climatology: per station 12 calendar-month means, then mean over stations; season =
  mean of its 3 months.
- Statistics across stations: bias, RMSE, Pearson r (Fig 3).
- Period sensitivity (D3c): 2015–2020 and 2021–2024 shown separately; break test with an
  exact permutation test over whole years (210 splits) (Fig S1).
- Method-switch test (D5, pre-registered in commit 1371c3e): rules as in §4 D5;
  difference-in-differences vs 36 stable instrument stations; bootstrap CI; sign test.

## 4. Results

### 4.1 Ten-year mean fields — Fig 1 (`figures/fig_a_mean_maps.png`)
- Box means: CLAAS-3 0.682, ERA5 0.674 (§8).
- CLAAS-3 range 0.62–0.82, higher over sea and along coasts; ERA5 smoother, 0.63–0.70.
- Note: box means include sea; station comparisons follow.

### 4.2 Seasonal cycle at the stations — Fig 2 + Table 1
- Table 1 (instrument stations, 2015–2024): station / ERA5 / CLAAS-3 / differences per
  season (§8). Source: `data/processed/table1_seasonal_differences.csv`.
- JJA: ERA5 − CLAAS-3 = +0.022; Jun +0.035, Aug +0.029, Sep +0.022; other months within ±0.01.
- Both datasets below instrument stations in all 12 months; observer stations within ~±0.03.

### 4.3 Station-level agreement — Fig 3 (`figures/fig_c_station_scatter.png`)
- Across stations ERA5 r 0.50–0.64, CLAAS-3 r 0.14–0.33 (every season).
- Largest positive CLAAS − station: Baltic coast/island sites (Schönhagen, Greifswalder
  Oie, Boltenhagen); most negative: inland (Quickborn, Schwerin, Marnitz).

### 4.4 Robustness to the CLAAS-3 record period — Table 1 + Fig S1
- JJA has the largest ERA5 − CLAAS-3 in both periods (CDR +0.012, ICDR +0.035).
- Break test: CLAAS − station −0.017 (p = 0.09), ERA5 − station −0.001 (p = 0.96),
  CLAAS − ERA5 −0.016 (p = 0.02); gradual decline from ~2020 rather than a step.

### 4.5 How the referee measures matters — Fig S2
- 11 of 15 switching stations usable; DiD +0.024 vs ERA5 (95 % CI 0.014–0.034, 10/11
  positive, p = 0.012); +0.023 vs CLAAS-3 (9/11, p = 0.065).
- Caveat: composite rises gradually; composition changes along the axis.
- Wording: "consistent with" (H3 feedback).

## 5. Discussion

⚠ The user writes this section. Material, with ownership marked:

- 5.1 Summer divergence (I2, Claude's interpretation): direction holds for both referee
  types and both periods; size uncertain. No physical mechanism proposed yet —
  ⚠ needs literature if one is to be named.
- 5.2 The referee (H2/H3 user; I1 Claude): instrument offset 0.03–0.05 vs switch effect
  ~0.024 vs observer stations ~0; S4 on observer night-time underestimation and scenery
  effect (opposite directions, H3 feedback); which referee is closer to truth is unknown.
- 5.3 Viewing angle (H1 user; I3 Claude): documented overestimate at high VZA (S3/S4)
  vs no general excess at land stations in our data; coastal pattern not analysed.
- 5.4 CLAAS-3 temporal stability (I4 Claude): S3 "slight anomalies after 2018";
  S4 ICDR/TCDR consistency.
- Limitations (from §4 open items and caveats): observer n = 3 (two in Berlin); D5
  gradual-rise caveat; nearest-cell sampling vs point measurement; `V_N = -1` code
  undefined; ERA5 monthly-mean construction not verified; CLAAS version label (3.0 vs
  "004" in file names) ⚠.

## 6. Conclusions (3 bullets)

1. ERA5 and CLAAS-3 diverge most in summer at Northern German stations; robust to period.
2. Against instrument stations both datasets are lower in every season, but this offset
   is at least partly a property of the referee.
3. Attributing model vs satellite error requires knowing the referee's measurement
   method; follow-ups in `next_questions.md`.

## Data and code availability

- Repository (GitHub) + tagged release (phase 6); `make all` / `python run.py` (phase 6).
- Data sources and licences as in README (CC BY 4.0 for all three).

## Acknowledgements / credits

- © EUMETSAT, CM SAF (CLAAS-3); Copernicus Climate Change Service / ECMWF (ERA5);
  Deutscher Wetterdienst.

## References (verified so far)

- Copernicus Climate Change Service (2023): ERA5 monthly averaged data on single levels
  from 1940 to present. C3S Climate Data Store (CDS). doi:10.24381/cds.f17050d7.
- Hersbach, H., et al. (2020): The ERA5 global reanalysis. Q. J. R. Meteorol. Soc.,
  doi:10.1002/qj.3803.
- Meirink, J. F., et al. (2022): CLAAS-3: CM SAF CLoud property dAtAset using SEVIRI –
  Edition 3. Satellite Application Facility on Climate Monitoring.
  doi:10.5676/EUM_SAF_CM/CLAAS/V003.
- CM SAF (2022): Product User Manual, SEVIRI cloud products, CLAAS Edition 3,
  SAF/CM/KNMI/PUM/SEV/CLD, Issue 3.1.
- CM SAF (2022): Validation Report, SEVIRI cloud products, CLAAS Edition 3,
  SAF/CM/KNMI/VAL/SEV/CLD, Issue 3.1.
- Karlsson (2003) is cited inside S4 for the scenery effect — ⚠ not read by us; cite
  only after reading.
- ⚠ Introduction references: to be chosen by the user.
