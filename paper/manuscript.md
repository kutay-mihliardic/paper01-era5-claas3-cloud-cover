# Model error or satellite artefact? A three-way comparison of cloud cover over Northern Germany

**[AUTHOR NAME]**<sup>1</sup>

<sup>1</sup> [Affiliation or "Independent researcher"], [City, Country] · ORCID: [0000-0000-0000-0000]

Correspondence: [e-mail]

*Manuscript v1.0, 19 November 2026*

## Abstract

Monthly total cloud cover from the ERA5 reanalysis and from the CM SAF CLAAS-3 satellite
record are compared over Northern Germany (52–55.5°N, 6–14.5°E) for 2015–2024, using
German Weather Service (DWD) stations as a ground reference. All three sources are
converted to a cloud fraction between 0 and 1, and ERA5 and CLAAS-3 are sampled at 39
stations in the months for which each station reports. ERA5 and CLAAS-3 agree within
0.01 in winter, spring and autumn, but differ by 0.022 in summer (June–August), when
CLAAS-3 is lower; summer remains the season of largest difference in both the
2015–2020 and the 2021–2024 parts of the satellite record. Compared with the 36 stations
that measure cloud cover with ceilometers, both datasets are lower in every season, by
0.03–0.05. The three stations with human observers agree with both datasets to within
0.03 in every season. At 11 stations that switched from observer to ceilometer during the period,
the station value rises by 0.024 (about 0.2 octa) relative to ERA5 after the switch. The
summer difference between model and satellite is therefore a robust result, whereas the
question of which of the two is closer to the truth depends on how the ground reference
measures cloud cover.

## 1. Introduction

Clouds strongly modulate the Earth's radiation budget (Ramanathan et al., 1989), and
cloud–climate feedbacks remain one of the least understood parts of the climate system
(Stephens, 2005). Total cloud cover is therefore one of the most basic quantities
against which weather and climate models are evaluated. Two widely used long-term records of cloud
cover are the ERA5 reanalysis (Hersbach et al., 2020) and the CM SAF Cloud property
dAtAset using SEVIRI, edition 3 (CLAAS-3; Meirink et al., 2022), derived from the
geostationary Meteosat satellites. They are produced in fundamentally different ways —
one by a numerical weather prediction model constrained by observations, the other by
classifying satellite pixels as cloudy or clear — and they do not always agree.

When two such records disagree, ground stations are the usual referee. However, ground
observations of cloud cover are themselves made in two different ways: by human
observers who estimate the covered fraction of the whole sky, and by ceilometers that
detect clouds directly above the station (CM SAF, 2022b). Over Northern Germany the
geostationary satellite also views the surface at a steep angle — a viewing zenith angle
of 60–65° over our study region — where CM SAF reports that CLAAS-3 tends to
overestimate cloud cover (CM SAF, 2022a).

This note asks two questions: (1) in which season does ERA5 total cloud cover deviate
most from CLAAS-3 over Northern Germany, and (2) using DWD stations as a referee, how
much of that deviation comes from ERA5 and how much from the satellite? In addition to
answering them, we test the referee itself, using stations that changed their
measurement method during the study period.

## 2. Data

### 2.1 ERA5

We use ERA5 monthly averaged reanalysis of total cloud cover (`tcc`) on single levels at
0.25° resolution (Copernicus Climate Change Service, 2023). `tcc` is "the proportion of a
grid box covered by cloud", calculated "from the cloud occurring at different model
levels through the atmosphere", with "assumptions [...] about the degree of
overlap/randomness between clouds at different heights" (Copernicus Climate Change
Service, 2023). It is
therefore a model quantity: ERA5 is produced with 4D-Var data assimilation and forecasts
of one fixed version (cycle CY41R2) of the ECMWF Integrated Forecasting System (IFS), at
about 31 km horizontal resolution with 137 model levels (Hersbach et al., 2020; ECMWF,
2026). For analysed parameters such as `tcc`, the monthly means are averages of all
hourly analyses with a validity time in the month, 00–23 UTC (ECMWF, 2026). All months
used are final ERA5 (no preliminary ERA5T data).

