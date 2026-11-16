"""
Extract: download the raw Superstore sales dataset.

Tries two mirrors in order. If both fail (corporate firewall, etc.),
download manually from any of the URLs below and save the file to:
    data/raw/superstore.csv
"""

from pathlib import Path

import requests

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
RAW_FILE = RAW_DIR / "superstore.csv"

MIRRORS = [
    "https://huggingface.co/s-a-n-08/superstoredataset1/resolve/main/Sample%20-%20Superstore.csv",
    "https://raw.githubusercontent.com/leonism/sample-superstore/master/data/superstore.csv",
]


def extract() -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if RAW_FILE.exists():
        print(f"Raw file already exists: {RAW_FILE}")
        return RAW_FILE

    for url in MIRRORS:
        print(f"Trying {url} ...")
        try:
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()
            RAW_FILE.write_bytes(resp.content)
            print(f"Downloaded {len(resp.content):,} bytes -> {RAW_FILE}")
            return RAW_FILE
        except requests.RequestException as exc:
            print(f"  failed: {exc}")

    raise SystemExit(
        "All mirrors failed. Download the Sample Superstore CSV manually from "
        "https://www.kaggle.com/datasets/vivek468/superstore-dataset-final "
        f"and save it as {RAW_FILE}"
    )


if __name__ == "__main__":
    extract()
