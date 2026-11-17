# Study notes — Note #1 (short version for review)

The teaching points from the project in one place. Details, numbers and sources:
`methods_notes.md` (section numbers in brackets).

## 1. How each dataset "sees" clouds (§3, §9)

| | ERA5 `tcc` | CLAAS-3 `cfc` | DWD `MO_N` |
|---|---|---|---|
| What it is | Model output (reanalysis), not a measurement | Satellite retrieval (SEVIRI on Meteosat, 36 000 km, every 15 min) | Ground station: human observer **or** ceilometer |
| How cloud is decided | Cloud scheme gives a cloud fraction per model layer; layers combined into one number with an **overlap assumption** | Each pixel gets a cloud probability; **> 50 % → cloudy** (binary). L3 value = fraction of cloudy pixels in the 0.05° box | Observer: estimates how many eighths of the **whole sky** are covered. Ceilometer: laser pointing **straight up**, cloud cover derived from the time series over one point |
| Kind of quantity | Area fraction of a grid box (~17 × 28 km) | Effectively a frequency of "cloudy" at a ~pixel ⚠ | Observer: sky-area fraction · Ceilometer: frequency at a point |
| Time | Hourly → monthly mean | 15-min → daily → monthly (mean of daily means) | Hourly → daily → monthly (verified 24-h mean) |
| Unit | 0–1 | % | octas (0–8) |

User's own pairing: ceilometer ↔ CLAAS (both a frequency), observer ↔ ERA5 (both an
area fraction). ⚠ Claude's teaching statement, not yet checked in literature.

**Viewing angle:** SEVIRI sees Northern Germany at 60–65° from vertical. CM SAF: "CFC is
overestimated at high viewing angles" (S3).

**Unit conversion:** % ÷ 100, octas ÷ 8. Example: 6 octas = 0.75; 75 % = 0.75.

## 2. The referee (§2, §4)

- A comparison with a referee only works if the referee is **homogeneous in time**. A
  change of instrument, method or location makes a non-climatic jump: a
  **homogeneity break (inhomogeneity)**.
- 15 DWD stations switched observer → ceilometer in 2015–2024 → excluded as referees (D2a).
- Completeness per **season** (≥ 21 of 30 months each), not only in total, because the
  research question is seasonal: a station missing many winters gives an unreliable
  winter mean (D2b). → 39 stations: 36 instrument, 3 observer, reported separately (D2c).
- Potsdam: two series at the same site → use only the regular station 03987; justify
  with criteria fixed in advance, not "the one whose values look right" (D1).

## 3. Method habits (§4, §8)

- **Fair comparison:** ERA5 and CLAAS-3 sampled at each station, only in months where the
  station has data (matched sampling).
- **Decide rules before seeing results** (pre-registration). Choosing a threshold after
  seeing the outcome is choosing the outcome. Switch-test rules were committed before the
  run (commit 1371c3e).
- **Control series:** to test the CLAAS-3 change in 2021, compare CLAAS − station with
  ERA5 − station. ERA5 has no product change in 2021, so if only CLAAS − station shifts,
  the satellite side is the suspect; if both shift, the cause is common (weather or station).
- **Difference-in-differences:** the switch effect at a station minus the change at
  stable stations over the same months → removes changes common to all.
- **Sensitivity analysis:** when a decision is uncertain, show both views (full period
  and CDR / ICDR sub-periods) instead of picking one (D3c).

## 4. Error types

- **Precision (random error):** values scatter around the truth; averages out over many
  samples. Ceilometers' small sky sample mainly hurts precision (S4).
- **Bias (accuracy, systematic error):** values are shifted in one direction; does not
  average out. Instrument stations reading higher than ERA5 and CLAAS-3 in every month
  and at most stations is a **bias**.
- A hypothesis must predict a **direction**: observers at night → too little cloud;
  observers in summer (scenery effect) → too much convective cloud. They push opposite ways.

## 5. Results (§8, Table 1)

- **Main result:** ERA5 and CLAAS-3 differ most in **summer** (JJA, ERA5 − CLAAS-3 = +0.022
  at the stations; other seasons within ±0.01). Holds in 2015–2020 and 2021–2024. It is
  independent of the referee because it compares the two datasets directly — the station
  is not in the difference.
- Instrument stations read 0.03–0.05 above both datasets in every season; the 3 observer
  stations agree within ~±0.03.
- Switch test (11 stations): after observer → instrument the station reads ~+0.024
  (~0.2 octa) higher relative to ERA5 — **consistent with** a method effect; caveat: the
  rise is gradual, not a clean step.
- Therefore: who is "wrong" (ERA5 or satellite) depends on which referee is trusted (D6).

## 6. Reproducibility

- `make all` reproduces every figure and table from the committed data.
- Release **v1.0.0** freezes the exact code + data behind the paper's numbers; `main`
  can keep changing. The paper cites the release, not the branch.