### 2.2 CLAAS-3

CLAAS-3 cloud fractional cover (CFC) is derived from the SEVIRI imager on Meteosat
Second Generation, which scans every 15 minutes with pixels of 3 × 3 km² at the
sub-satellite point (CM SAF, 2022a). A pixel is counted as cloudy if its cloud
probability exceeds 50 %; the Level-3 CFC is "the fraction of cloudy pixels per grid box
compared to the total number of analyzed pixels in the grid box" (CM SAF, 2022a). We use
edition 3 (product version 3.0 in the file metadata) monthly means on a 0.05° grid, in
percent; daily means are based on all available 15-minute slots and the monthly mean is
the average of all daily means (CM SAF, 2022a). Data come from the climate data
record (CDR, 2015–2020) and the interim climate data record (ICDR, 2021–2024), which is
produced with the same algorithms (CM SAF, 2022b). All 120 months are present, with no
fill values and all records flagged as valid. The satellite platform attribute changes
several times during the period (Meteosat-10, -11 and, in January 2019, -9).

### 2.3 DWD stations

Station data are monthly means of total cloud cover (`MO_N`, in octas) from the DWD
Climate Data Center, retrieved with the wetterdienst package with unit conversion
switched off; the retrieved values are identical to the raw DWD files. Of 146 stations in
the study region, 76 report `MO_N` in 2015–2024. Comparing `MO_N` with the hourly cloud
cover of the same stations shows that `MO_N` is a 24-hour mean (median absolute
difference 0.007 octa, against 0.12–0.16 octa for a mean of the 06, 12 and 18 UTC
observations only).

The hourly data also record, for every hour, whether cloud cover was estimated by a
person or measured by an instrument. In 2015–2024, 48 stations used instruments
throughout, 12 used observers throughout, and 15 switched from observer to instrument
between 2016 and 2023.

## 3. Methods

**Common unit.** CLAAS-3 percentages are divided by 100 and DWD octas by 8; ERA5 is
already a fraction between 0 and 1.

**Station selection.** A referee must be homogeneous in time: a change of measurement
method introduces a jump that has nothing to do with the climate. We therefore exclude
the 15 stations that switched method. Because the question is seasonal, we further
require at least 21 of the 30 months of every season (DJF, MAM, JJA, SON); a criterion
on the total number of months alone would admit stations with only 16 of 30 winter or
autumn months. Of two co-located Potsdam series, the regular station is used. This leaves
39 stations: 36 with instruments and 3 with observers, reported separately because the
two methods measure cloud cover in different ways.

**Matched sampling.** ERA5 and CLAAS-3 are taken at the grid cell nearest to each station
(at most 14.1 km and 3.1 km away, respectively) and only in the months in which the
station reports, so that all three sources share exactly the same sampling.

**Climatologies and statistics.** For each station we form a 12-month climatology from
the available years, average these over stations and define a season as the mean of its
three months. Across stations we compute bias (dataset minus station), root-mean-square
error and Pearson correlation of the seasonal means.

**Sensitivity to the satellite record.** Results are given for 2015–2024 and, separately,
for the CDR (2015–2020) and ICDR (2021–2024) periods. To test for a change at the
CDR–ICDR transition, we remove each station's mean seasonal cycle from the differences
CLAAS-3 − station, ERA5 − station and CLAAS-3 − ERA5, average over stations, and compare
the means before and after January 2021. ERA5 has no product change at that date and
serves as a control: a shift in CLAAS-3 − station but not in ERA5 − station points to
the satellite side. Significance is assessed with an exact permutation test over all
210 ways of assigning 4 of the 10 years to the "after" group.

**Measurement-method test.** For the 15 switching stations, the switch month is the month
after the last month with at most 50 % instrument hours; months with 10–90 % instrument
hours are discarded, and stations need at least 12 months before and after the switch.
We compute the change of the deseasonalised station − ERA5 difference after the switch
and subtract the change over the same months at the 36 stable instrument stations
(difference-in-differences). The same is done with CLAAS-3 as reference. We report the
mean over stations with a bootstrap 95 % confidence interval and a sign test. These rules
were fixed before the test was run.

