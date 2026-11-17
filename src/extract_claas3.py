"""Verify and extract the CM SAF CLAAS-3 order archives.

The two .tar archives in data/raw/claas3/ are committed to git. This script
checks their MD5 checksums against the values published by CM SAF and
extracts the monthly NetCDF files next to them (the .nc files are git-ignored).

Usage (from the repository root or anywhere else):
    python src/extract_claas3.py
"""

import hashlib
import sys
import tarfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CLAAS3_DIR = REPO_ROOT / "data" / "raw" / "claas3"

# MD5 checksums as provided by CM SAF with the order.
ARCHIVES = {
    "ORD71208.tar": "4d1511bb27a1624149448cdb36a83345",  # CDR v004, 2015-01..2020-12
    "ORD71209.tar": "d25b4f5197cb97a9d56cfabe99e0bd70",  # ICDR v004i1, 2021-01..2024-12
}


def md5sum(path: Path, chunk_size: int = 1 << 20) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def extract(archive: Path, dest: Path) -> int:
    """Extract only plain .nc files with no directory components."""
    with tarfile.open(archive) as tar:
        members = tar.getmembers()
        for member in members:
            name = member.name
            if not member.isfile() or "/" in name or not name.endswith(".nc"):
                raise ValueError(f"Unexpected archive member in {archive.name}: {name}")
        # filter="data" blocks absolute paths, links and other unsafe members.
        tar.extractall(path=dest, filter="data")
    return len(members)


def main() -> int:
    total = 0
    for name, expected in ARCHIVES.items():
        archive = CLAAS3_DIR / name
        if not archive.exists():
            print(f"ERROR: missing {archive}", file=sys.stderr)
            return 1
        actual = md5sum(archive)
        if actual != expected:
            print(f"ERROR: MD5 mismatch for {name}: {actual} != {expected}", file=sys.stderr)
            return 1
        print(f"{name}: MD5 OK ({actual})")
        n = extract(archive, CLAAS3_DIR)
        print(f"{name}: extracted {n} files")
        total += n
    print(f"Total: {total} files in {CLAAS3_DIR.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
