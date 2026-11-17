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

## 2026-11-08 — Phase 3 (Data), session 1 (continued): referee check ("professor mode")

**Asked:** The user asked me to act as a supervisor and guide them with questions instead
of deciding for them.

**Facts found (DWD documentation and per-station metadata, not interpretation):**
- DWD's dataset description (DESCRIPTION_obsgermany-climate-monthly-kl_en.pdf) gives MO_N
  in 1/8 and does not explain monthly values above 8.
- Potsdam Säkularstation (03988): special secular series, ends 2019-12; MO_N is the
  arithmetic mean of daily means built from 3 fixed observation times (~07, 14, 21 local).
  The 9 months > 8 octas have QN = 1 (formal control only).
- A regular Potsdam station (03987) exists at practically the same location: 114 months
  in 2015–2024, max 7.44.
- Hamburg-Fuhlsbüttel (01975): cloud instrument metadata lists ceilometers (2008-06..2017-05
  and 2021-04..), i.e. instrumental, not visual; gap in the instrument list 2017-05..2021-04.

**User decision:** Use Potsdam 03987, drop 03988 (avoid two series at the same point).
I pointed out the justification should be an a-priori criterion (regular operational
series, longer record, QC level), not "the one whose values stay below 8".

**Uncertain on my side:** My description of CLAAS-3 `cfc` as a cloudy-observation
frequency within the 0.05° box, and of the DWD sampling, still needs to be checked
against the CLAAS-3 Product User Manual and the per-station Metadaten_Parameter files.

## 2026-11-08 — Phase 3 (Data), session 1 (continued): how the DWD referee measures

**Asked:** Build a per-station table of how cloud cover was measured (observer vs
instrument, sampling), keep teaching.

**Done:** `src/dwd_station_metadata.py` → `data/processed/dwd_cloud_method_by_station.csv`
and `..._by_station_year.csv`, from DWD hourly cloudiness (`V_N_I`: P = person,
I = instrument) and the monthly kl metadata. Station zips cached in `data/raw/dwd/zips/`
(git-ignored, ~73 MB).

**Facts (no interpretation):**
- 76 stations with MO_N data; 75 have an hourly cloudiness file (missing: 03988 Potsdam
  Säkularstation).
- Majority method per year, 2015–2024: 48 stations instrument only, 12 observer only,
  15 switch observer → instrument (first instrument year 2016–2023, e.g. Hamburg and
  Bremen 2022, Potsdam 03987 2020). The observer-only group has a median of 40 months of
  MO_N vs 102 (instrument only) and 113 (switching).
- MO_N matches the mean of all valid hourly V_N values (median abs. difference
  0.007 octa for instrument months, 0.010 for observer months), not the mean of the
  06/12/18 UTC terms (median 0.12–0.16). So for these stations MO_N is effectively a
  24-hour mean.
- Valid hours per day: median 23.9 (instrument) and 23.5 (observer) per station-year; the
  10th percentile for observer years is 16.0 h/day. Night share (21–03 UTC) ≈ 0.29 ≈ 7/24.
- Code V_N = -1 is not defined in DWD's hourly description; it occurs in 17,105 hours,
  more often in observer years (median share 0.8 % vs 0 %). Not resolved.

**Mistakes / uncertainty:**
- Reading the DWD CSV with polars inferred `value` as string (first rows empty); caught
  by a TypeError, fixed with an explicit schema. Analysis code must set the dtype.
- "Majority method per year" is a simplification; mixed months exist (197 station-months
  with both P and I).

## 2026-11-08 — Phase 3 (Data), session 1 (continued): decisions D2–D3, methods_notes

**Asked:** The user asked me to keep track of everything that should go into the paper
("I can't keep it in my head") and to lead; then answered the station-selection and
break-handling questions; approved a CLAUDE.md rule for `methods_notes.md`.