## 4. Results

### 4.1 Ten-year mean fields

Averaged over the study region, the 2015–2024 mean cloud fraction is 0.682 in CLAAS-3
and 0.674 in ERA5 (Fig. 1a, b). CLAAS-3 shows more spatial structure, ranging from 0.62
to 0.82, with higher values over the sea and along the coastlines than over land; ERA5
ranges only from 0.63 to 0.70. The selected stations report 0.63–0.77 (Fig. 1c). Because
the regional means include sea areas, the comparison with stations is made at the
station locations (Sections 4.2–4.3).

### 4.2 Seasonal cycle at the stations

At the 36 instrument stations, all three sources show the same seasonal cycle, with the
most cloud in winter (0.82 at the stations) and the least in spring and summer (0.66 and
0.64) (Fig. 2a; Table 1). ERA5 and CLAAS-3 agree closely in winter, spring and autumn
(ERA5 − CLAAS-3 between −0.006 and +0.007), but not in summer, when ERA5 exceeds CLAAS-3
by 0.022. The largest monthly differences occur in June (+0.035), August (+0.029) and
September (+0.022); in all other months the two datasets are within 0.01 of each other.

Both datasets are lower than the instrument stations in all twelve months (Fig. 2c):
ERA5 by 0.027–0.036 depending on the season and CLAAS-3 by 0.029–0.049, with the largest
CLAAS-3 difference in summer. At the three observer stations the monthly differences are much
smaller, between −0.039 and +0.027, and both are positive in October–December (Fig. 2b, d).

**Table 1.** Seasonal mean cloud fraction at the 36 instrument stations, 2015–2024, and
the ERA5 − CLAAS-3 difference in the two parts of the satellite record.

| Season | Station | ERA5 | CLAAS-3 | ERA5 − station | CLAAS-3 − station | ERA5 − CLAAS-3 | ERA5 − CLAAS-3, 2015–2020 | ERA5 − CLAAS-3, 2021–2024 |
|---|---|---|---|---|---|---|---|---|
| DJF | 0.818 | 0.783 | 0.789 | −0.035 | −0.029 | −0.006 | −0.012 | +0.004 |
| MAM | 0.659 | 0.622 | 0.622 | −0.036 | −0.037 | +0.001 | −0.001 | +0.003 |
| JJA | 0.639 | 0.611 | 0.590 | −0.027 | −0.049 | +0.022 | +0.012 | +0.035 |
| SON | 0.741 | 0.709 | 0.701 | −0.032 | −0.040 | +0.007 | −0.005 | +0.021 |

*Differences are computed from unrounded values and may differ by 0.001 from the difference of the rounded columns.*

### 4.3 Station-level agreement

Across the instrument stations, ERA5 reproduces the station-to-station differences in
seasonal mean cloud cover better than CLAAS-3 in every season (Fig. 3): the correlation
is 0.50–0.64 for ERA5 and 0.14–0.33 for CLAAS-3. The RMSE is 0.039–0.047 for ERA5 and
0.041–0.065 for CLAAS-3, the largest value being CLAAS-3 in summer. CLAAS-3 exceeds the
station value most at three Baltic coast or island stations (Schönhagen, Greifswalder Oie
and Boltenhagen) and falls furthest below it at inland stations (Quickborn, Schwerin and
Marnitz).

### 4.4 Robustness to the satellite record period

Summer is the season with the largest ERA5 − CLAAS-3 difference both in the CDR period
(+0.012) and in the ICDR period (+0.035) (Table 1). After January 2021, the deseasonalised
CLAAS-3 − station difference is lower by 0.017 (permutation p = 0.09) and CLAAS-3 − ERA5
by 0.016 (p = 0.02), while ERA5 − station does not change (−0.001, p = 0.96) (Fig. S1).
The decrease in the CLAAS-3 differences is gradual, beginning around 2020, rather than a
single step at the transition.

### 4.5 The measurement method of the referee

