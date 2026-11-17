"""One-command pipeline for Note #1 (ERA5 vs CLAAS-3 vs DWD cloud cover).

    python run.py          # = python run.py all: reproduce every figure and table
                           #   from the data committed in this repository
    python run.py data     # re-download / re-derive the raw inputs (network; ERA5
                           #   needs a CDS account, see README). DWD updates its
                           #   archive, so re-downloaded data may differ slightly.
    python run.py list     # show the steps

Each step is a script in src/ and is run in order; the pipeline stops at the first error.
"""

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent

STEPS = {
    "data": [
        ("Download ERA5 monthly tcc (CDS key needed)", "src/download_era5.py", ["--force"]),
        ("Download DWD monthly MO_N", "src/download_dwd.py", ["--force"]),
        ("DWD measurement method per station (hourly files)", "src/dwd_station_metadata.py", []),
    ],
    "all": [
        ("Verify and extract CLAAS-3 archives", "src/extract_claas3.py", []),
        ("Figure 1: 10-year mean maps", "src/fig_a_mean_maps.py", []),
        ("Figure 2: seasonal cycle at stations", "src/fig_b_seasonal_cycle.py", []),
        ("Figure 3: station scatter by season", "src/fig_c_station_scatter.py", []),
        ("Table 1: seasonal differences + period sensitivity", "src/table1_seasonal_differences.py", []),
        ("Figure S1: CDR/ICDR break test", "src/break_test_2021.py", []),
        ("Figure S2: observer -> instrument switch test", "src/method_switch_test.py", []),
    ],
}


def run(target: str) -> int:
    for i, (label, script, args) in enumerate(STEPS[target], 1):
        print(f"\n[{target} {i}/{len(STEPS[target])}] {label}  ({script})", flush=True)
        t0 = time.time()
        result = subprocess.run([sys.executable, str(ROOT / script), *args], cwd=ROOT)
        if result.returncode != 0:
            print(f"FAILED: {script} (exit code {result.returncode})", file=sys.stderr)
            return result.returncode
        print(f"done in {time.time() - t0:.0f} s", flush=True)
    return 0


def main() -> int:
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    if target == "list":
        for name, steps in STEPS.items():
            print(name)
            for label, script, _ in steps:
                print(f"  {script:40s} {label}")
        return 0
    if target not in STEPS:
        print(f"unknown target '{target}'; use one of: {', '.join(STEPS)}, list", file=sys.stderr)
        return 2
    return run(target)


if __name__ == "__main__":
    sys.exit(main())