**Done:**
- Created `methods_notes.md` (facts with status tags, definitions, decisions, user's
  hypotheses, open questions, points the paper must state). CLAUDE.md: rule 10 added
  (read/maintain it each session); "Current phase" line changed from 2 to 3 — it still
  said only a connectivity test was allowed, which would have blocked the next session.
- Pointed out that CLAUDE.md assigns writing/interpretation to the user and suggested I
  keep notes, ask and critique, while the user writes. The user did not change the rule.
- Decisions recorded: D2a (no method change), D2b (per-season ≥ 21/30 months → 39
  stations, chosen over ≥ 84 months total), D2c (instrument and observer stations
  reported separately; observer n = 3), D3 (control-series test for the 2021 break).

**Where I went wrong / was uncertain:**
- Earlier in this session I told the user DWD MO_N "varies by station, maybe 3 times a
  day"; the hourly-data check showed it is a 24-h mean for the stations used. Corrected
  in the notes and told the user explicitly.
- The conceptual pairing (ceilometer ↔ CLAAS frequency, observer ↔ ERA5 area fraction)
  is my teaching statement, not from a cited source; marked [to verify] in the notes.
- Teaching the control-series test comes close to suggesting the analysis design. I
  framed it as a method and left the decision and the "what if a jump is found" part
  to the user.

## 2026-11-08 — Phase 4 (Analysis) start

**Asked:** User passed the phase 3 gate, said they had lost track of the overall
picture and had not seen any visual of the data yet; asked for a supervisor-style
overview.

**Done:** Overview (§0 of `methods_notes.md`, also a roadmap of phase 4 steps);
`src/load_data.py` (all three datasets in fraction 0–1; D1/D2 station rules in code,
reproducing the 39 stations, 36/3); `src/fig_a_mean_maps.py` → `figures/fig_a_mean_maps.png`;
descriptive numbers in `methods_notes.md` §8. CLAUDE.md current phase set to 4.

**Where I went wrong / was uncertain:**
- The user answered several conceptual questions before seeing any figure of the data.
  In hindsight a quick-look map right after the phase 3 checks would have helped.
- First render of fig (a) used a 0.50–0.85 colour range (fields looked flat), the study
  box was hidden under the data and the colour bar wasted space; the legend then
  covered stations. Caught by looking at the rendered PNG, fixed in three iterations.
- Station means use only available months while grid means use all 120 months;
  noted as a caveat, not yet matched.

## 2026-11-14 — Phase 4 (Analysis), session 2: figure (b)

**Asked:** Move on to figure (b); user chose option (a) for D3 (report CDR and ICDR
periods separately if a CLAAS-only jump is found). User also asked whether the paper
can be finished tonight.

**Done:** Read `methods_notes.md` first (rule 10); fixed a broken row in its decisions
table (D4 had ended up below the station list) and the stale "unit conversion not yet
done" heading; recorded D3b. Added `sample_at_stations` / `matched_station_table` to
`src/load_data.py` (ERA5/CLAAS-3 sampled at stations only in months with MO_N; spot
check of one station-month matched the raw CLAAS value). `src/fig_b_seasonal_cycle.py`
→ `figures/fig_b_seasonal_cycle.png` + `data/processed/fig_b_monthly_climatology.csv`.

**Where I went wrong / was uncertain:**
- The station line is drawn in neutral ink, which fails the categorical palette
  validator (lightness/chroma) by design; identity is carried by marker shape and
  direct labels. ERA5/CLAAS blue/orange pass (CVD ΔE 24.7).
- First render had the ERA5 and CLAAS-3 direct labels on top of each other; fixed.
- Choosing to compare at station locations with matched months (instead of box means)
  is an analysis design choice I made; documented in the notes so the user can object.

## 2026-11-14 — Phase 4, session 2 (continued): figure (c) and break test

**Done:** `src/fig_c_station_scatter.py` → `figures/fig_c_station_scatter.png` (+ two CSVs);
`src/break_test_2021.py` → `figures/figS1_break_test_2021.png` (+ CSV). Results in
`methods_notes.md` §8.