Eleven of the 15 switching stations meet the selection rules. After the switch from
observer to instrument, the station value increases relative to ERA5 by 0.024 on average
(95 % confidence interval 0.014–0.034; 10 of 11 stations positive; sign test p = 0.012),
which corresponds to about 0.2 octa (Fig. S2b). Relative to CLAAS-3 the increase is 0.023
(0.010–0.033; 9 of 11 positive; p = 0.065). The composite aligned on the switch month
(Fig. S2a) rises gradually over several years around the switch rather than in one step,
and the set of contributing stations changes along the time axis.

## 5. Discussion

**The summer difference does not depend on the referee.** The difference between ERA5
and CLAAS-3 is computed without the station data, so it is not affected by how the
stations measure cloud cover. It is largest in summer in both parts of the satellite
record, and in summer CLAAS-3 is further from both kinds of station than ERA5 is
(instrument stations: −0.049 versus −0.027; observer stations: −0.027 versus −0.003).
The direction of the summer difference is therefore robust; its size is less certain,
because it grows from +0.012 to +0.035 between the two periods and the observer group
contains only three stations. This study does not identify the physical cause of the
summer difference; doing so would require separating cloud types and the time of day.

**The referee depends on how it measures.** Three results point the same way: the
instrument stations are higher than both datasets in every season, the observer stations
are not, and stations become higher relative to ERA5 when they switch from observer to
instrument. Together they indicate that a substantial part of the offset to the
instrument stations is a property of the measurement method rather than an error of
ERA5 or CLAAS-3. The size of the switch effect (0.024) is comparable to the offset
between ERA5 and the instrument stations (0.027–0.036). The CM SAF validation report
lists known errors of human observations that act in opposite directions — observers
tend to report too little cloud at night, and too much convective cloud when it is seen
at a slant angle in summer — and notes that ceilometers sample only a very small part of
the sky (CM SAF, 2022b). Our data cannot tell whether observers report too little or
instruments too much. The answer to the second research question — how much of the
deviation belongs to ERA5 and how much to the satellite — therefore depends on which
referee is trusted, and should not be given as a single number.

**Viewing angle.** CM SAF documents that CLAAS-3 overestimates cloud cover at high
viewing angles (CM SAF, 2022a, 2022b), and the viewing zenith angle over Northern Germany
is 60–65°. At the land stations, however, CLAAS-3 is not higher than ERA5: the two agree
outside summer and CLAAS-3 is lower in summer. A general overestimation is thus not
visible at land stations relative to ERA5 in our data, although it could be present and
offset by other effects. The higher CLAAS-3 values over the sea and at Baltic coast and
island stations are a separate pattern that this study did not analyse.

**Stability of the satellite record.** The gradual decrease of the CLAAS-3 differences
from about 2020, together with the unchanged ERA5 − station difference, is consistent
with a slow change on the satellite side rather than a step caused by the CDR–ICDR
transition itself; CM SAF reports a very high consistency between the two records in
their overlap year (CM SAF, 2022b) and "slight anomalies [...] after 2018, which
originate from nighttime observations" (CM SAF, 2022a). The main result does not depend
on this: summer has the largest ERA5 − CLAAS-3 difference in both periods.

**Limitations.** (i) The observer group has only three stations, two of them in Berlin.
(ii) The method-switch test cannot separate a step from a gradual trend, and the
contributing stations change along the time axis. (iii) Grid values are taken from the
nearest cell, whereas stations measure at a point or over the visible sky.

## 6. Conclusions

1. Over Northern Germany, ERA5 and CLAAS-3 total cloud cover differ most in summer
   (ERA5 higher by 0.022 at the stations), and this holds in both parts of the CLAAS-3
   record.
2. Against ceilometer stations both datasets are lower in every season by 0.03–0.05,
   but a comparable offset appears when a station switches from observer to ceilometer,
   so this offset is at least partly a property of the reference.
3. Attributing the model–satellite difference to one of the two requires knowing how the
   ground reference measures cloud cover; an independent reference (e.g. active remote
   sensing at a few sites) would be needed to settle it.

## Data and code availability

Code, input and processed data, and figures are available at
https://github.com/kutay-mihliardic/paper01-era5-claas3-cloud-cover/releases/tag/v1.0.0
(`make all` reproduces all figures and tables). ERA5, CLAAS-3 and DWD data are
distributed under CC BY 4.0 by their providers.

