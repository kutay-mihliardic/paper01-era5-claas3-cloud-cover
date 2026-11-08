# CLAUDE.md — Monthly Research Notes

Talk to me in Turkish. Write code, comments, and file content in English.

## What this repo is

Part of a monthly research-note series in atmospheric science (clouds, satellite remote sensing). Each month: one small, reproducible study → preprint (ESS Open Archive / EarthArXiv) → Substack post. Long-term goal: a portfolio for PhD applications. Physics understanding matters more than code volume.

## Your role in this repo

You handle phases 3, 4 and 6 of a 9-phase cycle. Phases 1, 2, 5, 7, 8, 9 (question, physics, interpretation, writing) happen elsewhere and are mine.

| # | Phase | Gate (done when) |
|---|---|---|
| 3 | Data | Both datasets on disk; units and value ranges verified and reported to me |
| 4 | Analysis | Final figures saved in `figures/` |
| 6 | Code packaging | README, environment file, one-command run (`make all` or `python run.py`), tagged release |

## Rules

1. **Gates are hard.** Don't start a phase before the previous gate is passed. Ask me if unsure which phase we're in.
2. **No physics interpretation on your own.** Report what the data shows; don't explain *why*. If I ask for an interpretation, first ask me for my own hypothesis.
3. **Verify before plotting.** Check units (fraction vs percent), value ranges, missing values, grid alignment. Tell me what you checked.
4. **No scope creep.** New ideas go to `next_questions.md`, not into the current analysis.
5. **After phase 5, the analysis is frozen.** In phase 6, only clean and package; don't change results.
6. **AI log.** After each session, append to `ai_log.md`: what I asked, where you went wrong or were uncertain, how it was caught. Be honest about your own mistakes.
7. **Reproducibility.** Raw data in `data/raw/`, processed in `data/processed/`, code in `src/`, figures in `figures/`. No hardcoded absolute paths. Small raw data (< ~50 MB total, openly licensed) is committed to the repo; anything larger is downloaded by a script and git-ignored.
8. **Secrets.** Never write API keys, passwords or download credentials into code, CLAUDE.md, commits or logs. Read the CDS key from the environment / `~/.cdsapirc` only.
9. **Data licence.** CLAAS-3 is CC BY 4.0: README and any figure using it must credit "© EUMETSAT" and cite DOI 10.5676/EUM_SAF_CM/CLAAS/V003.
10. **Methods notes.** At the start of every session, read `methods_notes.md` (verified facts, decisions, open questions). Keep it up to date whenever something is verified, decided or left open. I should never have to remember these things myself.

## Current note

**Note #1 — Model error or satellite artefact? A three-way comparison of cloud cover over Northern Germany**
- Question: In which season does ERA5 total cloud cover deviate most from CLAAS-3 over Northern Germany, and — using DWD ground stations as a referee — how much of that deviation comes from ERA5 and how much from the satellite?
- Region: 52–55.5°N, 6–14.5°E (land-focused; seas secondary)
- Period: 2015–2024, monthly means
- Model: ERA5 total cloud cover (`tcc`, 0–1 fraction), Copernicus CDS via `cdsapi`
- Satellite: CM SAF CLAAS-3 cloud fractional cover (CFC, likely percent — verify)
- Referee: DWD station monthly mean cloud cover `MO_N` (octas, 0–8), opendata.dwd.de, via the `wetterdienst` Python package
- Three different units (fraction, percent, octas): convert all to one before any comparison and report the conversion.
- Planned figures: (a) side-by-side 10-year mean maps, (b) seasonal cycle of all three, (c) ERA5 and CLAAS-3 sampled at station locations vs station values
- Data on hand: `data/raw/claas3/` holds two CM SAF order archives (.tar): CDR v004 2015-01..2020-12 (72 monthly files) and ICDR v004i1 2021-01..2024-12 (48 files), already cut to 51.5–56°N, 5.5–15°E at 0.05°. Watch for a possible discontinuity at Jan 2021 (CDR → ICDR).
- Current phase: 3 (Data) — all three datasets on disk and checked; station-selection and break-handling decisions are being made (see `methods_notes.md` §4). No analysis code or figures yet.