**Where I went wrong / was uncertain:**
- When I taught the D3 control-series test I did not ask the user to fix in advance
  what counts as "a jump" (threshold and which series). The result is borderline
  (CLAAS−station p = 0.09, CLAAS−ERA5 p = 0.02), so the decision is now harder to make
  without seeing the result. Caught when reading the output; reported to the user
  instead of applying D3b myself.
- The test assumes a step at 2021-01; the series looks more like a gradual decline.
  A step test is not designed for that; noted, not changed.
- fig (c) imports `station_climatology` from the fig (b) script; should move to
  `load_data.py` in phase 6.

## 2026-11-14 — Phase 4, session 2 (continued): D3c, Table 1, viewing angle

**Asked:** User asked me to decide the break-handling question "the way a peer-reviewed
journal would expect" and to lead more, since this is the first project.

**Done:** Decided D3c (full period main result; CDR/ICDR as sensitivity analysis
regardless of the test) and recorded it as my decision at the user's request.
`src/table1_seasonal_differences.py` → `data/processed/table1_seasonal_differences.csv`.
Computed the SEVIRI viewing zenith angle over the box (59.7–64.6° at 0°E), closing one
[to verify] item.

**Uncertain:** D3c is a methodological decision I made, not the user; flagged as such
in the notes so it can be revisited before phase 5 freezes the analysis.

## 2026-11-14 — Phase 4/5 boundary: sources for [to verify] items

**Done:** Web-fetch subagents could not reach ECMWF/CM SAF/doi.org (not in the network
allowlist). Found the verbatim ERA5 tcc definition and the required CDS citation in the
CDS catalogue layout JSON (allowed host). Added doi.org, www.cmsaf.eu, wui.cmsaf.eu to the
environment (user-approved card), read the CLAAS-3 PUM and Validation Report (Issue 3.1)
and the DOI citation. Quotes recorded in `methods_notes.md` §9; §3 definitions updated.

**Where I went wrong / was uncertain:**
- README cited the ERA5 dataset as "Hersbach et al. (2023)"; the CDS entry asks for
  "Copernicus Climate Change Service (2023)". Corrected; Hersbach et al. (2020) kept as
  the key ERA5 paper.
- The documents contain statements directly relevant to the user's hypotheses (viewing
  angle, observer vs ceilometer). I recorded them as quotes and did not link them to our
  results (rule 2); that is for the user in phase 5.
- Still unverified: how ERA5 monthly means of instantaneous fields are formed; "cloud
  fraction observations are not assimilated in ERA5"; my "one pixel per box" inference.

## 2026-11-14 — Phase 4 (continued): method-switch natural experiment (D5)

**Asked:** User chose to test H2's premise now (option a) rather than defer it.

**Done:** Wrote `src/method_switch_test.py`, recorded its rules as D5 and committed them
(1371c3e) before running. Result: DiD +0.024 vs ERA5 (10/11 stations positive, p = 0.012),
+0.023 vs CLAAS-3 (9/11, p = 0.065). Fig S2.

**Where I went wrong / was uncertain:**
- My console filter `grep -v -i warn` (meant to hide warnings) also hid the line for
  "Rostock-Warnemünde", so I briefly thought a station was missing. Caught by counting
  stations in the output CSV; no analysis change. Lesson: don't filter output by
  substrings that can appear in data.
- The event-study composite rises gradually before the switch rather than stepping;
  the before/after DiD cannot distinguish a step from a trend, and station composition
  changes along the axis. Recorded as a caveat; I did not add a post-hoc test.
- This analysis was added after the original figure plan (a–c); it was the user's
  explicit choice to include it in this note rather than in next_questions.md.

## 2026-11-14 — Phase 4 gate passed; phase 5 start; paper skeleton

**Asked:** User approved the figures as final (phase 4 gate), chose main message (a)
(D6), said they are not an expert and asked me to advance the interpretation, and asked
for the paper skeleton.