## Acknowledgements

The work performed was done (i.a.) by using data from EUMETSAT's Satellite Application
Facility on Climate Monitoring (CM SAF); CLAAS-3 data © EUMETSAT. ERA5 data: Copernicus Climate Change Service (C3S),
ECMWF. Station data: Deutscher Wetterdienst (DWD), Climate Data Center. Coastlines:
Natural Earth.

## Figures

![**Figure 1.** Mean cloud fraction 2015–2024: (a) CLAAS-3, (b) ERA5, (c) DWD stations (circles: instrument, squares: observer). Dashed box: study region. CLAAS-3: © EUMETSAT, doi:10.5676/EUM_SAF_CM/CLAAS/V003.](../figures/fig_a_mean_maps.png)

![**Figure 2.** Seasonal cycle at the stations, 2015–2024: (a, b) cloud fraction; (c, d) difference to the station, for the 36 instrument stations (a, c; band: 25–75 % of stations) and the 3 observer stations (b, d). ERA5 and CLAAS-3 are sampled at the stations in matched months.](../figures/fig_b_seasonal_cycle.png)

![**Figure 3.** Seasonal mean of ERA5 (top) and CLAAS-3 (bottom) at each station against the station value. Circles: instrument stations; open squares: observer stations; dashed: 1:1. Statistics refer to instrument stations.](../figures/fig_c_station_scatter.png)

## Supplementary figures

![**Figure S1.** Deseasonalised differences averaged over the instrument stations: CLAAS-3 − station, ERA5 − station and CLAAS-3 − ERA5, with the CDR–ICDR transition (solid vertical line), platform-attribute changes (dotted) and the means of both periods (dashed).](../figures/figS1_break_test_2021.png)

![**Figure S2.** Observer-to-instrument switch at 11 DWD stations: (a) composite of station − reference aligned on the switch month, minus the stable-station control; (b) difference-in-differences change per station.](../figures/figS2_method_switch.png)

## References

- CM SAF (2022a): Product User Manual, SEVIRI cloud products, CLAAS Edition 3,
  SAF/CM/KNMI/PUM/SEV/CLD, Issue 3.1, 8 August 2022.
- CM SAF (2022b): Validation Report, SEVIRI cloud products, CLAAS Edition 3,
  SAF/CM/KNMI/VAL/SEV/CLD, Issue 3.1, 8 August 2022.
- Copernicus Climate Change Service (2023): ERA5 monthly averaged data on single levels
  from 1940 to present. Copernicus Climate Change Service (C3S) Climate Data Store (CDS),
  doi:10.24381/cds.f17050d7 (accessed on 8 November 2026).
- ECMWF (2026): ERA5: data documentation. Copernicus Knowledge Base,
  https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation (accessed 19
  November 2026).
- Hersbach, H., Bell, B., Berrisford, P., et al. (2020): The ERA5 global reanalysis.
  Q. J. R. Meteorol. Soc., 146(730), 1999–2049, doi:10.1002/qj.3803.
- Meirink, J. F., Karlsson, K.-G., Solodovnik, I., Hüser, I., Benas, N., Johansson, E.,
  Håkansson, N., Stengel, M., Selbach, N., Schröder, M., Hollmann, R. (2022): CLAAS-3: CM
  SAF CLoud property dAtAset using SEVIRI – Edition 3, Satellite Application Facility on
  Climate Monitoring, doi:10.5676/EUM_SAF_CM/CLAAS/V003.
- Ramanathan, V., Cess, R. D., Harrison, E. F., Minnis, P., Barkstrom, B. R., Ahmad, E.,
  Hartmann, D. (1989): Cloud-radiative forcing and climate: results from the Earth
  Radiation Budget Experiment. Science, 243(4887), 57–63, doi:10.1126/science.243.4887.57.
- Stephens, G. L. (2005): Cloud feedbacks in the climate system: a critical review.
  J. Climate, 18(2), 237–273, doi:10.1175/JCLI-3243.1.
