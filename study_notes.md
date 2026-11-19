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

### Four ways of seeing clouds: frequency vs area fraction

- **Ceilometer:** asks at every moment, at one point, "is there cloud overhead — yes or
  no?", then averages over time. Result: a **frequency**.
- **CLAAS-3:** classifies each pixel at every scan as "cloudy or clear" (binary), then
  averages over time. Result: also a **frequency**.
- **Observer:** estimates how much of the sky is covered at that moment. Result: an
  **area fraction**.
- **ERA5:** gives how much of the grid box is covered. Result: also an **area fraction**.

So: ceilometer ↔ CLAAS-3 (frequency), observer ↔ ERA5 (area fraction). The spatial
footprints still differ: a point, a ~pixel, the sky dome, a ~25 km box.
⚠ Teaching statement, not yet checked in literature.

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

## 7. Background (not part of the paper): how models make clouds

⚠ General background from Claude's knowledge, not checked against sources in this
project. Check before citing.

**IFS, ERA5, AIFS — who is who**
- **IFS** (Integrated Forecasting System): ECMWF's physics-based weather model. It
  solves the equations of motion, thermodynamics and moisture on a grid.
- **ERA5** is not a separate model and does not "learn" from IFS: it *is* IFS (cycle
  CY41R2, about 31 km, 137 levels — verified in ECMWF's ERA5 documentation, S5) run over past decades with **data assimilation**
  — every 12 h the model's short forecast is combined with the observations available
  then. Clouds in ERA5 therefore come from the IFS cloud scheme, steered indirectly by
  the assimilated observations (temperature, humidity, wind, …).
- **AIFS** (Artificial Intelligence Forecasting System): ECMWF's machine-learning
  forecast model, trained on ERA5 and then on operational IFS analyses. It learns
  statistical relationships from that data; it has **no** physics equations and **no**
  parametrization schemes inside. It inherits what it learned — including the
  strengths and weaknesses of the IFS/ERA5 training data.

**ERA5 clouds vs today's IFS clouds**
- Same kind of physics: ERA5 clouds come from the IFS cloud scheme.
- But not identical to today's operational IFS: ERA5 uses one IFS version (2016),
  **frozen** for the whole record, at ~31 km; operational IFS is updated every year
  (cloud and convection schemes included) and runs at ~9 km for forecasting.
- Why freeze it? **Homogeneity** — the same reason we dropped DWD stations that
  switched method: if the model changed during the record, a change in ERA5 over time
  could come from the model update instead of the climate.
- Still [to verify]: how directly cloud observations enter ERA5 (§3 of methods_notes).
- 📌 Review again before the paper is submitted (user's request, 2026-11-17).

**Why parametrization exists**
- A model only "sees" the average state of each grid box. Processes smaller than a box
  (individual cumulus clouds, turbulence, cloud droplets) cannot be computed directly.
- A **parametrization** describes the net effect of these sub-grid processes on the
  box, from the resolved variables (temperature, humidity, wind). It is not made up:
  it is built from physics (e.g. a rising, mixing air parcel), but it needs
  simplifying assumptions and some numbers that are tuned against observations and
  high-resolution simulations — that is where uncertainty enters.

**Convective parametrization — when is it used?**
- **Coarse models (> ~10 km, e.g. ERA5 at ~31 km):** convective updrafts are only
  hundreds of metres to a few km wide → **always parametrized**. A mass-flux scheme
  decides *if* convection starts (trigger), *how strong* it is (closure, e.g. using
  instability/CAPE) and *how much* air mixes in (entrainment) — these choices are the
  uncertain part.
- **Convection-permitting models (≲ 3–4 km, e.g. DWD's ICON-D2 at ~2 km):** deep
  convection is resolved explicitly; shallow convection is still parametrized.
- **"Grey zone" (~1–10 km):** convection is partly resolved, partly not — the hardest
  range for scheme design.

**Cloud scheme and total cloud cover (link to §1)**
- In IFS, cloud fraction is a model variable in every layer (with cloud liquid and ice);
  convection feeds condensate into it.
- `tcc` combines the layer cloud fractions into one number with an **overlap
  assumption** (how clouds in different layers stack — e.g. maximally where adjacent,
  randomly otherwise). Different overlap choices give different `tcc` from the same
  layers.