**Done:** CLAUDE.md current phase → 5. `methods_notes.md`: D6; §5b "Claude's
interpretation" (I1–I4) with evidence strength, explicitly separated from the user's
hypotheses H1–H3. `paper/skeleton.md`: section-by-section facts, numbers, figure and
source pointers, with ownership and ⚠ items; no prose. One more item in next_questions.md.

**Where I went wrong / was uncertain:**
- CLAUDE.md rule 2 and the phase split give interpretation to the user. The user
  explicitly asked me to develop it after giving their own hypotheses, so I did, but
  labelled every point as mine, graded the evidence, refused to propose an unsourced
  physical mechanism for the summer divergence, and added an AI-use statement to the
  skeleton. This is a deviation from the original division of labour and should be
  visible to anyone reading the repository.

## 2026-11-14 — Phase 6 (Code packaging)

**Asked:** Package the code. Also: whether teaching notes like the user's own summary of
the four "ways of seeing clouds" are being saved (yes: `methods_notes.md` §3, §5, §9).

**Done:** `run.py` + `Makefile` (`make all` from committed data, `make data` to
re-download), `requirements.txt` (pinned) and `environment.yml`, README rewritten.
Clean-ups without result changes: `station_climatology` moved to `load_data.py`; the
monthly instrument share is now produced by `dwd_station_metadata.py` and committed, so
the switch test no longer depends on git-ignored hourly zips. Verified by cloning the repo
into an empty directory, deleting all outputs, running `make all` and comparing SHA-256
hashes with the outputs before packaging: all 13 outputs identical, PNGs included.

**Where I went wrong / was uncertain:**
- Before packaging, `figS2` could not be reproduced from a fresh clone because it read
  git-ignored files; found while planning the clean-clone test.
- Earlier in this session I added an "AI use" section to the paper skeleton and pushed
  the topic more than the user wanted; removed at the user's request.

## 2026-11-17 — Phase 6: PR, merge, release tag

**Asked:** Open the PR to main (option a), then tag v1.0.0 after the user merged it.

**Done:** Read `methods_notes.md` at session start (rule 10). Opened PR #1; the user
merged it (merge commit bc03028). Re-ran `make all` on a clean checkout of main: all
outputs regenerated identical to the committed files. Created annotated tag `v1.0.0` on
bc03028 locally.

**Where I went wrong / was uncertain:**
- Pushing the tag failed five times ("unexpected disconnect while reading sideband
  packet"), while branch pushes work and a dry run succeeds; most likely this
  environment's git connection does not accept tag pushes. I retried with backoff first
  (as for a network error) before concluding it is not transient. The user creates the
  tag as a GitHub release instead.
- Release v1.0.0 published by the user via the GitHub UI on bc03028 (verified with git ls-remote). Phase 6 gate passed.

## 2026-11-17 — Exam preparation
- User asked to look at notes before answering the 10 exam questions. Created `study_notes.md` (the teaching points in one place, as promised earlier). Read `methods_notes.md` section list at session start (rule 10).
- Added to study_notes §7: ERA5 vs today's IFS (frozen 2016 version, homogeneity). User asked to review §7 again before submission; reminder recorded in methods_notes §6b.

## 2026-11-17 — Phase 7: draft v0.1

**Asked:** User said writing section by section with them would cost too much time and
asked me to write the paper. CLAUDE.md assigns writing to the user; the user decided
otherwise for this note.

**Done:** `paper/draft.md` (~3000 words: abstract, sections 1–6, Table 1, figure list,
references) using only numbers from `methods_notes.md` / `data/processed/` and the
sources read in this project. Unsourced or unchecked statements are marked [REF] or
[CHECK] instead of being filled in.

**Where I went wrong / was uncertain:**
- First version of Table 1 computed ERA5 − CLAAS-3 from rounded columns (MAM 0.000,
  JJA +0.021, SON +0.008 instead of +0.001, +0.022, +0.007). Caught by checking the table
  against the CSV before sending; fixed.
- The introduction needs one reference for the importance of clouds that I could not
  verify here ([REF]).
